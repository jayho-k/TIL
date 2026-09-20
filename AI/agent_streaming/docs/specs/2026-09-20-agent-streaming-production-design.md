# DeepAgent 운영형 스트리밍 비교 설계

> 2026-09-21 수정: 아래는 최초 비교 설계의 기록이다. 현재 운영 경로는 모두
> EventSourceResponse로 통일했다. 초기화를 HTTP 응답 전에 수행하고, 최종 DB 저장 후
> 완료 이벤트를 전송한다. source 전용 task와 크기 1 queue로 lifecycle을 관리한다.
> 현재 계약·제약은 `../../README.md`와 `../reports/load-test-report.md`를 따른다.

> 작성일: 2026-09-20  
> 대상: DeepAgent/LangGraph `astream()`을 FastAPI SSE로 제공하는 운영 코드  
> 비교 대상: Starlette `StreamingResponse`, `sse-starlette` `EventSourceResponse`

## 1. 목표

일반 멀티턴 채팅을 동일한 실행 조건에서 두 가지 Response로 제공한다. Agent 실행, Redis checkpoint, PostgreSQL 로그, 외부 이벤트 계약은 공유하고 HTTP 전송 adapter만 교체한다. 이 구조로 구현 중복을 막고 두 Response의 정확성, 안정성, 지연, CPU 및 메모리 차이를 비교한다.

운영 부하의 초기 검증 기준은 다음과 같다.

- DAU 약 7,000명
- 집중 시간대 08:00~17:00
- 현재 테스트 환경의 열린 SSE 연결 30개
- 현재 테스트 환경의 동시 Agent 실행 10개
- 현재 테스트 환경의 신규 요청 1 RPS
- 일반 실행시간 2분, 최대 실행시간 10분

실제 운영 장비와 현재 PC/GPU가 다르므로 운영 가정(300 connections, 100 Agent runs,
10 RPS)의 1/10을 현재 환경의 검증 목표로 사용한다. 이 결과는 구조적 안정성을 확인하는
자료이며 운영 장비의 절대 용량으로 외삽하지 않는다.

## 2. 확정 범위

구현한다.

- `POST /v1/chat/streaming-response`
- `POST /v1/chat/event-source-response`
- 공통 DeepAgent/LangGraph `astream()` 실행 파이프라인
- Redis `AsyncRedisSaver` 기반 `thread_id` 멀티턴
- PostgreSQL run 및 완성 메시지 로그
- 공통 외부 event contract
- heartbeat, token batching, timeout, disconnect cancellation
- connection 수와 Agent 실행 수의 독립 제한
- 단위, 통합, live Ollama, 장애 및 부하 테스트
- readiness, liveness, metrics

구현하지 않고 후속 과제로 기록한다.

- 동일 `thread_id` 요청의 queue, branch, 이전 실행 선점
- SSE event replay와 `Last-Event-ID`
- run과 HTTP transport를 분리하는 background worker
- 인증·인가 시스템 자체
- Kubernetes, Nginx 배포 manifest
- PostgreSQL 및 Redis Docker Compose

## 3. 핵심 원칙

1. 두 endpoint의 차이는 Response adapter뿐이어야 한다.
2. LangGraph 내부 event를 그대로 외부에 노출하지 않는다.
3. Redis checkpoint는 멀티턴 state용이며 SSE replay log가 아니다.
4. PostgreSQL은 운영 로그용이며 network stream 동안 connection을 점유하지 않는다.
5. disconnect는 Agent 및 upstream LLM을 취소한다.
6. async generator 내부에서 blocking I/O를 수행하지 않는다.
7. connection 수, Agent run 수, model request 수를 서로 다른 자원으로 관측한다.

## 4. 아키텍처

```text
POST /v1/chat/{transport}
  -> request validation
  -> connection admission
  -> Agent concurrency permit
  -> PostgreSQL: RUNNING run + user message (짧은 transaction)
  -> DeepAgent / LangGraph astream(version="v2")
  -> StreamEventProjector
  -> TokenBatcher + response accumulator
  -> ResponseAdapter
       |- StreamingResponseAdapter
       `- EventSourceResponseAdapter
  -> client

정상 완료
  -> PostgreSQL: assistant message + COMPLETED

오류/timeout
  -> PostgreSQL: FAILED

client disconnect
  -> Agent/LLM cancel
  -> PostgreSQL RUNNING row는 그대로 유지
```

### 4.1 SOLID 경계

| 구성요소 | 단일 책임 |
| --- | --- |
| `ChatStreamService` | 한 chat run의 orchestration |
| `AgentEventSource` | DeepAgent/LangGraph 실행 추상화 |
| `StreamEventProjector` | 내부 LangGraph event를 공개 event로 변환 |
| `TokenBatcher` | 작은 token을 제한된 시간·크기로 병합 |
| `RunRepository` | PostgreSQL 로그 계약 |
| `CheckpointProvider` | Redis checkpointer lifecycle |
| `ConnectionLimiter` | 열린 SSE connection 제한 |
| `AgentRunLimiter` | 실제 Agent 실행 제한 |
| `ResponseAdapter` | domain event를 HTTP/SSE로 표현 |
| `MetricsRecorder` | transport 독립 관측값 기록 |

FastAPI route는 request 검증과 adapter 선택만 담당한다. 상위 계층은 구체적인 SQLAlchemy session, Redis client, Response class에 직접 의존하지 않는다. 각 계약에는 fake 구현을 주입할 수 있어 외부 인프라 없이 단위 테스트할 수 있다.

## 5. 모델과 Agent

기존 `AI/agent_hitl`의 설정 방식을 따른다.

- `ChatOpenAI`로 OpenAI 호환 Ollama endpoint 사용
- `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_API_KEY`
- `OLLAMA_REASONING_EFFORT_ENABLED`
- Deep Agents `0.7.13` 기준
- 실제 모델 호출은 opt-in live test로 분리
- 자동 테스트는 결정적인 fake streaming model 또는 fake `AgentEventSource` 사용

런타임은 운영 재현성을 위해 CPython 3.12 계열로 고정한다. Agent는 `create_deep_agent()`로 생성한다. 사용자 stream에는 `astream(stream_mode=["messages", "updates", "custom"], version="v2")`에서 허용한 event만 투영한다. `values`, `debug`, `checkpoints`, prompt, 내부 state 및 tool 원문 결과는 노출하지 않는다.

## 6. 외부 event contract

공통 envelope:

```json
{
  "schema_version": "1",
  "event_id": "<run_id>:<sequence>",
  "run_id": "uuid",
  "thread_id": "client-provided-id",
  "sequence": 12,
  "timestamp": "UTC ISO-8601",
  "data": {}
}
```

공개 event:

| 이름 | 의미 |
| --- | --- |
| `stream.started` | run, thread, transport 정보 |
| `message.delta` | batching된 assistant text |
| `tool.started` | 공개가 허용된 tool 시작 |
| `tool.completed` | 공개가 허용된 tool 완료 요약 |
| `stream.completed` | 정상 완료, 사용량, 소요시간 |
| `stream.error` | stream 시작 후 정규화된 오류 |

Heartbeat는 application event가 아니라 SSE comment `: ping`으로 보낸다. 두 adapter는 event 이름과 JSON payload를 동일하게 유지한다.

## 7. Response adapter

### 7.1 `StreamingResponseAdapter`

다음을 애플리케이션 코드가 직접 책임진다.

- UTF-8 SSE framing
- `event`, `id`, 여러 줄 `data` 처리
- event 이름과 ID의 CR/LF 제거
- heartbeat와 Agent event multiplexing
- 개별 send deadline을 적용할 수 있는 ASGI send wrapper
- disconnect 및 generator cancellation 정리
- 종료 delimiter와 header

이 구현은 단순 `yield f"data: ...\\n\\n"` 예제가 아니라 `EventSourceResponse`와 같은 운영 조건을 만족해야 한다.

### 7.2 `EventSourceResponseAdapter`

구조화된 `ServerSentEvent` 또는 `JSONServerSentEvent`를 생성하고 다음 기능을 사용한다.

- `ping=15`
- `send_timeout=30`
- disconnect listener
- server shutdown coordination
- SSE 전용 header 및 framing

두 구현 모두 `Cache-Control: no-store`, `X-Accel-Buffering: no`, `Content-Type: text/event-stream`을 동일하게 적용한다. SSE compression은 사용하지 않는다.

## 8. lifecycle과 오류 정책

| 항목 | 정책 |
| --- | --- |
| heartbeat | 15초 |
| 전체 Agent timeout | 10분 |
| 개별 send timeout | 30초 |
| permit 대기 | 최대 5초 |
| token batching | 최대 20ms 또는 설정된 문자 수 |
| connection limit | 현재 환경 process 기준 30, 설정 가능 |
| Agent run limit | 현재 환경 process 기준 10, 설정 가능 |

- permit을 얻지 못하면 stream 시작 전에 `503 Service Unavailable`과 `Retry-After`를 반환한다.
- stream 시작 전 오류는 HTTP status와 JSON body로 응답한다.
- stream 시작 후에는 status를 바꿀 수 없으므로 `stream.error`를 보낸 뒤 종료한다.
- timeout과 애플리케이션 오류는 run을 `FAILED`로 갱신한다.
- disconnect 시 Agent와 upstream LLM을 취소한다. PostgreSQL의 해당 run은 `RUNNING`으로 남겨 로그에서 중단된 요청으로 해석한다.
- `CancelledError`는 resource cleanup 뒤 다시 전파한다.
- application-level queue는 추가하지 않는다. LangGraph 내부 queue가 unbounded일 수 있으므로 느린 client는 send timeout으로 차단하고 payload와 stream mode를 제한한다.

## 9. Redis checkpoint와 멀티턴

- 기본 URL은 `redis://localhost:6379`이다.
- `AsyncRedisSaver.from_conn_string()`을 lifespan에서 한 번 생성한다.
- 시작 시 `asetup()`과 연결 검증을 실행한다.
- request의 `thread_id`를 `configurable.thread_id`로 전달한다.
- 같은 `thread_id`의 다음 turn은 이전 graph state를 이어받는다.
- checkpoint와 서비스용 key namespace를 분리한다.
- checkpoint는 token event log나 replay 보장을 제공하지 않는다.

같은 `thread_id`의 동시 실행은 checkpoint update 순서를 왜곡할 수 있다. 최초 버전은 활성 실행이 있을 때 fail-fast하는 guard를 둘 수 있는 인터페이스 경계만 유지하며, queue/branch/선점 정책은 후속 설계로 남긴다. 이 문제는 본 실험의 Response 비교보다 우선하지 않는다.

## 10. PostgreSQL 로그

PostgreSQL은 애플리케이션 외부에서 실행한다. 접속 정보는 `POSTGRES_DSN`으로 받고, 코드에는 실제 credential을 저장하지 않는다. SQLAlchemy async engine, `asyncpg`, Alembic을 사용한다.

### 10.1 `chat_runs`

- `id`: UUID primary key
- `thread_id`
- `transport`: `streaming_response` 또는 `event_source_response`
- `status`: `RUNNING`, `COMPLETED`, `FAILED`
- `started_at`, `completed_at`
- `latency_ms`
- `model`
- `input_chars`, `output_chars`
- `error_code`, `error_message`

### 10.2 `chat_messages`

- `id`: UUID primary key
- `run_id`: foreign key
- `thread_id`
- `role`: `user`, `assistant`
- `content`
- `created_at`

트랜잭션 경계:

1. stream 전 run과 user message를 insert하고 commit한다.
2. DB session과 connection을 반환한다.
3. Agent stream을 실행한다.
4. 정상 완료 시 새 session으로 assistant message와 완료 상태를 기록한다.
5. 오류 시 새 session으로 실패 상태를 기록한다.

token/chunk 단위 insert와 stream 전체 transaction은 금지한다.

## 11. API

두 endpoint는 같은 request schema를 받는다.

```json
{
  "thread_id": "conversation-uuid",
  "message": "사용자 질문"
}
```

`thread_id`와 message에는 길이 제한을 둔다. 인증·인가 구현은 범위 밖이지만 route/service 경계에는 향후 principal과 tenant limit을 전달할 자리를 둔다. URL query에는 질문이나 bearer token을 넣지 않는다.

운영 endpoint:

- `GET /health/live`: process 생존 확인
- `GET /health/ready`: PostgreSQL, Redis 및 Agent 초기화 확인
- `GET /metrics`: Prometheus format

## 12. 테스트 전략

### 12.1 단위 테스트

- v2 event projection과 metadata filtering
- SSE multiline, UTF-8, 빈 data, CR/LF injection 방어
- 두 adapter의 application event contract 동일성
- token batching의 시간·크기 flush
- assistant 응답 누적
- 오류 정규화
- concurrency limit과 timeout
- disconnect cancellation 및 `CancelledError` 재전파

### 12.2 통합 테스트

- 두 FastAPI endpoint의 실제 streaming
- PostgreSQL run/message 기록
- stream 중 DB pool을 점유하지 않는지 검증
- Redis checkpoint로 2턴 이상의 문맥 유지
- 새 application instance에서 checkpoint 복원
- Redis와 PostgreSQL 장애
- 느린 client, send timeout, 즉시 disconnect
- 같은 입력에서 두 endpoint의 event schema 일치

### 12.3 live test

- 기존 Ollama 환경변수가 있고 opt-in flag가 설정된 경우에만 실행
- 실제 DeepAgent token stream
- 동일 `thread_id`의 멀티턴
- 공개 가능한 tool/custom event

### 12.4 부하 테스트

Locust client가 SSE body를 끝까지 소비하도록 구현한다.

- idle connection
- 빠른 token producer
- 느린 consumer
- 연결 직후 disconnect
- 30 connection 유지
- 10 Agent run 제한
- 1 RPS ramp 및 steady load
- 각 adapter를 같은 fake Agent workload로 독립 실행
- 실제 Ollama는 provider 용량 시험과 transport 시험을 분리해 낮은 동시성으로 실행

## 13. 관측 지표와 합격 기준

기본 지표:

- `active_sse_connections{transport}`
- `active_agent_runs`
- `stream_time_to_first_event_seconds{transport}`
- `stream_duration_seconds{transport,status}`
- `stream_send_seconds{transport}`
- `stream_events_total{transport,event}`
- `stream_bytes_total{transport}`
- `stream_disconnects_total{transport}`
- `stream_errors_total{transport,code}`
- `db_pool_checked_out`, `db_pool_wait_seconds`
- `redis_operation_seconds`
- process RSS와 event-loop lag

초기 합격 조건:

- 단위 및 통합 테스트 전부 통과
- 두 adapter의 application event 순서와 schema가 동일
- disconnect 후 Agent task가 남지 않음
- SSE connection 동안 PostgreSQL connection이 장기 checkout되지 않음
- 30 connection 시나리오에서 process crash, 무제한 memory 증가, event-loop stall이 없음
- 10 Agent 제한이 초과 실행을 허용하지 않음
- 느린 client가 send timeout 뒤 정리됨

구체적인 latency 및 RSS 임계값은 기준 장비에서 baseline을 측정한 뒤 load-test report에 고정한다. 측정 전 임의 수치를 성공 기준으로 만들지 않는다.

## 14. 프로젝트 구조

```text
AI/agent_streaming/
|- pyproject.toml
|- uv.lock
|- .env.example
|- README.md
|- alembic.ini
|- migrations/
|- docs/
|  |- specs/
|  |- plans/
|  `- reports/
|- app/
|  |- config.py
|  |- domain/
|  |- agents/
|  |- streaming/
|  |  `- adapters/
|  |- persistence/
|  |- service/
|  `- api/
|- tests/
|  |- unit/
|  |- integration/
|  `- live/
`- load_tests/
```

## 15. 운영상 알려진 한계

- 직접 POST streaming이므로 disconnect 후 run을 계속 실행하거나 event를 replay하지 않는다.
- process 기준 semaphore는 pod 전체의 글로벌 limit이 아니다. 실제 배포에서는 pod 수와 provider quota를 함께 계산한다.
- Redis checkpoint가 있어도 같은 thread의 동시 turn을 안전하게 merge하지는 않는다.
- PostgreSQL의 오래된 `RUNNING` row는 disconnect 또는 process crash를 의미할 수 있다.
- proxy buffering, idle timeout, file descriptor limit, connection draining은 실제 배포 환경에서 별도로 검증해야 한다.
- `EventSourceResponse`가 기본 선택지에 가깝지만, 어느 adapter가 더 빠르다는 결론은 부하 측정 전 확정하지 않는다.

## 16. 구현 순서

1. 프로젝트 설정, domain model, config
2. PostgreSQL schema와 repository
3. Redis checkpointer와 DeepAgent factory
4. v2 event projector와 token batcher
5. 공통 lifecycle service
6. `StreamingResponseAdapter`
7. `EventSourceResponseAdapter`
8. FastAPI routes와 lifespan
9. metrics와 health endpoint
10. 단위·통합·live test
11. Locust 부하 테스트와 결과 보고서
