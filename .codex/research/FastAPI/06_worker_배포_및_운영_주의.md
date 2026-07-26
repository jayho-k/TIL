# Worker, lifespan, background task: 배포·운영에서 생기는 hang

> 선행: [요청 실행 모델](./01_FastAPI_요청_실행_모델.md), [timeout/backpressure](./04_timeout_cancellation_backpressure.md)  
> 핵심: worker 수는 concurrency를 늘리는 설정이지만, 동시에 메모리·thread token·connection pool·semaphore의 총량도 늘리는 설정이다.

> Gunicorn으로 Uvicorn ASGI worker를 관리하는 환경의 master/worker·timeout 차이는 [07_Gunicorn_UvicornWorker와_hang_운영.md](./07_Gunicorn_UvicornWorker와_hang_운영.md)에서 별도로 다룬다.

## 1. Uvicorn worker는 process다

`uvicorn app.main:app --workers 4`에서 4는 thread 수가 아니라 worker **process** 수다. 각 process는 서로 메모리를 공유하지 않는 독립 실행 단위다.

```text
worker 1
  - event loop
  - AnyIO thread limiter
  - DB/HTTP client 및 connection pool
  - in-memory cache, semaphore, model

worker 2
  - 위 자원을 별도로 다시 가짐
```

따라서 worker를 두 배로 늘리면 다음도 대략 두 배가 될 수 있다.

- DB connection 상한
- outbound HTTP connection 상한
- `asyncio.Semaphore`가 허용하는 동시 작업 수
- in-memory cache와 model memory
- background task 실행량

### semaphore는 worker 간 공유되지 않는다

```python
vendor_limit = asyncio.Semaphore(5)
```

worker가 4개면 이 코드는 전역 5개가 아니라 **최대 20개**의 vendor API 호출을 허용할 수 있다. 전역 quota가 필요하면 Redis, DB, message broker, gateway rate limit처럼 process 밖의 조정 장치가 필요하다.

## 2. worker를 늘릴 때의 올바른 질문

틀린 질문은 "CPU core가 8개니까 worker도 8개면 되나?"다. 먼저 아래를 계산한다.

| 자원 | 계산 예시 |
| --- | --- |
| DB connection | workers × (pool_size + max_overflow) ≤ 서비스에 배정된 DB 예산 |
| HTTP downstream | workers × client max_connections ≤ 상대 서비스의 허용량 |
| 메모리 | workers × (기본 앱 메모리 + 모델/cache) < container/VM limit의 여유 범위 |
| GPU | 모델/GPU context가 worker마다 중복되는지 확인 |
| app semaphore | workers × local semaphore 값이 global quota를 넘지 않는지 확인 |

worker 증설은 event-loop blocking의 영향을 한 process에 가두는 데는 도움될 수 있다. 그러나 blocking 코드 자체를 고치지 않으면 각 worker가 같은 방식으로 멎고, DB/remote service 부담만 증가할 수 있다.

## 3. Uvicorn의 ingress 보호 장치

Uvicorn은 다음과 같은 server-level 설정을 제공한다.

| 옵션 | 의미 | hang 예방 관점 |
| --- | --- | --- |
| `--limit-concurrency` | 허용할 concurrent connection/task 상한, 초과 시 503 | 무한 in-flight request와 memory queue 방지 |
| `--backlog` | accept 전 대기 가능한 connection 수 | burst 시 OS/socket 대기열 조절 |
| `--limit-max-requests` | worker가 처리할 request 수 상한 | memory leak 영향 완화용, 근본 해결책은 아님 |
| `--timeout-keep-alive` | idle keep-alive 연결 종료 시간 | idle connection 장기 점유 완화 |
| `--timeout-graceful-shutdown` | graceful shutdown 대기 상한 | 종료 시 무한 대기 방지 |
| `--timeout-worker-healthcheck` | worker healthcheck 응답 대기 상한 | 시작/정지/stall 감지 |

`--limit-concurrency`의 503은 기능 장애가 아니라 overload를 제한해 기존 요청의 성공 확률을 지키는 backpressure다. 이 값은 worker가 처리할 수 있는 CPU·memory뿐 아니라 DB/HTTP/GPU downstream capacity와 맞춰 정한다.

## 4. lifespan: startup과 shutdown도 request path와 같은 규칙을 따른다

FastAPI `lifespan`은 요청을 받기 전과 모든 요청 처리가 끝난 뒤에 실행된다. DB/HTTP client pool, model, shared resource를 process당 한 번 만들고 닫는 위치다.

```python
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(
        timeout=httpx.Timeout(3.0),
        limits=httpx.Limits(max_connections=30),
    )
    try:
        yield
    finally:
        await app.state.http.aclose()

app = FastAPI(lifespan=lifespan)
```

### startup hang

startup에서 모델 download/load, migration, 동기 DNS/HTTP, 긴 CPU 초기화를 하면 worker는 ready가 되지 않는다. 이때 요청을 처리하지 않으므로 event-loop stall과는 성격이 다르지만, deployment는 healthcheck timeout으로 실패할 수 있다.

- 정말 필요한 초기화만 startup에 둔다.
- 외부 호출에는 timeout과 재시도 정책을 둔다.
- model loading처럼 의도적으로 오래 걸리는 작업은 readiness probe와 deployment timeout을 맞춘다.
- 여러 worker가 동시에 동일한 migration·초기화를 실행하지 않게 leader/init job을 분리한다.

### shutdown hang

shutdown 때는 in-flight request, background task, client close, thread 작업이 남을 수 있다. 동기 worker thread는 안전하게 강제 종료하기 어렵다. 그래서 정상 동작 중부터 모든 I/O에 timeout을 걸고, graceful shutdown 상한을 둔다.

## 5. BackgroundTasks는 durable queue가 아니다

FastAPI/Starlette background task는 response 전송 뒤에 같은 worker process에서 실행된다.

- process가 죽으면 작업이 유실될 수 있다.
- sync task는 shared AnyIO thread pool을 소비한다.
- async task가 CPU-heavy 또는 blocking code를 실행하면 event loop를 다시 막을 수 있다.
- 트래픽이 많으면 background task가 계속 쌓여 memory/CPU/thread를 잠식한다.

메일 한 통, 짧은 로그 기록처럼 작고 실패해도 재처리 요구가 낮은 작업에만 적합하다. 이미지 변환, 대량 AI inference, PDF 생성, 대규모 fan-out, 반드시 실행돼야 하는 업무는 broker 기반 worker로 보낸다.

## 6. Streaming, SSE, WebSocket은 긴 연결을 별도 용량으로 본다

일반 request/response API는 끝나면 socket과 in-flight slot이 빨리 반환된다. Streaming/SSE/WebSocket은 의도적으로 오랫동안 연결을 유지한다.

주의점은 다음과 같다.

- slow client가 읽지 않으면 send buffer와 task가 오래 남을 수 있다.
- 매 connection마다 무한 polling loop를 만들면 CPU와 connection 수가 누적된다.
- disconnect cancellation을 처리하지 않으면 upstream stream을 계속 읽을 수 있다.
- 일반 API와 같은 concurrency limit을 공유하면 긴 연결이 짧은 API 용량을 잠식할 수 있다.

연결 수, connection lifetime, bytes sent, disconnect/cancellation, upstream subscription 수를 별도 metric으로 둔다. 필요하면 streaming endpoint를 별도 service 또는 별도 worker pool로 격리한다.

## 7. large request/response와 memory pressure

FastAPI hang처럼 보이는 현상은 실제로 memory pressure일 수 있다.

- 큰 multipart upload를 동시에 받음
- 큰 JSON body를 여러 요청이 동시에 parsing/validation
- 큰 response를 한 번에 materialize/serialize
- `asyncio.gather()`에 매우 큰 task 목록을 생성
- retry와 queue가 오래된 payload를 계속 보유

memory가 부족하면 GC가 잦아지고 swap/OOM killer가 발생하며 latency가 급격히 나빠진다. request body limit은 proxy와 application 모두에서 두고, pagination·chunking·streaming·bounded queue를 사용한다.

## 8. 운영 체크리스트

### 배포 전

- [ ] worker 수 기준으로 DB/HTTP connection 총량을 계산했는가?
- [ ] worker마다 중복되는 model/cache 메모리를 계산했는가?
- [ ] local semaphore가 global quota를 넘지 않는가?
- [ ] `--limit-concurrency`와 endpoint별 concurrency budget이 있는가?
- [ ] startup의 외부 호출과 model load에 timeout/readiness 계획이 있는가?

### 운영 중

- [ ] worker별 event-loop lag, CPU/RAM/FD, restart 횟수를 본다.
- [ ] DB/HTTP pool wait와 timeout을 worker별·전체로 본다.
- [ ] 429/503이 증가하면 "서버가 나빠졌다"고만 보지 않고 capacity 보호가 작동하는지 확인한다.
- [ ] background task queue/in-flight를 측정한다.
- [ ] graceful shutdown 때 남은 task·thread·connection이 있는지 확인한다.

## 9. 이 장의 결론

> FastAPI worker 증설은 동시성의 총량을 키우는 행위다. process마다 복제되는 pool·memory·semaphore까지 함께 계산하지 않으면, hang의 위치가 event loop에서 DB·GPU·메모리로 옮겨갈 뿐이다.

## 출처

- [FastAPI — Deployment Concepts](https://fastapi.tiangolo.com/deployment/concepts/) — worker process, process별 memory와 replication 개념.
- [FastAPI — Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/) — multiple worker process 사용.
- [Uvicorn — Settings](https://www.uvicorn.org/settings/), [Server Behavior](https://www.uvicorn.org/server-behavior/) — workers, concurrency limit, backlog, keep-alive, graceful shutdown.
- [FastAPI — Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) — startup/shutdown 리소스 수명 관리.
- [FastAPI — Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) — in-process background task와 heavy computation caveat.
