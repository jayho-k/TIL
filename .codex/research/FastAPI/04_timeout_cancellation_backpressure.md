# Timeout, cancellation, backpressure: 기다림을 통제하는 방법

> 선행: [pool과 대기열](./03_스레드풀_커넥션풀_대기열.md)  
> 핵심: timeout은 단지 사용자에게 빨리 에러를 보여 주는 장치가 아니라, 점유 중인 자원이 계속 쌓여 전체 서비스가 hang으로 번지는 것을 막는 경계다.

## 1. timeout은 하나가 아니다

요청 하나는 여러 단계의 대기를 거친다.

```text
client
  → API ingress queue
  → application semaphore 대기
  → HTTP/DB connection pool 대기
  → TCP connect
  → remote read/write
  → DB query / lock wait
  → response serialization
```

맨 바깥 request timeout만 두면 안쪽 작업이 계속 실행되거나, 어느 단계에서 느렸는지 알 수 없다. 각 경계의 timeout을 분리한다.

| 계층 | 제한할 대상 | 목적 |
| --- | --- | --- |
| ingress | reverse proxy/Uvicorn concurrency, body size | 과도한 유입을 application 앞에서 거절 |
| application queue | semaphore/thread token을 기다리는 시간 | 이미 포화된 기능에 새 요청을 오래 묶지 않음 |
| client pool | DB/HTTP connection checkout | connection leak·포화 발견 |
| network | connect/read/write | remote 장애가 thread/task를 무한 점유하지 않게 함 |
| database | statement/lock/transaction | query·lock wait를 DB에서 실제로 중단 |
| endpoint | 전체 deadline | 하위 timeout 누락 시 마지막 안전망 |

## 2. timeout budget을 위에서 아래로 배분한다

전체 응답 목표가 2초라면 각 단계가 2초를 독립적으로 쓰게 하면 안 된다. 예를 들어 아래처럼 예산을 정한다.

```text
API 전체 deadline: 2.0s
  ├─ queue/semaphore 획득: 0.1s
  ├─ HTTP pool 획득: 0.1s
  ├─ connect: 0.2s
  ├─ remote read/write: 1.2s
  └─ validation/serialization 및 여유: 0.4s
```

실제 값은 서비스 계약에 따라 정한다. 중요한 것은 하위 dependency의 timeout이 상위 deadline보다 길어서, 이미 포기한 요청의 작업이 뒤에서 계속 달리지 않게 하는 것이다.

## 3. outbound HTTP의 권장 구조

```python
import httpx

timeout = httpx.Timeout(
    connect=0.3,
    read=1.0,
    write=1.0,
    pool=0.1,
)
limits = httpx.Limits(max_connections=30, max_keepalive_connections=10)

# 실제 앱에서는 lifespan에서 한 번 만들고 shutdown에 닫는다.
client = httpx.AsyncClient(timeout=timeout, limits=limits)
```

`timeout=None`은 장애 전파 관점에서 거의 항상 위험하다. 단, streaming/SSE/대용량 download처럼 긴 연결이 의도된 API는 일반 API와 별도의 client·timeout·concurrency budget을 둔다.

HTTP retry는 timeout과 짝으로 설계한다.

- idempotent한 요청에만 제한적으로 재시도한다.
- 최대 횟수와 전체 deadline을 둔다.
- exponential backoff와 jitter를 써서 장애 시 동시 재시도를 분산한다.
- 4xx validation error, 명확한 business error에는 재시도하지 않는다.
- downstream이 포화됐을 때 retry가 유입량을 증폭하지 않는지 확인한다.

## 4. DB timeout은 application timeout과 별개다

Python coroutine을 취소하거나 endpoint deadline이 끝났다고 DB query가 항상 즉시 멈추는 것은 아니다. driver와 protocol에 따라 실제 DB 작업이 계속될 수 있다.

PostgreSQL에서는 보통 다음을 구분한다.

- `statement_timeout`: query 실행 전체에 대한 상한
- `lock_timeout`: lock 획득 대기에 대한 상한
- `transaction_timeout`: transaction 전체에 대한 상한
- `idle_in_transaction_session_timeout`: 열린 transaction을 두고 client가 idle인 상태의 상한

특히 transaction을 잡은 채 remote HTTP를 호출하면 timeout/cancellation 때 DB lock과 connection을 오래 붙잡을 수 있다. transaction 내부는 DB 작업과 짧은 검증만 두고, 원격 호출은 transaction 전후로 분리하는 편이 안전하다.

## 5. `asyncio.timeout()`이 할 수 있는 것과 없는 것

```python
async def endpoint():
    async with asyncio.timeout(2.0):
        return await async_operation()
```

await 가능한 `async_operation()`에는 매우 유용하다. task가 대기 중이면 cancellation이 전달되어 context manager가 `TimeoutError`로 변환한다.

하지만 아래 경우는 다르게 이해해야 한다.

```python
async def endpoint():
    async with asyncio.timeout(2.0):
        return await anyio.to_thread.run_sync(blocking_legacy_call)
```

host coroutine은 취소될 수 있지만, 이미 시작된 Python worker thread를 안전하게 강제 종료할 방법은 없다. AnyIO의 `abandon_on_cancel=True`도 thread를 죽이는 것이 아니라, 기다리던 task가 결과를 포기하게 하는 옵션이다. 동기 라이브러리 자체의 connect/read timeout, DB statement timeout, cooperative cancellation을 같이 설정해야 한다.

## 6. 취소와 resource cleanup

timeout·client disconnect·server shutdown은 취소를 만든다. 다음 원칙이 필요하다.

```python
async def use_resource():
    acquired = False
    try:
        await semaphore.acquire()
        acquired = True
        return await operation()
    finally:
        if acquired:
            semaphore.release()
```

실제 코드에서는 가능하면 `async with semaphore:`와 async context manager를 우선한다. connection, file, response body도 context manager로 닫는다.

취소를 무조건 `except Exception`으로 삼키지 않는다. Python의 `CancelledError` 처리와 framework의 cancellation semantics를 이해하지 못한 채 무시하면 shutdown이 길어지거나 task가 계속 살아남을 수 있다. 취소가 필요한 cleanup은 `finally`에 두고, 정말 필요한 경우에만 짧은 shielded cleanup을 사용한다.

## 7. lock과 semaphore의 deadlock 패턴

### 7.1 `threading.Lock`을 async path에서 쓰는 경우

`threading.Lock.acquire()`는 event loop thread를 block할 수 있다. event loop 내부 상호 배제에는 같은 loop에서 동작하는 `asyncio.Lock`을 사용한다. thread와 async task를 넘나드는 공유 상태라면 구조를 분리하거나 thread-safe queue/message passing을 검토한다.

### 7.2 lock을 잡은 채 오래 `await`

`asyncio.Lock`은 `await`를 해도 자동 해제되지 않는다. lock을 잡은 상태에서 DB/HTTP를 기다리면 다른 task가 모두 lock 앞에서 밀린다. 그 await 경로가 다시 같은 non-reentrant lock을 요구하면 deadlock이 된다.

원칙은 다음과 같다.

- lock 구간은 메모리 상태를 읽고 갱신하는 짧은 코드로 제한한다.
- lock 안에서 network, disk, DB 호출을 하지 않는다.
- 여러 lock은 항상 같은 순서로 획득한다.
- lock/semaphore 대기에도 deadline을 둔다.

### 7.3 bounded resource를 잡은 채 다른 bounded resource를 기다림

thread token → DB connection → GPU semaphore처럼 순서가 겹치면 연쇄 대기가 길어진다. 가능하면 고비용 작업에 진입하기 직전에 필요한 자원을 잡고, 더 이상 필요 없는 자원은 먼저 반환한다.

## 8. backpressure: 무한 queue 대신 명시적으로 거절하기

처리율보다 유입률이 계속 높으면 대기열은 늘어난다. 대기열이 길수록 이미 timeout될 요청에도 메모리·connection·CPU가 소모되고, 정상 요청도 늦어진다.

backpressure는 "지금은 처리하지 못한다"는 것을 빠르게 드러내는 설계다.

| 방식 | 동작 | 적합한 상황 |
| --- | --- | --- |
| Uvicorn `--limit-concurrency` | 한도를 넘는 연결/task에 503 | process 전체 메모리·in-flight 제한 |
| endpoint semaphore | 특정 비싼 기능만 제한 | GPU, vendor API, 대용량 변환 |
| bounded queue | producer가 무한히 쌓지 못함 | 내부 worker pipeline |
| 202 + job queue | 요청 처리와 장기 작업 분리 | 수초~수분 작업, 재시도·내구성 필요 |
| rate limit | client/tenant별 유입 제한 | 공정성, abuse 방지 |

거절 응답은 실패가 아니라 장애 격리다. retry-after, job status endpoint, idempotency key처럼 클라이언트가 복구할 수 있는 계약을 함께 제공한다.

## 9. FastAPI `BackgroundTasks`의 한계

`BackgroundTasks`는 응답을 보낸 뒤 같은 process에서 실행되는 in-process task다. sync background task는 Starlette thread pool도 사용한다. 따라서 무거운 작업을 넣으면 응답은 빨리 갔더라도 thread token, CPU, 메모리를 계속 점유할 수 있다.

다음 조건이면 외부 job queue가 맞다.

- 작업이 CPU/GPU를 오래 씀
- process restart 뒤에도 반드시 실행돼야 함
- 재시도, 지연 실행, 진행 상태가 필요함
- 여러 서버에서 수평 확장해야 함

FastAPI 공식 문서도 heavy background computation에는 Celery 같은 별도 도구를 고려하라고 안내한다.

## 10. 이 장의 체크리스트

- [ ] 모든 outbound HTTP에 connect/read/write/pool timeout이 있는가?
- [ ] DB checkout, statement, lock, transaction timeout이 구분돼 있는가?
- [ ] endpoint 전체 deadline이 하위 timeout보다 짧거나 같은가?
- [ ] timeout 시에도 connection·semaphore·file이 `finally`/context manager로 반환되는가?
- [ ] thread offload 작업은 library 자체 timeout을 가지는가?
- [ ] retry는 bounded이고 idempotent한가?
- [ ] capacity가 찼을 때 오래 기다리지 않고 429/503 또는 async job으로 전환하는가?

## 출처

- [HTTPX — Timeouts](https://www.python-httpx.org/advanced/timeouts/) — HTTP connect/read/write/pool timeout의 의미.
- [AnyIO — Working with threads](https://anyio.readthedocs.io/en/stable/threads.html), [Cancellation and timeouts](https://anyio.readthedocs.io/en/stable/cancellation.html) — worker thread의 강제 취소 불가와 cancel scope.
- [Python — asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) — `asyncio.timeout()`의 task cancellation 기반 동작.
- [PostgreSQL — Client Connection Defaults](https://www.postgresql.org/docs/current/runtime-config-client.html) — statement/lock/transaction timeout.
- [Uvicorn — Settings](https://www.uvicorn.org/settings/) — concurrency limit과 graceful shutdown timeout.
- [FastAPI — Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) — heavy task에 별도 queue/worker를 고려해야 하는 caveat.
