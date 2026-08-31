# DeepAgent 서비스 스켈레톤 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 확정한 Layered + Agent Orchestration 구조를 FastAPI, Deep Agents, LangGraph로 실행하고 테스트할 수 있는 최소 서비스 프로젝트를 만든다.

**Architecture:** HTTP route는 service 또는 agent registry만 호출하고, Agent tool은 business service를 거쳐 repository port를 사용한다. 외부 저장 기술의 client lifecycle은 `storage/`에 모으고, Agent별 prompt와 skill은 각각 `prompts/<agent>/`, `agents/<agent>/skills/`에서 소유한다.

**Tech Stack:** Python 3.11+, FastAPI 0.141.1, Deep Agents 0.7.11, LangGraph 1.2.11, Pydantic Settings 2.15, pytest, Ruff

---

## 1. 생성 위치와 범위

독립 예제 프로젝트 위치:

```text
.codex/research/DeepAgent/Architecture/code/deepagent-service/
```

이 저장소는 TIL 저장소이므로 운영 설정이나 실제 비밀값을 포함하지 않는다. PostgreSQL, Redis, Qdrant, MinIO 모듈은 typed settings와 client factory까지만 제공하며 실제 연결은 애플리케이션 lifespan에서 선택적으로 구성할 수 있게 한다.

## 2. 파일별 책임

```text
deepagent-service/
  pyproject.toml                 # runtime/dev dependency와 도구 설정
  .env.example                   # 비밀값 없는 설정 계약
  README.md                      # 실행, 계층 규칙, 확장 방법
  app/
    main.py                      # FastAPI composition root
    api/
      dependencies.py            # registry/service dependency provider
      routes/
        health.py                # liveness endpoint
        agents.py                # general Agent 실행 endpoint
        reflection_jobs.py       # Airflow가 호출할 job endpoint
    core/
      config.py                  # 환경 설정
      exceptions.py              # application exception
      logging.py                 # logging 초기화
    agents/
      registry.py                # 이름과 runner 매핑
      common/contracts.py        # AgentRunner protocol
      general/
        agent.py                 # create_deep_agent factory와 adapter
        tools.py                 # service-backed tool factory
        skills/knowledge-search/SKILL.md
      reflection/
        graph.py                 # 결정적인 LangGraph job workflow
        nodes.py                 # reflection 단계
        state.py                 # raw graph state
        skills/daily-reflection/SKILL.md
    prompts/
      registry.py                # prompt path 등록
      assembly.py                # deterministic prompt 조립
      shared/safety.md
      general/system.md
      reflection/system.md
    services/
      knowledge_service.py       # Agent가 사용하는 business use case
      reflection_service.py      # job 생성·조회·실행 orchestration
    repositories/
      document_repository.py     # DocumentRepository port와 memory adapter
      reflection_job_repository.py # job port와 memory adapter
    models/
      document.py
      reflection_job.py
    schemas/
      agent.py
      reflection.py
    storage/
      postgres.py                # SQLAlchemy async engine factory
      redis.py                   # async Redis client factory
      qdrant.py                  # async Qdrant client factory
      minio.py                   # MinIO client factory
    integrations/
      external_api.py            # 외부 HTTP client protocol
      mcp.py                     # MCP configuration value object
    workers/
      reflection.py              # API와 별도 process로 job 실행
  airflow/
    dags/deepagent_reflection.py # Airflow 3.1에서 HTTP API를 호출하는 DAG 예제
  tests/
    architecture/test_import_rules.py
    unit/test_agent_registry.py
    unit/test_prompt_assembly.py
    unit/test_knowledge_service.py
    unit/test_reflection_service.py
    api/test_health.py
    api/test_agents.py
    api/test_reflection_jobs.py
```

## 3. 구현 순서

### Task 1: 프로젝트 계약과 prompt 조립

**Files:**
- Create: `code/deepagent-service/pyproject.toml`
- Create: `code/deepagent-service/app/core/config.py`
- Create: `code/deepagent-service/app/prompts/registry.py`
- Create: `code/deepagent-service/app/prompts/assembly.py`
- Test: `code/deepagent-service/tests/unit/test_prompt_assembly.py`

- [ ] **Step 1: prompt 조립의 실패 테스트 작성**

```python
def test_build_prompt_places_shared_policy_before_agent_prompt(tmp_path):
    registry = PromptRegistry(tmp_path, {"shared.safety": "shared.md", "general.system": "general.md"})
    (tmp_path / "shared.md").write_text("SAFE", encoding="utf-8")
    (tmp_path / "general.md").write_text("GENERAL", encoding="utf-8")
    assert build_system_prompt(registry, "general") == "SAFE\n\nGENERAL"
```

- [ ] **Step 2: `pytest tests/unit/test_prompt_assembly.py -q`를 실행해 import 실패 확인**
- [ ] **Step 3: immutable registry와 순수 조립 함수 구현**
- [ ] **Step 4: 같은 명령으로 통과 확인**

### Task 2: service와 repository port

**Files:**
- Create: `code/deepagent-service/app/models/document.py`
- Create: `code/deepagent-service/app/models/reflection_job.py`
- Create: `code/deepagent-service/app/repositories/document_repository.py`
- Create: `code/deepagent-service/app/repositories/reflection_job_repository.py`
- Create: `code/deepagent-service/app/services/knowledge_service.py`
- Create: `code/deepagent-service/app/services/reflection_service.py`
- Test: `code/deepagent-service/tests/unit/test_knowledge_service.py`
- Test: `code/deepagent-service/tests/unit/test_reflection_service.py`

- [ ] **Step 1: repository를 주입받는 service 행동 테스트 작성**

```python
def test_search_normalizes_query_and_delegates_to_repository():
    repository = InMemoryDocumentRepository([Document(id="1", title="SOLID", content="SRP")])
    service = KnowledgeService(repository)
    assert service.search("  solid  ")[0].title == "SOLID"
```

```python
def test_created_reflection_job_is_pending():
    service = ReflectionService(InMemoryReflectionJobRepository())
    job = service.create_job(subject="daily")
    assert job.status is ReflectionJobStatus.PENDING
```

- [ ] **Step 2: 두 테스트를 실행해 import 실패 확인**
- [ ] **Step 3: Protocol port, memory adapter, application service 최소 구현**
- [ ] **Step 4: 두 테스트 통과 확인**

### Task 3: Agent registry, Deep Agent factory, LangGraph reflection

**Files:**
- Create: `code/deepagent-service/app/agents/common/contracts.py`
- Create: `code/deepagent-service/app/agents/registry.py`
- Create: `code/deepagent-service/app/agents/general/agent.py`
- Create: `code/deepagent-service/app/agents/general/tools.py`
- Create: `code/deepagent-service/app/agents/reflection/state.py`
- Create: `code/deepagent-service/app/agents/reflection/nodes.py`
- Create: `code/deepagent-service/app/agents/reflection/graph.py`
- Test: `code/deepagent-service/tests/unit/test_agent_registry.py`

- [ ] **Step 1: 이름 기반 등록·중복·미등록 행동 테스트 작성**

```python
def test_registry_resolves_registered_runner():
    runner = StubRunner()
    registry = AgentRegistry({"general": runner})
    assert registry.get("general") is runner
```

- [ ] **Step 2: 테스트를 실행해 import 실패 확인**
- [ ] **Step 3: `AgentRunner` protocol과 registry 구현**
- [ ] **Step 4: service-backed tool과 `create_deep_agent` adapter 구현**
- [ ] **Step 5: `START → reflect → END` LangGraph 구현**
- [ ] **Step 6: registry 테스트 통과 확인**

### Task 4: FastAPI composition과 route

**Files:**
- Create: `code/deepagent-service/app/api/dependencies.py`
- Create: `code/deepagent-service/app/api/routes/health.py`
- Create: `code/deepagent-service/app/api/routes/agents.py`
- Create: `code/deepagent-service/app/api/routes/reflection_jobs.py`
- Create: `code/deepagent-service/app/schemas/agent.py`
- Create: `code/deepagent-service/app/schemas/reflection.py`
- Create: `code/deepagent-service/app/main.py`
- Test: `code/deepagent-service/tests/api/test_health.py`
- Test: `code/deepagent-service/tests/api/test_agents.py`
- Test: `code/deepagent-service/tests/api/test_reflection_jobs.py`

- [ ] **Step 1: health, Agent 실행, reflection job 생성 API 테스트 작성**

```python
def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_agent_endpoint_uses_registered_runner(client):
    response = client.post("/v1/agents/general/runs", json={"message": "hello"})
    assert response.status_code == 200

def test_airflow_can_create_reflection_job(client):
    response = client.post("/v1/reflection-jobs", json={"subject": "daily"})
    assert response.status_code == 202
```

- [ ] **Step 2: API 테스트를 실행해 import 실패 확인**
- [ ] **Step 3: app factory와 dependency override가 가능한 route 구현**
- [ ] **Step 4: API 테스트 통과 확인**

### Task 5: storage adapter와 worker 경계

**Files:**
- Create: `code/deepagent-service/app/storage/postgres.py`
- Create: `code/deepagent-service/app/storage/redis.py`
- Create: `code/deepagent-service/app/storage/qdrant.py`
- Create: `code/deepagent-service/app/storage/minio.py`
- Create: `code/deepagent-service/app/workers/reflection.py`
- Create: `code/deepagent-service/app/integrations/external_api.py`
- Create: `code/deepagent-service/app/integrations/mcp.py`

- [ ] **Step 1: 각 factory가 typed settings만 입력받는 import 테스트를 architecture test에 추가**
- [ ] **Step 2: 테스트가 모듈 부재로 실패하는지 확인**
- [ ] **Step 3: SDK를 외부로 노출하지 않는 client factory 구현**
- [ ] **Step 4: job id를 받아 service를 실행하는 별도 worker entry point 구현**
- [ ] **Step 5: architecture test 통과 확인**

### Task 6: skill, Airflow, 문서와 전체 검증

**Files:**
- Create: `code/deepagent-service/app/agents/general/skills/knowledge-search/SKILL.md`
- Create: `code/deepagent-service/app/agents/reflection/skills/daily-reflection/SKILL.md`
- Create: `code/deepagent-service/app/prompts/shared/safety.md`
- Create: `code/deepagent-service/app/prompts/general/system.md`
- Create: `code/deepagent-service/app/prompts/reflection/system.md`
- Create: `code/deepagent-service/airflow/dags/deepagent_reflection.py`
- Create: `code/deepagent-service/.env.example`
- Create: `code/deepagent-service/README.md`
- Test: `code/deepagent-service/tests/architecture/test_import_rules.py`

- [ ] **Step 1: 금지 import와 skill 소유 경로를 검사하는 architecture test 작성**
- [ ] **Step 2: 누락 파일 때문에 실패하는지 확인**
- [ ] **Step 3: skill·prompt·Airflow 3.1 HTTP 호출 예제·실행 문서 작성**
- [ ] **Step 4: `pytest -q` 전체 통과 확인**
- [ ] **Step 5: `ruff check .`와 `ruff format --check .` 통과 확인**
- [ ] **Step 6: `python -m compileall app airflow` 통과 확인**

## 4. 의존 규칙

```text
api → agents/services/schemas
agents → prompts/services
tools → services
services → repository protocols/models
repositories → models
storage → vendor SDK

services -X→ FastAPI/LangGraph/Deep Agents/vendor SDK
tools    -X→ storage/repository implementation
models   -X→ framework/vendor SDK
```

## 5. 완료 기준

- FastAPI app factory가 외부 서비스 없이 생성된다.
- test double을 주입해 Agent endpoint를 실행할 수 있다.
- Deep Agent factory가 Agent별 prompt, tool, skill 경로를 조립한다.
- reflection job은 HTTP로 등록하고 별도 worker에서 실행할 수 있다.
- Airflow 3.1 + CeleryExecutor는 HTTP API 호출만 담당하며 애플리케이션 Celery를 추가하지 않는다.
- 네 저장 기술은 `storage/`에 모이지만 하나의 범용 service/interface로 결합되지 않는다.
- architecture test가 SOLID 의존 방향의 핵심 금지 규칙을 검사한다.

> 저장소 지침에 따라 Git add/commit 단계는 실행하지 않는다.
