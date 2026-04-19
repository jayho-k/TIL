# 03_Dynamic_Task_Mapping

> 대상 버전: Airflow 2.3+  
> 실전 케이스: Parser/Embedding API 비동기 파이프라인

---

## 1. 개념

Dynamic Task Mapping은 런타임에 task 수를 동적으로 결정하는 기능이다.  
`expand()`로 iterable을 넘기면 각 element마다 독립적인 Task Instance가 생성된다.

```python
# 정적: 미리 task 수를 알아야 함
task_1 = process(doc_id="doc_1")
task_2 = process(doc_id="doc_2")

# 동적: 런타임에 결정
results = process.expand(doc_id=["doc_1", "doc_2", ..., "doc_N"])
```

### 핵심 특성

- 각 mapped instance는 **독립적인 Task Instance** — 하나 실패해도 다른 index에 영향 없음
- downstream `expand()`도 같은 index끼리 1:1 매핑
- `finalize[i]`는 `wait_embed[i]`가 완료되는 순간 즉시 실행 — 전체 완료를 기다리지 않음

---

## 2. 실패 격리 — trigger_rule

### 기본값 ALL_SUCCESS의 문제

```
parse[0] ✅   parse[1] ❌   parse[2] ✅
    ↓              ↓              ↓
embed[0]       embed[1]       embed[2]
    ↓              ↓              ↓
            update_db_status
            (기본값: ALL_SUCCESS)
            → upstream 중 1개라도 실패 → 이 task 전체 실행 안 됨 ❌
```

### trigger_rule 종류

| TriggerRule | 동작 | 용도 |
|-------------|------|------|
| `ALL_SUCCESS` (기본값) | 모든 upstream 성공해야 실행 | 정상 흐름 |
| `ALL_DONE` | 성공/실패/skip 무관, 모두 종료되면 실행 | finalize, DB 상태 업데이트 |
| `NONE_FAILED` | 실패한 upstream 없어야 함 (skip 허용) | 부분 실패 허용 흐름 |
| `ONE_SUCCESS` | upstream 중 하나라도 성공하면 실행 | 병렬 중 하나만 성공해도 진행 |

### expand()와 ALL_DONE 조합

```python
# ✅ 각 finalize[i]는 wait_embed[i] 완료 즉시 독립 실행
@task(trigger_rule=TriggerRule.ALL_DONE)
def finalize(embed_result: dict):   # 단일 item
    ...
finalize.expand(embed_result=embedded)

# ❌ 전체 20개 완료를 기다림
@task(trigger_rule=TriggerRule.ALL_DONE)
def finalize(embed_results: list):  # 리스트 전체
    ...
finalize(embed_results=embedded)    # expand 아님
```

---

## 3. Airflow Pool — 동시 실행 제한

외부 API 서버의 동시 처리 한계를 Pool로 제어한다.

### Pool 생성

```
Airflow UI → Admin → Pools → +
  pool_name: doc_pdf_pool   slots: 6
  pool_name: ppt_pool       slots: 8
```

```python
from airflow.models import Pool
from airflow import settings

session = settings.Session()
session.add(Pool(pool="doc_pdf_pool", slots=6, description="doc/pdf 동시 처리 제한"))
session.add(Pool(pool="ppt_pool", slots=8, description="ppt 동시 처리 제한"))
session.commit()
```

### Pool 동작

```
문서 1000개 큐에 있어도:
  doc_pdf_pool = 6 slots → 동시 실행 6개
  ppt_pool     = 8 slots → 동시 실행 8개
  나머지는 Scheduler 큐에서 슬롯이 날 때까지 대기
```

---

## 4. AirflowRescheduleException — 비동기 API 폴링

비동기 API (job_id 반환 → status polling) 처리 시 `time.sleep()` 루프 대신 사용.  
raise하면 Worker 슬롯을 즉시 반납하고 지정 시각에 재실행된다.

```
실행 → HTTP 요청 (~1초) → 미완료
  → AirflowRescheduleException → Worker 즉시 해제
  → 10초 후 재큐 → Worker 재할당 → HTTP 요청 (~1초)
  → 완료 → return

Worker 점유 시간 = HTTP 요청 횟수 × ~1초 (전체 대기 중 극히 일부)
```

Pool(6~8개 동시) + AirflowRescheduleException 조합 → 사실상 Worker 부담 없음.

> **주의:** `AirflowRescheduleException`은 retry 카운트를 소진하지 않는다.  
> `retries=0`이어도 무한 reschedule 가능 → `execution_timeout` 필수.

---

## 5. 실전 DAG 구조 (Parser/Embedding 파이프라인)

### 요구사항

| 항목 | 내용 |
|------|------|
| 파이프라인 | Parser API → Embedding API (문서 내 순차) |
| 문서 수 | 수십 ~ 수천 개 가변 |
| API 타입 | 비동기 (job_id 반환 → polling) |
| 소요 시간 | 30초 ~ 2분 |
| API 동시 처리 제한 | doc+pdf 6개, ppt 8개 |
| DB 상태 | parsing → parsed → embedding → embedded → completed/failed |

### 전체 흐름

```
get_documents()
    ↓ expand(doc_id)
submit_parse(doc_id)         → DB: "parsing", job_id 반환
    ↓ expand
wait_parse(parse_info)       → Reschedule 폴링 → DB: "parsed"
    ↓ expand  [Pool: doc_pdf=6 / ppt=8]
submit_embed(parse_result)   → DB: "embedding", job_id 반환
    ↓ expand
wait_embed(embed_info)       → Reschedule 폴링 → DB: "embedded"
    ↓ expand  [Pool: doc_pdf=6 / ppt=8]
finalize(embed_result)       → DB: "completed"
    trigger_rule=ALL_DONE    on_failure_callback → DB: "failed"
```

### 코드

```python
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException, AirflowRescheduleException, AirflowSkipException
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta, timezone
import requests


def mark_failed(context):
    """실패 시 on_failure_callback — XCom에서 doc_id 추출해 즉시 DB 업데이트"""
    ti = context["task_instance"]
    parse_info = ti.xcom_pull(task_ids="submit_parse", map_indexes=ti.map_index)
    if parse_info:
        db.update(doc_id=parse_info["doc_id"], status="failed")


def mark_submit_failed(context):
    """submit_parse 실패 시 — 인자에서 직접 doc_id 추출"""
    ti = context["task_instance"]
    doc_id = ti.xcom_pull(task_ids="get_documents", map_indexes=ti.map_index)
    if doc_id:
        db.update(doc_id=doc_id, status="failed")


@dag(schedule=None, max_active_runs=1)
def document_pipeline():

    @task
    def get_documents() -> list[str]:
        docs = fetch_from_db()
        if not docs:
            raise AirflowSkipException("처리할 문서 없음")
        return docs

    @task(retries=1, on_failure_callback=mark_submit_failed)
    def submit_parse(doc_id: str) -> dict:
        db.update(doc_id=doc_id, status="parsing")
        resp = requests.post(PARSER_API, json={"doc_id": doc_id})
        resp.raise_for_status()
        return {"doc_id": doc_id, "job_id": resp.json()["job_id"]}

    @task(
        pool="doc_pdf_pool",
        retries=0,
        execution_timeout=timedelta(hours=2),
        on_failure_callback=mark_failed
    )
    def wait_parse(parse_info: dict) -> dict:
        resp = requests.get(f"{PARSER_API}/status/{parse_info['job_id']}")
        data = resp.json()

        if data["status"] == "FAILED":
            raise AirflowException(f"Parser failed: {parse_info['doc_id']}")

        if data["progress"] < 100:
            raise AirflowRescheduleException(
                reschedule_date=datetime.now(tz=timezone.utc) + timedelta(seconds=10)
            )

        db.update(doc_id=parse_info["doc_id"], status="parsed")
        return {"doc_id": parse_info["doc_id"], "result": data["result"]}

    @task(retries=1, on_failure_callback=mark_failed)
    def submit_embed(parse_result: dict) -> dict:
        db.update(doc_id=parse_result["doc_id"], status="embedding")
        resp = requests.post(EMBEDDING_API, json=parse_result)
        resp.raise_for_status()
        return {"doc_id": parse_result["doc_id"], "job_id": resp.json()["job_id"]}

    @task(
        pool="doc_pdf_pool",
        retries=0,
        execution_timeout=timedelta(hours=2),
        on_failure_callback=mark_failed
    )
    def wait_embed(embed_info: dict) -> dict:
        resp = requests.get(f"{EMBEDDING_API}/status/{embed_info['job_id']}")
        data = resp.json()

        if data["status"] == "FAILED":
            raise AirflowException(f"Embedding failed: {embed_info['doc_id']}")

        if data["progress"] < 100:
            raise AirflowRescheduleException(
                reschedule_date=datetime.now(tz=timezone.utc) + timedelta(seconds=10)
            )

        db.update(doc_id=embed_info["doc_id"], status="embedded")
        return {"doc_id": embed_info["doc_id"]}

    @task(trigger_rule=TriggerRule.ALL_DONE)
    def finalize(embed_result: dict | None):
        if embed_result is None:
            return  # on_failure_callback이 이미 "failed" 처리
        db.update(doc_id=embed_result["doc_id"], status="completed")

    docs        = get_documents()
    parse_infos = submit_parse.expand(doc_id=docs)
    parsed      = wait_parse.expand(parse_info=parse_infos)
    embed_infos = submit_embed.expand(parse_result=parsed)
    embedded    = wait_embed.expand(embed_info=embed_infos)
    finalize.expand(embed_result=embedded)
```

### 실행 흐름 (실패 포함)

```
doc_01: submit ✅ → wait_parse ✅ → submit_embed ✅ → wait_embed ✅ → finalize(completed) ✅
doc_02: submit ✅ → wait_parse ❌ → on_failure_callback(failed) ✅
                                  → finalize(None) ✅  ← ALL_DONE, 즉시 실행
doc_03: submit ✅ → wait_parse ✅ → ...

→ 각 문서 완료 즉시 독립 실행, 다른 문서 기다리지 않음
→ Pool이 동시 실행 수 제한 → API 서버 과부하 없음
```

---

## 6. 주의해야 할 엣지 케이스

### 6.1 up_for_retry — ALL_DONE이 기다리는 이유

`ALL_DONE`은 upstream이 **terminal 상태**여야 트리거된다.  
`up_for_retry`는 terminal이 아니므로 retry 소진 전까지 finalize가 실행되지 않는다.

```
task 실패 → retries > 0 → up_for_retry (대기) → 재실행 → ...
                                    ↑
                           ALL_DONE 여기서 멈춤

retries 소진 → failed (terminal) → ALL_DONE 트리거
```

**해결:** 폴링 task는 `retries=0`. 실패 판단은 폴링 로직 내부에서 직접 처리.  
**UI 테스트 시:** 단순 fail 클릭 → `up_for_retry`. 반드시 **"Mark Failed"** 사용.

---

### 6.2 AirflowRescheduleException ≠ retry

```
AirflowRescheduleException → retries 카운트 소진 안 함
retries=0이어도 무한 reschedule 가능
→ execution_timeout 필수 (무한 대기 방지)
```

---

### 6.3 Pool 슬롯과 DAG 동시 실행

Pool 슬롯은 DAG run 전체에서 공유된다.

```
DAG run A: wait_parse 6개 실행 중 → doc_pdf_pool 6슬롯 모두 점유
DAG run B: 동시 트리거 → wait_parse 대기 (슬롯 없음)
```

**해결:** `max_active_runs=1` 또는 pool slots ÷ 동시 task 수로 계산해서 설정.

---

### 6.4 submit_parse 실패 시 전파

`submit_parse[i]` 실패 → `wait_parse[i]`는 `upstream_failed` 상태로 실행되지 않는다.  
`on_failure_callback`을 `submit_parse`에도 붙여야 DB 상태를 업데이트할 수 있다.

---

### 6.5 DB 상태 idempotency

task Clear(재실행) 시 DB 업데이트가 중복 호출된다.

```python
# ❌ 단순 update → Clear 시 진행 중인 상태를 덮어씀
db.update(doc_id=doc_id, status="parsing")

# ✅ 상태 전이 조건 체크 후 update
db.update_if_status(doc_id=doc_id, from_status="pending", to_status="parsing")
```

---

### 6.6 빈 리스트 expand()

`get_documents()`가 빈 리스트 반환 시 expand task 전체가 `skipped`.  
`finalize`는 ALL_DONE이지만 upstream 없으므로 즉시 실행될 수 있다.

```python
@task
def get_documents() -> list[str]:
    docs = fetch_from_db()
    if not docs:
        raise AirflowSkipException("처리할 문서 없음")
    return docs
```

---

### 6.7 XCom 크기 주의

`expand()`에서 각 task가 반환하는 dict는 XCom으로 Meta DB에 저장된다.  
파싱 결과나 벡터 자체를 반환하면 DB가 빠르게 커진다.

```python
# ❌ 큰 데이터 직접 반환
return {"doc_id": doc_id, "content": full_parsed_text}

# ✅ 참조(경로, ID)만 반환
return {"doc_id": doc_id, "s3_path": "s3://bucket/parsed/doc_id.json"}
```

---

## 7. Deferrable Mode가 불필요한 이유 (이 케이스)

```
Deferrable의 이점: Worker 슬롯을 대기 중에 반납
Pool + AirflowRescheduleException으로 동일 효과 달성:
  - Pool(6~8 slots): 동시 실행 수 제한 → Worker 최대 6~8개
  - AirflowRescheduleException: Worker 점유 시간 ≈ HTTP 요청 ~1초
  - 실질 Worker 사용량: 거의 0에 수렴

Deferrable 추가 시 발생하는 비용:
  - Triggerer 별도 운영 + HA 구성 필수
  - asyncio 기반 코드 (aiohttp 등)
  - 분산 로깅으로 디버깅 복잡

결론: Pool 조건 하에서 Deferrable는 오버엔지니어링
```

Deferrable가 의미 있는 경우: Pool 제한 없이 수백 개 이상 동시 대기 + 수십 분 이상 대기.  
→ `02_Deferrable_Operators.md` 참고

---

## 참고

- `02_Deferrable_Operators.md` — Deferrable Mode 상세 원리 및 언제 쓸지
- [Airflow Dynamic Task Mapping 공식 문서](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html)
- [TriggerRule 종류](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules)
- [AirflowRescheduleException API](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/exceptions/index.html)
