# Deep Agents 프로젝트 아키텍처 조사

> 상태: 사용자 검토 전 조사 초안  
> 조사 기준일: 2026-08-30  
> 대상 스택: Python, FastAPI, LangGraph, LangChain Deep Agents  
> 운영 조건: 단일 조직, 현재 한 팀·단일 저장소·소수 배포 프로세스, 향후 여러 팀·독립 배포 가능  
> 외부 스케줄러: Apache Airflow 3.1 + CeleryExecutor  
> 설계 기준: SOLID, 점진적 확장, PostgreSQL·Qdrant·MinIO·Redis 및 외부 API 연동

## 1. 조사 목적

Deep Agents 기반 프로젝트가 성장하면서 다음 문제가 동시에 발생할 때의 애플리케이션 아키텍처와 디렉터리 구조를 조사한다.

- 범용 Deep Agent에 tool이 계속 추가된다.
- 업무별 전문 Agent가 추가된다.
- Agent가 아닌 일반 business service와 API가 늘어난다.
- PostgreSQL 같은 RDB, Qdrant 같은 vector DB, MinIO, Redis를 함께 사용한다.
- 하루 한 번 실행되는 장시간 성찰 작업을 Airflow가 시작한다.
- 현재는 한 팀이 관리하지만 향후 모듈별 팀 소유권과 독립 배포 가능성이 있다.
- 폴더 이름만 분리하는 것이 아니라 SOLID 원칙을 의존성 방향으로 지켜야 한다.

이 문서는 구조를 확정하는 설계서가 아니다. 공식 문서와 실제 오픈소스 사례를 비교하고, 검토할 후보 구조와 판단 기준을 남기는 조사 자료다.

## 2. 핵심 결론

현재 조건에 가장 적합한 후보는 **도메인 중심 모듈러 모놀리스 + 공통 Agent Platform + 독립 Agent factory**다.

```text
범용 Deep Agent
  ├── 단순한 업무 능력: application use case를 tool로 호출
  ├── 자율적인 전문 작업: 업무별 Deep Agent에 위임
  └── 결정적인 workflow: 업무별 LangGraph를 호출

FastAPI / Tool / Graph / Airflow entrypoint
  → Application Service
  → Port(interface)
  → PostgreSQL·Qdrant·MinIO·Redis·외부 API Adapter
```

핵심은 Agent를 business logic의 중심으로 만들지 않는 것이다. Agent, FastAPI router, Airflow 작업은 모두 application use case를 호출하는 입구다. 업무 규칙은 Deep Agents나 LangGraph 타입에서 독립되어야 한다.

현재는 단일 Python 저장소와 단일 이미지를 유지할 수 있다. 다만 실행 command는 `api`와 장시간 작업 `runner`처럼 분리할 수 있어야 한다. 처음부터 마이크로서비스나 다중 Python package로 나누는 것은 현재 팀 규모에 비해 비용이 크다.

## 3. 조사 기준과 출처 신뢰도

| 등급 | 출처 | 사용 방법 |
| --- | --- | --- |
| A | LangChain, LangGraph, Deep Agents, Airflow, FastAPI 공식 문서와 공식 GitHub | 현재 기능·버전·동작 판단의 근거 |
| A- | Dify, OpenHands, Open SWE 등 프로젝트 공식 GitHub의 실제 source tree와 배포 설정 | 실제 성장한 코드베이스의 구조 비교 |
| B | 프로젝트 README의 아키텍처 설명 | source tree와 함께 교차 확인 |
| C | 커뮤니티 블로그·개인 예제 | 이번 핵심 결론에는 사용하지 않음 |

오픈소스의 디렉터리는 그 프로젝트의 요구와 조직 구조를 반영한다. 따라서 그대로 복사하지 않고 어떤 문제 때문에 경계를 만들었는지를 중심으로 해석한다.

## 4. LangGraph와 Deep Agents의 정확한 관계

### 4.1 계층 관계

```text
LangGraph
  └── graph runtime
      └── LangChain create_agent
          └── Deep Agents create_deep_agent
```

- **LangGraph**는 상태, node, edge, checkpoint, interrupt, resume, streaming을 제공하는 graph runtime이다.
- **LangChain `create_agent`**는 LangGraph 위에 구성된 기본 tool-calling agent harness다.
- **Deep Agents**는 `create_agent` 위에 filesystem, context 관리, subagent, skills, middleware 등을 조립한 장기 작업용 harness다.

Deep Agents 공식 README도 LangGraph를 runtime, `create_agent`를 최소 harness, Deep Agents를 더 opinionated한 harness로 설명한다. 복잡한 custom orchestration이 필요하면 LangGraph를 직접 사용하는 관계이지, 둘 중 하나만 선택하는 관계가 아니다.

2026-08-30 기준 확인한 안정판은 다음과 같다.

| 구성 요소 | 기준 버전 | 공개일 |
| --- | --- | --- |
| Deep Agents | `0.7.11` | 2026-08-28 |
| LangGraph | `1.2.11` | 2026-08-11 |

Deep Agents는 아직 `1.0` 이전이므로 minor release에서도 호환성 변경을 확인해야 한다. 특히 `0.7.0`부터 기본 `TodoListMiddleware`, `write_todos`, todo state와 관련 기본 prompt가 제거됐다. 이전 튜토리얼의 계획 기능을 현재 기본 동작으로 가정하면 안 된다.

### 4.2 `create_deep_agent`가 조립하는 것

현재 공식 source의 `create_deep_agent`는 다음 범주의 구성 요소를 받으며 최종적으로 `CompiledStateGraph`를 반환한다.

- model, tools, system prompt
- middleware, subagents, skills, memory, permissions
- backend
- interrupt 설정과 response format
- state schema와 runtime context schema
- checkpointer와 store

`tools=`에 전달한 tool은 Deep Agents의 내장 filesystem·task 계열 tool에 추가된다. 따라서 업무 tool 수가 많아질수록 모든 tool을 한 범용 Agent에 무조건 전달하지 말고 Agent별 allowlist와 registry가 필요하다.

### 4.3 LangGraph를 직접 써야 하는 경우

다음 조건은 Deep Agent의 자율 판단보다 직접 작성한 LangGraph가 더 적합하다.

- 단계와 순서가 업무 규칙으로 고정된다.
- 특정 검증이나 승인을 반드시 거쳐야 한다.
- 실패 분기와 보상 경로가 명시적이어야 한다.
- 동일 입력에 대한 실행 경로를 예측·평가해야 한다.
- node별 timeout, retry, observability가 중요하다.

### 4.4 Deep Agent가 적합한 경우

- 여러 tool 중 무엇을 어떤 순서로 사용할지 미리 고정하기 어렵다.
- 장시간 조사·분석에서 context offloading이 필요하다.
- 전문 subagent로 context를 격리해야 한다.
- skills와 작업 파일을 필요할 때 읽어야 한다.
- 결과 도출 과정이 개방형이며 LLM의 계획·판단이 제품 가치다.

### 4.5 Tool, subagent, 별도 graph를 선택하는 기준

| 요구 | 권장 실행 단위 |
| --- | --- |
| 원자적인 조회·명령 | tool → application use case |
| 고정된 단계·조건 분기 | 직접 작성한 LangGraph |
| 여러 tool을 자율 조합하는 전문 업무 | 업무별 Deep Agent |
| 여러 업무 영역을 판단해 위임 | 범용 Deep Agent supervisor |
| 별도 API·권한·상태·SLA·배포 필요 | 독립 compiled graph 또는 독립 서비스 |

subagent는 서비스 경계가 아니다. 부모 Agent 내부에서 전문 작업을 위임하고 context를 격리하는 실행 경계다. 독립 API와 lifecycle이 필요하다면 subagent로만 감추지 말고 별도 graph entrypoint를 제공해야 한다.

## 5. 상태와 저장소의 책임 분리

### 5.1 서로 다른 네 가지 저장 영역

| 영역 | 수명 | 맡는 일 | 맡기지 않는 일 |
| --- | --- | --- | --- |
| LangGraph checkpointer | thread·run | graph 실행 snapshot, interrupt, resume | business 원장, 장기 memory 검색 |
| LangGraph store | cross-thread | 사용자·조직·Agent의 장기 정보 | thread 실행 단계 |
| Deep Agents backend | 작업 공간 | Agent-visible file, skill, artifact, sandbox filesystem | canonical business record |
| Business storage | 업무 수명 | 업무 entity, transaction, 감사, 권한 | LLM scratchpad |

이들을 하나의 범용 `StorageService` 또는 `Repository`로 합치면 SRP와 ISP가 깨진다.

### 5.2 데이터 저장소별 후보 책임

| 저장소 | 후보 책임 | 주의점 |
| --- | --- | --- |
| PostgreSQL | 업무 원장, job 상태, idempotency, 관계·감사 데이터 | Agent checkpoint와 업무 transaction을 같은 개념으로 취급하지 않음 |
| Qdrant | document·memory vector index와 retrieval payload | 업무 원장으로 사용하지 않음 |
| MinIO | 원문, 첨부, 대형 artifact, 결과 bundle | DB에는 immutable object reference와 metadata 저장 |
| Redis | cache, rate limit, lock, 짧은 수명의 coordination·stream | canonical business state를 Redis에만 두지 않음 |

하나의 use case가 PostgreSQL과 Qdrant 또는 MinIO를 함께 갱신할 때는 분산 transaction을 가장하지 않는다. PostgreSQL transaction과 outbox를 기준으로 비동기 index·object 처리를 재시도하는 eventual consistency가 현실적이다.

## 6. SOLID를 구조에 적용하는 방법

### 6.1 SRP: Single Responsibility Principle

변경 이유가 다른 코드를 분리한다.

- Agent factory: model, prompt, middleware, tool 구성 변경
- tool adapter: LLM 입력·출력을 application DTO로 변환
- application service: use case와 transaction 정책 변경
- repository adapter: 특정 DB SDK와 query 변경
- FastAPI router: HTTP contract 변경

tool 안에 SQL, 권한, retry, business validation을 함께 넣으면 SRP를 위반한다.

### 6.2 OCP: Open/Closed Principle

- 새 Agent는 registry에 descriptor를 추가하고 factory를 등록한다.
- 새 tool provider는 공통 catalog 계약을 구현한다.
- 새 DB provider는 기존 port를 구현하는 adapter로 추가한다.
- 기존 범용 Agent의 거대한 `if/elif`를 수정하는 방식은 피한다.

OCP는 무조건적인 plugin framework가 아니다. 실제 variation point인 Agent, tool provider, storage adapter에만 적용한다.

### 6.3 LSP: Liskov Substitution Principle

Repository와 provider adapter는 이름만 같은 것이 아니라 동일한 observable contract를 지켜야 한다.

- 반환 순서와 pagination 의미
- not-found와 timeout error 의미
- transaction과 idempotency 보장
- vector score와 filter semantics
- object overwrite·version 정책

이를 unit test만이 아니라 adapter contract test로 검증한다.

### 6.4 ISP: Interface Segregation Principle

다음과 같은 거대 인터페이스를 피한다.

```text
DatabaseService
  get_user()
  search_vector()
  upload_file()
  cache_result()
  save_checkpoint()
```

대신 use case가 필요한 작은 port를 둔다.

```text
ConversationReader
MemoryWriter
DocumentSearchPort
ArtifactStore
ReflectionJobRepository
```

### 6.5 DIP: Dependency Inversion Principle

```text
domain/application
  └── port protocol 정의

infrastructure
  └── PostgreSQL/Qdrant/MinIO/Redis adapter 구현

bootstrap
  └── concrete adapter를 생성해 주입
```

Agent, application service 또는 domain entity가 `qdrant_client`, `boto3`, `redis`, SQLAlchemy session 생성 코드를 직접 import하지 않게 한다.

## 7. 실제 오픈소스 프로젝트 비교

### 7.1 요약

| 프로젝트 | 패턴 | 참고할 점 | 현재 프로젝트에 그대로 적용하기 어려운 점 |
| --- | --- | --- | --- |
| Dify `1.17.0` | 모듈러 모놀리스 + 선택적 서비스 분리 | API/worker 코드 공유, tool provider, plugin/sandbox 경계 | 전역 수평 namespace와 높은 운영 복잡도 |
| OpenHands | SDK·tools·workspace·Agent Server·automation 분리 | 위험한 실행 환경과 automation 분리 | 작은 팀에는 저장소·버전 계약 비용이 큼 |
| Open SWE | FastAPI/webhook → dispatch → LangGraph graph → tools | Agent 중심 제품의 간결한 구조 | 일반 업무 영역이 늘면 service/domain 계층 부족 |
| CrewAI | Agent runtime 내부 package 분리 | engine 내부 책임 분리 참고 | 제품 backend 구조가 아님 |
| Microsoft Agent Framework | provider별 독립 Python package | optional dependency와 provider 확장 | package/version matrix 관리 비용 |

### 7.2 Dify

Dify API는 크게 `controllers`, `services`, `core`, `repositories`, `models`, `tasks`, `extensions/storage`로 나뉜다. 동기 API와 Celery worker가 같은 application code를 사용하고, agent backend, plugin daemon, sandbox는 필요에 따라 별도 프로세스로 둔다.

도구는 builtin, custom API, plugin, MCP, workflow-as-tool 등을 provider abstraction으로 관리한다. tool 수가 늘어날 때 Agent별 조건문보다 catalog·provider·credential 경계를 확장하는 점은 참고할 만하다.

장점:

- CRUD, workflow, RAG, Agent, plugin이 함께 성장하기 좋다.
- API와 worker가 코드를 재사용하면서 프로세스만 분리할 수 있다.
- 위험한 code/plugin 실행을 별도 서비스로 격리한다.

단점:

- 최상위 `services`, `core`, `models`가 거대한 전역 namespace가 되기 쉽다.
- 모듈별 독립 배포보다는 coordinated deployment에 가깝다.
- 작은 팀이 전체 인프라를 따라 하면 과도하다.

### 7.3 OpenHands

OpenHands는 현재 SDK, built-in tools, workspace, Agent Server, automation의 책임을 저장소·package·서비스 수준으로 분리한다. 특히 shell, browser, repository 작업을 수행하는 workspace와 Agent Server가 명시적 실행 경계다.

참고할 원칙:

- code/shell/browser 실행은 일반 API 프로세스에 무제한으로 넣지 않는다.
- tool registry와 allowlist가 실제 권한 경계다.
- 스케줄·webhook lifecycle과 Agent 실행 lifecycle을 분리할 수 있다.

현재 프로젝트에 처음부터 적용하면 저장소 간 버전·API 호환성 관리 비용이 크다. sandbox가 실제 요구가 될 때 분리하는 편이 적절하다.

### 7.4 Open SWE

Open SWE는 `api`, `webhooks`, `dispatch`, `graphs`, `tools`라는 짧은 경로를 사용하며 durable run과 persistence를 LangGraph runtime에 많이 위임한다.

Agent가 제품의 대부분인 경우에는 효율적이다. 그러나 business API와 여러 DB가 계속 추가될 현재 요구에서는 `graphs/`에 모든 규칙을 넣지 않고 domain/application 계층을 별도로 둬야 한다.

### 7.5 CrewAI와 Microsoft Agent Framework

두 프로젝트의 패키지 구조는 Agent runtime과 provider 확장 방법을 이해하는 데 유용하다. 하지만 tenant, 업무 transaction, FastAPI business API, RDB schema, background worker까지 포함한 제품 아키텍처는 아니다.

프레임워크 repository의 폴더를 제품 backend 구조로 그대로 사용하는 것은 피한다. framework 객체가 business entity가 되면 프레임워크 교체와 version update가 곧 domain migration이 된다.

## 8. 비교할 세 가지 아키텍처 접근

### 8.1 A안: 수평 계층형

```text
src/
  api/
  agents/
  graphs/
  tools/
  services/
  repositories/
  models/
  infrastructure/
```

장점:

- 시작이 쉽다.
- 소규모 PoC에서 파일 위치가 직관적이다.
- FastAPI의 기본적인 multi-file 예제와 유사하다.

단점:

- `tools/`, `services/`, `models/`가 전역 namespace로 커진다.
- 한 기능을 수정할 때 여러 최상위 폴더를 오가게 된다.
- 어떤 Agent와 어떤 service가 같은 업무 경계인지 드러나지 않는다.
- 거대한 `CommonService`, `ToolService`, `DatabaseService`가 생기기 쉽다.

평가: 초기 PoC에는 가능하지만 예상되는 기능 증가에는 부적합하다.

### 8.2 B안: 도메인 중심 모듈러 모놀리스

```text
src/
  bootstrap/

  interfaces/
    api/
    jobs/

  agent_platform/
    runtime/
    middleware/
    persistence/
    backends/
    tool_registry/
    observability/

  modules/
    conversation/
      domain/
      application/
      infrastructure/
      agent/
    knowledge/
      domain/
      application/
      infrastructure/
      agent/
    reflection/
      domain/
      application/
      infrastructure/
      agent/

  agents/
    general/
    registry.py
```

장점:

- 기능별 응집도가 높다.
- 범용 Agent와 업무별 Agent를 함께 지원한다.
- 프레임워크·DB 교체의 영향이 모듈 내부로 제한된다.
- 특정 모듈을 나중에 별도 서비스나 package로 추출하기 쉽다.
- SOLID를 import 방향과 contract test로 강제하기 좋다.

단점:

- 수평 구조보다 초기 파일 수가 많다.
- 업무 경계를 잘못 나누면 port와 DTO 중복이 생긴다.
- 팀이 각 모듈의 public API와 import rule을 지켜야 한다.

평가: 현재 조건의 권장 후보다.

### 8.3 C안: package monorepo와 독립 서비스

```text
apps/
  public_api/
  agent_gateway/
  reflection_worker/

packages/
  agent_core/
  conversation_domain/
  knowledge_domain/
  storage_postgres/
  storage_qdrant/
  storage_minio/
  tool_providers/
```

장점:

- 팀 소유권과 독립 배포 경계가 강하다.
- provider dependency 충돌을 package별로 격리하기 쉽다.
- Agent나 worker를 독립적으로 확장할 수 있다.

단점:

- package version과 compatibility matrix가 필요하다.
- 로컬 개발과 통합 테스트가 복잡하다.
- 현재 한 팀에는 release overhead가 크다.
- 아직 발견되지 않은 경계를 너무 일찍 고정할 수 있다.

평가: 장기 진화 방향으로는 가능하지만 시작 구조로는 과하다.

## 9. 권장 후보 구조의 책임

### 9.1 `interfaces/`

FastAPI router, request/response schema, 인증 dependency, streaming protocol, Airflow용 internal endpoint를 둔다. 업무 규칙을 두지 않는다.

### 9.2 `agent_platform/`

특정 업무에 속하지 않는 Agent 실행 기반을 둔다.

- model factory와 runtime context
- 공통 middleware와 permission
- checkpointer/store wiring
- Deep Agents backend와 sandbox adapter
- tool descriptor, catalog, allowlist
- tracing, metric, evaluation hook

`agent_platform`이 모든 업무를 아는 역방향 의존성을 만들면 안 된다. 업무 모듈이 제공한 Agent·tool descriptor를 bootstrap이 registry에 조립한다.

### 9.3 `modules/<domain>/domain/`

프레임워크에 독립적인 entity, value object, domain rule, domain error를 둔다. FastAPI, LangGraph, Deep Agents, SQLAlchemy, Qdrant SDK를 import하지 않는다.

### 9.4 `modules/<domain>/application/`

use case, command/query DTO, transaction boundary, port protocol을 둔다. Agent tool과 API가 공통으로 호출하는 계층이다.

### 9.5 `modules/<domain>/infrastructure/`

PostgreSQL repository, Qdrant index, MinIO artifact store, Redis cache, 외부 HTTP client 등 구체 adapter를 둔다.

### 9.6 `modules/<domain>/agent/`

업무별 Agent와 LangGraph adapter를 둔다.

- Deep Agent factory
- 직접 작성한 graph factory
- prompt
- tool adapter
- Agent-specific state/schema
- 업무 모듈이 외부에 제공할 Agent descriptor

tool은 application use case를 호출하는 얇은 adapter여야 한다.

### 9.7 `agents/general/`

범용 supervisor를 조립한다. 각 업무 모듈의 public descriptor만 알고 내부 repository나 DB adapter를 직접 import하지 않는다.

## 10. Tool 증가를 다루는 방법

### 10.1 Tool을 세 종류로 구분

| 종류 | 예 | 위치 후보 |
| --- | --- | --- |
| 업무 tool | 문서 검색, 메모리 승격, 대화 조회 | `modules/<domain>/agent/tools/` |
| platform tool | 파일 읽기, 공통 artifact 접근 | `agent_platform/tools/` |
| 외부 provider tool | MCP, 사내 API, SaaS integration | 업무 모듈 infrastructure 또는 별도 provider adapter |

### 10.2 Registry가 관리할 metadata

```text
name
description
owner domain
required scopes
risk level
timeout
idempotency classification
read/write classification
allowed agents
```

Agent가 Python package 전체를 scan해 임의 tool을 자동 등록하게 하지 않는다. bootstrap에서 명시적으로 구성하고, Agent별 최소 tool set을 제공한다.

### 10.3 Tool과 service의 경계

```python
# 개념 예시
@tool
async def search_documents(query: str, runtime: Runtime[AppContext]):
    return await runtime.context.search_documents.execute(query=query)
```

tool은 LLM schema와 runtime context 변환만 담당한다. 권한, filter 강제, transaction, retry, DB query는 application/infrastructure가 담당한다.

## 11. 범용 Agent와 업무별 Agent 공존 방식

### 11.1 권장 혼합형

각 업무별 Agent는 독립 factory와 명시적인 tool set을 가진다. 범용 Agent는 필요한 업무별 Agent를 subagent로 등록하거나, 단순 use case tool을 직접 사용한다.

```text
General Supervisor
  ├── conversation-agent
  ├── knowledge-agent
  ├── reflection-agent
  └── simple tools
```

업무 Agent가 자체 API, thread, 권한, SLA를 가져야 할 때는 같은 factory를 별도 compiled graph entrypoint로 노출한다.

### 11.2 피할 패턴

- 모든 tool을 범용 Agent에 등록한다.
- subagent가 부모의 전체 tool을 자동 상속한다.
- Agent별로 동일한 service logic을 복사한다.
- 업무 Agent가 다른 모듈의 infrastructure를 직접 호출한다.
- prompt로 권한을 통제하고 실제 tool/backend 권한은 열어둔다.

Deep Agents 공식 보안 원칙도 LLM의 자기 통제보다 tool과 sandbox 수준에서 경계를 강제하라고 설명한다.

## 12. Airflow, 성찰 작업, Celery 판단

### 12.1 현재 책임 경계

사용 중인 Airflow는 `3.1 + CeleryExecutor`다.

```text
Airflow
  └── schedule, DAG dependency, retry, operational visibility

Agent application
  └── reflection business state, execution, result, idempotency
```

Airflow의 CeleryExecutor는 Airflow task instance를 분산 실행한다. Agent 애플리케이션에 Celery queue를 추가하는 것과는 별개의 결정이다. CeleryExecutor를 사용한다는 이유만으로 Agent 서비스에 Celery를 추가할 필요는 없다.

### 12.2 단순한 동기 API 호출

```text
Airflow HttpOperator
  → POST /internal/reflections/run
  → HTTP connection을 유지하며 완료 대기
```

장점:

- 구현이 가장 작다.
- 별도 job table과 runner가 없다.

단점:

- proxy, load balancer, HTTP client timeout에 취약하다.
- 작업 동안 Airflow Celery worker slot을 점유한다.
- API pod 재시작 시 복구가 어렵다.
- 일반 API traffic과 장시간 compute가 자원을 경쟁한다.

작업 시간이 짧고 실패 시 처음부터 안전하게 재실행할 수 있을 때만 허용할 수 있다.

### 12.3 비동기 Job API + 소형 runner

```text
Airflow
  → POST /internal/v1/reflection-jobs
      ← 202 Accepted + job_id
  → GET /internal/v1/reflection-jobs/{job_id}
  → result_ref 확인

API process
  └── job 등록과 상태 조회

reflection runner
  └── PostgreSQL job claim → 실행 → heartbeat → result 저장
```

후보 API:

```text
POST   /internal/v1/reflection-jobs
GET    /internal/v1/reflection-jobs/{job_id}
POST   /internal/v1/reflection-jobs/{job_id}:cancel
GET    /internal/v1/reflection-jobs/{job_id}/result
```

필수 특성:

- `Idempotency-Key`를 PostgreSQL에 저장한다.
- 같은 key와 같은 payload는 기존 job을 반환한다.
- 같은 key와 다른 payload는 `409 Conflict`로 거절한다.
- runner는 lease와 heartbeat를 사용한다.
- stale job을 다시 claim하거나 reconciliation한다.
- 성찰 use case는 재실행에 안전하거나 checkpoint를 가진다.
- 대형 결과는 MinIO에 저장하고 DB에는 reference를 둔다.

이 runner는 별도 Celery가 아니라 동일 코드·동일 이미지의 다른 command일 수 있다. 현재처럼 하루 한 번이고 동시성이 낮다면 작은 DB-backed claim loop로 충분할 수 있다.

### 12.4 Airflow의 대기

논리적 DAG는 다음처럼 나눌 수 있다.

```text
submit_job → wait_status → consume_result
                    ↘ cleanup/cancel
```

Airflow 3.1에서 deferrable operator는 waiting 중 Airflow worker slot을 반환하고 Triggerer가 비동기 상태 감시를 담당한다. Triggerer는 성찰 compute를 실행하는 worker가 아니다.

조사 시점의 `apache-airflow-providers-http 6.0.5`는 `HttpOperator`와 `HttpSensor`의 deferrable 실행을 제공한다. 실제 적용 전 현재 환경의 provider 버전과 Triggerer HA 구성을 확인해야 한다. Trigger는 중복 실행 가능성을 전제하므로 상태 조회만 수행하고 side effect를 발생시키면 안 된다.

### 12.5 FastAPI `BackgroundTasks`

장시간·내구성이 필요한 성찰에는 사용하지 않는다. FastAPI 공식 문서도 `BackgroundTasks`를 같은 프로세스의 작은 후처리에 적합한 기능으로 설명하고, 무거운 계산과 다중 프로세스·서버 실행에는 Celery 같은 별도 도구를 고려하라고 안내한다.

### 12.6 Agent 서비스에 Celery를 도입할 조건

다음 중 여러 항목이 반복되면 도입을 검토한다.

- 성찰 외 background job이 계속 늘어난다.
- queue backlog와 높은 동시성이 생긴다.
- CPU/GPU/IO 유형별 queue routing과 priority가 필요하다.
- API와 worker의 독립 autoscaling이 필요하다.
- 직접 작성한 claim, lease, heartbeat, dead-job recovery가 커진다.
- broker redelivery와 표준 retry/backoff가 필요하다.

Celery도 exactly-once를 자동 보장하지 않으므로 task idempotency는 여전히 필요하다.

### 12.7 Temporal류를 검토할 조건

- 수시간~수일 대기 후 중단 지점에서 재개한다.
- 사용자 승인, signal, timer가 workflow 핵심이다.
- 여러 서비스에 대한 saga와 보상 작업이 필요하다.
- 진행 중 workflow의 코드 version 변경을 안전하게 관리해야 한다.
- 장기 실행 상태 자체가 제품의 핵심 기능이다.

## 13. 테스트와 관측성 방향

### 13.1 테스트 계층

```text
unit/
  domain/
  application/

contract/
  postgres/
  qdrant/
  minio/
  redis/
  external_api/

agent/
  tool_schema/
  tool_policy/
  graph_transition/
  prompt_evaluation/

integration/
  api/
  reflection_job/
  persistence/

architecture/
  import_boundaries/
```

### 13.2 핵심 검증

- domain/application이 FastAPI, LangGraph, DB SDK를 import하지 않는가
- tool이 repository를 건너뛰고 application use case를 호출하는가
- Agent별 허용 tool만 노출되는가
- graph retry가 외부 side effect를 중복 생성하지 않는가
- checkpointer state와 business transaction 실패가 구분되는가
- storage adapter가 port contract를 동일하게 지키는가
- job runner가 duplicate submission과 stale lease를 처리하는가

### 13.3 관측성 분리

- HTTP request trace
- Agent run과 graph node trace
- tool call trace
- application use case metric
- DB·외부 API adapter latency
- reflection job queue·lease·heartbeat metric

사용자 입력, memory 원문, prompt, tool output에 개인정보나 secret이 포함될 수 있으므로 trace와 log의 redaction 정책이 필요하다.

## 14. 잠정 판단과 미확정 사항

### 14.1 잠정 권고

상세 설계의 기준 후보는 B안인 **도메인 중심 모듈러 모놀리스**다.

- 단일 repository와 Python package를 유지한다.
- domain module별 `domain/application/infrastructure/agent` 경계를 둔다.
- 공통 Agent runtime은 `agent_platform`으로 분리한다.
- 범용 Agent는 업무별 Agent factory와 application tool을 조립한다.
- API와 장시간 runner는 같은 code/image를 사용할 수 있지만 process command는 분리한다.
- package·서비스 분리는 실제 독립 SLA, 자원, 보안, 팀 소유권이 생길 때 수행한다.

### 14.2 검토 후 결정해야 할 사항

1. 실제 업무 bounded context 목록
2. self-hosted LangGraph와 LangSmith Agent Server 중 배포 방식
3. LangGraph checkpointer와 store의 실제 backend
4. 성찰 작업의 최대 시간, 동시성, 재개 단위
5. 현재 `apache-airflow-providers-http` 버전과 Triggerer HA
6. tool credential과 permission model
7. shell/code 실행 및 sandbox 필요 여부
8. PostgreSQL과 vector/object update의 outbox 범위
9. Agent별 독립 API와 thread ownership 기준

## 15. 참고 자료

### 15.1 Deep Agents와 LangGraph 공식 자료

- [Deep Agents 공식 GitHub](https://github.com/langchain-ai/deepagents)
- [Deep Agents 0.7.11 release](https://github.com/langchain-ai/deepagents/releases/tag/deepagents%3D%3D0.7.11)
- [Deep Agents changelog](https://github.com/langchain-ai/deepagents/blob/main/libs/deepagents/CHANGELOG.md)
- [Deep Agents customization](https://docs.langchain.com/oss/python/deepagents/customization)
- [Deep Agents subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Deep Agents backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph application structure](https://docs.langchain.com/langsmith/application-structure)
- [LangGraph Agent Server](https://docs.langchain.com/langsmith/agent-server)
- [LangGraph monorepo support](https://docs.langchain.com/langsmith/monorepo-support)

### 15.2 FastAPI와 Airflow 공식 자료

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [FastAPI Server Workers](https://fastapi.tiangolo.com/deployment/server-workers/)
- [Airflow 3.1 Deferrable Operators](https://airflow.apache.org/docs/apache-airflow/3.1.6/authoring-and-scheduling/deferring.html)
- [HTTP provider 6.0.5 HttpOperator](https://airflow.apache.org/docs/apache-airflow-providers-http/stable/_api/airflow/providers/http/operators/http/index.html)
- [HTTP provider HttpSensor](https://airflow.apache.org/docs/apache-airflow-providers-http/stable/_api/airflow/providers/http/sensors/http/index.html)
- [Airflow supported deferrable operators](https://airflow.apache.org/docs/apache-airflow-providers/core-extensions/deferrable-operator-ref.html)

### 15.3 실제 프로젝트

- [Dify API source tree](https://github.com/langgenius/dify/tree/main/api)
- [Dify Docker Compose](https://github.com/langgenius/dify/blob/main/docker/docker-compose.yaml)
- [OpenHands repository boundaries](https://github.com/OpenHands/OpenHands#repository-boundaries)
- [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk)
- [OpenHands Automation](https://github.com/OpenHands/automation)
- [Open SWE agent source](https://github.com/langchain-ai/open-swe/tree/main/agent)
- [Open SWE installation](https://github.com/langchain-ai/open-swe/blob/main/docs/INSTALLATION.md)
- [CrewAI core package](https://github.com/crewAIInc/crewAI/tree/main/lib/crewai/src/crewai)
- [Microsoft Agent Framework Python packages](https://github.com/microsoft/agent-framework/tree/main/python/packages)

