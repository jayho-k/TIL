# Airflow Mode 선택 — Parser/Embedding API 파이프라인 케이스

> 조사일: 2026-04-19  
> 상태: 초안 (토론 완료)

---

## 요구사항 정의

| 항목 | 내용 |
|------|------|
| 파이프라인 | Parser API → Embedding API (문서 내 순차 실행) |
| 문서 수 | 수십 ~ 수백~수천 개 가변적 |
| API 타입 | 비동기 (job_id 반환 → status polling → progress 100% 시 다음 단계) |
| 소요 시간 | 빠르면 30초, 느리면 1분+ |
| API 동시 처리 제한 | doc+pdf 최대 6개, ppt 최대 8개 동시 처리 가능 |
| 실패 격리 | 1개 실패 시 나머지에 영향 없음 |
| DB 상태 | 각 문서 완료 즉시 상태 반영 (parsing → parsed → embedding → embedded → completed/failed) |

---

## Mode 선택 결론

> **`AirflowRescheduleException` + Airflow Pool + Dynamic Task Mapping**

Deferrable Mode 불필요. 이유는 아래 분석 참고.

---

## 핵심 문제 1: 1개 실패 시 전체 영향

### 원인: trigger_rule 기본값 ALL_SUCCESS

```
parse[0] ✅   parse[1] ❌   parse[2] ✅
    ↓              ↓              ↓
embed[0]       embed[1]       embed[2]
    ↓              ↓              ↓
            update_db_status
            (기본값: ALL_SUCCESS)
            → upstream 중 1개라도 실패 → 이 task 전체 실행 안 됨 ❌
```

`ALL_SUCCESS`는 upstream 중 하나라도 실패/skip이면 task 자체를 실행하지 않는다.

### 해결: trigger_rule=ALL_DONE

| TriggerRule | 동작 | 이 케이스 |
|-------------|------|-----------|
| `ALL_SUCCESS` (기본값) | 모든 upstream 성공해야 실행 | ❌ 1개 실패하면 실행 안 됨 |
| `ALL_DONE` | 성공/실패/skip 무관, 모두 종료되면 실행 | ✅ finalize에 적합 |
| `NONE_FAILED` | 실패한 upstream 없어야 함 (skip 허용) | ❌ 실패 시 실행 안 됨 |
| `ONE_SUCCESS` | upstream 중 하나라도 성공하면 실행 | ❌ 실패한 건 DB 업데이트 안 됨 |

> **주의:** UI 강제 fail과 코드 내 `raise AirflowException`은 동작이 다를 수 있다.  
> 실패 시뮬레이션은 코드에서 직접 `raise AirflowException`으로 테스트해야 정확하다.

---

## 핵심 문제 2: finalize가 전체 완료를 기다리는가?

**아니다.** `expand()`로 펼쳐진 downstream은 각 index가 독립적으로 실행된다.

```python
# ✅ 올바른 구조: finalize[i]는 wait_embed[i] 완료 즉시 실행
@task(trigger_rule=TriggerRule.ALL_DONE)
def finalize(embed_result: dict):   # 단일 item
    ...
finalize.expand(embed_result=embedded)

# ❌ 잘못된 구조: 전체 완료를 기다림
@task(trigger_rule=TriggerRule.ALL_DONE)
def finalize(embed_results: list):  # 리스트 전체
    ...
finalize(embed_results=embedded)    # expand 아님
```

Dynamic Task Mapping에서 같은 task의 서로 다른 index는 완전히 독립적이다.  
`parse[1]`이 실패해도 `parse[0]`, `parse[2]`, ...는 계속 실행된다.

---

## Airflow Pool — API 동시 호출 제한

### Pool 생성

```
Airflow UI → Admin → Pools → +
  pool_name: doc_pdf_pool   slots: 6
  pool_name: ppt_pool       slots: 8
```

```python
# 코드로 생성 시 (DAG 외부에서 1회 실행)
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
  나머지는 Airflow 스케줄러 큐에서 슬롯이 날 때까지 대기
```

---

## AirflowRescheduleException — 폴링 패턴

비동기 API polling 시 Worker 슬롯을 잡아먹는 `time.sleep()` 루프 대신 사용.  
`AirflowRescheduleException`을 raise하면 Worker 슬롯을 즉시 반납하고 지정 시각에 재실행된다.

```
실행 → HTTP 요청 (~1초) → 미완료
  → AirflowRescheduleException → Worker 즉시 해제
  → 10초 후 재큐 → Worker 재할당 → HTTP 요청 (~1초)
  → 완료 → return

Worker 점유 시간 = HTTP 요청 횟수 × ~1초 (전체 대기 중 극히 일부)
```

Pool(6~8개 동시)과 조합하면: 최대 Worker 6~8개, 각 1초 미만 점유 → 사실상 Worker 부담 없음.

---

## 최종 DAG 구조

### 전체 흐름

```
get_documents()
    ↓ expand(doc_id)
submit_parse(doc_id)         → DB: "parsing", Parser API 제출, job_id 반환
    ↓ expand
wait_parse(parse_info)       → AirflowRescheduleException 폴링 → DB: "parsed"
    ↓ expand  [Pool: doc_pdf=6 / ppt=8 슬롯 소비]
submit_embed(parse_result)   → DB: "embedding", Embedding API 제출, job_id 반환
    ↓ expand
wait_embed(embed_info)       → AirflowRescheduleException 폴링 → DB: "embedded"
    ↓ expand  [Pool: doc_pdf=6 / ppt=8 슬롯 소비]
finalize(embed_result)       → DB: "completed" / on_failure_callback: "failed"
    trigger_rule=ALL_DONE    → 각 문서 완료 즉시 독립 실행
```

### 코드

```python
from airflow.decorators import dag, task
from airflow.exceptions import AirflowException, AirflowRescheduleException
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta, timezone
import requests


def mark_failed(context):
    """실패 시 on_failure_callback — XCom에서 doc_id 추출해 즉시 DB 업데이트"""
    ti = context["task_instance"]
    parse_info = ti.xcom_pull(task_ids="submit_parse", map_indexes=ti.map_index)
    if parse_info:
        db.update(doc_id=parse_info["doc_id"], status="failed")


@dag(schedule=None)
def document_pipeline():

    @task
    def get_documents() -> list[str]:
        return ["doc_1.pdf", "doc_2.ppt", ..., "doc_N.pdf"]

    @task
    def submit_parse(doc_id: str) -> dict:
        db.update(doc_id=doc_id, status="parsing")
        resp = requests.post(PARSER_API, json={"doc_id": doc_id})
        resp.raise_for_status()
        return {"doc_id": doc_id, "job_id": resp.json()["job_id"]}

    @task(pool="doc_pdf_pool", on_failure_callback=mark_failed)
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

    @task(on_failure_callback=mark_failed)
    def submit_embed(parse_result: dict) -> dict:
        db.update(doc_id=parse_result["doc_id"], status="embedding")
        resp = requests.post(EMBEDDING_API, json=parse_result)
        resp.raise_for_status()
        return {"doc_id": parse_result["doc_id"], "job_id": resp.json()["job_id"]}

    @task(pool="doc_pdf_pool", on_failure_callback=mark_failed)
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

> **주의:** `pool` 파라미터는 `@task` 데코레이터에서 정적으로만 지정 가능하다.  
> doc/pdf와 ppt를 다른 Pool로 분리하려면 `wait_parse_doc`, `wait_parse_ppt`처럼 task를 분리하고, 문서 타입별로 `expand()` 전에 분기해야 한다.

### 실행 흐름 (실패 포함)

```
doc_01: submit ✅ → wait_parse ✅ → submit_embed ✅ → wait_embed ✅ → finalize(completed) ✅  ← 완료 즉시
doc_02: submit ✅ → wait_parse ❌ → on_failure_callback(failed) ✅
                                  → finalize(None) ✅  ← ALL_DONE, 즉시
doc_03: submit ✅ → wait_parse ✅ → submit_embed ✅ → wait_embed ✅ → finalize(completed) ✅

→ 각 문서 완료 즉시 독립 실행, 다른 문서 기다리지 않음
→ Pool이 동시 실행 수 제한 → API 서버 과부하 없음
```

---

## Deferrable Mode가 불필요한 이유

```
Deferrable의 이점: Worker 슬롯을 대기 중에 반납
이미 Pool + AirflowRescheduleException으로 동일 효과 달성:
  - Pool: 동시 실행 6~8개로 제한 → Worker 최대 6~8개만 사용
  - AirflowRescheduleException: Worker 점유 시간 ≈ HTTP 요청 ~1초
  - 실질 Worker 사용량: 거의 0에 수렴

Deferrable 추가 시 발생하는 비용:
  - Triggerer 프로세스 별도 운영 필요
  - HA 구성 필수 (단일 장애점)
  - asyncio 기반 코드 작성 (aiohttp 등)
  - 분산 로깅으로 디버깅 복잡

결론: Pool 조건 하에서 Deferrable는 오버엔지니어링
```

**실패 격리 문제도 Deferrable와 무관하다.**  
`trigger_rule=ALL_DONE` + `expand()` 패턴이 해결하는 문제이며, Deferrable로 바꿔도 `ALL_SUCCESS` 기본값이면 동일하게 전체 영향을 받는다.

---

## 주의해야 할 엣지 케이스

### 1. up_for_retry — ALL_DONE이 기다리는 이유

`ALL_DONE`은 upstream이 terminal 상태여야 트리거된다.  
`up_for_retry`는 terminal이 아니므로 retry가 소진될 때까지 summarize/finalize가 실행되지 않는다.

```
task 실패 → retries > 0 → up_for_retry (대기) → 재실행 → 실패 반복
                                    ↑
                           ALL_DONE 여기서 멈춤

retries 소진 → failed (terminal) → ALL_DONE 트리거
```

**해결:** 폴링 task는 `retries=0` 설정. 실패 판단은 폴링 로직 내부에서 직접 처리.

```python
@task(retries=0, on_failure_callback=mark_failed)
def wait_parse(parse_info: dict) -> dict:
    ...
```

**UI 테스트 시:** 단순 fail 클릭은 `up_for_retry` 진입. 반드시 **"Mark Failed"** 사용해야 즉시 terminal 상태로 전환됨.

---

### 2. AirflowRescheduleException은 retry가 아니다

```
AirflowRescheduleException → retries 카운트 소진 안 함
                           → retries=0이어도 무한 reschedule 가능

→ 반드시 execution_timeout 설정 필요 (무한 대기 방지)
```

```python
@task(
    retries=0,
    execution_timeout=timedelta(hours=2),   # 2시간 내 완료 안 되면 강제 실패
    on_failure_callback=mark_failed
)
def wait_parse(parse_info: dict) -> dict:
    resp = requests.get(f"{PARSER_API}/status/{parse_info['job_id']}")
    if data["progress"] < 100:
        raise AirflowRescheduleException(...)   # retry 아님, reschedule
    ...
```

---

### 3. Pool 슬롯과 DAG 동시 실행

Pool 슬롯은 **DAG run 전체에서 공유**된다.

```
DAG run A: wait_parse 6개 실행 중 → doc_pdf_pool 6슬롯 모두 점유
DAG run B: 동시 트리거 → wait_parse 실행 대기 (슬롯 없음)

→ 의도치 않은 처리 지연 발생 가능
```

**해결:** DAG 레벨에서 동시 실행 run 수 제한.

```python
@dag(
    schedule=None,
    max_active_runs=1,   # 동시에 1개 run만 허용
    # 또는
    max_active_runs=2,   # pool slots / 동시 task 수로 계산
)
def document_pipeline():
    ...
```

---

### 4. submit_parse 실패 시 전파

`submit_parse[i]`가 실패하면 하위 `wait_parse[i]`는 `upstream_failed` 상태가 되어 실행되지 않는다.  
이때 `on_failure_callback`은 `wait_parse`가 아닌 `submit_parse`에 붙어야 DB 상태를 업데이트할 수 있다.

```python
@task(retries=1, on_failure_callback=mark_failed)   # ← submit에도 callback 필요
def submit_parse(doc_id: str) -> dict:
    db.update(doc_id=doc_id, status="parsing")
    resp = requests.post(PARSER_API, json={"doc_id": doc_id})
    resp.raise_for_status()
    return {"doc_id": doc_id, "job_id": resp.json()["job_id"]}
```

단, `submit_parse`의 `mark_failed` callback은 XCom pull이 아닌 직접 인자에서 `doc_id`를 꺼내야 한다.

```python
def mark_submit_failed(context):
    ti = context["task_instance"]
    # submit_parse는 doc_id를 직접 인자로 받으므로 XCom pull 불필요
    doc_id = ti.xcom_pull(task_ids="get_documents", map_indexes=ti.map_index)
    if doc_id:
        db.update(doc_id=doc_id, status="failed")
```

---

### 5. DB 상태 idempotency — task 재실행 시 중복 업데이트

task Clear(재실행) 시 DB 업데이트가 중복 호출된다.  
`status="parsing"`을 이미 처리 중인 문서에 다시 쓰면 문제가 생길 수 있다.

```python
# ❌ 단순 update → Clear 시 진행 중인 상태를 덮어씀
db.update(doc_id=doc_id, status="parsing")

# ✅ 상태 전이 조건 체크 후 update
db.update_if_status(doc_id=doc_id, from_status="pending", to_status="parsing")
# 또는 upsert + updated_at 갱신 방식
```

---

### 6. get_documents()가 빈 리스트 반환 시

`expand()`에 빈 리스트가 들어오면 해당 task 전체가 `skipped` 상태가 된다.  
`finalize`는 `ALL_DONE`이지만 upstream이 없으므로 **즉시 실행**된다 — 의도치 않은 동작 가능.

```python
@task
def get_documents() -> list[str]:
    docs = fetch_from_db()
    if not docs:
        raise AirflowSkipException("처리할 문서 없음")  # DAG run 전체 skip
    return docs
```

---

### 7. XCom 크기 주의

`expand()`에서 각 task가 반환하는 dict는 XCom으로 저장된다.  
파싱 결과나 임베딩 벡터 자체를 반환하면 Meta DB가 빠르게 커진다.

```python
# ❌ 큰 데이터 직접 반환
return {"doc_id": doc_id, "content": full_parsed_text, "vectors": [0.1, 0.2, ...]}

# ✅ 참조(경로, ID)만 반환
return {"doc_id": doc_id, "s3_path": "s3://bucket/parsed/doc_id.json"}
```

---

## 참고

- `deferrable_operators.md` — Deferrable Mode 상세 원리
- [Airflow Dynamic Task Mapping 공식 문서](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html)
- [TriggerRule 종류](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#trigger-rules)
- [AirflowRescheduleException](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/exceptions/index.html)
