# Deferrable Operators — 심층 조사

> 조사일: 2026-04-19  
> 대상 버전: Airflow 2.2 ~ 3.2  
> 상태: 초안 (이관 전)

---

## 1. 개념 및 배경

### 1.1 왜 만들어졌나? (AIP-40)

Airflow 2.1 이전의 Sensor/외부 job 모니터링은 두 가지 방식이 있었다.

| 방식 | 문제 |
|------|------|
| **Poke mode** | Worker 슬롯을 연속 점유 — 대기 중에도 다른 task 실행 불가 |
| **Reschedule mode** | Scheduler가 rescheduling loop를 반복 — DB/Scheduler 부담 |

예를 들어 100개 Sensor가 각각 1시간 대기 중이면, poke 모드에서는 Worker 100개가 1시간 동안 아무것도 못 하고 점유된다.  
AIP-40은 이 문제를 "비동기 Trigger + 별도 Triggerer 프로세스"로 해결한다.

### 1.2 핵심 개념 한 줄 요약

> **Task가 외부 이벤트를 기다려야 할 때, Worker 슬롯을 반납하고 Triggerer 프로세스에 감시를 위임한다.**

---

## 2. 동작 원리

### 2.1 전체 사이클

```
[1] Worker: Operator.execute() 실행
        ↓
    self.defer(trigger=MyTrigger(...), method_name="resume_fn")
        ↓
    내부적으로 TaskDeferred 예외 발생
        ↓
[2] Task 상태: RUNNING → DEFERRED
    DB 저장: next_method, next_kwargs, trigger 직렬화 정보
    Worker 슬롯 해제 ← 핵심!

[3] Triggerer (asyncio event loop):
    Trigger.run() 실행 (비동기 제너레이터)
    - await asyncio.sleep(10) 반복
    - 조건 충족 시 yield TriggerEvent({...})

[4] Triggerer → Scheduler 신호
    Task 상태: DEFERRED → SCHEDULED

[5] Worker: Operator.resume_fn(context, event) 실행
    event.payload 처리 → 완료
```

### 2.2 TaskDeferred 예외 메커니즘

`defer()` 메서드 내부에서 `TaskDeferred` 예외를 발생시킨다.  
Task runner가 이 예외를 catch해서 trigger 정보를 DB에 저장하고 Worker를 해제한다.

```python
def execute(self, context):
    job_id = external_api.submit_job(...)

    self.defer(
        trigger=MyTrigger(job_id=job_id),
        method_name="check_status",   # 재개될 메서드명
        kwargs={"job_id": job_id},    # 재개 시 전달할 kwargs
        timeout=timedelta(hours=24)   # 최대 대기 시간
    )

def check_status(self, context, event):
    # Trigger가 yield TriggerEvent() 한 후 이 메서드로 재개됨
    if event.payload["status"] == "SUCCESS":
        return event.payload["result"]
    raise AirflowException(f"Job failed: {event.payload['error']}")
```

### 2.3 Triggerer 컴포넌트

- Scheduler, Worker와 독립적인 **별도 프로세스**
- Python **asyncio** 이벤트 루프로 수백~수천 개 Trigger 동시 실행
- 기본 용량: `triggerer.capacity = 1000` (1 Triggerer당 1000개)
- HA 구성: 여러 Triggerer 인스턴스가 DB heartbeat로 trigger를 분산 처리

### 2.4 asyncio 기반 — 왜 중요한가

Triggerer 안에서 Trigger는 모두 **하나의 asyncio 이벤트 루프** 위에서 실행된다.  
`time.sleep()` 같은 블로킹 호출 하나가 루프 전체를 멈춘다. 반드시 `await asyncio.sleep()` 사용해야 한다.

---

## 3. Trigger 클래스 구현

### 3.1 필수 구조

```python
from airflow.triggers.base import BaseTrigger, TriggerEvent
import asyncio
import aiohttp

class MyTrigger(BaseTrigger):
    def __init__(self, job_id: str, poll_interval: int = 10):
        self.job_id = job_id
        self.poll_interval = poll_interval

    async def run(self):
        """
        비동기 제너레이터 (AsyncGenerator).
        - yield TriggerEvent() 로 신호 보냄 (return X)
        - 블로킹 작업은 반드시 await
        """
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.example.com/jobs/{self.job_id}") as resp:
                    data = await resp.json()

            if data["status"] == "COMPLETED":
                yield TriggerEvent({"status": "success", "result": data["result"]})
                return
            elif data["status"] == "FAILED":
                yield TriggerEvent({"status": "failed", "error": data["error"]})
                return

            await asyncio.sleep(self.poll_interval)

    def serialize(self):
        """DB 저장용 직렬화 — (클래스 경로, kwargs 딕셔너리)"""
        return (
            "my_package.triggers.MyTrigger",
            {"job_id": self.job_id, "poll_interval": self.poll_interval}
        )

    async def cleanup(self):
        """리소스 정리 (선택). Trigger 종료 시 항상 호출됨."""
        pass
```

### 3.2 메서드 요약

| 메서드 | 필수 | 설명 |
|--------|------|------|
| `__init__()` | ✅ | Operator에서 받은 파라미터 저장 |
| `run()` | ✅ | 비동기 제너레이터, TriggerEvent yield |
| `serialize()` | ✅ | `(클래스경로, kwargs)` 튜플 반환 |
| `cleanup()` | ❌ | 연결 해제, 진행 중 작업 취소 등 |

### 3.3 흔한 실수

```python
# ❌ time.sleep → Triggerer 전체 이벤트 루프 블로킹
time.sleep(10)

# ✅ asyncio.sleep → 다른 Trigger는 계속 실행됨
await asyncio.sleep(10)

# ❌ 동기 HTTP (requests)
resp = requests.get(url)

# ✅ 비동기 HTTP (aiohttp)
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()
```

---

## 4. 장단점 분석

### 4.1 장점

**Worker 슬롯 절약 (핵심)**

```
시나리오: Sensor 100개, 각 1시간 대기

Poke Mode:
  - Worker 100개 × $0.44/h = $44/h (AWS MWAA 기준)
  - CPU: 100% (polling loop)

Deferrable Mode:
  - Worker 0개 (대기 중에는 사용 안 함)
  - Triggerer 1개: ~$0.02/h
  - 비용 절감: 약 99%
```

| 메트릭 | Poke | Reschedule | Deferrable |
|--------|------|------------|------------|
| Worker 점유 | 연속 | 간헐적 | 없음 |
| 메모리/worker | 100MB | 50MB | 0MB |
| DB row (대기 중) | 1개 | 재스케줄 마다 증가 | 1개 |
| 응답 속도 | 빠름 | 중간 | 10초 수준 |

**대량 동시 대기에 최적**  
1000개 Sensor가 동시에 대기 중이라도 Triggerer 1-2개로 처리 가능하다.

### 4.2 단점

**1. Triggerer SPOF (단일 장애점)**
- Triggerer 다운 시 모든 DEFERRED 상태 task가 멈춤
- 해결: Triggerer 2개 이상 HA 구성 필수

**2. 분산 로깅 — 디버깅 복잡**
- 같은 task의 로그가 Worker(실행 전) + Triggerer(대기 중) + Worker(재개 후) 에 나뉨
- Airflow UI > Triggers 패널로 확인 필요

**3. asyncio 제약**
- Trigger 내부 모든 I/O는 비동기 라이브러리 사용 필요 (aiohttp, aiobotocore 등)
- 동기 라이브러리를 쓰면 Triggerer 전체 성능 저하

**4. 짧은 대기에 오히려 오버헤드**
- asyncio 세팅, DB 저장/복원 오버헤드 존재
- 대기 시간 < 1분이면 표준 Poke Mode가 나을 수 있음

---

## 5. 언제 쓸까? 언제 쓰지 말까?

### 5.1 Deferrable 추천 상황

| 상황 | 이유 |
|------|------|
| 대기 시간 > 1분인 Sensor | Worker 점유 낭비 방지 |
| 동시 Sensor 수 많음 (10개+) | Triggerer 1개로 처리 가능 |
| AWS Glue/EMR, GCP BigQuery/Dataproc 등 외부 job 모니터링 | job 완료까지 수십 분 대기 |
| S3/GCS 파일 도착 대기 | 언제 올지 모르는 파일 감지 |
| API 폴링 (5분+ 간격) | Worker 낭비 없이 주기적 체크 |

### 5.2 Deferrable 비추천 상황

| 상황 | 대안 |
|------|------|
| 대기 시간 < 1분 | Poke Mode (mode="poke") |
| Triggerer 운영 불가 환경 | Reschedule Mode (mode="reschedule") |
| 비동기 라이브러리 없는 연동 | 표준 Operator + Reschedule |
| 디버깅이 매우 중요한 파이프라인 | 표준 모드 사용, 로그 단순화 우선 |

### 5.3 결정 트리

```
대기 시간이 필요한가?
├── 아니오 → 표준 Operator
└── 예 → 동시 대기 task 수가 많은가?
          ├── 아니오 + 짧은 대기 (< 5분) → Poke Mode
          ├── 예 또는 긴 대기 (> 5분)
          │    └── Triggerer 운영 가능한가?
          │         ├── 예 → Deferrable Operator ✅
          │         └── 아니오 → Reschedule Mode
```

---

## 6. 실제 사용 사례

### 6.1 AWS 서비스

```python
# S3 파일 대기
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_file = S3KeySensor(
    task_id="wait_s3_file",
    bucket_name="my-data-lake",
    bucket_key="processed/results.parquet",
    deferrable=True,
    timeout=timedelta(hours=24)
)

# Glue Job 실행 및 완료 대기
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

run_glue = GlueJobOperator(
    task_id="run_glue_etl",
    job_name="my_etl_job",
    deferrable=True,
    timeout=timedelta(hours=6)
)

# EMR 클러스터 생성 대기
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator

create_emr = EmrCreateJobFlowOperator(
    task_id="create_emr",
    deferrable=True,
    timeout=timedelta(hours=2)
)

# ECS Task 실행 대기
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator

run_ecs = EcsRunTaskOperator(
    task_id="run_ecs_task",
    task_definition="my-task:1",
    cluster="my-cluster",
    deferrable=True
)
```

### 6.2 GCP 서비스

```python
# BigQuery 쿼리 완료 대기
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

run_bq = BigQueryInsertJobOperator(
    task_id="run_bq_query",
    configuration={"query": {"query": "SELECT ...", "useLegacySql": False}},
    deferrable=True,
    timeout=timedelta(hours=1)
)

# GCS 파일 대기
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor

wait_gcs = GCSObjectExistenceSensor(
    task_id="wait_gcs_file",
    bucket="my-bucket",
    object="data/output.csv",
    deferrable=True,
    timeout=timedelta(hours=12)
)

# Dataproc 배치 완료 대기
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator

run_dataproc = DataprocCreateBatchOperator(
    task_id="run_dataproc",
    project_id="my-project",
    region="us-central1",
    batch={"spark_batch": {"jar_file_uris": ["gs://bucket/job.jar"]}},
    deferrable=True,
    timeout=timedelta(hours=4)
)
```

### 6.3 커스텀 HTTP 폴링

```python
class JobStatusTrigger(BaseTrigger):
    def __init__(self, job_id: str, api_url: str):
        self.job_id = job_id
        self.api_url = api_url

    async def run(self):
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/jobs/{self.job_id}") as resp:
                    data = await resp.json()
            status = data["status"]
            if status in ("SUCCESS", "FAILED"):
                yield TriggerEvent({"status": status, "result": data.get("result")})
                return
            await asyncio.sleep(30)

    def serialize(self):
        return ("my_triggers.JobStatusTrigger", {"job_id": self.job_id, "api_url": self.api_url})
```

---

## 7. 설정 및 운영

### 7.1 주요 설정값

```ini
# airflow.cfg
[triggerer]
capacity = 1000                      # 1 Triggerer당 동시 trigger 수
max_trigger_to_select_per_loop = 50  # 루프당 최대 선택 수 (HA 균형)
job_heartbeat_sec = 60               # 하트비트 간격

[operators]
default_deferrable = True  # 모든 deferrable 가능 operator 자동 적용
```

```bash
# 환경변수로도 설정 가능
export AIRFLOW__TRIGGERER__CAPACITY=2000
export AIRFLOW__OPERATORS__DEFAULT_DEFERRABLE=True
```

### 7.2 HA 구성 (필수 권장)

```yaml
# Kubernetes Deployment
spec:
  replicas: 2  # Triggerer 2개 이상
  template:
    spec:
      containers:
      - name: triggerer
        command: ["airflow", "triggerer"]
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
```

Triggerer 여러 개 실행 시 DB heartbeat로 trigger를 자동 분산한다.  
한 Triggerer가 다운되면 나머지가 해당 trigger를 인수인계한다.

### 7.3 모니터링 메트릭 (Prometheus)

```
triggers.running              # 현재 실행 중인 trigger 수
triggers.blocked_main_thread  # main thread 블로킹 경고 (0이어야 정상)
triggerer.capacity            # 남은 용량
```

**Trigger 목록 확인:** Airflow UI → Admin → Triggers

---

## 8. Airflow 버전별 진화

| 버전 | 변화 |
|------|------|
| **2.2** | Deferrable Operators 도입 (AIP-40). BaseTrigger, TaskDeferred, Triggerer 컴포넌트 |
| **2.3~2.8** | AWS(Glue, EMR, ECS), GCP(BigQuery, Dataproc, GCS) provider 지원 확대 |
| **2.9** | Trigger kwargs 암호화 저장 (비밀번호/API 키 보호) |
| **3.0~3.1** | Async Hooks 도입, async callable 실험적 지원 |
| **3.2** | **Native async execution** — Triggerer 없이 Worker에서 직접 `async def` task 실행 가능 |

### Airflow 3.2의 Native Async (차세대)

```python
# Triggerer 없이 Worker에서 직접 비동기 실행
@task
async def fetch_all_data(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [await r.json() for r in results]
```

Astronomer 발표에 따르면 SFTP 17,000개 파일 처리: 3시간 → 3.5분으로 단축.

---

## 9. 핵심 요약

```
일반 Sensor       → Worker 점유하며 polling (단순하지만 비효율)
Reschedule Mode   → 주기적으로 Worker 해제/재점유 (중간 효율)
Deferrable Mode   → Worker 완전 해제, asyncio Triggerer가 감시 (최고 효율)
Native Async(3.2) → Triggerer도 없이 Worker에서 async 실행 (미래 방향)
```

**한 줄 결론:**  
대기 시간이 길고 동시 대기 task가 많을수록 Deferrable Mode의 효과가 극대화된다.  
하지만 Triggerer HA 구성과 asyncio 기반 개발이 필요하다는 운영 복잡도가 따른다.

---

## 참고 출처

- [Apache Airflow 공식 문서 — Deferrable Operators](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html)
- [AIP-40 설계 문서](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=177050929)
- [Astronomer — Running asynchronous processes in Airflow](https://www.astronomer.io/docs/learn/deferrable-operators)
- [AWS Blog — MWAA Deferrable Operators](https://aws.amazon.com/blogs/big-data/introducing-amazon-mwaa-support-for-apache-airflow-version-2-7-2-and-deferrable-operators/)
- [GCP Docs — Use deferrable operators](https://docs.cloud.google.com/composer/docs/composer-2/use-deferrable-operators)
- [Astronomer — Airflow 3.2 Release](https://www.astronomer.io/blog/apache-airflow-3-2-release/)
