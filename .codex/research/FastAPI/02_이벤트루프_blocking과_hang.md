# 이벤트 루프 blocking: FastAPI에서 가장 파급이 큰 hang

> 선행: [FastAPI 요청 실행 모델](./01_FastAPI_요청_실행_모델.md)  
> 결론: `async def` 안에서 동기 I/O 또는 긴 CPU 작업을 하면 "그 요청만" 기다리는 것이 아니라 같은 worker의 event loop가 다른 요청을 처리하지 못한다.

## 1. 왜 영향 범위가 큰가

한 Uvicorn worker의 이벤트 루프는 많은 요청 task를 스케줄한다. task가 `await` 가능한 작업을 기다리면 loop는 다른 task를 실행할 수 있다. 반면 task가 event loop thread를 점유한 채 반환하지 않으면 scheduler가 돌지 않는다.

```text
정상
request A: await DB ────────────────┐
request B:              실행 → 응답 │
request C:                    실행  │
                                  A 재개

blocking
request A: time.sleep(10) / requests.get(...) / CPU loop
request B: 실행 기회를 얻지 못함
request C: 실행 기회를 얻지 못함
```

여기서 "모든 요청"은 정확히는 **그 worker에 연결·배정된 요청**이다. 여러 worker가 있으면 다른 worker는 살아 있을 수 있지만, 문제가 모든 worker에 같은 코드 경로로 발생하면 전체 서비스 장애처럼 보인다.

## 2. 흔한 원인

### 2.1 `time.sleep()`과 동기 wait

```python
@app.get("/bad-sleep")
async def bad_sleep():
    time.sleep(5)  # 이벤트 루프 block
    return {"ok": True}

@app.get("/good-sleep")
async def good_sleep():
    await asyncio.sleep(5)  # 다른 task에 실행 기회를 줌
    return {"ok": True}
```

`time.sleep()`은 단지 예시다. `threading.Lock.acquire()`, 동기 queue의 `get()`, `future.result()` 같은 동기 대기도 같은 문제가 된다.

### 2.2 동기 HTTP SDK

```python
import requests

@app.get("/bad-http")
async def bad_http():
    response = requests.get("https://partner.example.com")
    return response.json()
```

`requests`는 blocking client다. connect/read가 오래 걸리면 event loop가 그대로 멈춘다. 해결의 우선순위는 async client를 쓰는 것이다.

```python
import httpx

@app.get("/good-http")
async def good_http():
    response = await shared_async_client.get("https://partner.example.com")
    return response.json()
```

legacy SDK처럼 async 대안이 없을 때만 thread offload를 사용한다.

```python
from functools import partial
from starlette.concurrency import run_in_threadpool

@app.get("/legacy-http")
async def legacy_http():
    response = await run_in_threadpool(
        partial(requests.get, "https://partner.example.com", timeout=2.0)
    )
    return response.json()
```

이것은 event loop block을 thread pool 대기로 바꾼다. timeout과 동시성 상한 없이 대량 사용하면 다음 병목이 thread pool이 된다.

### 2.3 동기 DB driver / ORM

동기 SQLAlchemy engine, psycopg2, 일부 cloud SDK는 호출 thread를 기다리게 한다. `async def` endpoint 안에서 직접 호출하면 event loop block이다.

선택지는 두 가지다.

- async driver와 async ORM/engine을 써서 `await`한다.
- 동기 stack을 유지해야 한다면 endpoint/dependency를 `def`로 두거나 명시적으로 thread offload한다.

둘 중 무엇을 택해도 DB connection 수, query time, lock wait는 별도로 제한해야 한다. async driver는 DB가 빨라지게 하는 기능이 아니며, **대기 중 event loop를 양보**하게 하는 기능이다.

### 2.4 파일·이미지·압축·직렬화

"파일은 I/O니까 async겠지"라고 생각하면 위험하다.

- `UploadFile.read()` 같은 framework API는 내부적으로 thread pool을 쓸 수 있다.
- 읽은 bytes를 Pillow로 decode/resize/convert 하는 작업은 대체로 동기 CPU 작업이다.
- 큰 JSON을 만들고 Pydantic validation/serialization 하는 작업도 event loop에서 CPU 시간을 오래 쓸 수 있다.
- 큰 압축·해시·PDF/Excel 생성도 request path에 넣으면 tail latency를 키운다.

대용량 request/response에는 크기 제한, pagination, streaming 여부, CPU offload 또는 비동기 job 전환을 함께 설계해야 한다.

### 2.5 CPU-bound Python code

```python
def score_everything(items: list[int]) -> int:
    total = 0
    for item in items:
        total += item * item
    return total

@app.post("/bad-cpu")
async def bad_cpu(items: list[int]):
    return {"score": score_everything(items)}  # await 없음
```

이 작업은 I/O를 기다리지 않는다. thread pool로 보내도 기본 CPython의 GIL 환경에서는 순수 Python bytecode가 여러 core에서 충분히 병렬 실행되지 않는다. 또한 많은 CPU thread가 GIL과 CPU를 경쟁하면 event loop도 지연될 수 있다.

기본 선택은 다음과 같다.

| 작업 | 우선 해법 |
| --- | --- |
| 짧은 CPU 계산 | request 제한·알고리즘 개선·응답 크기 축소 |
| 긴 CPU 계산 | process pool 또는 별도 worker process |
| 내구성 필요한 긴 작업 | broker 기반 job queue + 202 Accepted + status 조회 |
| GPU inference | 전용 serving 계층의 queue/batching/concurrency 제어 |

## 3. "async library를 썼는데도" loop가 막히는 경우

비동기 client를 사용한다고 endpoint 전체가 non-blocking이 되는 것은 아니다.

```python
@app.get("/mixed")
async def mixed():
    data = await client.get("https://example.com")  # 정상적으로 양보
    report = huge_python_transformation(data.json())  # 다시 loop 점유
    return report
```

I/O phase는 효율적이어도 transform phase가 길면 event loop lag가 생긴다. endpoint를 I/O와 CPU phase로 나눠 관찰해야 한다.

또한 어떤 C extension은 CPU 작업 중 GIL을 풀기도 하지만, 라이브러리·입력 크기·native 구현에 따라 다르다. "NumPy/Pillow니까 자동으로 안전"처럼 가정하지 말고 부하 테스트에서 event-loop lag를 측정한다.

## 4. 예방 규칙

### 규칙 A: `async def` 안에서 호출하는 모든 함수의 대기 방식을 확인한다

함수 이름에 `async`가 없다고 위험하다는 뜻도, 있다고 안전하다는 뜻도 아니다. 다음을 확인한다.

1. 이 함수가 I/O 중 thread를 block하는가?
2. coroutine/awaitable을 반환하는가?
3. 입력 크기에 따라 CPU 작업이 커지는가?
4. timeout을 호출자·driver·원격 시스템 모두에 설정했는가?

### 규칙 B: blocking I/O는 명시적으로 격리한다

가능하면 async driver/client를 우선한다. 불가피한 blocking I/O는 `run_in_threadpool()` 또는 `anyio.to_thread.run_sync()`로 옮기되, shared thread pool을 소모한다는 사실을 인지한다.

### 규칙 C: CPU work를 request event loop에 두지 않는다

thread offload가 event loop를 살리는 경우는 있어도 CPU 처리량과 tail latency를 보장하지 않는다. process 또는 queue를 선택하고, 요청 크기·동시 실행 수·작업 시간에 명시적 상한을 둔다.

### 규칙 D: 빠른 async health check를 둔다

DB나 external API를 호출하지 않는 가벼운 endpoint가 event-loop block 탐지에 도움이 된다. 단, 이것만 healthy라고 해서 DB pool이나 thread pool도 건강하다는 뜻은 아니다. liveness와 dependency readiness를 분리한다.

## 5. 증상으로 구분하기

| 관측 | event loop blocking 가능성 |
| --- | --- |
| 단순 async health endpoint도 느리거나 timeout | 높음 |
| 해당 worker의 event-loop lag가 증가 | 높음 |
| CPU가 높은데 async 요청이 함께 지연 | CPU-bound/serialization 의심 |
| async health는 빠르지만 sync route만 지연 | 낮음; thread pool·DB pool을 먼저 의심 |
| 특정 downstream 호출만 지연 | 외부 timeout·connection pool·DB lock을 먼저 의심 |

## 6. 핵심 교훈

> `async def`는 "이 함수가 thread를 쓰지 않는다"가 아니라 "이 함수가 event loop를 직접 점유한다"는 의미에 가깝다. 그러므로 그 안에는 await 가능한 I/O와 짧은 CPU 작업만 남겨야 한다.

## 출처

- [FastAPI — Concurrency and async / await](https://fastapi.tiangolo.com/async/) — `async def`와 일반 `def`의 dispatch 차이.
- [Python — asyncio event loop](https://docs.python.org/3/library/asyncio-eventloop.html) — blocking I/O를 thread executor로, CPU-bound 작업을 process pool로 다루는 기준.
- [Python — threading](https://docs.python.org/3/library/threading.html) — GIL-enabled CPython에서 CPU-bound thread 병렬성의 한계와 I/O-bound thread의 유효성.
- [Starlette — Thread Pool](https://www.starlette.io/threadpool/) — blocking 작업의 thread pool 전환과 shared limiter.
