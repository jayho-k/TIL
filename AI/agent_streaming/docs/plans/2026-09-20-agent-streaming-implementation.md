# DeepAgent Production Streaming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two production-oriented FastAPI SSE endpoints that share one DeepAgent/LangGraph streaming pipeline, persist multi-turn state in Redis, write run/message logs to PostgreSQL, and can be compared under identical automated and load tests.

**Architecture:** `ChatStreamService` emits transport-neutral `StreamEvent` values from a injected `AgentEventSource`. FastAPI selects either a custom `StreamingResponse` implementation or `EventSourceResponse`; persistence, projection, batching, limits, metrics, and lifecycle policies remain shared. PostgreSQL transactions end before streaming begins, while `AsyncRedisSaver` remains process-scoped and receives `thread_id` on every Agent invocation.

**Tech Stack:** CPython 3.12, Deep Agents 0.7.13, LangGraph v2 streaming, langgraph-checkpoint-redis 0.5.2, FastAPI, Starlette, sse-starlette, SQLAlchemy 2 async, asyncpg, Alembic, Prometheus client, HTTPX, pytest, pytest-asyncio, Locust, uv.

**Source design:** `AI/agent_streaming/docs/specs/2026-09-20-agent-streaming-production-design.md`

**Repository rule:** Do not run `git add`, `git commit`, or any other Git-mutating command unless the user explicitly requests it.

---

## File map

```text
AI/agent_streaming/
├─ pyproject.toml                 dependencies, pytest and Ruff configuration
├─ .env.example                  non-secret configuration contract
├─ alembic.ini                   migration runner configuration
├─ migrations/env.py             async SQLAlchemy metadata binding
├─ migrations/versions/0001_chat_logs.py
├─ app/config.py                 validated runtime settings
├─ app/domain/events.py          transport-neutral event types
├─ app/domain/models.py          run/message domain types and enums
├─ app/agents/model.py           OpenAI-compatible Ollama model factory
├─ app/agents/factory.py         DeepAgent construction
├─ app/agents/source.py          AgentEventSource protocol and LangGraph adapter
├─ app/persistence/database.py   engine/session lifecycle
├─ app/persistence/orm.py        SQLAlchemy tables
├─ app/persistence/repository.py short transaction log repository
├─ app/streaming/projector.py    LangGraph v2 event filtering
├─ app/streaming/batching.py     bounded token batching
├─ app/streaming/framing.py      safe SSE byte encoding
├─ app/streaming/adapters.py     both Response adapters
├─ app/service/limits.py         connection and Agent admission
├─ app/service/chat.py           shared streaming orchestration
├─ app/observability/metrics.py  Prometheus instruments
├─ app/api/schemas.py            request validation
├─ app/api/routes.py             chat, health, metrics routes
├─ app/api/main.py               lifespan and dependency assembly
├─ tests/unit/                   isolated contract tests
├─ tests/integration/            ASGI, Redis and PostgreSQL tests
├─ tests/live/                   opt-in Ollama tests
└─ load_tests/locustfile.py      equivalent transport workloads
```

### Task 1: Bootstrap configuration and domain contracts

**Files:**
- Create: `AI/agent_streaming/pyproject.toml`
- Create: `AI/agent_streaming/.env.example`
- Create: `AI/agent_streaming/app/__init__.py`
- Create: `AI/agent_streaming/app/config.py`
- Create: `AI/agent_streaming/app/domain/__init__.py`
- Create: `AI/agent_streaming/app/domain/events.py`
- Create: `AI/agent_streaming/app/domain/models.py`
- Test: `AI/agent_streaming/tests/unit/test_config.py`
- Test: `AI/agent_streaming/tests/unit/test_events.py`

- [x] **Step 1: Write failing configuration tests**

```python
def test_settings_have_safe_stream_defaults(monkeypatch):
    monkeypatch.setenv("POSTGRES_DSN", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    settings = Settings(_env_file=None)
    assert settings.redis_url == "redis://localhost:6379"
    assert settings.max_sse_connections == 30
    assert settings.max_agent_runs == 10
    assert settings.heartbeat_seconds == 15
    assert settings.send_timeout_seconds == 30
    assert settings.agent_timeout_seconds == 600
```

- [x] **Step 2: Run tests and verify import failure**

Run: `uv run pytest tests/unit/test_config.py -q`  
Expected: FAIL because `app.config` does not exist.

- [x] **Step 3: Implement settings and domain types**

Define `Settings(BaseSettings)` with required `postgres_dsn`, `ollama_base_url`, and `ollama_model`; default Redis and stream limits; positive integer validation; pool settings; request length limits; and opt-in live test flags. Define `Transport`, `RunStatus`, `PublicEventType`, immutable `StreamEvent`, `ChatRun`, and `ChatMessage`. `StreamEvent` must build `event_id` as `<run_id>:<sequence>` and serialize UTC timestamps and `data` through Pydantic JSON mode.

- [x] **Step 4: Test event serialization**

```python
def test_stream_event_has_stable_envelope():
    event = StreamEvent.create(
        event_type=PublicEventType.MESSAGE_DELTA,
        run_id=UUID(int=1), thread_id="thread-1", sequence=2,
        data={"text": "안녕"},
    )
    payload = event.payload()
    assert payload["schema_version"] == "1"
    assert payload["event_id"].endswith(":2")
    assert payload["data"] == {"text": "안녕"}
```

- [x] **Step 5: Run unit tests**

Run: `uv run pytest tests/unit/test_config.py tests/unit/test_events.py -q`  
Expected: PASS.

### Task 2: Add PostgreSQL schema and short-lived repository operations

**Files:**
- Create: `AI/agent_streaming/alembic.ini`
- Create: `AI/agent_streaming/migrations/env.py`
- Create: `AI/agent_streaming/migrations/script.py.mako`
- Create: `AI/agent_streaming/migrations/versions/0001_chat_logs.py`
- Create: `AI/agent_streaming/app/persistence/__init__.py`
- Create: `AI/agent_streaming/app/persistence/database.py`
- Create: `AI/agent_streaming/app/persistence/orm.py`
- Create: `AI/agent_streaming/app/persistence/repository.py`
- Test: `AI/agent_streaming/tests/unit/test_repository.py`
- Test: `AI/agent_streaming/tests/integration/test_postgres_repository.py`

- [x] **Step 1: Write repository contract tests with a fake session factory**

Test that `start_run()` writes one `RUNNING` run and one user message in one context-managed session; `complete_run()` writes the assistant message and completes the run in a new session; `fail_run()` stores a bounded error message; and no method exposes a session to the caller.

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/unit/test_repository.py -q`  
Expected: FAIL because repository types are missing.

- [x] **Step 3: Implement ORM and repository**

Create `ChatRunRow` and `ChatMessageRow` with the columns fixed by the design. Implement a `RunRepository` protocol and `SqlAlchemyRunRepository` whose public methods each use `async with session_factory.begin() as session`. Truncate persisted exception text to the configured maximum. Never retain ORM rows across session boundaries.

- [x] **Step 4: Add migration and real PostgreSQL integration test**

The test is gated by `RUN_POSTGRES_TESTS=1`, applies migration `upgrade head`, inserts/finishes a run, and queries both tables with a fresh session. It must also assert the async pool has no checked-out connection after each repository call.

- [x] **Step 5: Run repository tests**

Run: `uv run pytest tests/unit/test_repository.py -q`  
Expected: PASS.  
Run when PostgreSQL is available: `uv run pytest tests/integration/test_postgres_repository.py -q -s`  
Expected: PASS or SKIP when opt-in is absent.

### Task 3: Build Redis-backed DeepAgent and injectable event source

**Files:**
- Create: `AI/agent_streaming/app/agents/__init__.py`
- Create: `AI/agent_streaming/app/agents/model.py`
- Create: `AI/agent_streaming/app/agents/factory.py`
- Create: `AI/agent_streaming/app/agents/source.py`
- Test: `AI/agent_streaming/tests/unit/test_agent_source.py`
- Test: `AI/agent_streaming/tests/integration/test_redis_multiturn.py`

- [x] **Step 1: Write a fake graph source test**

```python
async def test_source_passes_thread_and_v2_modes(fake_graph):
    source = LangGraphEventSource(fake_graph)
    items = [item async for item in source.stream("hello", "thread-1")]
    assert items == fake_graph.items
    assert fake_graph.config["configurable"]["thread_id"] == "thread-1"
    assert fake_graph.kwargs == {
        "stream_mode": ["messages", "updates", "custom"],
        "version": "v2",
        "subgraphs": True,
    }
```

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/unit/test_agent_source.py -q`  
Expected: FAIL because `LangGraphEventSource` is missing.

- [x] **Step 3: Implement model, DeepAgent and source factories**

Reuse the `agent_hitl` `ChatOpenAI` options, including configurable `reasoning_effort`. Construct one general-chat DeepAgent with `create_deep_agent(model=model, system_prompt=...)` and inject the process-scoped checkpointer. Keep `AgentEventSource` as a protocol so tests never require a real model.

- [x] **Step 4: Add Redis multi-turn integration test**

Gate with `RUN_REDIS_TESTS=1`. Use `AsyncRedisSaver` at `redis://localhost:6379`, a deterministic model, and a unique `thread_id`. Invoke two turns and assert the second invocation receives the first turn in checkpointed state. Use unique IDs rather than clearing shared Redis.

- [x] **Step 5: Run source tests**

Run: `uv run pytest tests/unit/test_agent_source.py -q`  
Expected: PASS.  
Run opt-in: `uv run pytest tests/integration/test_redis_multiturn.py -q -s`  
Expected: PASS or SKIP.

### Task 4: Project LangGraph v2 events into the public contract

**Files:**
- Create: `AI/agent_streaming/app/streaming/__init__.py`
- Create: `AI/agent_streaming/app/streaming/projector.py`
- Test: `AI/agent_streaming/tests/unit/test_projector.py`

- [x] **Step 1: Write table-driven failing tests**

Cover `messages` token chunks, non-assistant messages, model metadata filtering, `updates` tool completion, whitelisted `custom` progress, subgraph namespace, empty chunks, `values`, `debug`, `checkpoints`, and malformed events. Assert forbidden events produce no public output and never expose raw state.

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/unit/test_projector.py -q`  
Expected: FAIL because projector is missing.

- [x] **Step 3: Implement a pure projector**

`StreamEventProjector.project(raw_event, context) -> tuple[ProjectedEvent, ...]` must contain no network or persistence calls. It accepts only v2 envelopes, maps allowed message content to `message.delta`, maps explicit public custom events, and reduces tool events to name/status/summary. Sequence assignment stays in the service, not the projector.

- [x] **Step 4: Run projector tests**

Run: `uv run pytest tests/unit/test_projector.py -q`  
Expected: PASS.

### Task 5: Implement bounded token batching and SSE framing

**Files:**
- Create: `AI/agent_streaming/app/streaming/batching.py`
- Create: `AI/agent_streaming/app/streaming/framing.py`
- Test: `AI/agent_streaming/tests/unit/test_batching.py`
- Test: `AI/agent_streaming/tests/unit/test_framing.py`

- [x] **Step 1: Write failing batching and framing tests**

Assert size flush, 20ms timer flush, final flush, event boundary flush, UTF-8 preservation, multiline JSON data, empty data, `id`/`event` CR-LF stripping, comment framing as `: ping\n\n`, and exactly one blank-line delimiter.

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/unit/test_batching.py tests/unit/test_framing.py -q`  
Expected: FAIL because implementations are missing.

- [x] **Step 3: Implement batching and safe framing**

`TokenBatcher` must hold at most the configured character count and use an injected monotonic clock for deterministic tests. `encode_sse(event)` must JSON-encode with `ensure_ascii=False`, prefix every physical data line with `data:`, sanitize field newlines, and return bytes. `encode_comment("ping")` must return `b": ping\n\n"`.

- [x] **Step 4: Run batching and framing tests**

Run: `uv run pytest tests/unit/test_batching.py tests/unit/test_framing.py -q`  
Expected: PASS.

### Task 6: Implement shared chat lifecycle and limits

**Files:**
- Create: `AI/agent_streaming/app/service/__init__.py`
- Create: `AI/agent_streaming/app/service/limits.py`
- Create: `AI/agent_streaming/app/service/chat.py`
- Test: `AI/agent_streaming/tests/unit/test_limits.py`
- Test: `AI/agent_streaming/tests/unit/test_chat_service.py`

- [x] **Step 1: Write failing service tests**

Test this exact order: acquire Agent permit, `start_run`, emit `stream.started`, consume/project/batch source events, emit `stream.completed`, `complete_run`, release permit. Also assert timeout calls `fail_run`, domain errors emit `stream.error`, disconnect cancellation neither completes nor fails the run, accumulated assistant content excludes tool text, and all permits are released.

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/unit/test_limits.py tests/unit/test_chat_service.py -q`  
Expected: FAIL because service and limiters are missing.

- [x] **Step 3: Implement limiters and service**

Use bounded `asyncio.Semaphore` wrappers with a 5-second acquisition deadline and async context managers. `ChatStreamService.stream(command, transport)` is an async iterator of `StreamEvent`; use `asyncio.timeout(600)`, preserve `CancelledError`, normalize safe error codes, assign monotonic sequence numbers, and call repository methods only outside event production awaits.

- [x] **Step 4: Run service tests**

Run: `uv run pytest tests/unit/test_limits.py tests/unit/test_chat_service.py -q`  
Expected: PASS.

### Task 7: Implement both Response adapters

**Files:**
- Create: `AI/agent_streaming/app/streaming/adapters.py`
- Test: `AI/agent_streaming/tests/unit/test_adapters.py`

- [x] **Step 1: Write failing parity and lifecycle tests**

Feed identical `StreamEvent` lists to each adapter and parse the wire output. Assert equal event name, ID, JSON payload and order. Separately assert 15-second comment heartbeat, headers, terminal body, generator close on disconnect, and 30-second send timeout.

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/unit/test_adapters.py -q`  
Expected: FAIL because adapters are missing.

- [x] **Step 3: Implement `EventSourceResponseAdapter`**

Map `StreamEvent` to `JSONServerSentEvent(data=event.payload(), event=event.event_type, id=event.event_id)`. Return `EventSourceResponse` with `ping`, `send_timeout`, `Cache-Control: no-store`, and `X-Accel-Buffering: no`.

- [x] **Step 4: Implement `StreamingResponseAdapter`**

Subclass `StreamingResponse` only as needed to wrap each ASGI `send()` in `asyncio.timeout(send_timeout)`. Multiplex the service iterator and a heartbeat timer without an unbounded queue, frame values through `encode_sse`, emit comments through `encode_comment`, cancel the pending timer/anext task each iteration, and close the source iterator on cancellation.

- [x] **Step 5: Run adapter tests**

Run: `uv run pytest tests/unit/test_adapters.py -q`  
Expected: PASS.

### Task 8: Assemble FastAPI, health checks and metrics

**Files:**
- Create: `AI/agent_streaming/app/observability/__init__.py`
- Create: `AI/agent_streaming/app/observability/metrics.py`
- Create: `AI/agent_streaming/app/api/__init__.py`
- Create: `AI/agent_streaming/app/api/schemas.py`
- Create: `AI/agent_streaming/app/api/routes.py`
- Create: `AI/agent_streaming/app/api/main.py`
- Test: `AI/agent_streaming/tests/integration/test_api.py`
- Test: `AI/agent_streaming/tests/unit/test_metrics.py`

- [x] **Step 1: Write failing ASGI tests**

Use `httpx.ASGITransport` and injected fake service. Assert both POST routes accept the same schema, reject blank/oversized input with 422, set SSE headers, emit equivalent application events, and return `503` with `Retry-After` before response start when admission fails. Test `/health/live`, dependency-driven `/health/ready`, and Prometheus text from `/metrics`.

- [x] **Step 2: Run and verify failure**

Run: `uv run pytest tests/integration/test_api.py tests/unit/test_metrics.py -q`  
Expected: FAIL because the app is missing.

- [x] **Step 3: Implement metrics and routes**

Create registry-local metrics to avoid duplicate collectors in tests. Instrument active connections/runs, first-event and total duration, send latency, bytes/events, disconnects, errors, DB pool, Redis latency, and event-loop lag. Keep metric labels bounded to transport, event type, status, and error code.

- [x] **Step 4: Implement application lifespan**

Create settings, SQLAlchemy engine/session factory, Redis client, `AsyncRedisSaver`, model, DeepAgent, repositories, service, and adapters once per process. Run Redis ping, checkpointer `asetup()`, and a PostgreSQL `SELECT 1` readiness probe. Close checkpointer, Redis, HTTP/model resources where supported, and database engine in reverse order.

- [x] **Step 5: Run API tests**

Run: `uv run pytest tests/integration/test_api.py tests/unit/test_metrics.py -q`  
Expected: PASS.

### Task 9: Verify real infrastructure, cancellation and recovery

**Files:**
- Create: `AI/agent_streaming/tests/integration/test_infrastructure_failures.py`
- Create: `AI/agent_streaming/tests/integration/test_stream_disconnect.py`
- Create: `AI/agent_streaming/tests/live/test_ollama_chat.py`

- [x] **Step 1: Add opt-in infrastructure tests**

Assert unavailable PostgreSQL prevents readiness and fails before stream start; unavailable Redis prevents readiness; Redis failure during checkpointing becomes `stream.error`; slow consumer exceeds send timeout and closes the source; disconnect cancels the fake Agent; and the PostgreSQL run remains `RUNNING` on disconnect.

- [x] **Step 2: Add restart/multi-turn test**

Create application instance A, execute turn one with a unique `thread_id`, close it, create instance B using the same Redis, execute turn two, and assert prior conversation state is present. Gate real services with `RUN_REDIS_TESTS=1` and `RUN_POSTGRES_TESTS=1`.

- [x] **Step 3: Add Ollama live test**

Gate with `RUN_LIVE_TESTS=1`. Call both transports with different unique thread IDs, assert at least one `message.delta` and one `stream.completed`, then perform a second turn that refers to a fact from turn one.

- [x] **Step 4: Run integration suites**

Run: `uv run pytest tests/integration -q`  
Expected: deterministic tests PASS; external-service tests SKIP unless opted in.  
Run opt-in: `uv run pytest tests/live/test_ollama_chat.py -q -s`  
Expected: PASS with configured Ollama, Redis and PostgreSQL.

### Task 10: Add equivalent Locust workloads and operations documentation

**Files:**
- Create: `AI/agent_streaming/load_tests/clients.py`
- Create: `AI/agent_streaming/load_tests/locustfile.py`
- Create: `AI/agent_streaming/docs/reports/load-test-report.md`
- Create: `AI/agent_streaming/README.md`
- Modify: `C:/Users/jayho/Developer/practice/.codex/MAP.md`

- [x] **Step 1: Implement an SSE-aware Locust client**

Parse lines incrementally, record first event time, event count, bytes, terminal event, malformed event and disconnect. Provide `normal`, `idle`, `slow_consumer`, and `early_disconnect` tasks. Select transport only through `STREAM_TRANSPORT`, keeping message distribution and wait times identical. This test host uses one tenth of the production assumption: 30 users, 10 Agent permits and 1 user spawned per second.

- [x] **Step 2: Document exact load commands**

```powershell
$env:STREAM_TRANSPORT='streaming-response'
uv run locust -f load_tests/locustfile.py --headless -u 30 -r 1 -t 15m --host http://127.0.0.1:8000

$env:STREAM_TRANSPORT='event-source-response'
uv run locust -f load_tests/locustfile.py --headless -u 30 -r 1 -t 15m --host http://127.0.0.1:8000
```

- [x] **Step 3: Write README operations guide**

Document environment variables, migration command, Redis/PostgreSQL prerequisites, Uvicorn command, endpoint request examples, event contract, cancellation semantics, metrics, all test commands, proxy requirements, and known limitations. State explicitly that old `RUNNING` rows can mean disconnect or process crash.

- [x] **Step 4: Register the project in `.codex/MAP.md`**

Add an `AI/agent_streaming/` entry describing the two Response implementations, Redis multi-turn checkpoint, PostgreSQL logs, and load-test report.

- [x] **Step 5: Run static and automated verification**

Run: `uv run ruff check app tests load_tests`  
Expected: PASS.  
Run: `uv run pytest -q`  
Expected: PASS with opt-in suites SKIP.  
Run: `uv run alembic upgrade head`  
Expected: migration completes against configured PostgreSQL.

### Task 11: Execute and report the capacity comparison

**Files:**
- Modify: `AI/agent_streaming/docs/reports/load-test-report.md`

- [x] **Step 1: Establish the fake-Agent baseline**

Run each transport at 3, 10 and 30 concurrent clients with identical duration and event schedule. Record host CPU, process RSS, event-loop lag, time-to-first-event p50/p95/p99, completion p95/p99, send timeout count, disconnect cleanup time and error rate. Treat results as test-host evidence, not production capacity certification.

- [x] **Step 2: Run failure workloads**

Use at least 10% slow consumers and 5% early disconnects. Verify RSS returns toward baseline after clients leave and active connection/run gauges return to zero.

- [x] **Step 3: Run controlled Ollama workload**

Use a concurrency within the configured provider capacity and report it separately from transport capacity. Do not attribute provider queue latency to a Response implementation.

- [x] **Step 4: Record evidence and decision**

Put commands, machine specification, configuration, raw summary, comparison table, observed bottlenecks and production recommendation in the report. Do not declare a winner without measured evidence.
