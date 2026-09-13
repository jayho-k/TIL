# DeepAgent File Translation HITL PoC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit에서 TXT를 업로드하고 FastAPI SSE를 통해 DeepAgent 실행을 관찰한 뒤, RedisSaver에 중단된 HITL을 사용자 선택으로 재개하여 결과 TXT를 다운로드하는 PoC를 만든다.

**Architecture:** Document DeepAgent는 `CompiledSubAgent` 형태로 등록된 File Translation DeepAgent에 작업을 위임한다. 여기서 `CompiledSubAgent`는 수동 StateGraph가 아니라 `create_deep_agent()`로 만든 중첩 DeepAgent를 상위 Agent에 등록하기 위한 어댑터다. File Translation Agent의 `before_model` Middleware가 Validation SubAgent의 구조화 결과를 감지해 자동 interrupt한다.

**Tech Stack:** Python 3.11+, Deep Agents 0.7.13, LangChain OpenAI, LangGraph, langgraph-checkpoint-redis 0.5.2, FastAPI, sse-starlette, Streamlit, Redis Stack, Pydantic v2, HTTPX, pytest.

**설계 문서:** `AI/agent_hitl/docs/specs/2026-09-13-deepagent-hitl-poc-design.md`

**Git:** 저장소 `AGENTS.md`가 명시적 요청 없는 Git 변경을 금지하므로 commit 단계는 포함하지 않는다.

---

## 1. 생성할 파일 구조

```text
AI/agent_hitl/
├─ README.md                         # 실행법과 검증 시나리오
├─ pyproject.toml                    # 애플리케이션과 테스트 의존성
├─ .env.example                     # Ollama 및 Redis 설정 예시
├─ .gitignore                       # .env, cache, 실행 파일 제외
├─ docker-compose.yml               # Redis Stack 한 개
├─ app/
│  ├─ __init__.py
│  ├─ config.py                     # 환경변수 설정
│  ├─ domain/
│  │  ├─ __init__.py
│  │  ├─ models.py                  # segment, validation, review, run 모델
│  │  └─ review.py                  # review decision 검증과 최종 번역 결정
│  ├─ storage/
│  │  ├─ __init__.py
│  │  └─ files.py                   # TXT 저장·분할·재조립
│  ├─ runs/
│  │  ├─ __init__.py
│  │  └─ repository.py              # Redis run metadata와 멱등 상태
│  ├─ agents/
│  │  ├─ __init__.py
│  │  ├─ model.py                   # ChatOpenAI 생성
│  │  ├─ schemas.py                 # Agent structured output 모델
│  │  ├─ tools.py                   # Replace Tool과 호출 계측
│  │  ├─ middleware.py              # before_model review gate
│  │  ├─ subagents.py               # 네 역할과 File Translation DeepAgent
│  │  └─ document.py                # 최상위 Document DeepAgent
│  ├─ service/
│  │  ├─ __init__.py
│  │  └─ runner.py                  # start/resume와 stream event 변환
│  └─ api/
│     ├─ __init__.py
│     ├─ schemas.py                 # HTTP 요청·상태 응답
│     ├─ sse.py                     # SSE 직렬화
│     ├─ routes.py                  # 네 Endpoint
│     └─ main.py                    # lifespan과 의존성 조립
├─ streamlit_app/
│  ├─ __init__.py
│  ├─ client.py                     # FastAPI와 SSE 통신
│  └─ main.py                       # 업로드·비교·수정·다운로드 UI
├─ tests/
│  ├─ conftest.py
│  ├─ unit/
│  │  ├─ test_review.py
│  │  ├─ test_files.py
│  │  ├─ test_middleware.py
│  │  └─ test_sse.py
│  └─ integration/
│     ├─ test_hitl_spike.py
│     └─ test_api_flow.py
└─ data/runs/.gitkeep
```

## 2. Task 1: 프로젝트와 실행 환경 구성

**Files:**

- Create: `AI/agent_hitl/pyproject.toml`
- Create: `AI/agent_hitl/.env.example`
- Create: `AI/agent_hitl/.gitignore`
- Create: `AI/agent_hitl/docker-compose.yml`
- Create: 위 구조의 `__init__.py`
- Create: `AI/agent_hitl/app/config.py`
- Test: `AI/agent_hitl/tests/unit/test_config.py`

- [ ] **Step 1: 설정 로딩 실패 테스트 작성**

`test_config.py`에 Ollama URL, model, Redis URL이 없을 때 설정 오류가 발생하고, 환경변수를 넣으면 값을 보존하는 테스트를 작성한다.

```python
def test_settings_loads_ollama_and_redis(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test/v1")
    monkeypatch.setenv("OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_API_KEY", "ollama")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    settings = Settings(_env_file=None)
    assert settings.ollama_model == "test-model"
    assert settings.redis_url == "redis://localhost:6379"
```

- [ ] **Step 2: 프로젝트 설정 작성**

`pyproject.toml`에 Python `>=3.11,<4.0`, `deepagents==0.7.13`, `langgraph-checkpoint-redis==0.5.2`, `langchain-openai`, `fastapi`, `uvicorn`, `sse-starlette`, `streamlit`, `httpx`, `pydantic-settings`, `python-multipart`, `redis`를 등록한다. dev group에는 `pytest`, `pytest-asyncio`, `ruff`를 등록한다.

- [ ] **Step 3: Redis Stack과 환경 예시 작성**

`docker-compose.yml`은 `redis/redis-stack-server`를 6379 포트로 실행하고 healthcheck에 `redis-cli ping`을 사용한다. `.env.example`에는 승인된 Ollama 값과 `REDIS_URL=redis://localhost:6379`를 기록한다.

- [ ] **Step 4: Settings 구현 후 테스트**

`Settings(BaseSettings)`에 Ollama 설정, Redis URL, data dir, API URL을 정의한다. 실행:

```powershell
uv sync
uv run pytest tests/unit/test_config.py -v
```

Expected: `1 passed`.

## 3. Task 2: TXT와 Review 도메인 구현

**Files:**

- Create: `AI/agent_hitl/app/domain/models.py`
- Create: `AI/agent_hitl/app/domain/review.py`
- Create: `AI/agent_hitl/app/storage/files.py`
- Test: `AI/agent_hitl/tests/unit/test_review.py`
- Test: `AI/agent_hitl/tests/unit/test_files.py`

- [ ] **Step 1: Review 선택 테스트 작성**

세 segment에 각각 `first`, `validated`, `custom`을 적용했을 때 정확한 최종 문자열이 나오는 테스트와 다음 오류 테스트를 작성한다.

- 존재하지 않는 `segment_id`
- 중복 `segment_id`
- custom text 누락
- revision 불일치
- 결정 개수 부족

- [ ] **Step 2: Pydantic 모델 작성**

`Segment`, `ValidationSegment`, `ValidationResult`, `ReviewRequest`, `SegmentDecision`, `ReviewDecision`, `RunStatus`, `RunRecord`를 정의한다. `selected`는 `Literal["first", "validated", "custom"]`로 제한한다.

- [ ] **Step 3: 결정 정규화 구현**

```python
def resolve_review(
    request: ReviewRequest,
    decision: ReviewDecision,
) -> list[FinalTranslation]:
    ...
```

입력 검증 후 원래 순서를 보존하여 최종 번역 목록을 반환한다.

- [ ] **Step 4: TXT round-trip 테스트와 구현**

빈 줄이 아닌 문단을 segment로 만들되 원래 빈 줄 위치를 보존하는 `parse_txt()`와 `render_txt()`를 작성한다. UTF-8 이외 입력에는 `InvalidTextEncoding`을 발생시킨다.

- [ ] **Step 5: 단위 테스트 실행**

```powershell
uv run pytest tests/unit/test_review.py tests/unit/test_files.py -v
```

Expected: 모든 선택 및 round-trip 테스트 PASS.

## 4. Task 3: Run metadata와 파일 저장 구현

**Files:**

- Create: `AI/agent_hitl/app/runs/repository.py`
- Extend: `AI/agent_hitl/app/storage/files.py`
- Test: `AI/agent_hitl/tests/unit/test_run_repository.py`

- [ ] **Step 1: 상태 전이와 중복 Resume 테스트 작성**

허용 전이는 `CREATED → RUNNING → WAITING_FOR_REVIEW → RESUMING → COMPLETED|FAILED`로 제한한다. 동일 `review_request_id/revision`의 동일 결정은 기존 결과를 반환하고, 다른 결정은 `ReviewConflict`를 발생시키는 테스트를 작성한다.

- [ ] **Step 2: RedisRunRepository 구현**

checkpoint key와 겹치지 않도록 `agent-hitl:run:{run_id}` namespace를 사용한다. Hash에 `thread_id`, status, input/output path, review JSON, decision hash를 저장한다. 상태 갱신은 Redis transaction으로 compare-and-set한다.

- [ ] **Step 3: LocalRunFileStore 구현**

`data/runs/{run_id}/input.txt`, `output.txt`만 허용한다. 사용자 파일명을 경로로 사용하지 않는다. output write는 임시 파일 후 같은 디렉터리에서 atomic replace한다.

- [ ] **Step 4: Redis 단위 테스트 실행**

```powershell
docker compose up -d redis
uv run pytest tests/unit/test_run_repository.py -v
```

Expected: 상태 전이와 중복 결정 테스트 PASS.

## 5. Task 4: `before_model` HITL Spike

**Files:**

- Create: `AI/agent_hitl/app/agents/schemas.py`
- Create: `AI/agent_hitl/app/agents/middleware.py`
- Create: `AI/agent_hitl/app/agents/model.py`
- Create: `AI/agent_hitl/app/agents/subagents.py`
- Create: `AI/agent_hitl/tests/integration/test_hitl_spike.py`

- [ ] **Step 1: Middleware 순수 판별 테스트 작성**

`find_validation_result(messages)`가 `task` Tool Call의 target이 `file-validation`이고 같은 `tool_call_id`의 ToolMessage가 `ValidationResult` schema를 만족할 때만 결과를 반환하도록 테스트한다. Analyzer, 일반 ToolMessage, 잘못된 JSON에는 `None`을 반환해야 한다.

- [ ] **Step 2: Ollama model factory 구현**

승인된 `ChatOpenAI` 설정을 사용하되 `reasoning_effort`를 boolean setting으로 켜고 끌 수 있게 한다. Endpoint가 인자를 거부하면 설정을 끈 상태로 재실행할 수 있어야 하며 런타임 자동 fallback은 두지 않는다.

- [ ] **Step 3: 네 역할의 단순 SubAgent 정의**

각 SubAgent는 명확한 JSON만 반환하도록 system prompt와 Pydantic response format을 사용한다. Analyzer는 TXT, Extractor는 segment, Translator는 한국어 1차 번역, Validation은 두 후보와 note를 반환한다.

- [ ] **Step 4: File Translation DeepAgent 구성**

`create_deep_agent()`로 File Translation Agent를 만들고 네 SubAgent와 `TranslationReviewGateMiddleware`를 등록한다. 이것은 수동 StateGraph가 아니다. 생성된 runnable은 이후 Document Agent에 `CompiledSubAgent`로 등록한다.

- [ ] **Step 5: Middleware 구현**

`before_model`에서 이미 completed인 revision은 통과시키고, 새 Validation 결과에는 결정적인 ID `review:{validation_run_id}`를 사용해 `interrupt(request.model_dump())`한다. Resume 값은 `ReviewDecision`으로 검증한 뒤 final translations와 completed status를 state에 반환한다.

- [ ] **Step 6: 중단·재개 통합 테스트 작성**

테스트는 RedisSaver를 사용해 첫 실행이 interrupt를 반환하고, 같은 `thread_id`의 `Command(resume=...)`이 완료되며 Validation 호출 counter가 1인지 검사한다. 별도 테스트 프로세스에서 checkpoint를 만든 뒤 새 Agent instance로 resume하는 케이스도 작성한다.

- [ ] **Step 7: Spike 실행과 판정**

```powershell
uv run pytest tests/integration/test_hitl_spike.py -v -s
```

통과 기준:

- 최상위 결과에서 review interrupt 확인
- Resume decision이 middleware state에 반영
- Validation counter `1`
- 새 Agent instance에서 같은 thread resume 성공

실패하면 본 구현을 계속 확장하지 않고 trace를 설계 문서에 기록하여 Middleware와 Wrapper 결정을 다시 검토한다.

## 6. Task 5: Replace Tool과 Document DeepAgent 완성

**Files:**

- Create: `AI/agent_hitl/app/agents/tools.py`
- Create: `AI/agent_hitl/app/agents/document.py`
- Test: `AI/agent_hitl/tests/unit/test_replace_tool.py`

- [ ] **Step 1: 검수 우회 실패 테스트 작성**

review status가 completed가 아니거나 revision이 다르면 파일이 생성되지 않는지 검사한다. 동일 run/revision으로 두 번 호출하면 같은 output path를 반환하고 write counter가 1인지 검사한다.

- [ ] **Step 2: Replace Tool 구현**

LLM이 번역 본문을 다시 전달하지 않게 한다. Tool 입력은 `run_id`, `review_request_id`, `revision`이고, 실제 final translations는 runtime state에서 읽는다. `LocalRunFileStore`로 output을 atomic write한다.

- [ ] **Step 3: Document DeepAgent 구성**

File Translation DeepAgent runnable을 `CompiledSubAgent`로 등록한다. Document system prompt는 TXT 번역 요청을 해당 SubAgent에 한 번 위임하고 interrupt를 가공하지 않도록 제한한다.

- [ ] **Step 4: 테스트 실행**

```powershell
uv run pytest tests/unit/test_replace_tool.py tests/integration/test_hitl_spike.py -v
```

Expected: 우회 차단, 멱등 write, 중첩 interrupt PASS.

## 7. Task 6: Runner와 SSE 변환 구현

**Files:**

- Create: `AI/agent_hitl/app/service/runner.py`
- Create: `AI/agent_hitl/app/api/sse.py`
- Test: `AI/agent_hitl/tests/unit/test_sse.py`
- Test: `AI/agent_hitl/tests/unit/test_runner.py`

- [ ] **Step 1: SSE 직렬화 테스트 작성**

`progress`, `hitl.required`, `completed`, `failed`가 `event`, JSON `data`를 가진 SSE dict로 변환되는지 검사한다. 내부 LangGraph 객체와 `thread_id`는 노출하지 않는다.

- [ ] **Step 2: AgentRunner start 구현**

run을 `RUNNING`으로 바꾸고 `agent.astream(..., version="v2")`을 순회한다. interrupt를 만나면 review request를 repository에 기록하고 `hitl.required`를 yield한 뒤 종료한다.

- [ ] **Step 3: AgentRunner resume 구현**

repository가 decision을 원자적으로 수락한 뒤 같은 thread ID로 `Command(resume=decision.model_dump())`을 stream한다. completed에는 output path 존재를 검사하고 URL만 반환한다.

- [ ] **Step 4: Runner 테스트 실행**

가짜 graph stream을 주입하여 내부 이벤트 필터링, interrupt 종료, completed 조건, model error 변환을 테스트한다.

## 8. Task 7: FastAPI Endpoint 구현

**Files:**

- Create: `AI/agent_hitl/app/api/schemas.py`
- Create: `AI/agent_hitl/app/api/routes.py`
- Create: `AI/agent_hitl/app/api/main.py`
- Create: `AI/agent_hitl/tests/integration/test_api_flow.py`

- [ ] **Step 1: API 실패 테스트 작성**

UTF-8이 아닌 파일, `.txt`가 아닌 파일, 없는 run, waiting이 아닌 resume, 오래된 revision, 미완료 download가 각각 400/404/409를 반환하는지 작성한다.

- [ ] **Step 2: Lifespan 구성**

Redis client와 AsyncRedisSaver를 한 번 생성하고 `asetup()`을 실행한다. repository, file store, DeepAgent, runner를 조립하고 종료 시 연결을 닫는다.

- [ ] **Step 3: 네 Endpoint 구현**

`POST /runs`, `POST /runs/{run_id}/resume`, `GET /runs/{run_id}`, `GET /runs/{run_id}/download`를 설계 문서 계약대로 구현한다. SSE에는 `EventSourceResponse`를 사용한다.

- [ ] **Step 4: API 통합 테스트 실행**

LLM과 AgentRunner를 fake로 교체해 업로드 → interrupt → 상태 조회 → resume → download 전체 HTTP 계약을 검증한다.

```powershell
uv run pytest tests/integration/test_api_flow.py -v
```

Expected: 전체 API 계약 PASS.

## 9. Task 8: Streamlit UI 구현

**Files:**

- Create: `AI/agent_hitl/streamlit_app/client.py`
- Create: `AI/agent_hitl/streamlit_app/main.py`
- Test: `AI/agent_hitl/tests/unit/test_streamlit_client.py`

- [ ] **Step 1: SSE client parser 테스트 작성**

분할된 HTTP chunk, 여러 data line, 빈 줄 경계가 있어도 event와 JSON payload를 정확히 복원하는지 검사한다.

- [ ] **Step 2: FastAPIClient 구현**

HTTPX sync streaming으로 start/resume SSE를 iterator로 노출하고 get status/download를 제공한다. Streamlit 코드는 HTTP 세부 형식을 직접 다루지 않는다.

- [ ] **Step 3: Streamlit session state 설계**

`run_id`, `run_status`, `review_request`, `decisions`, `download_url`, `events`만 저장한다. `thread_id`와 파일 시스템 경로는 저장하지 않는다.

- [ ] **Step 4: 검수 화면 구현**

각 segment에 원문, 1차 번역, 검증 번역, validation note를 표시한다. radio로 first/validated/custom을 선택하고 custom일 때 text area를 활성화한다. 모든 항목이 유효할 때만 “검수 완료 및 재개” 버튼을 활성화한다.

- [ ] **Step 5: 새로고침 복구 구현**

run ID가 있지만 review request가 없으면 상태 API를 호출해 waiting review 또는 download 상태를 복원한다.

- [ ] **Step 6: client 테스트 실행**

```powershell
uv run pytest tests/unit/test_streamlit_client.py -v
```

Expected: SSE parsing과 HTTP 오류 변환 PASS.

## 10. Task 9: 실제 Ollama End-to-End와 재시작 검증

**Files:**

- Create: `AI/agent_hitl/tests/integration/test_live_ollama.py`
- Create: `AI/agent_hitl/README.md`
- Modify: `AI/agent_hitl/.gitignore`

- [ ] **Step 1: live test marker 추가**

`RUN_LIVE_OLLAMA=1`일 때만 실행하는 pytest marker를 만든다. 짧은 두 문단 TXT를 업로드하고 interrupt payload schema까지만 자동 검사한다.

- [ ] **Step 2: 수동 E2E 실행**

터미널 1:

```powershell
docker compose up -d redis
uv run uvicorn app.api.main:app --reload --port 8000
```

터미널 2:

```powershell
uv run streamlit run streamlit_app/main.py --server.port 8501
```

TXT를 업로드하고 두 후보가 표시되는지 확인한다. FastAPI를 종료 후 다시 시작하고 custom 번역으로 resume하여 output을 다운로드한다.

- [ ] **Step 3: 계측 결과 확인**

run 상태에서 `validation_call_count == 1`, `replace_call_count == 1`을 확인한다. 다운로드한 TXT가 custom 입력을 포함하는지 확인한다.

- [ ] **Step 4: 전체 자동 테스트 실행**

```powershell
uv run ruff check .
uv run pytest -m "not live" -v
```

Expected: lint 오류 0, non-live tests 전체 PASS.

- [ ] **Step 5: README 작성**

환경 설정, Redis/FastAPI/Streamlit 실행 명령, PoC 성공 시나리오, 알려진 제한, live test 실행법을 기록한다. 실제 `.env`, `data/runs/*`, Python cache를 `.gitignore`에 포함한다.

## 11. 완료 판정

다음 조건을 모두 만족해야 구현 완료로 판정한다.

- Streamlit에서 UTF-8 TXT 업로드 가능
- Document DeepAgent가 File Translation DeepAgent에 위임
- 네 역할의 SubAgent 호출 trace 확인
- Validation 완료 후 LLM의 별도 검수 Tool Call 없이 interrupt
- 첫 SSE에서 `hitl.required` 수신 후 정상 종료
- FastAPI 재시작 뒤 같은 run resume 성공
- first, validated, custom 결정 모두 결과에 반영
- Validation 호출 1회, Replace 호출 1회
- 결과 TXT 다운로드 가능
- non-live test와 lint 전체 통과

## 12. 구현 중 의사결정 규칙

- `before_model` Middleware Spike가 실패하면 우회 구현을 즉시 추가하지 않고 실행 trace와 실패 이유를 먼저 기록한다.
- DeepAgent 최신 patch에서 API가 문서와 다르면 설치된 타입과 공식 reference를 기준으로 계획 문서의 시그니처를 갱신한다.
- Ollama 모델이 중첩 Tool Call을 안정적으로 생성하지 못하면 SubAgent 수를 줄이지 않고 prompt와 structured output부터 조정한다.
- 큰 번역 payload로 checkpoint가 비대해지는 문제는 TXT PoC 측정값을 기록하되 첫 범위에서 외부 object storage를 추가하지 않는다.
