# Gunicorn + UvicornWorker: FastAPI hang을 운영 계층에서 이해하기

> 선행: [FastAPI 요청 실행 모델](./01_FastAPI_요청_실행_모델.md), [worker 배포·운영](./06_worker_배포_및_운영_주의.md)  
> 작성 기준: 2026-07-24, Gunicorn 23.0.0 및 Uvicorn 공식 배포 문서 확인  
> 핵심: Gunicorn은 process manager, Uvicorn worker는 ASGI server, FastAPI는 ASGI application이다. 세 계층의 timeout과 concurrency 설정을 혼동하지 않는다.

## 1. Gunicorn을 쓰는 FastAPI의 실제 계층

```text
client / load balancer / reverse proxy
  → Gunicorn master process
      ├─ UvicornWorker process 1
      │    → Uvicorn ASGI server → event loop → FastAPI app
      ├─ UvicornWorker process 2
      │    → Uvicorn ASGI server → event loop → FastAPI app
      └─ ...
```

역할은 다음처럼 분리된다.

| 계층 | 책임 | FastAPI hang과의 관계 |
| --- | --- | --- |
| Gunicorn master | worker 생성·감시·재시작·signal 처리 | 멎거나 죽은 worker를 교체, graceful restart 조정 |
| Uvicorn worker class | HTTP/ASGI protocol, event loop, FastAPI lifespan 실행 | request task와 event loop를 실제로 실행 |
| FastAPI/Starlette/AnyIO | route, dependency, response, sync offload | event-loop block·thread pool 포화가 생기는 지점 |
| DB/HTTP/GPU 등 | 실제 외부 작업 | connection/lock/downstream wait가 생기는 지점 |

Gunicorn master는 개별 HTTP 요청을 처리하지 않는다. 요청·응답과 event loop는 Uvicorn worker process 안에서 동작한다. 따라서 Gunicorn을 도입해도 `async def` 안의 blocking I/O, shared AnyIO thread pool 40-token 포화, DB connection 고갈은 그대로 존재한다.

## 2. worker class는 반드시 ASGI용이어야 한다

Gunicorn의 기본 worker class는 `sync`이며 WSGI의 전통적인 request-per-worker 모델이다. FastAPI는 ASGI application이므로 Gunicorn에서는 Uvicorn ASGI worker class를 사용해야 한다.

최근 Uvicorn 공식 문서는 기존 경로 `uvicorn.workers.UvicornWorker`가 deprecated 되었고, 별도 패키지 `uvicorn-worker` 사용을 권고한다. 문서의 일부 예제에는 구 경로가 남아 있을 수 있으므로 새 배포에서는 현재 경로를 명시적으로 사용한다.

```bash
python -m pip install gunicorn uvicorn-worker
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn_worker.UvicornWorker \
  --bind 0.0.0.0:8000
```

`uvicorn_worker.UvicornWorker`의 정확한 호환 버전은 배포 image의 `gunicorn`, `uvicorn`, `uvicorn-worker` release note까지 함께 고정·검증한다.

## 3. Gunicorn의 `workers`, `threads`와 FastAPI thread pool은 다른 설정이다

| 설정 | 적용 대상 | FastAPI에서 의미 |
| --- | --- | --- |
| Gunicorn `workers` | OS process 수 | event loop·memory·DB/HTTP pool이 process마다 복제 |
| Gunicorn `threads` | Gunicorn `gthread` worker type | Uvicorn ASGI worker의 AnyIO sync pool 조절 수단이 아님 |
| AnyIO thread limiter | FastAPI/Starlette가 offload한 동기 작업 | `def` endpoint/dependency/file/background task의 동시 실행량 |
| app semaphore | 애플리케이션 특정 기능 | GPU/vendor API/비싼 작업의 정책상 동시성 |

따라서 Gunicorn `--threads` 값을 바꿔 FastAPI의 sync dependency thread pool을 조정하려고 하면 안 된다. `UvicornWorker` 환경에서 FastAPI의 동기 작업 한도는 AnyIO/Starlette 계층을 봐야 한다.

worker 수를 늘릴 때는 총량을 계산한다.

```text
총 AnyIO sync 작업 가능량(기본값 기준) ≈ Gunicorn workers × 40
총 DB connection 상한              ≈ Gunicorn workers × (pool_size + max_overflow)
총 HTTP client connection 상한     ≈ Gunicorn workers × max_connections
총 local semaphore 허용량          ≈ Gunicorn workers × semaphore 값
```

이 수식은 최대치의 근사다. 핵심은 Gunicorn worker가 늘면 FastAPI process-local 자원도 함께 늘어난다는 것이다.

## 4. Gunicorn `timeout`은 request timeout이 아니다

Gunicorn의 `timeout` 기본값은 30초이며, 문서상 의미는 **그 시간 동안 silent한 worker를 kill하고 restart**하는 것이다.

이 값은 다음과 혼동하면 안 된다.

| 설정 | 무엇을 제한하는가 | 무엇을 보장하지 않는가 |
| --- | --- | --- |
| Gunicorn `timeout` | worker가 master에 대해 침묵한 시간 | 개별 HTTP request의 최대 처리 시간 |
| Gunicorn `graceful_timeout` | restart/shutdown 신호 후 worker가 종료될 때까지의 시간 | downstream HTTP/DB query를 정상 취소한다는 보장 |
| HTTP client timeout | connect/read/write/pool 대기 | DB lock wait 또는 CPU loop |
| DB statement/lock timeout | query·lock 대기 | application thread/event loop의 다른 block |
| endpoint deadline | coroutine의 전체 작업 시간 | 이미 시작한 blocking thread의 강제 종료 |

Uvicorn 같은 non-sync worker에서 Gunicorn `timeout`은 요청 하나가 오래 걸리는 시간과 직접 동일하지 않다. long-polling/streaming request가 있다고 `timeout`을 무조건 크게 올리면 안 된다. 반대로 event loop가 동기 CPU loop나 blocking call로 완전히 멎어 worker heartbeat가 끊기면 Gunicorn은 worker를 kill/restart할 수 있다.

**운영 결론:** Gunicorn timeout은 최후의 worker watchdog으로 보고, 정상 request path의 timeout은 HTTP client·DB·application semaphore·endpoint deadline에서 별도로 설계한다.

## 5. graceful restart와 shutdown에서 hang이 보이는 방식

Gunicorn master가 `TERM` 또는 reload signal을 받으면 worker를 graceful하게 교체하려 한다. worker는 `graceful_timeout` 안에 기존 요청을 마쳐야 하고, 넘기면 강제 종료될 수 있다.

이때 다음 작업은 shutdown을 길게 하거나 강제 종료를 유발할 수 있다.

- timeout 없는 outbound HTTP/DB 호출
- 취소되지 않는 worker thread의 blocking I/O
- 끝나지 않는 background task
- client disconnect를 처리하지 않는 streaming/SSE/WebSocket
- shutdown hook에서 긴 blocking cleanup

따라서 timeout budget은 일반 장애뿐 아니라 deploy/scale-in 안정성에도 필요하다. graceful timeout을 크게 잡기 전에 실제 longest legitimate request, streaming 정책, load balancer drain timeout, application cleanup 시간의 관계를 확인한다.

## 6. `max_requests`는 leak 완화 장치이지 hang 해결책이 아니다

Gunicorn `max_requests`는 worker가 일정 request 수를 처리한 뒤 재시작하게 하며, `max_requests_jitter`는 worker가 동시에 재시작하지 않게 분산한다.

이 설정은 장기 memory leak의 영향 범위를 제한하는 보조 수단이 될 수 있다. 하지만 다음 문제를 해결하지는 못한다.

- event loop blocking code
- DB lock/connection leak의 근본 원인
- timeout 없는 downstream 호출
- 과도한 inbound concurrency

또한 in-process background task나 process-local queue에 의존한다면 restart가 작업 유실로 이어질 수 있다. durable 작업은 외부 queue를 사용한다.

## 7. `preload_app`과 fork 이후 자원 초기화

Gunicorn은 pre-fork 모델이다. `preload_app=True`/`--preload`는 master가 application code를 먼저 load한 후 worker를 fork한다. 공식 문서상 RAM 절감과 boot 속도 개선 가능성이 있지만, worker restart로 code reload하기 어려워지는 trade-off가 있다.

FastAPI에서 중요한 실무 원칙은 다음이다.

- module import 시점에 DB connection, HTTP connection, thread pool, event loop, GPU context를 실제로 열지 않는다.
- process별 resource는 FastAPI lifespan 안에서 만들고 shutdown에 닫는다.
- fork 이전에 열린 socket/connection/client가 worker 사이에 상속되는지 확인한다.
- `preload`는 read-only model memory처럼 copy-on-write 효과가 검증된 경우에만 성능 실험 후 사용한다.

마지막 두 항목은 Gunicorn의 pre-fork 특성과 FastAPI lifespan의 역할을 연결한 운영상 추론이다. 특정 driver·GPU runtime의 fork 안전성은 해당 라이브러리 공식 문서를 추가로 확인해야 한다.

## 8. Gunicorn 환경에서 overload를 제한하는 방법

Uvicorn 문서는 Gunicorn과 함께 실행할 때 Uvicorn의 일부 옵션(예: `--limit-concurrency`)을 직접 사용할 수 없다고 명시한다. 따라서 Gunicorn 배포에서 `uvicorn --limit-concurrency`를 설정했다고 가정하면 안 된다.

overload 방어는 계층별로 둔다.

| 계층 | 방법 |
| --- | --- |
| reverse proxy/load balancer | request body 제한, connection/rate limit, upstream timeout |
| Gunicorn | worker 수·backlog·worker watchdog·graceful restart |
| FastAPI application | endpoint별 semaphore, bounded queue, 429/503, request deadline |
| client library | DB/HTTP pool limit과 timeout |
| downstream | DB lock/statement timeout, vendor quota/circuit breaker |

특히 FastAPI app 내부 semaphore는 worker마다 독립이다. 전역 rate/concurrency 제한은 proxy, Redis, broker 등 process 밖에서 조정한다.

## 9. Gunicorn 고유의 운영 진단 포인트

### 9.1 worker timeout 로그

Gunicorn이 worker timeout 후 재시작했다면 "Gunicorn timeout을 더 키울지"보다 먼저 다음을 확보한다.

1. 해당 worker의 CPU/RAM/file descriptor
2. event-loop lag와 in-flight request
3. asyncio task stack, worker thread stack
4. DB/HTTP pool checkout/wait와 downstream latency
5. timeout 직전 request route·trace ID

이 자료 없이 timeout을 올리면 blocking bug를 더 오래 숨기게 될 수 있다.

### 9.2 heartbeat temporary directory

Gunicorn `worker_tmp_dir`는 worker heartbeat temporary file을 둔다. 공식 문서는 disk-backed filesystem에서 heartbeat의 `os.fchmod`가 임의로 오래 block될 수 있다고 경고한다. container/VM 환경에서는 이 경로가 느린 network/disk mount가 아닌지 확인한다.

### 9.3 로그

Gunicorn access log는 request duration(`T`, `M`, `D`, `L`)과 worker PID를 남길 수 있다. 다만 Uvicorn worker package/version이 Gunicorn access log format을 어떻게 반영하는지는 실제 배포 image에서 확인한다. application 내부 DB pool wait·event-loop lag까지는 access log만으로 알 수 없으므로 metrics/tracing을 결합한다.

## 10. 기본 설정 예시와 읽는 법

아래는 출발점일 뿐, 숫자를 복사하는 운영 설정이 아니다.

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn_worker.UvicornWorker"

# worker watchdog / graceful deploy
timeout = 30
graceful_timeout = 30
keepalive = 5

# 장기 leak의 영향 완화용; jitter로 동시 재시작 방지
max_requests = 10000
max_requests_jitter = 1000

# container 환경에서 stdout/stderr에 남기는 예시
accesslog = "-"
errorlog = "-"
```

request duration 형식 같은 access log customization은 `gunicorn --print-config`와 실제 emitted log로 worker package의 반영 여부를 확인한 뒤 적용한다.

검증 순서는 다음과 같다.

1. `gunicorn --check-config --config gunicorn.conf.py app.main:app`으로 config를 확인한다.
2. `gunicorn --print-config ...`으로 환경변수까지 반영된 값을 확인한다.
3. worker 수를 정하기 전에 worker당 memory, DB/HTTP pool 총량, downstream quota를 계산한다.
4. blocking·timeout·graceful restart를 포함한 부하 테스트에서 p99와 worker restart를 관찰한다.

## 11. Gunicorn + FastAPI hang 체크리스트

- [ ] `worker_class`가 ASGI용 `uvicorn_worker.UvicornWorker`인가?
- [ ] Gunicorn `timeout`을 request timeout으로 오해하지 않았는가?
- [ ] worker 수를 기준으로 DB/HTTP/semaphore 총량을 계산했는가?
- [ ] Uvicorn `--limit-concurrency`가 Gunicorn 배포에서 적용된다고 가정하지 않았는가?
- [ ] FastAPI lifespan에서 process별 client/resource를 열고 닫는가?
- [ ] `preload`를 쓴다면 fork 이전에 열린 connection/thread/GPU resource가 없는가?
- [ ] `graceful_timeout`이 longest legitimate request와 load balancer drain 정책에 맞는가?
- [ ] worker timeout/restart 때 event loop·thread·pool 상태를 남기는가?
- [ ] `max_requests`를 근본 원인 해결이 아닌 leak 완화책으로 쓰는가?

## 출처

- [Gunicorn 23.0.0 — Design](https://docs.gunicorn.org/en/stable/design.html) — master/pre-fork worker 모델과 worker 관리.
- [Gunicorn 23.0.0 — Settings](https://docs.gunicorn.org/en/stable/settings.html) — `workers`, `worker_class`, `timeout`, `graceful_timeout`, `max_requests`, `preload_app`, `worker_tmp_dir`, logging 설정.
- [Uvicorn — Deployment](https://www.uvicorn.org/deployment/) — Gunicorn과 Uvicorn worker 배포, `uvicorn.workers` deprecation, Gunicorn에서 일부 Uvicorn 옵션이 직접 지원되지 않는 점.
- [uvicorn-worker](https://github.com/Kludex/uvicorn-worker) — 별도 `uvicorn-worker` package와 `uvicorn_worker.UvicornWorker` 사용 예시.
