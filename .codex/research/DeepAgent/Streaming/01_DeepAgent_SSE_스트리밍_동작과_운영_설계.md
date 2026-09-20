# DeepAgent SSE 스트리밍 동작과 운영 설계 조사

> 조사 기준일: 2026-09-20  
> 대상: Python Deep Agents → LangGraph `astream()` → FastAPI/Starlette → ASGI/Uvicorn → SSE 클라이언트  
> 목적: 단순 스트리밍 예제를 실제 서비스 트래픽에 적용할 때 필요한 동작 원리와 설계 판단을 확정한다.

## 결론

Deep Agents의 스트리밍은 독립적인 전송 기능이 아니다. Deep Agents가 만든 Agent는 LangGraph runtime 위에서 실행되고, LangGraph가 실행 이벤트를 Python async iterator로 노출한다. FastAPI/Starlette는 그 iterator의 값을 ASGI body message로 바꾸며, Uvicorn과 운영체제가 TCP 흐름 제어를 담당한다. SSE는 이 byte stream에 `event`, `data`, `id`, `retry` 필드를 붙이는 wire format이다.

```text
model/tool/subagent
  -> LangChain callback
  -> LangGraph AsyncQueue (현재 공식 소스는 unbounded)
  -> graph.astream() async iterator
  -> event projection/filter/serialization
  -> Starlette EventSourceResponse 또는 StreamingResponse
  -> ASGI send()
  -> Uvicorn write buffer
  -> reverse proxy / load balancer
  -> TCP
  -> browser fetch/EventSource
```

`async for chunk in agent.astream(...): yield chunk`만으로도 기능은 동작하지만 다음 운영 성질은 해결되지 않는다.

- LangGraph의 현재 in-process 스트림 큐는 크기 제한이 없으며 callback은 `put_nowait()`로 넣는다.
- 느리거나 멈춘 클라이언트가 model/tool 생산 속도를 끝까지 제어한다는 보장이 없다.
- 연결 종료와 Agent run 종료가 같은 의미인지 제품 정책이 정해져 있지 않다.
- process/pod가 바뀌면 in-memory event를 재생할 수 없다.
- SSE 연결이 열린 뒤에는 HTTP status code를 오류에 맞게 바꿀 수 없다.
- proxy buffering과 idle timeout을 맞추지 않으면 서버는 전송했지만 사용자는 늦게 받거나 연결이 끊긴다.

서비스 기본안은 다음 두 단계다.

1. 초기 버전은 **연결 결합형**으로 만든다. 하나의 request task가 `agent.astream()`을 직접 소비하고 SSE로 보낸다. 동시 run 제한, send timeout, disconnect 취소, heartbeat, 작은 event, 관측 지표를 반드시 둔다.
2. 연결이 끊겨도 실행을 계속해야 하거나 수평 확장·재접속·긴 작업이 필요해지면 **run/transport 분리형**으로 전환한다. run은 background worker가 수행하고, event는 Redis Pub/Sub 또는 Redis Streams를 거쳐 SSE gateway가 전달한다. 최종 상태와 checkpoint는 PostgreSQL에 둔다.

`asyncio.Queue`를 무조건 추가하는 것은 최적화가 아니다. 같은 request 안에서 producer와 consumer를 분리하면 task 수와 복사만 늘고, unbounded queue는 메모리 위험을 추가한다. 큐가 필요한 경우에는 `maxsize`가 있는 per-run 채널과 명시적인 overflow 정책이 있어야 한다.

## 1. 각 계층의 실제 책임

### 1.1 Deep Agents

Deep Agents 공식 architecture는 계층을 다음처럼 구분한다.

| 계층 | 스트리밍 책임 |
| --- | --- |
| Deep Agents | middleware, planning, filesystem, subagent 등 Agent harness |
| LangChain | model/tool callback과 Agent loop |
| LangGraph | state, checkpoint, interrupt, 실행 및 stream event |

즉 Deep Agents를 사용한다고 별도 SSE 구현이 생기지 않는다. `create_deep_agent()` 결과가 LangGraph compiled graph와 같은 streaming interface를 제공하는 구조다. Deep Agents CLI도 graph의 `astream()`을 소비한다.

근거: [Deep Agents architecture](https://github.com/langchain-ai/deepagents/blob/main/libs/ARCHITECTURE.md), [Deep Agents source](https://github.com/langchain-ai/deepagents)

### 1.2 LangGraph

LangGraph `astream()`은 `messages`, `updates`, `custom`, `values`, `tasks`, `debug` 등의 projection을 제공한다.

- `messages`: `(AIMessageChunk, metadata)` 형태의 model token/message chunk
- `updates`: node 실행 뒤의 state delta; HITL의 `__interrupt__`도 여기서 확인
- `custom`: node/tool이 `StreamWriter`로 직접 발행한 진행 이벤트
- `values`: 매 step의 전체 state라 payload가 커지기 쉬움
- `tasks`, `debug`: 운영 UI의 기본 응답보다 진단 목적에 가깝다.

사용자 UI에는 보통 `messages + updates + custom`의 필요한 일부만 투영해야 한다. `values`나 `debug`를 그대로 SSE에 흘리면 누적 message state와 내부 정보가 반복 직렬화되어 CPU, bandwidth, 정보 노출 비용이 커진다.

근거: [LangGraph stream types](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/types.py), [LangGraph streaming cookbook](https://github.com/langchain-ai/streaming-cookbook)

### 1.3 Starlette/FastAPI와 ASGI

Starlette `StreamingResponse`는 async iterator에서 다음 chunk를 받고 ASGI의 `http.response.body`를 `more_body=True`로 보낸다. SSE protocol의 framing, ping, send timeout을 직접 구현하려면 실수할 여지가 있으므로 `sse-starlette`의 `EventSourceResponse`가 더 적합하다.

여기서 “더 적합하다”는 더 빠르거나 더 낮은 계층이라는 뜻이 아니다. 두 클래스는 모두 Starlette `Response`를 기반으로 ASGI message를 보내며, 현재 `EventSourceResponse`는 `StreamingResponse`를 상속하지도 않는다. 차이는 **범용 byte stream**과 **SSE protocol 및 장기 연결 lifecycle을 구현한 전용 response**라는 책임 범위에 있다.

#### 공통으로 하는 일

두 response 모두 다음 순서로 동작한다.

```text
iterator에서 값 받기
  -> bytes로 변환
  -> http.response.start 한 번 전송
  -> http.response.body(more_body=True) 반복
  -> 마지막에 빈 body(more_body=False) 전송
```

따라서 `StreamingResponse`로도 SSE를 완전히 구현할 수 있다. 다만 아래 기능을 application generator와 header 설정으로 직접 책임져야 한다.

#### 차이 요약

| 항목 | `StreamingResponse` | `EventSourceResponse` |
| --- | --- | --- |
| 목적 | 임의의 byte/text stream | SSE 전용 stream |
| 기본 media type | 호출자가 지정 | `text/event-stream` |
| 입력 값 | `bytes`, `memoryview`, encode 가능한 값 | `bytes`, `dict`, `ServerSentEvent`, 기타 값 |
| SSE framing | 직접 `data: ...\n\n` 생성 | `event`, `data`, `id`, `retry`, comment를 규격대로 encode |
| 여러 줄 data | 직접 각 줄에 `data:` 필요 | 각 줄을 별도 `data:` field로 변환 |
| event ID/name newline | 직접 sanitize | newline 제거 |
| heartbeat | 직접 generator/timer 구현 | 별도 ping task, 기본 15초 |
| send timeout | 없음 | data와 ping 각각 `send_timeout` 적용 |
| disconnect | Starlette 기본 처리 | 항상 listener를 두고 callback 및 active state 관리 |
| proxy header | 직접 설정 | `X-Accel-Buffering: no` 기본 설정 |
| cache/connection header | 직접 설정 | `Cache-Control: no-store`, `Connection: keep-alive` |
| server shutdown | 기본 cancellation | shutdown signal과 선택적 grace period |
| push producer/channel | 직접 task lifecycle 관리 | `data_sender_callable` 지원 |
| compression | 일반 response 설정에 따름 | SSE compression을 명시적으로 거부 |
| 추가 비용 | 상대적으로 작은 실행 경로 | ping/disconnect/shutdown tasks와 send lock |

#### `StreamingResponse`가 실제로 하는 일

현재 Starlette 공식 소스의 핵심은 매우 작다.

```python
async def stream_response(self, send):
    await send({"type": "http.response.start", ...})
    async for chunk in self.body_iterator:
        if not isinstance(chunk, bytes | memoryview):
            chunk = chunk.encode(self.charset)
        await send({
            "type": "http.response.body",
            "body": chunk,
            "more_body": True,
        })
    await send({
        "type": "http.response.body",
        "body": b"",
        "more_body": False,
    })
```

이 클래스는 chunk의 의미를 모른다. 다음 문자열을 yield해도 그대로 전송할 뿐, 이것이 완전한 SSE event인지 검사하거나 수정하지 않는다.

```python
yield 'data: hello\n\n'
```

예를 들어 data가 `"first line\nsecond line"`이면 SSE 규격상 다음처럼 만들어야 한다.

```text
data: first line
data: second line

```

`StreamingResponse`는 이를 대신하지 않는다. JSON serialization, `id:`, `event:`, 빈 줄 delimiter, newline injection 방지까지 모두 application code의 책임이다.

Starlette는 client disconnect도 처리한다. ASGI 2.4 이상에서는 socket `send()`가 `OSError`를 내면 `ClientDisconnect`로 변환하고, 이전 ASGI 버전에서는 response task와 `http.disconnect` listener를 함께 실행한다. 그러므로 `StreamingResponse`가 disconnect를 전혀 모른다는 설명은 정확하지 않다. 차이는 SSE 전용 callback과 ping 등의 lifecycle을 함께 조정하지 않는다는 점이다.

#### `EventSourceResponse`가 추가하는 일

`EventSourceResponse`의 전송 loop는 iterator 값마다 `ensure_bytes()`를 호출한다.

```python
async for data in self.body_iterator:
    chunk = ensure_bytes(data, self.sep)
    await self._send_with_timeout(
        send,
        {
            "type": "http.response.body",
            "body": chunk,
            "more_body": True,
        },
    )
```

`ensure_bytes()`는 입력에 따라 다음처럼 처리한다.

- `bytes`: 이미 formatting된 event로 보고 그대로 사용
- `ServerSentEvent`: `event`, `data`, `id`, `retry`, `comment`를 encode
- `dict`: dict의 key를 `ServerSentEvent` constructor에 전달
- 기타 값: 하나의 `data:` event로 변환

따라서 application은 framing 문자열을 조립하지 않고 구조화된 값을 낼 수 있다.

```python
yield {
    "event": "message.delta",
    "id": "1842",
    "data": '{"text":"안녕"}',
    "retry": 3000,
}
```

전송 결과는 다음과 같다.

```text
id: 1842
event: message.delta
data: {"text":"안녕"}
retry: 3000

```

JSON object를 자동으로 JSON 문자열로 만드는 것은 일반 `ServerSentEvent`가 아니라 `JSONServerSentEvent`의 책임이다. dict를 `data` 값에 넣는 것과 event field dict를 yield하는 것을 혼동하면 안 된다.

장기 연결에서는 data가 한동안 나오지 않을 수 있다. 예를 들어 DeepAgent가 긴 tool을 실행하는 동안 model token이 90초간 없을 수 있다. 이때 `StreamingResponse` generator가 조용하면 proxy가 idle connection을 닫을 수 있다. `EventSourceResponse`는 data producer와 독립적인 ping task가 기본 15초마다 다음 comment를 보낸다.

```text
: ping - 2026-09-20T...

```

SSE client는 comment를 application event로 전달하지 않지만 network path에는 byte가 흐르므로 idle timeout을 방지할 수 있다. data와 ping이 동시에 ASGI `send()`를 호출하지 않도록 내부 `anyio.Lock`도 사용한다.

느린 client가 socket을 유지한 채 읽기를 멈추면 `http.disconnect`가 즉시 오지 않을 수 있다. Uvicorn의 write buffer가 가득 찬 뒤 `send()`가 오래 block될 수 있다. `StreamingResponse`에는 개별 send deadline이 없지만 `EventSourceResponse`는 `send_timeout`이 지나면 `SendTimeoutError`를 발생시키고 body iterator를 닫거나 task group을 취소한다. 이 차이가 production에서 특히 중요하다.

`EventSourceResponse.__call__()`은 다음 작업을 하나의 AnyIO task group으로 묶는다.

```text
_stream_response             # application event 전송
_ping                        # heartbeat 전송
_listen_for_disconnect       # client disconnect 감시
_listen_for_exit_signal      # server shutdown 감시
data_sender_callable         # 선택적 channel producer
```

어느 핵심 task든 종료되면 나머지를 취소한다. server shutdown 때 generator가 cleanup/farewell event를 처리할 수 있도록 `shutdown_event`와 `shutdown_grace_period`도 제공한다.

#### 같은 응답을 두 방식으로 구현하면

`StreamingResponse`에서는 SSE 규격과 heartbeat를 generator가 함께 구현해야 한다.

```python
async def stream():
    while True:
        # 실제 event와 heartbeat timer를 직접 multiplex해야 한다.
        item = await next_item_or_heartbeat()
        if item.is_heartbeat:
            yield b": ping\n\n"
        else:
            payload = json.dumps(item.data, ensure_ascii=False)
            yield f"id: {item.id}\nevent: {item.type}\ndata: {payload}\n\n"

return StreamingResponse(
    stream(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-store",
        "X-Accel-Buffering": "no",
    },
)
```

이 예제에도 send timeout과 shutdown coordination은 아직 없다.

`EventSourceResponse`에서는 data generator와 protocol/lifecycle을 분리할 수 있다.

```python
async def stream():
    async for item in agent_events():
        yield JSONServerSentEvent(
            data=item.data,
            event=item.type,
            id=str(item.seq),
        )

return EventSourceResponse(
    stream(),
    ping=15,
    send_timeout=30,
)
```

#### 언제 `StreamingResponse`가 더 나은가

다음 조건이라면 범용 response를 직접 쓰는 선택도 타당하다.

- SSE가 아니라 NDJSON, raw token text, file/media stream을 보낸다.
- gateway나 별도 transport layer가 이미 framing, heartbeat, timeout을 책임진다.
- 매우 높은 event rate에서 ping task와 send lock 비용이 측정 가능한 병목이다.
- 정확한 connection lifecycle을 직접 구현하고 유지할 팀과 test가 있다.
- 단기 내부 PoC이며 proxy와 reconnect 요구가 없다.

실제로 `EventSourceResponse`는 ping과 data send의 race를 막기 위한 lock을 사용하므로 범용 `StreamingResponse`보다 실행 경로가 무겁다. 따라서 “EventSourceResponse가 성능 최적화 도구”라고 표현하면 틀리다. 선택 이유는 protocol correctness와 운영 안전장치다.

#### DeepAgent 서비스에서의 판단

DeepAgent는 model token만 흘리는 것이 아니라 긴 tool/subagent 구간, HITL interrupt, 오류, server shutdown을 포함한다. 이 workload에서는 다음 항목을 매 endpoint마다 직접 구현하는 비용이 크다.

- typed event와 `id` formatting
- 긴 무응답 구간 heartbeat
- 읽지 않는 client의 send timeout
- disconnect 시 Agent iterator cleanup
- server shutdown 시 task 정리
- Nginx buffering 방지 header

따라서 현재 설계에서는 `EventSourceResponse`를 기본으로 선택한다. 부하 시험에서 이 클래스 자체가 병목으로 확인될 때만 필요한 SSE 기능을 유지한 custom `StreamingResponse`로 교체한다. 그때도 단순한 `yield` loop만 남기는 것이 아니라 위 lifecycle 요구사항을 회귀 test로 고정해야 한다.

`EventSourceResponse`는 다음을 제공한다.

- `text/event-stream`, `Cache-Control`, `Connection`, `X-Accel-Buffering` header
- 주기적 ping comment
- client disconnect 감시
- `send_timeout`
- generator 외에 AnyIO memory channel 사용 가능
- server shutdown과 producer task의 lifecycle 관리

근거: [Starlette responses](https://www.starlette.io/responses/), [sse-starlette README](https://github.com/sysid/sse-starlette), [EventSourceResponse source](https://github.com/sysid/sse-starlette/blob/main/sse_starlette/sse.py)

소스 검증 기준:

- Starlette `57de5fa9c2a98089a78d32d560e9b23e62560d5f` (2026-09-20)
- sse-starlette `6754ef387da97cf6cfbcd1bd5c216b533937b304` (2026-09-05)

### 1.4 Uvicorn, TCP, 느린 소비자

Uvicorn은 transport write buffer가 high-water mark를 넘으면 ASGI `send()`가 buffer가 low-water mark 아래로 줄 때까지 반환되지 않도록 write flow control을 적용한다. 따라서 HTTP 계층에는 backpressure가 존재한다.

그러나 이것이 LangGraph의 event 생산까지 그대로 전파된다는 뜻은 아니다. 공식 LangGraph 소스에서 `astream()`은 `AsyncQueue()`를 만들고 callback이 `put_nowait()`로 event를 넣는다. 이 queue는 `asyncio.Queue` 기본값을 사용하므로 unbounded다. SSE 쪽 `send()`가 느려져 다음 `anext()` 호출이 늦어져도 model callback task는 이미 생성되는 token을 queue에 넣을 수 있다.

이는 소스에서 직접 확인한 내용이다.

```python
# langgraph/_internal/_queue.py
class AsyncQueue(asyncio.Queue):
    """Async unbounded FIFO queue with a wait() method."""

# langgraph/pregel/main.py
stream = AsyncQueue()
stream_put = partial(aioloop.call_soon_threadsafe, stream.put_nowait)
```

검증한 공식 commit:

- LangGraph `aa742fb31e2827d569b843e3600aeda2e0528e4b` (2026-09-18)
- Deep Agents `bc3c2935650f8e8a0862d51226d986d842bd3824` (2026-09-20)

근거: [Uvicorn flow control](https://www.uvicorn.org/server-behavior/), [LangGraph queue source](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/_internal/_queue.py), [LangGraph Pregel source](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/pregel/main.py)

## 2. “내부적으로 큐를 쓰는가?”에 대한 정확한 답

쓴다. 다만 서로 목적이 다른 여러 queue/buffer를 한 개념으로 보면 안 된다.

| 위치 | 목적 | 크기·특성 | 느린 client의 영향 |
| --- | --- | --- | --- |
| LangGraph `AsyncQueue` | 실행 callback event를 `astream()` 소비자에게 전달 | 현재 unbounded FIFO | 직접적인 producer backpressure 없음 |
| 선택적 app memory channel | Agent event와 SSE writer 분리 | 반드시 bounded 권장 | 가득 찼을 때 block/drop/cancel 정책 가능 |
| Uvicorn write buffer | ASGI bytes를 socket에 전달 | high/low water mark | `await send()`를 block |
| kernel TCP send buffer | network 전송 | OS 설정 | 가득 차면 socket write 지연 |
| proxy buffer | upstream response를 모아 client에 전달 | 제품/설정별 | token이 뭉쳐 보이거나 지연 발생 |
| Redis Pub/Sub | 다른 process의 live event fan-out | 비영속 | 느린/끊긴 subscriber가 event 유실 |
| Redis Streams | 순서 있는 replay log | retention으로 제한 | reconnect replay와 process 분리 가능 |

핵심은 app-level bounded queue가 LangGraph 내부 unbounded queue를 자동으로 bounded로 바꾸지는 않는다는 점이다. 별도 producer task가 `astream()`을 빠르게 pull하여 bounded app queue에 넣는다면 app queue가 찼을 때 그 task는 멈추지만, 그동안 LangGraph 안에서 진행 중인 model callbacks가 내부 queue를 채울 수 있다.

따라서 LLM token stream에서는 “모든 token에 완전한 end-to-end backpressure”를 만들려 하기보다 다음 보호 장치를 함께 사용해야 한다.

1. 느린 client의 `send()`에 timeout을 둔다.
2. disconnect/timeout 정책에 따라 run을 cancel하거나 background run으로 분리한다.
3. event payload와 stream mode를 최소화한다.
4. 전체 동시 run과 tenant/user별 run 수를 제한한다.
5. queue depth, send latency, disconnect, dropped/coalesced event를 측정한다.

## 3. SSE protocol에서 꼭 알아야 할 것

SSE는 UTF-8 text stream이며 event는 빈 줄로 구분한다.

```text
id: 1842
event: token
data: {"run_id":"r1","seq":1842,"text":"안녕"}

: heartbeat

event: done
data: {"run_id":"r1","finish_reason":"stop"}

```

브라우저의 native `EventSource`는 연결이 끊기면 재접속하고, 서버가 `id:`를 보냈다면 `Last-Event-ID`를 전송한다. 그러나 event ID를 발행하는 것만으로 replay가 생기지는 않는다. 서버가 해당 ID 이후의 event를 저장하고 다시 읽는 로직을 구현해야 한다.

Native `EventSource`의 제약도 설계에 영향을 준다.

- GET 기반이며 임의의 `Authorization` header를 지정하기 어렵다. cookie 인증을 사용하거나 `fetch` + `ReadableStream`/`fetch-event-source` 계열을 고려한다.
- HTTP/1.1에서는 browser+domain당 열린 연결 수가 낮다. MDN은 일반적으로 6개 제한을 설명한다. HTTP/2에서는 stream 수를 협상한다.
- reconnect는 자동이어도 중복·누락을 제거해 주지 않는다.

근거: [MDN Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)

## 4. 연결 결합형과 run/transport 분리형

### 4.1 연결 결합형

```text
POST /runs/stream
  -> request task가 agent.astream() 실행
  -> event 직렬화
  -> 같은 HTTP response로 전송
  -> disconnect 시 iterator close + run cancel
```

적합한 조건:

- 대부분 수십 초 안에 끝난다.
- UI가 떠난 뒤 결과를 계속 만들 필요가 없다.
- 재접속 replay가 제품 요구사항이 아니다.
- 한 run의 event 생산자와 client가 1:1이다.
- 초기 서비스로 운영 복잡성을 낮춰야 한다.

장점은 hops가 적어 first-token latency가 낮고 구현과 디버깅이 쉽다는 것이다. 단점은 client lifecycle과 비싼 Agent 실행이 묶이며 rolling deploy, mobile background, network 단절에 취약하다는 것이다.

이 모델에서도 연결마다 별도 unbounded `asyncio.Queue`를 만들 필요는 없다. `agent.astream()`을 직접 iterate하는 경로부터 시작한다. generator와 별도 producer가 필요한 구체적 이유가 생기면 bounded AnyIO channel을 사용한다.

### 4.2 run/transport 분리형

```text
POST /runs
  -> run row 생성 (PostgreSQL)
  -> worker queue에 run 알림
  -> background worker가 agent 실행/checkpoint 저장
  -> live event publish (Redis Pub/Sub)
  -> 선택적 replay event append (Redis Streams)

GET /runs/{run_id}/stream
  -> authorization
  -> Last-Event-ID 이후 replay
  -> live channel subscribe
  -> SSE forward
```

적합한 조건:

- 수분 이상 걸리는 research/code task가 있다.
- 연결이 끊겨도 계산을 계속해야 한다.
- page 이동, mobile background, multi-device handoff 뒤 재접속해야 한다.
- API pod와 worker를 독립 확장해야 한다.
- 동일 run을 여러 observer가 볼 수 있다.

LangSmith Agent Server는 실제로 이 분리를 사용한다. PostgreSQL에 thread/run/checkpoint를 저장하고, API server와 queue worker 사이의 wake-up·cancel·live output에 Redis를 사용한다. 공식 문서는 streaming output에는 Redis Pub/Sub을 사용하며 event를 Redis에 저장하지 않는다고 명시한다. 즉 live reconnect 동안 놓친 event replay가 필요하면 Pub/Sub만으로 충분하지 않고 별도 resumable stream 기능 또는 durable log가 필요하다.

근거: [LangSmith data plane](https://docs.langchain.com/langsmith/data-plane), [join/rejoin streams](https://docs.langchain.com/oss/javascript/langchain/frontend/join-rejoin)

## 5. Pub/Sub과 Redis Streams를 구분해야 하는 이유

| 요구 | Redis Pub/Sub | Redis Streams |
| --- | --- | --- |
| live fan-out | 적합 | 가능 |
| 끊긴 동안 event replay | 불가 | 적합 |
| retention 제한 | 저장하지 않음 | `MAXLEN`/`MINID` 필요 |
| per-event ID | application 별도 | stream ID 사용 가능 |
| consumer ack | 없음 | consumer group에서 가능 |
| 비용·복잡성 | 낮음 | 더 높음 |

Agent token은 최종 답변 state로 복구할 수 있으므로 모든 token을 영구 보관할 필요는 없는 경우가 많다. 다음 중 하나를 제품 요구에 맞게 선택한다.

- **live only**: Redis Pub/Sub. reconnect하면 현재 run status와 누적 answer snapshot을 다시 받고 이후 live event를 구독한다.
- **짧은 replay window**: Redis Streams에 최근 N분/N개 event만 저장하고 `Last-Event-ID` 이후를 재생한다.
- **durable audit**: token 전체보다 node transition, tool call, approval, final answer를 PostgreSQL/audit store에 저장한다.

Redis Streams는 append-only log이며 ID 기반 range/read와 trimming을 제공한다. 그러나 stream 하나가 자동 partition되는 것은 아니므로 `run_id` 또는 tenant 단위 key 설계, TTL/trim, hot key를 실측해야 한다.

근거: [Redis Streams official documentation](https://redis.io/docs/latest/develop/data-types/streams/)

## 6. 현업 사례에서 반복되는 설계

### LangSmith Agent Server

#### 어떤 문제를 해결하려는 구조인가

가장 단순한 Agent SSE endpoint는 하나의 API process 안에서 요청 접수, Agent 실행, SSE 연결을 모두 처리한다.

```text
browser
  -> API request task
       -> agent.astream()
       -> model/tool 실행
       -> SSE send
```

이 구조에서는 하나의 process가 서로 성질이 다른 두 부하를 동시에 가진다.

1. **API/SSE 부하**: 인증, request validation, thread 조회, 열린 socket, heartbeat, byte 전송
2. **Agent 실행 부하**: LLM 대기, tool I/O, subagent, checkpoint write, retry, 긴 실행 시간

예를 들어 Agent 요청이 갑자기 100개 들어오면 model provider rate limit 때문에 80개가 실행 대기 상태가 될 수 있다. 이때 같은 process가 모든 run과 SSE 연결을 소유하면 단순한 thread 조회나 health check도 영향을 받는다. 또 client connection이 끊기거나 API pod가 재시작될 때 Agent run까지 같이 사라지기 쉽다.

LangSmith Agent Server는 이 두 lifecycle을 분리한다.

```text
                     PostgreSQL
                  run/thread/checkpoint
                         ^
                         |
browser -> API server --+--> run 생성
             |                   |
             |              Redis list wake-up
             |                   |
             |             background worker
             |                   |
             +-- Redis Pub/Sub <-+-- agent stream event
             |
             +--> SSE response -> browser
```

#### run 요청 한 건의 흐름

공식 data-plane 문서를 바탕으로 요청 흐름을 풀면 다음과 같다.

1. API server가 요청을 인증하고 run record를 PostgreSQL에 만든다.
2. API server가 Redis list에 sentinel을 넣어 대기 중인 worker를 깨운다.
3. worker는 Redis list에서 실제 run payload를 받는 것이 아니라 PostgreSQL에서 처리할 run 정보를 조회한다.
4. worker가 Agent graph를 실행하고 checkpoint를 PostgreSQL에 저장한다.
5. worker가 생성한 token/state event를 Redis Pub/Sub channel에 publish한다.
6. `/stream` 요청을 잡고 있는 API server가 해당 channel을 subscribe하고 event를 SSE로 client에 전달한다.
7. client가 cancel을 요청하면 API server와 해당 worker 사이의 cancellation 통신에도 Redis string과 Pub/Sub channel이 사용된다.

여기서 Redis list에 run 전체가 아니라 sentinel만 넣는 점이 중요하다.

```text
Redis list  = "새 일이 있으니 DB를 확인하라"는 wake-up 신호
PostgreSQL  = run이 실제로 존재하며 어떤 상태인지 판단하는 source of truth
```

만약 queue payload만 run의 원본으로 사용하면 Redis 장애, message 유실, worker crash 때 DB의 run 상태와 queue가 서로 어긋날 수 있다. 공식 문서는 설계 이유까지 명시하지 않지만, sentinel과 PostgreSQL 조회를 분리한 구조는 Redis를 durable business store로 만들지 않고 notification/coordination 계층으로 제한한다는 의미로 해석할 수 있다. 이 문장은 문서의 사실을 바탕으로 한 설계적 추론이다.

#### 왜 live output에는 Redis Pub/Sub을 사용하는가

Agent를 실행하는 worker와 browser socket을 보유한 API server가 같은 process라는 보장이 없다.

```text
worker A: token 생산
API server B: client SSE socket 보유
```

두 process 사이에 전달 통로가 필요하므로 worker가 Redis Pub/Sub에 publish하고 API server가 subscribe한다. Pub/Sub은 event를 저장하지 않기 때문에 live forwarding에는 빠르고 단순하지만 subscriber가 끊긴 동안의 event는 사라진다. LangSmith 공식 문서도 streaming event가 Redis에 저장되지 않는다고 명시한다.

따라서 세 종류의 “복구”를 구분해야 한다.

| 복구 대상 | 담당 저장소/기능 |
| --- | --- |
| Agent 계산 상태 | PostgreSQL checkpoint |
| run/thread의 최종 상태 | PostgreSQL |
| 연결 중 실시간 event 전달 | Redis Pub/Sub |
| 연결이 끊긴 동안의 token replay | 기본 Pub/Sub만으로는 불가능 |

checkpoint가 있다고 과거 SSE token event가 그대로 재생되는 것은 아니다. checkpoint는 graph state를 복구하고 실행을 이어가기 위한 snapshot이고, event log는 특정 cursor 이후의 출력 조각을 순서대로 다시 보내기 위한 log다. 두 데이터의 목적과 access pattern이 다르다.

#### 왜 API server와 worker를 서로 다르게 scale하는가

LangSmith 문서는 API server를 CPU/memory로, queue worker를 pending run 수로 scale한다고 설명한다.

```text
SSE 연결과 조회 증가
  -> API server CPU/memory 증가
  -> API server 확장

Agent 요청 backlog 증가
  -> pending run 증가
  -> worker 확장
```

두 부하는 반드시 같이 증가하지 않는다. 이미 완료된 conversation을 조회하는 사용자가 많으면 API만 바쁘다. 반대로 client 수는 적어도 각 사용자가 긴 deep research를 실행하면 worker backlog가 커진다. 이를 같은 replica count로 묶으면 한쪽은 부족하고 다른 쪽은 놀 수 있다.

공식 문서가 제시하는 dedicated deployment 기준은 CPU와 memory 목표 75%, worker당 pending run 목표 10개다. 이는 LangSmith의 운영 기준이지 우리 서비스의 권장값은 아니다. 우리 Agent의 model latency, tool 시간, provider quota에 맞춰 다시 측정해야 한다.

#### 이 사례에서 가져올 것과 가져오지 않을 것

가져올 원칙:

- HTTP connection lifecycle과 Agent run lifecycle을 분리할 수 있어야 한다.
- PostgreSQL/checkpointer를 run state의 source of truth로 둔다.
- Redis는 coordination과 live event 전달에 제한해 사용할 수 있다.
- API와 worker는 서로 다른 지표로 확장한다.

바로 복사하지 않을 부분:

- 초기 서비스부터 API/worker/Redis를 모두 분리할 필요는 없다.
- token replay가 필요하다면 Pub/Sub만으로는 부족하다.
- worker 수를 늘려도 provider rate limit이 그대로라면 처리량은 늘지 않고 throttling만 증가한다.

근거: [LangSmith data plane](https://docs.langchain.com/langsmith/data-plane)

### Artera의 multi-node SSE gateway

#### 먼저 바로잡을 점: Redis Pub/Sub이 아니라 Redis Streams다

Artera 글은 중앙 stream을 pub/sub topic처럼 사용한다고 표현하지만 실제 명령은 `PUBLISH/SUBSCRIBE`가 아니라 `XADD`, `XREAD`, `XRANGE`다. 즉 event를 저장하지 않는 Redis Pub/Sub이 아니라 일정 기간 event를 보관하는 Redis Streams 구조다.

이 차이는 reconnect에서 결정적이다.

```text
Redis Pub/Sub
  client가 없을 때 publish -> event 소멸

Redis Streams
  XADD -> event가 ID와 함께 저장
  나중에 XREAD/XRANGE -> 놓친 event 조회 가능
```

#### 배경과 해결하려던 문제

Artera는 환자 관련 실시간 notification을 외부 서비스에 의존하다가 국제 확장 과정에서 data sovereignty와 규제 요구 때문에 자체 real-time infrastructure를 만들었다. corporate firewall이 WebSocket upgrade를 막는 경우가 있다는 초기 실험을 근거로 단방향 notification에는 표준 HTTP 위에서 동작하는 SSE를 선택했다.

단일 gateway라면 process memory에 connection map을 두고 event를 바로 전달할 수 있다.

```text
publisher -> gateway A -> gateway A에 연결된 clients
```

gateway가 여러 대가 되면 문제가 생긴다.

```text
user 1 socket -> gateway A
publisher event -> gateway B
```

Gateway B는 Gateway A의 memory에 있는 socket에 접근할 수 없다. load balancer가 어느 gateway로 event producer와 client를 보낼지도 보장하지 않는다. 그래서 모든 gateway가 볼 수 있는 중앙 event bus가 필요하다.

#### 세 가지 Redis 자료구조

Artera는 목적이 다른 세 구조를 둔다.

```text
rtg:presence                  Redis Sorted Set
rtg:notifications             전역 capped Redis Stream
rtg:history:{USER_ID}         사용자별 TTL Redis Stream
```

##### 1. Presence Store: 받을 사람이 없으면 앞에서 버린다

`rtg:presence` sorted set에는 user ID를 member로, 최근 activity timestamp를 score로 저장한다.

```redis
ZADD rtg:presence <current_timestamp> <user_id>
ZSCORE rtg:presence <user_id>
```

새 event를 받으면 target channel에 최근 활동 사용자가 있는지 먼저 확인한다. 글에서는 최근 30분 이내 활동을 online으로 간주한 예를 들며, active user가 없으면 event를 downstream에 넣지 않는다. 이 필터로 불필요한 event 처리의 90% 이상을 제거했다고 보고한다.

이 최적화가 가능한 이유는 notification이 offline 사용자에게 즉시 전달될 필요가 없고 별도 canonical data에서 나중에 상태를 확인할 수 있기 때문이다. Agent token에는 그대로 적용하기 어렵다. 사용자가 잠시 background로 이동했다고 이미 비용을 지불한 Agent 결과를 버릴지, run을 계속하고 final state를 저장할지는 별도 제품 정책이다.

##### 2. Notification Stream: 모든 gateway가 보는 전역 live log

모든 최근 event를 하나의 capped stream에 추가한다.

```redis
XADD rtg:notifications MAXLEN ~ 10000 * \
  data <payload> channelId <user_id>
```

Redis가 `1692632147971-0` 같은 단조 증가 ID를 만든다. 각 gateway는 마지막으로 읽은 ID 이후를 blocking `XREAD`로 가져온다.

```redis
XREAD COUNT 100 BLOCK 5000 \
  STREAMS rtg:notifications <last_event_id>
```

각 gateway는 받은 event의 target user가 자기 in-memory subscription map에 있으면 해당 SSE socket으로 전달한다.

```text
publisher
  -> global Redis Stream
       -> gateway A -> A에 연결된 target client
       -> gateway B -> B에 연결된 target client
       -> gateway C -> target이 없으면 무시
```

이 구조는 routing table을 중앙에서 관리하지 않아 단순하지만 모든 gateway가 모든 event를 읽는다. gateway가 20대면 같은 Redis event가 20대 모두로 전달된다. Artera는 network 효율보다 service discovery와 routing 단순성을 선택했다고 명시한다.

##### 3. History Stream: 사용자 reconnect 전용 짧은 buffer

전역 stream만으로 client별 replay를 처리하면 target filtering과 cursor 관리가 복잡해진다. Artera는 online user마다 별도 history stream을 둔다.

```redis
MULTI
XADD rtg:history:<user_id> MAXLEN ~ <message_count> * data <payload>
EXPIRE rtg:history:<user_id> <expiration_seconds>
EXEC
```

client가 마지막으로 받은 SSE `id`를 `Last-Event-ID`로 보내면 gateway가 그 이후 event를 조회한다.

```redis
XRANGE rtg:history:<user_id> <last_event_id> +
```

공개된 command만 보면 두 가지 구현 세부가 모호하다.

1. 전역 notification stream과 사용자 history stream에서 각각 `*`로 ID를 생성하면 두 stream의 entry ID가 같다는 보장이 없다. SSE에 어느 ID를 넣고 history가 그 ID를 어떻게 유지하는지 추가 정보가 필요하다. 실제 구현에서는 global event ID를 history payload/cursor로 보존하거나 history entry에 같은 explicit ID를 사용하는 등의 규칙이 필요하다.
2. Redis `XRANGE key <id> +`의 시작 ID는 inclusive다. client가 이미 받은 event를 제외하려면 exclusive lower bound인 `(<id>`를 사용하거나 application에서 첫 중복을 제거해야 한다. 블로그의 명령은 개념 설명용일 수 있으므로 그대로 복사하면 안 된다.

그 다음 live stream 구독으로 전환한다.

```text
client reconnect(Last-Event-ID=42)
  -> history에서 42 이후 event replay
  -> 현재 live event forwarding 시작
```

여기에는 replay와 live subscribe 사이에 event가 빠지는 race가 없어야 한다. Artera 글은 상세한 atomic handoff algorithm까지 공개하지 않으므로 구현 단계에서는 “live cursor 확보 → history replay → cursor 이후 live catch-up” 같은 전환 절차를 별도로 검증해야 한다. 이는 공개 사례가 답하지 않는 부분이다.

#### 왜 연결을 서버가 10~15분마다 끊는가

SSE connection은 몇 시간도 유지될 수 있다. rolling deployment에서 새 pod가 생겨도 기존 connection은 이전 pod에 계속 붙어 있으므로 load balancer가 이미 열린 연결을 새 pod로 옮기지 못한다.

```text
배포 전: gateway A에 10,000 connections
배포 중: gateway B 생성
결과: 새 connection만 B로 가고 기존 10,000개는 A에 남음
```

서버가 10~15분마다 연결을 의도적으로 종료하면 client가 재접속하면서 load balancer가 connection을 새 replica들에 재분배할 기회를 얻는다. 재접속 시 인증도 다시 수행되고 새로운 trace가 만들어지는 부가 효과가 있다.

이는 모든 서비스에 10~15분 제한을 권장한다는 뜻이 아니다. reconnect storm을 피하려면 connection lifetime에 jitter를 넣고, reconnect backoff와 replay capacity를 함께 설계해야 한다. Artera 글은 정확한 jitter 정책은 공개하지 않는다.

#### 왜 native EventSource 대신 fetch 기반 client를 사용했는가

브라우저 native `EventSource` constructor는 arbitrary request header를 지정할 수 없다. Bearer token을 `Authorization` header로 보내야 하는 환경에서는 제약이 된다. Artera는 Microsoft의 `fetch-event-source`를 사용해 custom header, retry 제어, stream parsing을 처리했다.

cookie 인증을 사용한다면 native EventSource도 가능하다. fetch 기반 client를 선택해야 한다는 보편 규칙은 아니다.

#### SSE가 안 되는 network를 위한 fallback

Artera는 일부 corporate firewall/proxy가 long-lived connection을 막는다고 보고했다. 해당 비율은 자사 환경에서 1% 미만이었다. SSE가 stuck/timeout되면 long polling을 보조 연결로 시작하고, SSE가 정상화되면 long polling을 닫는 fallback을 만들었다.

이는 HTTP 표준 위의 SSE도 모든 network에서 항상 통과한다는 보장이 없음을 보여 준다. 우리 서비스 대상이 사내망·병원망·금융망이라면 브라우저와 서버만 시험하지 말고 실제 proxy 환경을 포함해야 한다.

#### 공개된 결과와 해석의 한계

Artera는 다음 결과를 자체 보고했다.

- 일일 6천만 event
- 기존 대비 message latency 32% 개선
- server footprint 63% 감소
- publisher 1,000 requests/s
- Redis peak 100,000 requests/s

수치의 측정 방법, payload 크기, latency percentile, Redis 비용은 공개되지 않았다. 참고 가능한 production evidence이지만 동일 성능을 보장하는 benchmark로 사용하면 안 된다.

#### DeepAgent에 적용할 때

가져올 수 있는 원칙:

- event producer와 SSE socket을 가진 pod가 다르면 shared bus가 필요하다.
- event ID와 짧은 replay log가 있어야 `Last-Event-ID`가 실제 의미를 가진다.
- connection map은 gateway local memory에 두고 durable state와 분리할 수 있다.
- rolling deploy에서 long-lived connection 재분배 전략이 필요하다.
- 실제 target network에 따라 fetch client나 fallback transport가 필요할 수 있다.

다르게 판단할 부분:

- notification은 inactive user 대상 event를 버릴 수 있지만 Agent result는 그럴 수 없을 수 있다.
- 모든 token을 사용자별 Redis Stream에 복제하면 event 수와 memory 비용이 커진다. final snapshot + progress event만 replay하는 대안과 비교해야 한다.
- 전역 stream을 모든 gateway가 읽는 방식은 gateway 수와 token rate가 커지면 amplification이 심하다. per-run/per-tenant channel 또는 sharding이 필요할 수 있다.

근거: [Artera scalable SSE architecture](https://innovation.artera.io/blog/our-journey-to-a-scalable-sse-architecture/)

### sse-starlette 운영 이슈

#### disconnect와 stalled connection은 다르다

정상적인 disconnect에서는 browser가 tab을 닫거나 network가 끊어지고, ASGI server가 `http.disconnect`를 받거나 socket write에서 오류를 얻는다. response task는 이를 감지하고 generator를 취소할 수 있다.

stalled connection에서는 TCP connection이 여전히 열린 것으로 보이지만 client application이 response를 읽지 않는다.

```text
정상 disconnect
  socket 종료 -> server가 종료 신호/오류 감지

stalled client
  socket은 열림
  client read 중단
  server는 당분간 disconnect로 판단하지 못함
```

따라서 `request.is_disconnected()`만 반복 확인해도 stalled client를 바로 찾을 수 없다.

#### issue #89의 재현 과정

보고자는 `curl`로 SSE를 읽다가 `Ctrl+Z`로 process를 suspend했다.

```bash
curl -s -N localhost:8000/events > /dev/null
# Ctrl+Z로 curl process 정지
```

TCP connection 자체를 close한 것이 아니므로 server 입장에서는 연결이 살아 있다. 예제 server는 1ms마다 약 4 KiB payload를 계속 생성했다.

```python
while True:
    i += 1
    yield {"data": {i: " " * 4096}}
    await anyio.sleep(0.001)
```

처음에는 다음 buffer들이 대신 받아 준다.

```text
application event
  -> Uvicorn/asyncio transport write buffer
  -> server kernel TCP send buffer
  -> network
  -> client kernel receive buffer
```

client process가 읽지 않아도 kernel receive buffer에 공간이 있는 동안 server send는 성공할 수 있다. 시간이 지나 모든 buffer가 차면 TCP window가 줄어들고, 결국 ASGI `send()`가 write flow control에서 기다린다. issue의 예제는 약 400번째 출력 뒤 진행이 멈췄다. 이 숫자는 payload와 OS buffer 설정에 따른 재현 결과이며 일반 임계값은 아니다.

#### 왜 이것이 server resource 문제인가

멈춘 `send()` 하나만 보면 await 중이라 CPU를 많이 쓰지 않는다. 그러나 connection마다 다음 resource를 계속 점유한다.

- socket/file descriptor
- ASGI request task
- generator와 그 closure가 참조하는 객체
- Agent run과 model/tool resource
- 아직 전송되지 않은 buffer/event memory
- connection·tenant concurrency slot

공격자나 잘못된 client가 이런 connection을 많이 만들면 정상 사용자가 사용할 slot과 memory를 고갈시킬 수 있다. issue 작성자가 이를 DoS-like risk로 표현한 이유다.

#### `send_timeout`이 해결하는 범위

추가된 기능은 ASGI `send()` 한 번에 deadline을 둔다.

```python
return EventSourceResponse(
    event_generator(),
    send_timeout=30,
)
```

현재 구현은 AnyIO cancel scope 안에서 `send()`를 기다린다.

```python
with anyio.move_on_after(self.send_timeout) as cancel_scope:
    await send(message)

if cancel_scope.cancel_called:
    raise SendTimeoutError()
```

data event 전송이 timeout되면 body iterator의 `aclose()`를 호출하고 예외를 올린다. ping 전송이 timeout된 경우에는 실행 중인 async generator를 동시에 `aclose()`하지 않고 task group 전체를 취소해 generator의 `finally`가 실행되도록 한다.

이 timeout은 다음을 보장한다.

- 읽지 않는 client 때문에 `send()`가 무기한 매달리지 않는다.
- generator cleanup과 connection resource 회수 경로가 시작된다.

다음은 보장하지 않는다.

- 이미 provider에 전송된 LLM 요청의 과금이 즉시 멈춘다.
- 별도 background task로 분리된 Agent run이 자동 취소된다.
- LangGraph 내부 unbounded event queue에 이미 쌓인 memory가 즉시 사라진다.
- proxy가 buffering하면서 upstream data를 계속 받아 주는 경우 최종 client의 느림을 application이 즉시 안다.

따라서 `send_timeout`은 하나의 방어선이지 전체 backpressure 해결책이 아니다.

#### timeout 값을 어떻게 봐야 하는가

너무 짧으면 일시적으로 느린 mobile network를 끊고, 너무 길면 stalled connection이 resource를 오래 점유한다. 다음 latency를 관측해 정해야 한다.

```text
ASGI send latency p99
network가 일시적으로 느려지는 허용 시간
proxy/LB idle timeout
connection당 resource 비용
재접속 및 replay 가능 여부
```

replay가 없다면 aggressive timeout은 사용자 output 유실로 이어질 수 있다. replay 가능한 architecture라면 느린 연결을 더 빠르게 끊고 재접속시키는 선택이 가능하다.

#### DeepAgent에 대한 의미

client가 멈췄을 때 정책을 두 가지로 분리해야 한다.

```text
cancel_on_disconnect
  -> SSE 종료
  -> agent iterator close
  -> graph/provider cancellation 전파 시도

continue_on_disconnect
  -> SSE subscriber만 종료
  -> background run 계속
  -> checkpoint/final state 저장
  -> 나중에 client가 재접속 또는 결과 조회
```

짧은 chat은 첫 정책이 단순하다. 수분 걸리는 deep research나 code task는 두 번째 정책이 사용자 경험과 이미 지출한 model 비용을 보존할 가능성이 크다.

근거: [sse-starlette frozen connection issue](https://github.com/sysid/sse-starlette/issues/89)

## 7. proxy와 load balancer 설정

### Nginx

Nginx의 `proxy_buffering`이 켜지면 upstream response를 buffer에 모으므로 token이 즉시 보이지 않을 수 있다. SSE endpoint에서는 response의 `X-Accel-Buffering: no` 또는 endpoint별 `proxy_buffering off`를 적용한다.

`proxy_read_timeout`은 전체 응답 시간이 아니라 upstream의 연속 두 read 사이 timeout이다. 기본 60초이므로 heartbeat 간격은 이보다 짧아야 한다.

근거: [Nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

### AWS ALB

ALB의 default idle timeout은 60초다. timeout 전에 최소 1 byte의 application data를 보내야 하며 HTTP/2 PING frame은 ALB idle timeout을 reset하지 않는다. SSE comment heartbeat를 application payload로 보내는 이유다.

근거: [AWS ALB attributes](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-load-balancer-attributes.html)

운영 설정은 다음 부등식을 만족시켜야 한다.

```text
heartbeat interval
  < 가장 짧은 proxy/LB idle timeout
  < application stream idle timeout
  < absolute run/connection timeout
```

## 8. 권장 event contract

LangGraph 객체를 그대로 JSON 직렬화하지 말고 공개 schema로 projection한다.

```json
{
  "schema_version": 1,
  "run_id": "run_01...",
  "seq": 1842,
  "type": "token",
  "timestamp": "2026-09-20T10:00:00.123Z",
  "data": {"text": "안녕", "node": "model"}
}
```

최소 event type:

- `run.started`
- `message.delta`
- `tool.started`, `tool.completed`
- `subagent.started`, `subagent.completed`
- `approval.required`
- `run.completed`
- `run.failed`
- `heartbeat`는 SSE comment로 보내 application event에서 제외 가능

설계 규칙:

1. `seq`는 run 안에서 단조 증가하게 한다.
2. event는 작고 immutable하게 한다.
3. internal state, prompt, tool secret을 그대로 내보내지 않는다.
4. terminal event에는 final state를 조회할 수 있는 run ID를 포함한다.
5. error는 HTTP status가 아니라 typed SSE event로 보낸다. header 전송 후에는 status를 바꿀 수 없기 때문이다.
6. serialization 실패도 `run.failed`로 정규화하고 stream을 닫는다.

## 9. 초기 구현의 권장 형태

연결 결합형의 핵심 구조는 다음과 같다. 이는 다음 구현 단계에서 프로젝트의 실제 Agent interface에 맞춰 작성할 기준이며, 아직 repository code에 반영한 코드는 아니다.

```python
async def stream_agent(request, agent, input_, config):
    try:
        async for mode, chunk in agent.astream(
            input_,
            config=config,
            stream_mode=["messages", "updates", "custom"],
            subgraphs=True,
        ):
            if await request.is_disconnected():
                return

            event = project_public_event(mode, chunk)
            if event is not None:
                yield event
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        yield public_error_event(exc)
```

```python
return EventSourceResponse(
    stream_agent(request, agent, input_, config),
    ping=15,
    send_timeout=30,
    headers={
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
    },
)
```

구현 시 보완할 점:

- disconnect 시 `return`만 하지 말고 iterator `aclose()`와 run cancellation이 실제 provider HTTP request까지 전파되는지 통합 시험한다.
- sync tool을 event loop에서 직접 실행하지 않는다. async I/O 또는 bounded thread pool을 사용한다.
- global/tenant/user별 `CapacityLimiter`로 admission control을 한다. 제한 초과는 stream을 연 뒤 기다리지 말고 429/503으로 거부한다.
- 하나의 사용자가 동일 요청을 중복 제출하지 않도록 idempotency key 또는 run ID를 사용한다.
- `messages` metadata로 main agent와 subagent/node를 필터링한다.
- token 하나마다 무거운 logging, DB write, JSON model validation을 반복하지 않는다.
- UI가 허용하면 10~30ms 또는 소량 byte 단위로 token을 coalesce하는 방식을 부하 시험한다. TTFT는 유지하면서 event 수와 syscall/serialization 비용을 줄일 수 있다.

## 10. 피해야 할 구현

### 무제한 per-connection queue

```python
queue = asyncio.Queue()  # maxsize 없음
```

client가 느릴 때 run마다 memory가 제한 없이 증가한다. LangGraph에도 이미 unbounded queue가 있으므로 같은 위험을 한 층 더 만든다.

### 모든 event를 Redis Pub/Sub으로 보내면 replay도 된다는 가정

Pub/Sub은 subscriber가 끊겨 있던 event를 저장하지 않는다. reconnect 보장은 snapshot 재동기화 또는 Streams 같은 log가 필요하다.

### heartbeat 없이 LB timeout만 크게 조정

중간 CDN/proxy와 client network 장비의 timeout이 다를 수 있다. 작은 comment heartbeat와 timeout 정렬이 함께 필요하다.

### disconnect면 언제나 run cancel

짧은 채팅에는 합리적이지만 long-running research에는 사용자 결과를 잃고 model 비용만 낭비할 수 있다. endpoint 또는 run policy로 `cancel_on_disconnect`와 `continue_on_disconnect`를 구분한다.

### checkpoint를 token event log로 사용

checkpoint는 graph state 복구용이고 SSE cursor replay log와 access pattern이 다르다. 책임을 분리한다.

## 11. 성능과 안정성 검증 계획

평균 latency만 재면 느린 client와 장애 상황을 놓친다. 다음 시나리오를 구분한다.

| 시나리오 | 확인할 내용 |
| --- | --- |
| 정상 client 1개 | TTFT, token inter-arrival, serialization CPU |
| 정상 client N개 | connection memory, event-loop lag, run throughput |
| 매우 느린 reader | queue/memory 증가, send timeout, run cancel |
| 읽기를 완전히 멈춘 client | half-open 정리 시간, file descriptor 회수 |
| client 중도 disconnect | provider call/tool/subagent cancellation 전파 |
| proxy buffering on/off | browser에서 실제 token 도착 간격 |
| heartbeat 없는 긴 tool | Nginx/ALB timeout 여부 |
| pod restart | run 상태, reconnect, 중복/누락 event |
| Redis 장애 | live stream degradation과 final state 보존 |
| provider rate limit | admission/retry가 연결 수를 폭증시키는지 |

필수 지표:

- active SSE connections
- active/pending Agent runs
- time to first event / first token
- stream duration
- events와 bytes per run
- ASGI send latency p50/p95/p99
- disconnect reason, send timeout, cancellation count
- process RSS와 event-loop lag
- app channel depth를 둘 경우 current/max depth와 overflow count
- Redis Pub/Sub subscriber 및 Streams lag를 둘 경우 해당 lag
- final run 성공률과 client delivery 성공률을 별도 집계

## 12. 결정 기준

현 시점의 권장 결정은 다음과 같다.

| 질문 | 초기 선택 | 전환 신호 |
| --- | --- | --- |
| HTTP와 run 결합 | 결합 | disconnect 후 계속 실행 필요 |
| app queue | 직접 iterator 소비 | producer 분리 요구가 명확해짐 |
| queue 크기 | 추가한다면 bounded | 무제한은 금지 |
| live broker | 없음 | API/worker process 분리 |
| Redis 방식 | live only면 Pub/Sub | event replay가 필요하면 Streams |
| replay | final snapshot 재조회 | token/progress 연속성이 제품 요구 |
| stream modes | 필요한 `messages/updates/custom`만 | 진단 시 제한적으로 추가 |
| slow client | send timeout 후 종료 | resumable stream으로 전환 |

## 13. 남은 질문과 불확실성

다음 내용은 문서만으로 정할 수 없고 실제 서비스 요구 또는 부하 시험이 필요하다.

1. 평균·p95 run 시간과 output token 수는 얼마인가?
2. client disconnect 시 run을 중단해야 하는가, 계속해야 하는가?
3. 동시 연결 수와 동시 Agent run 수 중 어느 쪽이 먼저 병목인가?
4. 인증이 cookie인지 bearer token인지, native EventSource를 사용할 수 있는가?
5. 배포 환경이 Nginx, ALB, API Gateway, Cloudflare 중 무엇인가?
6. subagent와 tool progress를 어느 수준까지 사용자에게 공개할 것인가?
7. 재접속 시 token 단위 replay가 필요한가, 누적 answer snapshot이면 충분한가?
8. 사용 중인 model provider의 cancellation이 실제 inference 비용 중단으로 이어지는가?

## 14. 근거의 신뢰도

| 주장 | 근거 | 신뢰도 |
| --- | --- | --- |
| Deep Agents의 runtime streaming은 LangGraph가 담당 | 공식 architecture/source | 강함 |
| LangGraph in-process stream queue가 unbounded이고 `put_nowait()` 사용 | 2026-09-18 공식 source 직접 확인 | 강함 |
| Uvicorn `send()`에 write flow control 존재 | 공식 Uvicorn 문서 | 강함 |
| SSE reconnect, `Last-Event-ID`, HTTP/1.1 연결 제한 | MDN와 web platform 동작 | 강함 |
| Nginx buffering/read timeout 동작 | 공식 Nginx 문서 | 강함 |
| ALB default idle timeout과 HTTP/2 PING 제약 | 공식 AWS 문서 | 강함 |
| API server/worker/Redis 분리 운영 패턴 | LangSmith 공식 data plane 문서 | 강함 |
| Redis Streams가 replay log에 적합 | 공식 Redis 문서 | 강함 |
| 10~30ms token coalescing이 유리 | 일반적인 최적화 가설, 우리 workload 실측 전 | 중간 |
| 특정 queue size, timeout, connection lifetime | workload와 infra에 종속 | 아직 미정 |

## 다음 단계

1. 실제 서비스의 Agent 호출 코드, 배포 경로, client 요구사항을 이 문서의 남은 질문에 매핑한다.
2. 먼저 연결 결합형의 최소 production implementation과 계약 test를 작성한다.
3. slow-reader/disconnect/proxy buffering을 포함한 load harness를 만든다.
4. 측정 결과로 bounded channel, token coalescing, background run 분리를 결정한다.
5. 구현과 실험 결과가 확정되면 완성 노트를 `AI/agent/text/`로 이관하고 `.codex/MAP.md`에 등록한다.
