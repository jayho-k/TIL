# Hindsight 심화 조사

조사일: 2026-07-11

## 공식 자료

- 공식 문서: https://hindsight.vectorize.io/
- Storage: https://hindsight.vectorize.io/developer/storage
- LangGraph / LangChain integration: https://hindsight.vectorize.io/sdks/integrations/langgraph
- GitHub: https://github.com/vectorize-io/hindsight
- Hermes integration: https://hindsight.vectorize.io/integrations/hermes
- Python client: https://pypi.org/project/hindsight-client/
- DeepAgents overview: https://docs.langchain.com/oss/python/deepagents/overview
- DeepAgents memory: https://docs.langchain.com/oss/python/deepagents/memory

## GitHub 지표

2026-07-11 GitHub page 기준:

- Stars: 18.2k
- Forks: 1.1k
- Commits: 2,062
- Issues: 63
- Pull requests: 56
- License: MIT

판단:

- Mem0보다는 작지만 Honcho보다 훨씬 큰 GitHub traction을 가진다.
- commit 수와 repo 구조를 보면 단순 SDK가 아니라 server, clients, CLI, docs, helm, docker, integrations를 포함한 꽤 큰 프로젝트다.
- MIT 라이선스라 self-host/상용 서비스 적용 부담이 낮다.

## Hindsight가 정확히 하는 역할

Hindsight는 agent memory system이다. 공식 문서는 Hindsight가 단순 conversation history recall이나 basic vector search가 아니라, agent가 시간이 지나며 "learn"하도록 만드는 memory system이라고 설명한다.

핵심 API:

- `retain`: 정보를 memory bank에 저장
- `recall`: memory 검색
- `reflect`: memory와 경험을 바탕으로 reasoning/synthesis

Hindsight가 담당하는 일:

- raw input에서 facts, temporal data, entities, relationships 추출
- world facts와 experience facts 저장
- observations로 consolidation
- semantic / keyword / graph / temporal multi-strategy retrieval
- reflect를 통한 memory-grounded reasoning
- mission/directives/disposition 기반 reasoning 성향 제어
- memory banks 기반 namespace
- LangGraph/LangChain tools/nodes/store integration
- cloud, Docker, Kubernetes, bare metal, embedded server 옵션 제공

Hindsight가 직접 담당하지 않는 일:

- procedural skill registry
- DeepAgents planning/subagent orchestration
- original object storage
- Qdrant 기반 vector store 재사용

따라서 Hindsight는 Chat Portal에서 "Postgres 기반 agent memory engine + reasoning/recall layer"로 보는 것이 정확하다.

## 핵심 메모리 타입

공식 Overview 기준 Hindsight는 knowledge를 다음 계층으로 조직한다.

| Type | 저장 내용 |
| --- | --- |
| Mental Model | common query를 위한 user-curated summary |
| Observation | raw facts에서 자동 consolidation된 지식 |
| World Fact | 외부 세계에 대한 객관 사실 |
| Experience Fact | agent 자신의 행동과 상호작용 경험 |

`reflect`는 Mental Models -> Observations -> Raw Facts 순서로 source를 확인한다.

중요한 점:

- raw memory만 쌓는 것이 아니라 observation을 만든다.
- observation은 deduplication, evidence tracking, proof count, freshness awareness를 가진다.
- 새로운 evidence가 기존 observation을 support/contradict/extend하면 overwrite가 아니라 history를 보존하며 refine한다.

## Retrieval 구조: TEMPR

Hindsight는 recall에서 네 가지 search strategy를 병렬로 사용한다고 설명한다.

| Strategy | 적합한 경우 |
| --- | --- |
| Semantic | 개념 유사성, paraphrase |
| Keyword / BM25 | 이름, 기술 용어, exact match |
| Graph | 관련 entity, indirect connection |
| Temporal | "last spring", "in June", time range |

이 점은 단순 vector DB 기반 memory보다 강하다. Chat Portal에서 "지난달에 이 고객이 말한 배포 규칙" 같은 temporal/entity query가 중요하다면 장점이다.

## 저장 모델

Storage 문서 기준:

- primary storage backend: PostgreSQL
- enterprise alternative: Oracle AI Database
- vector search: pgvector extension with HNSW indexes
- full-text search: PostgreSQL tsvector + GIN indexes
- relational data: native PostgreSQL
- JSON documents: JSONB with indexing
- graph queries: recursive CTEs

중요한 설계 결정:

- Hindsight는 generic storage abstraction을 제공하지 않는다.
- PostgreSQL 하나에 최적화하는 전략을 의도적으로 택했다.
- production은 PostgreSQL 15+와 pgvector 0.5.0+가 필요하다.
- local development에서는 pg0 embedded PostgreSQL을 사용하며 `~/.hindsight/pg0/`에 저장된다.
- `HINDSIGHT_API_DATABASE_URL`이 없으면 embedded PostgreSQL을 띄운다.

지원/검증된 managed PostgreSQL:

- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL
- Supabase
- Neon

## 무엇을 어디에 저장하는가

```text
PostgreSQL / pgvector
├─ memory banks
├─ raw retained memories
├─ world facts
├─ experience facts
├─ entities
├─ relationships
├─ temporal data
├─ observations
├─ mental models
├─ JSON documents / metadata
├─ full-text indexes
├─ vector indexes
└─ graph-like structures via recursive CTEs
```

Hindsight는 별도 Qdrant 같은 vector DB가 아니라 Postgres 내부 기능을 조합해 semantic memory system을 구성한다.

## Qdrant / Postgres / MinIO 결합성

### Postgres

결합성 매우 높음.

근거:

- Hindsight의 primary storage backend가 PostgreSQL이다.
- Postgres 하나에 relational, JSONB, full-text, pgvector, graph query를 모으는 것이 의도된 설계다.
- Docker external PostgreSQL, Kubernetes, bare metal, embedded server 옵션이 있다.

권장:

- 기존 Chat Portal Postgres와 같은 cluster를 쓰더라도 Hindsight 전용 DB 또는 schema를 분리한다.
- pgvector extension과 HNSW index 운영을 고려한다.
- memory write/read workload와 app OLTP workload를 분리한다.
- backup/restore는 Hindsight DB 단위로 설계한다.

### Qdrant

직접 결합성 낮음.

근거:

- Hindsight는 "No Storage Abstraction"을 명시한다.
- Qdrant를 backend로 쓰는 방향이 아니라 PostgreSQL/pgvector에 의도적으로 고정되어 있다.

판단:

- 기존 Qdrant를 memory backend로 재사용하고 싶은 경우 Hindsight는 맞지 않는다.
- 다만 Hindsight는 vector DB 이상의 기능을 Postgres 안에 구축하므로, 별도 memory DB로 둘 가치는 있다.
- Chat Portal의 기존 Qdrant는 document RAG용으로 유지하고, Hindsight는 memory-specific Postgres DB로 분리하는 것이 현실적이다.

### MinIO

직접 결합성 낮음.

Hindsight는 memory/fact/document metadata engine이지 object storage가 아니다. Documents API가 있지만 MinIO/S3-compatible storage를 raw object backend로 지정하는지까지는 확인되지 않았다.

권장:

- 원본 파일, transcript archive, artifact는 MinIO에 저장한다.
- Hindsight에는 extracted text, source metadata, MinIO object key, timestamp, tags를 retain한다.
- source evidence를 다시 보여줄 때 Chat Portal이 MinIO object를 조회한다.

## DeepAgents와 결합성

결합성은 3개 후보 중 가장 직접적일 수 있다. 이유는 Hindsight가 LangGraph/LangChain integration을 공식 문서로 제공하고, DeepAgents가 LangGraph 위에 구축된 agent runtime이기 때문이다.

공식 LangGraph/LangChain integration 패턴:

1. Memory Tools
   - `hindsight_retain`
   - `hindsight_recall`
   - `hindsight_reflect`
   - LangChain `@tool`, `bind_tools()`, LangGraph ToolNode와 호환

2. Graph Nodes
   - `create_recall_node`
   - `create_retain_node`
   - recall node가 LLM 호출 전 memory를 주입
   - retain node가 응답 후 human/AI messages를 저장

3. BaseStore Adapter
   - `HindsightStore`
   - LangGraph native memory pattern에 맞춘 store adapter
   - namespace tuple을 bank ID로 매핑

4. Dynamic Banks
   - `RunnableConfig`에서 user_id 등으로 bank_id 동적 결정

DeepAgents와 대응:

| DeepAgents 요소 | Hindsight 대응 | 판단 |
| --- | --- | --- |
| Long-term facts | World/Experience facts | 잘 맞음 |
| Session/task memory | bank + tags + metadata | 잘 맞음 |
| Startup memory injection | recall node or custom state `memory_context` | 잘 맞음 |
| Background consolidation | retain/reflect + observations | 강점 |
| LangGraph StoreBackend | HindsightStore | 직접적 |
| Skills/procedures | 별도 유지 필요 | Hindsight 역할 아님 |
| Sub-agent results | retain with tags/metadata | 가능 |
| Tool traces | retain with filtering | 가능하나 policy 필요 |

### 결합 방식 후보

#### A. DeepAgents tool로 붙이기

DeepAgent가 `hindsight_retain`, `hindsight_recall`, `hindsight_reflect` tools를 직접 호출한다.

장점:

- 구현이 빠르다.
- agent가 필요할 때 reflect까지 수행할 수 있다.
- LangChain tool 패턴과 잘 맞는다.

단점:

- agent가 search/retain 타이밍을 놓칠 수 있다.
- tool overuse와 bad retain을 제어해야 한다.

#### B. LangGraph recall/retain nodes로 자동화

DeepAgents graph 앞뒤에 recall/retain node를 둔다.

장점:

- LLM call 전 자동 memory injection
- response 후 자동 retain
- DeepAgents가 LangGraph 기반이라 구조적으로 잘 맞는다.

단점:

- DeepAgents 내부 graph 확장 포인트를 정확히 확인해야 한다.
- recall node가 SystemMessage를 append하는 ordering 문제가 있다. 공식 문서는 provider에 따라 system message가 첫 위치여야 하면 agent node에서 정렬/필터링하라고 설명한다.

#### C. HindsightStore를 LangGraph BaseStore로 사용

LangGraph store API를 Hindsight에 연결한다.

장점:

- LangGraph native memory pattern과 가장 가깝다.
- namespace tuple -> bank ID 매핑으로 user/project namespace를 표현하기 쉽다.

단점:

- 공식 문서상 `HindsightStore`는 async-only다.
- `get()`은 direct key lookup이 아니라 recall 기반이다.
- `delete`는 no-op이다.
- `list_namespaces`는 process-local tracking 한계가 있다.

따라서 StoreBackend로 완전한 KV store처럼 쓰면 안 된다.

#### D. Background consolidation target

Chat Portal session DB / DeepAgents event log를 source of truth로 두고, background worker가 Hindsight retain/reflect를 호출한다.

장점:

- user-facing latency 분리
- retain policy를 엄격히 적용 가능
- bad memory write를 줄일 수 있음

단점:

- 즉시 반영은 약함
- observation consolidation lag 모니터링 필요

추천:

- PoC는 A 또는 B가 빠르다.
- production은 B + D 조합이 좋아 보인다.
- Store adapter는 직접 쓰기 전에 limitations를 강하게 고려해야 한다.

## 장점

1. PostgreSQL 중심이라 기존 RDB 운영과 잘 맞는다.
   - pgvector, tsvector, JSONB, recursive CTE를 활용한다.

2. 라이선스가 MIT다.
   - Mem0와 마찬가지로 상용 적용 부담이 낮다.

3. LangGraph/LangChain integration이 매우 직접적이다.
   - tools, nodes, BaseStore adapter가 모두 있다.

4. Multi-strategy retrieval이 강하다.
   - semantic + keyword + graph + temporal

5. Observation consolidation이 있다.
   - dedup
   - evidence tracking
   - proof count
   - freshness awareness
   - contradiction/extension 처리

6. Reflect 기능이 있다.
   - 단순 recall이 아니라 memory-grounded reasoning/synthesis가 가능하다.

7. Deployment 옵션이 많다.
   - Cloud
   - Docker
   - Kubernetes
   - bare metal
   - Python embedded

8. Bank abstraction이 명확하다.
   - user/project/tenant/session 단위 namespace로 쓰기 쉽다.

## 단점 / 위험

1. Qdrant와 직접 맞지 않는다.
   - storage abstraction을 의도적으로 제공하지 않는다.
   - 기존 Qdrant를 memory backend로 쓰고 싶다면 부적합하다.

2. Postgres에 많은 역할이 집중된다.
   - vector, FTS, relational, JSON, graph-like query가 모두 Postgres에 들어간다.
   - 운영 튜닝이 중요하다.

3. Procedure memory는 별도 설계가 필요하다.
   - Hindsight는 skill registry가 아니다.
   - DeepAgents skills와 분리해야 한다.

4. Retain 품질과 비용이 중요하다.
   - retain이 LLM으로 facts/entities/time/relationships를 추출한다.
   - high-volume event ingestion에는 비용/latency/throughput 검증이 필요하다.

5. BaseStore adapter limitations가 있다.
   - async-only
   - direct key lookup 아님
   - delete no-op
   - namespace listing 제한

6. MinIO 직접 결합은 확인되지 않았다.
   - 원본 artifact는 별도 저장해야 한다.

7. Observations가 stale일 수 있다.
   - freshness awareness는 있지만, consolidation lag와 stale detection을 운영 지표로 봐야 한다.

## 추가 조사가 필요한 부분

1. Hindsight production DB 운영
   - pgvector HNSW index sizing
   - Postgres vacuum/autovacuum
   - FTS + vector + JSONB workload 분리
   - backup/restore

2. Chat Portal 기존 Postgres와의 배치
   - 같은 cluster vs 별도 cluster
   - schema 분리
   - connection pool
   - resource limit

3. DeepAgents integration 실험
   - tools pattern
   - recall/retain node pattern
   - HindsightStore pattern
   - DeepAgents 내부 graph와 충돌 여부

4. Bank namespace 설계
   - `tenant.{tenant_id}.user.{user_id}`
   - `workspace.{workspace_id}.project.{project_id}`
   - `agent.{agent_id}.session.{session_id}`

5. Retain filtering policy
   - human only vs AI messages 포함
   - sub-agent result 저장 여부
   - tool trace 저장 기준
   - tags/metadata schema

6. Memory defense / privacy
   - secret redaction
   - PII policy
   - prompt injection 내성
   - directive misuse 방지

7. MinIO provenance
   - object key를 metadata로 저장
   - source quote와 object range/page/chunk 연결
   - retrieval 결과에서 original artifact 표시

## Chat Portal 적용 판단

현재 3순위였지만, 심화 조사 후에는 **Mem0와 1~2위를 다툴 수 있는 후보**로 상향할 수 있다.

이유:

- MIT 라이선스
- PostgreSQL 기반
- LangGraph/LangChain integration이 직접적
- TEMPR retrieval이 Qdrant 단독보다 풍부함
- observation consolidation과 freshness awareness가 agent memory에 매우 적합함

다만 기존 Qdrant를 memory backend로 활용할 수 없다는 점이 큰 차이다.

선택 기준:

- "기존 Qdrant를 최대한 활용"이 우선이면 Mem0가 유리하다.
- "memory 전용 Postgres 기반 engine을 별도 운영"해도 된다면 Hindsight가 매우 강하다.
- "multi-agent peer modeling"이 중요하면 Honcho가 더 적합하다.

권장 구조:

```text
DeepAgents
├─ Skills/procedures = DeepAgents skills
├─ Working memory/files = DeepAgents filesystem
├─ Long-term facts/reasoned observations = Hindsight
├─ Session/task source of truth = Chat Portal Postgres
├─ Memory engine DB = Hindsight Postgres/pgvector
├─ RAG/document vectors = existing Qdrant
└─ Raw artifacts = MinIO
```

추천 PoC:

1. Hindsight를 external PostgreSQL로 self-host한다.
2. tenant/user/project 단위 bank naming을 정한다.
3. DeepAgents에 `hindsight_recall` / `hindsight_retain` tools를 붙인다.
4. 별도 실험으로 recall/retain nodes를 graph 전후에 배치한다.
5. 같은 scenario를 Mem0와 비교한다.
6. 측정 지표:
   - 다음 작업 default action 정확도
   - stale memory 비율
   - recall latency
   - DB resource usage
   - bad retain / over-retain 비율
   - DeepAgents workflow와의 충돌 여부

