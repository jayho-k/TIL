# Honcho 심화 조사

조사일: 2026-07-11

## 공식 자료

- GitHub: https://github.com/plastic-labs/honcho
- 공식 문서: https://honcho.dev/docs/v3/documentation/introduction/overview
- Architecture: https://honcho.dev/docs/v3/documentation/core-concepts/architecture
- SDK/API Reference: https://honcho.dev/docs
- Hermes integration: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/honcho
- DeepAgents overview: https://docs.langchain.com/oss/python/deepagents/overview
- DeepAgents memory: https://docs.langchain.com/oss/python/deepagents/memory

## GitHub 지표

2026-07-11 GitHub page 기준:

- Stars: 5.9k
- Forks: 706
- Commits: 576
- Issues: 77
- Pull requests: 84
- License: AGPL-3.0

판단:

- Mem0보다 star/activity 규모는 작지만, agent memory 전문 프로젝트로는 충분히 활발하다.
- 핵심 리스크는 AGPL-3.0이다. Chat Portal이 상용/폐쇄형 SaaS라면 법무 검토가 필요하다.
- self-host 가능한 FastAPI server이며 Python/TypeScript SDK를 제공한다.

## Honcho가 정확히 하는 역할

Honcho는 "stateful agent memory infrastructure"다. 단순히 vector search로 관련 chunk를 찾아주는 시스템이 아니라, peer 중심으로 메시지/이벤트를 저장하고 background reasoning을 통해 peer representation, conclusion, session context를 생성한다.

Honcho가 담당하는 일:

- conversation/event/document/tool trace 저장
- workspace/peer/session/message 모델링
- peer representation 생성
- conclusion 추출
- peer card 생성
- session summary/context 생성
- hybrid search
- natural-language insight query
- background reasoning / deriver worker
- MCP/agent tool integration

Honcho가 직접 담당하지 않는 일:

- DeepAgents planning/subagent orchestration
- procedural skill registry
- 기존 app object storage
- Qdrant 기반 외부 vector search를 그대로 재사용하는 것

따라서 Honcho는 Chat Portal에서 "user/project/agent state modeling + reasoning memory layer"로 보는 것이 정확하다.

## 핵심 데이터 모델

공식 README/Architecture 기준 primitive:

```text
Workspace
├─ Peers
│  ├─ Sessions
│  └─ internal collections keyed by (observer, observed)
└─ Sessions
   ├─ Peers
   └─ Messages
```

### Workspace

top-level container다. assistant, agent, AI feature, tenant, product environment를 분리할 수 있다.

Chat Portal 대응:

- tenant
- workspace
- environment
- application feature

### Peer

사람과 AI agent를 모두 나타내는 first-class entity다.

Chat Portal 대응:

- user
- assistant agent
- DeepAgents sub-agent
- team
- project
- organization

### Session

peers 사이의 interaction thread다. 단일 user-agent chat뿐 아니라 multi-peer interaction을 표현할 수 있다.

Chat Portal 대응:

- conversation
- agent task run
- project session
- support ticket

### Message

session에 속하는 atomic data unit이다. 대화, event, document chunk, tool trace를 저장할 수 있다.

Chat Portal 대응:

- chat message
- tool result
- uploaded document chunk
- task event
- sub-agent result

## 저장 모델

공식 self-host 문서 기준:

- API server: FastAPI
- DB: PostgreSQL with pgvector
- migrations: Alembic
- background worker: `src.deriver`
- queue system: Postgres table 기반으로 보임
- config section:
  - `[db]`
  - `[cache]`
  - `[llm]`
  - `[deriver]`
  - `[summary]`
  - `[dream]`
  - `[vector_store]`

GitHub README는 `[vector_store]` configuration에서 `pgvector`, `turbopuffer`, `lancedb`를 언급한다.

저장 흐름:

1. API로 messages가 생성된다.
2. Postgres에 synchronous write된다.
3. derivation task가 background queue에 enqueue된다.
4. deriver worker가 representation/summary/peer card/dreaming task를 처리한다.
5. 결과가 internal collections에 저장된다.
6. API는 context/search/chat/representation/conclusions로 결과를 반환한다.

## 무엇을 어디에 저장하는가

```text
Postgres
├─ workspaces
├─ peers
├─ sessions
├─ messages
├─ queue system
├─ summaries
├─ peer cards / representations metadata
└─ internal collections metadata

Vector store
└─ vector-embedded documents keyed by (observer, observed) peer pair

Background worker
└─ derives conclusions, summaries, representations
```

공식 README는 internal collections/documents가 직접 public API로 노출되지 않고, Conclusions API, representations, peer cards로 surface된다고 설명한다.

## Qdrant / Postgres / MinIO 결합성

### Postgres

결합성 매우 높음.

근거:

- self-host 문서가 PostgreSQL with pgvector를 필수 setup으로 설명한다.
- `DB_CONNECTION_URI`를 통해 Postgres 연결을 설정한다.
- migration으로 workspaces, peers, sessions, messages, queue tables를 생성한다.

권장:

- 기존 Chat Portal app DB와 같은 Postgres cluster를 쓰더라도 schema/database는 분리한다.
- Honcho migration이 독립적으로 schema를 관리하므로 app schema와 섞지 않는다.
- memory workload는 write-heavy + background worker + vector query가 있으므로 connection pool과 resource limit를 분리한다.

### Qdrant

직접 결합성은 낮거나 미확인이다.

근거:

- 공식 config가 `pgvector`, `turbopuffer`, `lancedb`를 언급한다.
- Qdrant backend는 확인되지 않았다.

대안:

- Honcho는 pgvector/lancedb/turbopuffer 중 하나로 운영하고, Chat Portal 기존 Qdrant는 RAG/document retrieval에 유지한다.
- Qdrant를 반드시 통합하려면 Honcho의 vector_store abstraction에 Qdrant adapter를 구현할 수 있는지 코드 분석이 필요하다.

판단:

- Qdrant를 이미 쓰는 점은 Honcho 도입의 약점이다.
- 하지만 Honcho는 "vector DB wrapper"가 아니라 peer reasoning system이므로, 별도 vector backend를 허용할 가치가 있을 수 있다.

### MinIO

직접 결합성은 미확인이다.

공식 README에는 `session.upload_file(...)`가 있지만, 파일 storage backend를 MinIO/S3-compatible로 지정할 수 있는지는 확인되지 않았다.

권장:

- 원본 파일은 MinIO에 저장한다.
- Honcho에는 extracted text/document chunk, MinIO object key, source metadata를 message로 저장한다.
- file upload를 Honcho에 직접 맡기기보다 Chat Portal ingestion pipeline에서 text를 추출해 Honcho에 넣는 구조가 안전하다.

## DeepAgents와 결합성

결합성은 개념적으로 매우 좋다. 특히 DeepAgents가 sub-agent, tool execution, long-running task를 다루는 경우 Honcho의 peer model과 잘 맞는다.

DeepAgents 공식 memory 구조:

- memory file / AGENTS.md style prompt memory
- filesystem-backed state
- StoreBackend / FilesystemBackend / CompositeBackend
- skills as procedural memory
- episodic memory via checkpoints/thread search
- background consolidation agent

Honcho와 대응:

| DeepAgents 요소 | Honcho 대응 | 판단 |
| --- | --- | --- |
| User | Peer | 잘 맞음 |
| Main agent | Peer | 잘 맞음 |
| Sub-agent | Peer | 매우 잘 맞음 |
| Thread/conversation | Session | 잘 맞음 |
| Tool trace/event | Message | 잘 맞음 |
| Long-term user model | Representation / Peer Card | 강점 |
| Session summary/context | Session context endpoint | 강점 |
| Skill/procedure | 별도 유지 필요 | Honcho 역할 아님 |
| Filesystem memory | 직접 대체 아님 | bridge 필요 |

### 결합 방식 후보

#### A. DeepAgent run을 Honcho session으로 mirror

각 DeepAgent run 또는 chat thread를 Honcho session으로 만들고, user/main agent/sub-agent를 peers로 등록한다.

저장:

- user message -> user peer message
- assistant response -> agent peer message
- subagent result -> subagent peer message
- important tool trace -> message metadata

장점:

- Honcho의 peer-centric model을 가장 잘 활용한다.
- sub-agent별 관찰/representation이 가능하다.
- long-running project context에 강하다.

단점:

- 모든 tool trace를 넣으면 noisy하다.
- 어떤 event를 message로 승격할지 policy가 필요하다.

#### B. Startup context로 Honcho session.context를 주입

DeepAgent 시작 전 Honcho에서 session/user/project context를 가져와 memory file 또는 prompt block으로 materialize한다.

장점:

- DeepAgents의 filesystem-backed memory 철학과 잘 맞는다.
- prompt-ready context를 Honcho가 직접 제공한다.

단점:

- background reasoning이 늦으면 최신 정보가 반영되지 않을 수 있다.
- stale representation이 강하게 작용할 수 있다.

#### C. Honcho를 background consolidation target으로 사용

Chat Portal session DB와 DeepAgent event log를 source of truth로 두고, background worker가 Honcho에 선별 ingest한다.

장점:

- user-facing latency를 낮춘다.
- ingestion policy를 세밀하게 조정할 수 있다.
- MinIO/Postgres/Qdrant 기존 구조와 충돌을 줄인다.

단점:

- 즉시 memory 반영은 약하다.
- retry/idempotency/ordering 관리가 필요하다.

추천:

- production은 A + C 조합이 좋아 보인다.
- startup context는 B를 제한적으로 사용한다.
- Honcho를 "모든 원본 로그의 primary store"로 두기보다, Chat Portal Postgres event log에서 선별 동기화하는 구조가 안전하다.

## 장점

1. data model이 Chat Portal과 잘 맞는다.
   - workspace/peer/session/message는 multi-user/multi-agent product에 자연스럽다.

2. DeepAgents sub-agent 모델과 잘 맞는다.
   - sub-agent를 peer로 표현할 수 있다.
   - agent 간 관찰/이해를 모델링할 수 있다.

3. Postgres 기반 self-host가 명확하다.
   - 기존 인프라와 운영 방식이 맞는다.

4. 단순 retrieval보다 reasoning memory에 가깝다.
   - conclusions
   - representations
   - peer cards
   - session context

5. prompt-ready context를 제공한다.
   - `.to_openai()`
   - `.to_anthropic()`

6. background worker 구조가 명확하다.
   - expensive reasoning을 async로 분리한다.

7. MCP/agent integrations가 있다.
   - Claude Code, OpenCode, OpenClaw, Hermes 등

## 단점 / 위험

1. AGPL-3.0 라이선스
   - 상용 SaaS에 직접 self-host하면 license obligation 검토가 필요하다.
   - managed API 사용과 self-host 사용의 법적/운영 차이를 확인해야 한다.

2. Qdrant와 직접 맞지 않는다.
   - 기본/공식 vector store는 pgvector/turbopuffer/lancedb 계열이다.
   - 기존 Qdrant와 memory vector를 통합하려면 adapter 개발이 필요할 수 있다.

3. background reasoning은 async다.
   - 새 메시지가 즉시 representation/chat response에 반영되지 않을 수 있다.
   - low-latency path와 eventual memory path를 분리해야 한다.

4. LLM 비용과 latency가 있다.
   - deriver, summary, dialectic, dream 등 다양한 LLM config가 있다.

5. 모든 데이터를 Honcho에 넣으면 noisy하다.
   - DeepAgents tool trace/subagent output을 선별하지 않으면 representation 품질이 떨어질 수 있다.

6. object storage integration은 불명확하다.
   - MinIO를 직접 backend로 쓰는 구조는 확인되지 않았다.

7. 운영 컴포넌트가 늘어난다.
   - API server
   - Postgres
   - vector store
   - deriver worker
   - optional cache/telemetry/monitoring

## 추가 조사가 필요한 부분

1. vector_store abstraction
   - Qdrant adapter 구현 난이도
   - pgvector/lancedb/turbopuffer 중 어느 것이 production에 적합한지

2. schema/migration
   - 기존 Postgres와 schema 격리 방법
   - multi-tenant workspace isolation
   - backup/restore 전략

3. license 검토
   - AGPL-3.0 self-host가 Chat Portal 배포 모델에 미치는 영향
   - managed API 사용 시 license/데이터 정책

4. event ingestion policy
   - 어떤 DeepAgent event를 Honcho message로 저장할지
   - tool trace를 metadata로만 저장할지 message로 저장할지
   - subagent output filtering

5. MinIO 연계
   - `session.upload_file` storage backend 확인
   - 원본 파일은 MinIO, extracted text는 Honcho message로 둘 때 provenance 연결 방식

6. consistency and latency
   - deriver queue lag 모니터링
   - context injection 시 최신성 보장
   - representation endpoint와 chat endpoint 사용 기준

7. privacy/security
   - peer별 data isolation
   - workspace-scoped tokens
   - PII/secret redaction before message ingest

## Chat Portal 적용 판단

현재 2순위 유지.

이유:

- Chat Portal이 multi-user/multi-agent product라면 Honcho의 peer/session/message model이 매우 잘 맞는다.
- DeepAgents의 sub-agent를 peer로 모델링할 수 있다는 점은 Mem0보다 강한 차별점이다.
- Postgres 기반 self-host가 명확해서 기존 RDB 운영 경험과 맞는다.
- 단순 fact memory가 아니라 reasoning-derived representation을 제공한다.

하지만 다음 이유로 Mem0보다 우선순위는 낮다.

- AGPL-3.0 리스크
- Qdrant 직접 결합성 부족
- 운영 컴포넌트와 LLM background worker 복잡도
- memory fact API보다 peer reasoning platform 성격이 강함

권장 구조:

```text
DeepAgents
├─ user/main-agent/sub-agent = Honcho peers
├─ conversation/task run = Honcho session
├─ selected messages/tool traces = Honcho messages
├─ prompt-ready long context = Honcho session.context
├─ stable user/project understanding = Honcho representation / peer card
├─ skills/procedures = DeepAgents skills, not Honcho
├─ raw artifacts = MinIO
├─ app source of truth = Chat Portal Postgres
└─ RAG vectors = existing Qdrant
```

추천 PoC:

1. Chat Portal의 user, main agent, one sub-agent를 Honcho peer로 만든다.
2. 하나의 DeepAgent task run을 Honcho session으로 mirror한다.
3. 중요한 user/assistant/sub-agent messages만 저장한다.
4. deriver 처리 후 `session.context`와 `peer.representation`을 다음 run startup context로 넣는다.
5. 기존 Mem0 방식과 비교해 다음 행동 정확도, latency, 운영 복잡도를 측정한다.

