# Agent 계층과 일반적 디렉터리 명명 보강 조사

> 상태: 사용자 피드백을 반영한 추가 조사 초안  
> 조사 기준일: 2026-08-30  
> 선행 문서: [01_Deep_Agents_프로젝트_아키텍처_조사.md](01_Deep_Agents_프로젝트_아키텍처_조사.md)  
> 핵심 질문: 일반적인 Python/FastAPI 명명, Agent 계층 방법론, prompt 관리, infrastructure 표현을 다시 검증한다.

## 1. 추가 조사의 배경

선행 문서의 B안은 도메인 중심 모듈러 모놀리스를 다음처럼 표현했다.

```text
interfaces/
agent_platform/
modules/<domain>/{domain,application,infrastructure,agent}/
```

책임과 의존 방향을 설명하는 아키텍처 용어로는 유효하지만, 실제 Python/FastAPI 프로젝트에서 가장 흔하고 바로 이해되는 디렉터리 이름은 아니다. 특히 다음 문제가 있다.

- `interfaces/`는 Python의 protocol/interface 정의와 혼동하기 쉽다.
- `agent_platform/`은 아직 플랫폼 팀이나 독립 제품이 없는 단계에는 과한 이름이다.
- `modules/`는 한 단계 깊이를 추가하지만 실질적인 의미를 주지 않을 수 있다.
- 각 업무 폴더마다 `infrastructure/`를 반복하면 파일 탐색이 어렵고 현재 팀의 익숙한 3-layer 구조와 멀어진다.
- prompt가 어디에 모이는지 한눈에 보이지 않는다.

따라서 이번 조사에서는 아키텍처 원칙과 실제 파일명 관례를 분리해 검토했다.

## 2. 결론

### 2.1 명명에 대한 결론

조사한 공식·운영 프로젝트에서 `interfaces/`, `agent_platform/`, 범용 `modules/` 조합은 공통 관례가 아니었다. 더 익숙한 기본 어휘는 다음과 같다.

```text
app/
  api/
  core/
  agents/
  prompts/
  services/
  repositories/
  models/
  schemas/
  storage/
  integrations/
  workers/
```

모든 폴더가 반드시 필요한 것은 아니다. 실제 코드가 생길 때 추가한다. 중요한 점은 이름보다 import 방향과 책임이다.

### 2.2 방법론에 대한 결론

Agent 시스템에 Spring의 `Controller → Service → Repository`와 일대일 대응하는 보편적인 Agent 전용 3-layer 표준은 없다.

그렇다고 기존 계층을 버리는 것도 아니다. Agent는 일반적으로 **application orchestration 계층**으로 해석하는 편이 가장 일관된다.

```text
일반 API
Controller/API → Service → Repository → DB

Agent API
Controller/API → Agent 또는 Graph → Tool → Service → Repository → DB
```

- FastAPI route는 controller/inbound adapter다.
- service는 business use case와 transaction을 소유한다.
- repository는 업무 entity의 persistence를 추상화한다.
- Agent는 불확실한 문제에서 계획, tool 선택, 반복을 수행하는 orchestrator다.
- LangGraph는 이 orchestration의 상태 전이와 실행 흐름을 표현한다.
- tool은 Agent가 service를 호출하는 adapter다.

따라서 Agent마다 다시 controller/service/repository를 복제하는 것이 아니라 기존 application layer 위에 Agent orchestration을 추가한다.

### 2.3 prompt에 대한 결론

사용자가 원하는 “prompt를 모아두는 곳”에는 일반 이름인 `prompts/`가 적합하다. 다만 하나의 거대한 전역 prompt 파일로 만들지 않고 다음 하이브리드를 권장한다.

- `prompts/shared/`: 여러 Agent가 함께 쓰는 안정적인 공통 조각
- `prompts/<agent>/`: 특정 Agent가 소유하는 system prompt와 examples
- `prompts/registry.py`: prompt key와 builder 등록
- `prompts/assembly.py`: 조립 순서와 조건을 결정하는 순수 함수
- `evals/`: prompt 자체가 아니라 평가 dataset과 grader
- `schemas/`: 출력 schema와 tool schema
- `agents/<agent>/skills/`: 해당 Agent가 소유하며 필요할 때만 로드하는 전문 절차
- `agents/shared/skills/`: 실제로 여러 Agent가 공동 소유할 때만 두는 선택적 공통 skill
- `AGENTS.md`: 항상 필요한 프로젝트·조직 지침

Deep Agents의 custom subagent는 각자 `skills` source 경로를 지정하며 상위 Agent의 skill과 격리된다. 따라서 skill은 기본적으로 소유 Agent 가까이에 두는 것이 자연스럽다. 단, 프레임워크가 자동으로 제공하는 general-purpose subagent는 main Agent에 전달된 skill을 상속한다. 이 동작을 모든 custom subagent의 상속 규칙으로 오해하면 안 된다.

## 3. 실제 프로젝트의 명명 관례

### 3.1 FastAPI 공식 자료

FastAPI 공식 “Bigger Applications”는 다음과 같은 일반적인 이름을 사용한다.

```text
app/
  main.py
  dependencies.py
  routers/
  internal/
```

FastAPI는 service나 repository 계층을 강제하지 않는다. `routers/services/repositories`는 프레임워크 표준이 아니라 애플리케이션 복잡도에 따라 선택하는 관례다.

공식 Full Stack FastAPI Template도 `backend/app` 아래에 `api`, `core`, `models`, CRUD·DB 관련 코드를 두는 비교적 평범한 이름을 사용한다.

### 3.2 LangGraph와 Deep Agents 공식 예제

LangGraph application structure 예제는 대체로 다음처럼 작다.

```text
my_agent/
  agent.py
  utils/
    tools.py
    nodes.py
    state.py
langgraph.json
pyproject.toml
```

Deep Agents의 `deep_research` 예제는 업무 패키지 안에 `agent.py`, `prompts.py`, `utils.py`를 둔다. 이는 프레임워크 예제에 적합한 작은 구조이지 business API와 여러 DB까지 가진 전체 backend의 표준 구조는 아니다.

### 3.3 Dify

Dify는 성장한 Python backend에서 익숙한 이름을 사용한다.

```text
api/
  controllers/
  services/
  repositories/
  models/
  core/
  tasks/
  extensions/
```

prompt도 모두 한곳에만 두지 않는다.

- 공통 transform과 parser: `core/prompt/`
- Agent prompt: `core/agent/prompt/`
- workflow prompt: `core/workflow/.../prompts/`
- RAG prompt: `core/rag/.../template_prompts.py`

즉 공통 엔진은 중앙화하고 정책 텍스트는 소유 기능 가까이에 두는 하이브리드다.

### 3.4 Open SWE

Open SWE는 다음처럼 Agent 중심의 일반적인 이름을 사용한다.

```text
agent/
  api/
  graphs/
  tools/
  integrations/
  resources/
  prompt.py
```

`agent/prompt.py`가 명명된 section을 조립하고 `agent/resources/default_prompt.md`와 대상 repository의 `AGENTS.md`를 추가한다. 중앙 조립기와 외부 Markdown instruction을 함께 사용한다.

### 3.5 OpenHands Software Agent SDK

OpenHands는 prompt 조립 자체가 복잡해지면서 다음 구조를 사용한다.

```text
context/prompts/
  registry.py
  presets.py
  section.py
  sections/
```

등록 순서에 따라 prompt를 결정적으로 조립하고 model·기능 조합별 golden snapshot test를 둔다. 반면 condenser처럼 특정 기능에만 속하는 prompt는 해당 기능 옆에 둔다.

### 3.6 Google agents-cli scaffold

Google의 agent project scaffold도 시작점은 단순하다.

```text
app/
  agent.py
  fast_api_app.py
  app_utils/
    services.py
tests/
  unit/
  integration/
  eval/
```

이는 작은 agent project에서 `app`, `agent`, `services`, `tests` 같은 일반 이름이 우선됨을 보여준다. 다만 DB와 복잡한 업무 계층까지 다루는 template은 아니다.

## 4. Java 3-layer와 Agent 시스템

### 4.1 Java/Spring의 3-layer 의미

Spring의 `@Controller`, `@Service`, `@Repository`는 presentation, application/service, persistence 역할을 나타내는 stereotype이다. Java 언어 자체의 의무 구조가 아니라 Spring 생태계의 강한 관례다.

Fowler의 패턴 정의를 기준으로 보면 다음과 같다.

- Controller: UI·Web 입력 처리
- Service Layer: 애플리케이션 경계와 use case 조정
- Repository: domain과 data mapping 사이에서 객체 collection 같은 접근 제공

DDD를 적용하면 service가 모든 business rule을 가지는 것이 아니라 application service는 흐름을 조정하고 핵심 규칙은 domain model에 둔다.

### 4.2 Agent 전용 3-layer가 없는 이유

Agent는 데이터 접근 계층처럼 하나의 고정 역할이 아니다.

- 사용자 목표를 받아 완수하면 application service에 가깝다.
- 상위 supervisor가 호출하는 remote agent라면 외부 collaborator다.
- Agent를 HTTP로 노출하는 route는 controller다.
- Agent가 호출하는 tool은 outbound port·adapter다.
- Agent 내부 node는 내용에 따라 business rule, LLM call, DB access, 외부 action 중 무엇이든 될 수 있다.

따라서 `AgentController`, `AgentService`, `AgentRepository`라는 계층을 기계적으로 만드는 것은 책임을 명확히 하지 못한다.

### 4.3 Clean/Hexagonal Architecture 적용

Agent 시스템에는 새로운 3-layer를 발명하기보다 기존 Ports and Adapters를 적용하는 편이 적합하다.

```text
                Driving side
        HTTP / Airflow / CLI / Test
                  │
                  ▼
          API route / controller
                  │
                  ▼
       Application orchestration
       ├── deterministic service
       ├── LangGraph workflow
       └── Deep Agent loop
                  │
                  ▼
                Ports
       ├── Repository
       ├── ModelGateway
       ├── DocumentSearch
       ├── MemoryStore
       ├── CheckpointStore
       └── ArtifactStore
                  │
                  ▼
               Adapters
       PostgreSQL / Qdrant / Redis
       MinIO / MCP / external API / LLM
```

Cockburn의 원래 Hexagonal Architecture는 UI뿐 아니라 batch script나 test도 동일 application port를 구동할 수 있게 하라고 설명한다. 현재 프로젝트에서는 FastAPI, Agent tool, Airflow가 같은 service를 호출할 수 있어야 한다는 의미다.

### 4.4 구성 요소 대응표

| 구성 요소 | 책임 | 아키텍처 관점 |
| --- | --- | --- |
| FastAPI route | 인증, validation, HTTP DTO, status·stream | controller / inbound adapter |
| Service | use case, transaction, 권한, business workflow | application service |
| Domain model | 반드시 지켜야 할 deterministic rule | domain |
| Agent | 계획, tool 선택, 반복, 결과 합성 | application orchestrator |
| LangGraph | 상태 전이, 분기, retry, HITL | workflow/orchestration runtime |
| Graph node | 한 단계의 계산·action·state update | 내용에 따라 계층이 달라짐 |
| Tool schema | Agent에 노출하는 capability contract | outbound port의 Agent-facing 표현 |
| Tool 구현 | service 호출과 Agent DTO 변환 | adapter |
| Repository interface | 업무 aggregate 조회·저장 계약 | application/domain port |
| Repository 구현 | SQLAlchemy·DB query | persistence adapter |
| Model client | LLM provider 호출 | provider adapter |
| Checkpointer | 실행 state snapshot 저장 | execution persistence adapter |
| Memory store | cross-thread memory 저장·검색 | memory adapter |

### 4.5 중요한 의존 방향

```text
api ───────────────→ services ─────→ repositories(interface)
 │                         ▲
 └→ agents/graphs → tools ─┘

repository implementations → db clients
agents/graphs → LangGraph/Deep Agents
services/domain → LangGraph/Deep Agents를 모름
```

일반 API는 Agent를 거치지 않아도 된다. Agent API는 Agent·Graph를 거친 뒤 tool을 통해 기존 service를 사용한다.

## 5. Agent 내부를 어떻게 나눌 것인가

Agent 전용 3-layer는 없지만, Agent가 커지면 runtime 책임에 따라 나눌 수 있다.

```text
agents/
  general/
    agent.py          # Deep Agent factory와 조립
    graph.py          # 직접 작성한 LangGraph가 있으면 topology
    nodes.py          # node 구현
    state.py          # raw execution state schema
    tools.py          # 이 Agent가 노출할 tool set 선택·wrapper
    middleware.py     # Agent lifecycle cross-cutting policy
```

각 파일의 역할은 다음과 같다.

| 파일 | 변경 이유 |
| --- | --- |
| `agent.py` | model, subagent, middleware, tool set 조합 변경 |
| `graph.py` | node·edge와 실행 흐름 변경 |
| `nodes.py` | 개별 workflow 단계 변경 |
| `state.py` | 단계 간 raw data 계약 변경 |
| `tools.py` | Agent에 공개할 capability와 schema 변경 |
| `middleware.py` | logging, permission, summarization, guardrail 변경 |

단순한 Agent에 빈 파일을 모두 만들 필요는 없다. 처음에는 `agent.py`와 `tools.py`만 두고 실제 복잡도가 생길 때 분리한다.

LangGraph 공식 설계 가이드는 state에 prompt template이나 포맷된 문자열이 아니라 단계 사이에 유지할 raw data를 넣고 prompt는 node 실행 시 조립하라고 권한다.

## 6. Prompt 저장과 조립

### 6.1 Prompt artifact 구분

| artifact | 역할 | 위치 후보 |
| --- | --- | --- |
| System prompt | 역할·행동 정책·안정적인 지침 | `prompts/<agent>/system.md` |
| Template | typed variable을 가진 prompt 조각 | `prompts/<agent>/` + builder |
| Few-shot example | 예제 데이터 | `prompts/<agent>/examples.yaml` |
| Output schema | 실행 가능한 출력 계약 | `schemas/`, Pydantic/JSON Schema |
| Tool description | tool 호출 계약 | tool 함수·schema 옆 |
| `SKILL.md` | 필요할 때만 읽는 Agent별 전문 절차 | `agents/<agent>/skills/<skill>/` |
| `AGENTS.md` | 매 실행에 필요한 프로젝트 지침 | 프로젝트 또는 대상 workspace |
| Eval dataset | 행동 품질 검증 | `evals/datasets/` |

출력 schema를 자연어 prompt에만 두면 안 된다. Pydantic·JSON Schema와 structured output으로 검증한다.

### 6.2 권장 조립 순서

```text
stable shared policy
  → organization/domain override
  → selected Agent instructions
  → skill index 또는 선택된 skill
  → dynamic runtime context
  → user input은 별도 user message
```

정적인 prefix를 앞에 두고 날짜·사용자별 정보 같은 dynamic context를 뒤에 둬야 provider prompt cache를 활용하기 쉽다.

### 6.3 권장 테스트

- prompt key 중복과 누락 변수 검사
- builder의 escaping과 untrusted input 경계 검사
- 최종 rendered system message golden snapshot
- model·provider·feature flag 조합별 snapshot
- representative·edge·prompt-injection eval dataset
- output schema validation
- trace에 prompt key, rendered hash, model snapshot, tool schema hash 기록

Deep Agents와 OpenHands는 실제로 최종 system prompt에 대한 snapshot test를 사용한다.

### 6.4 외부 prompt registry

LangSmith는 prompt commit, diff, `staging`·`production` 승격, rollback과 webhook을 제공한다. 다만 처음부터 외부 registry를 source of truth로 만들면 다음 비용이 생긴다.

- runtime network와 vendor availability 의존
- code와 prompt version drift
- 로컬 재현성 저하
- mutable production tag만 기록할 경우 사후 재현 불가

비개발자 편집, A/B test, code와 다른 release cadence가 실제로 필요할 때 도입한다. 도입 시 trace에는 tag가 아니라 resolved commit hash를 남기고 local fallback과 manifest를 둔다.

2026-08-30 기준 OpenAI 공식 prompt engineering 문서는 신규 작업에서 hosted reusable prompt object보다 application code 안의 작은 prompt builder, 기능 근처 배치, typed input/schema, test/eval과 code deployment를 권장한다. 따라서 외부 prompt registry를 기본안으로 두지 않는다.

## 7. 수정한 디렉터리 후보

### 7.1 후보 A: 익숙한 Layered + Agent Orchestration — 권장 후보

```text
app/
  main.py

  api/
    routes/
    dependencies.py

  core/
    config.py
    logging.py
    exceptions.py
    security.py

  agents/
    registry.py
    common/
      context.py
      middleware.py
    shared/
      skills/                  # 실제 공용 skill이 있을 때만
    general/
      agent.py
      tools.py
      skills/
        <skill>/
          SKILL.md
    knowledge/
      agent.py
      graph.py
      nodes.py
      state.py
      tools.py
      skills/
        <skill>/
          SKILL.md
    reflection/
      agent.py
      graph.py
      state.py
      tools.py
      skills/
        <skill>/
          SKILL.md

  prompts/
    registry.py
    assembly.py
    shared/
      safety.md
      style.md
    general/
      system.md
      examples.yaml
    knowledge/
      system.md
      examples.yaml
    reflection/
      system.md

  services/
    conversation_service.py
    knowledge_service.py
    reflection_service.py

  repositories/
    conversation_repository.py
    document_repository.py
    reflection_job_repository.py

  models/
    conversation.py
    document.py
    reflection_job.py

  schemas/
    conversation.py
    agent.py
    reflection.py

  storage/
    postgres.py
    redis.py
    qdrant.py
    minio.py

  integrations/
    mcp.py
    external_api.py

  workers/
    reflection.py

evals/
tests/
```

이 구조의 장점은 Java/Spring 경험자가 `api → services → repositories`를 바로 이해하면서 Agent 관련 코드는 `agents`, `prompts`에서 찾을 수 있다는 점이다.

`storage/`는 PostgreSQL, Redis, Qdrant, MinIO의 concrete client·session·connection lifecycle을 한곳에서 관리한다. 이는 저장 기술을 탐색하기 위한 **물리적 통합**이지, 네 기술을 하나의 범용 interface나 `StorageService`로 합치는 **책임 통합**은 아니다. `repositories/`는 여전히 업무 목적별 query와 persistence contract를 담당하고, 외부 API와 MCP는 `integrations/`에 둔다.

Agent별 `skills/`는 해당 Agent의 배포·변경 단위와 나란히 둔다. 공통 skill은 두 Agent 이상이 실제로 같은 절차와 release lifecycle을 공유할 때만 `agents/shared/skills/`로 승격한다. custom subagent에는 이 경로를 명시적으로 전달하고, general-purpose subagent의 자동 상속은 프레임워크 동작으로 취급한다.

주의점:

- `services/`, `repositories/`, `models/`가 커지면 업무별 subpackage를 만든다.
- `common/`에는 실제 두 곳 이상에서 안정적으로 공유되는 것만 둔다.
- `core/`에 business logic을 넣지 않는다.
- tool이 repository를 직접 호출하지 않는다.

### 7.2 후보 B: Layered root + 업무별 namespace

규모가 커지면 익숙한 최상위 이름을 유지하면서 업무별 namespace를 맞출 수 있다.

```text
app/
  api/
    knowledge/
    conversation/
    reflection/
  agents/
    general/
      skills/
    knowledge/
      skills/
    reflection/
      skills/
  prompts/
    shared/
    general/
    knowledge/
    reflection/
  services/
    knowledge/
    conversation/
    reflection/
  repositories/
    knowledge/
    conversation/
    reflection/
  models/
  schemas/
  storage/
  integrations/
  workers/
  core/
```

선행 문서 B안의 모듈 응집도를 어느 정도 유지하면서도 `modules/<domain>/domain/application/infrastructure`라는 깊은 용어를 피한다.

단점은 하나의 기능 변경이 여러 최상위 폴더를 오갈 수 있다는 점이다. 대신 팀이 익숙한 계층과 전체 prompt·Agent 목록의 탐색성이 좋아진다.

### 7.3 후보 C: Package by feature

```text
app/
  api/
  core/
  agents/
    general/
      skills/

  conversation/
    router.py
    service.py
    repository.py
    models.py
    schemas.py
    agent.py
    graph.py
    tools.py
    skills/

  knowledge/
    router.py
    service.py
    repository.py
    models.py
    schemas.py
    agent.py
    graph.py
    tools.py
    skills/

  reflection/
    router.py
    service.py
    repository.py
    models.py
    schemas.py
    agent.py
    graph.py
    tools.py
    skills/

  prompts/
    shared/
    conversation/
    knowledge/
    reflection/
```

`modules/` wrapper 없이 업무 폴더를 바로 두는 방식이다. 업무별 소유권과 독립 추출에는 강하지만, 어떤 파일이 어느 계층인지 전체 목록으로 보고 싶은 팀에는 후보 A·B보다 낯설 수 있다.

## 8. 후보 A의 요청 흐름

### 8.1 일반 business API

```text
api/routes/documents.py
  → services/knowledge_service.py
  → repositories/document_repository.py
  → storage/postgres.py 또는 storage/qdrant.py
```

### 8.2 범용 Agent 요청

```text
api/routes/agents.py
  → agents/general/agent.py
  → agents/general/tools.py
  → services/<business>_service.py
  → repositories/<business>_repository.py
```

### 8.3 결정적인 LangGraph workflow

```text
api/routes/agents.py 또는 업무 Agent
  → agents/knowledge/graph.py
  → agents/knowledge/nodes.py
  → service
  → repository
```

### 8.4 Airflow 성찰

```text
Airflow
  → api/routes/reflection_jobs.py
  → services/reflection_service.py       # job 등록
  → repositories/reflection_job_repository.py

workers/reflection.py
  → services/reflection_service.py       # job claim·상태 변경
  → agents/reflection/agent.py 또는 graph.py
  → services/*                           # 업무 능력
  → repository/storage
```

## 9. SOLID 검증

| 원칙 | 후보 A에서의 적용 |
| --- | --- |
| SRP | route, Agent factory, graph, tool, service, repository, client lifecycle의 변경 이유 분리 |
| OCP | registry에 Agent·prompt·tool descriptor 추가, 기존 거대 조건문 최소화 |
| LSP | repository·store adapter contract test로 semantics 검증 |
| ISP | `DatabaseService` 대신 목적별 repository/store/client 사용 |
| DIP | service는 구체 DB SDK를 모르며 bootstrap/dependency가 구현을 주입 |

단순히 폴더를 나눈다고 SOLID가 보장되지는 않는다. architecture test와 import rule이 필요하다.

```text
금지 예
services → FastAPI
services → LangGraph
services → qdrant_client/boto3/redis SDK
tools → SQLAlchemy session/query
repositories → FastAPI request
```

## 10. 이번 조사로 수정된 판단

### 유지하는 판단

- 현재는 모듈러 모놀리스가 적합하다.
- 범용 Agent와 업무별 Agent factory를 함께 사용한다.
- Agent·tool은 business service를 재사용한다.
- checkpointer, memory, business repository, file backend를 구분한다.
- API와 장시간 runner는 code를 공유하되 process lifecycle은 분리할 수 있다.

### 수정하는 판단

- `interfaces/`, `agent_platform/`, `modules/`를 기본 디렉터리명으로 권하지 않는다.
- 각 업무 모듈에 반복되는 `infrastructure/`를 기본안으로 두지 않는다.
- 일반적인 `api`, `core`, `agents`, `prompts`, `services`, `repositories`, `models`, `schemas`, `storage`, `integrations`, `workers`를 우선 검토한다.
- Agent는 독립적인 3-layer가 아니라 기존 service 계층을 이용하는 orchestration 계층으로 명시한다.
- prompt는 중앙 `prompts/`에서 찾을 수 있게 하되 Agent별 하위 폴더와 중앙 assembly를 함께 둔다.
- PostgreSQL, Redis, Qdrant, MinIO의 concrete adapter는 `storage/`로 모으되 목적별 repository와 client 책임은 합치지 않는다.
- skill은 최상위에 모으지 않고 기본적으로 `agents/<agent>/skills/`에 colocate한다.

### 현재 권장 후보

사용자의 Java 3-layer 경험, 현재 한 팀, 향후 확장, prompt 탐색 요구를 함께 고려하면 **후보 A: 익숙한 Layered + Agent Orchestration**을 우선 검토할 가치가 있다.

다만 이것은 선행 문서의 모듈러 모놀리스 원칙을 버리는 것이 아니다. 디렉터리 이름은 익숙한 계층형을 사용하고, 내부 package와 import rule로 업무 경계를 유지하는 절충안이다.

## 11. 추가로 결정할 질문

1. `models/`를 SQLAlchemy ORM 전용으로 사용할지, domain model도 포함할지
2. repository protocol과 구현을 같은 파일에 둘지 `repositories/base/`, `repositories/postgres/`로 나눌지
3. Qdrant의 업무 query를 어느 repository contract가 소유할지
4. prompt 원본을 Python string보다 Markdown 중심으로 둘지
5. 업무별 prompt를 중앙 `prompts/<agent>/`에 둘지 `agents/<agent>/prompts/`에 colocate할지
6. `graph.py`와 `agent.py`를 언제 분리할지
7. 실제 bounded context와 최초 Agent 목록

## 12. 참고 자료

### Architecture와 계층

- [Spring component stereotypes](https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html)
- [Fowler Repository pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Eric Evans DDD Reference](https://www.domainlanguage.com/ddd/reference/)
- [Alistair Cockburn Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture)
- [Robert C. Martin, The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Architecture Patterns with Python: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer)
- [LangGraph Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
- [LangGraph Workflows and Agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Microsoft Agent Pipeline Architecture](https://learn.microsoft.com/en-us/agent-framework/concepts/agents/agent-pipeline)

### 디렉터리와 실제 사례

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template)
- [LangGraph Application Structure](https://docs.langchain.com/langsmith/application-structure)
- [Deep Agents deep research prompts](https://github.com/langchain-ai/deepagents/blob/1c14626d068ee5e1724d53dc17927d37987ebe36/examples/deep_research/research_agent/prompts.py)
- [Dify prompt core](https://github.com/langgenius/dify/tree/02f9b3ca7c109fe1b0d5e26a8d553659e5e1e78e/api/core/prompt)
- [Open SWE customization](https://github.com/langchain-ai/open-swe/blob/4bed1112362d4ce74db86e704329fda0f3412b69/docs/CUSTOMIZATION.md#5-system-prompt)
- [OpenHands prompt registry](https://github.com/OpenHands/software-agent-sdk/blob/9d143aac35c2dcec9cbb046ff9f35ac5eb072f6a/openhands-sdk/openhands/sdk/context/prompts/registry.py)
- [Google agents-cli project structure](https://google.github.io/agents-cli/guide/project-structure/)

### Prompt 관리

- [Deep Agents Context Engineering](https://docs.langchain.com/oss/python/deepagents/context-engineering)
- [Deep Agents Skills](https://docs.langchain.com/oss/python/deepagents/skills)
- [Deep Agents Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Deep Agents deployment structure](https://github.com/langchain-ai/deepagents/blob/main/deepagents-deploy.md)
- [LangSmith Manage Prompts](https://docs.langchain.com/langsmith/manage-prompts)
- [LangSmith Prompt GitHub Sync](https://docs.langchain.com/langsmith/prompt-commit)
- [OpenAI Prompt Engineering: version prompts in code](https://developers.openai.com/api/docs/guides/prompt-engineering#version-prompts-in-code)
- [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
