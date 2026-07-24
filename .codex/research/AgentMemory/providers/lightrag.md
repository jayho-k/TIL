# LightRAG Deep Dive: Chat Portal RAG 성능 개선과 조합 판단
작성일: 2026-07-12

## 0. 이 문서가 답할 질문

Chat Portal에는 이미 업로드 문서 대화, 일반 대화, 회의록 생성, 사내 지식 RAG가 구현되어 있고 Qdrant, PostgreSQL, MinIO, Redis를 운영한다.

이 문서의 목적은 새 upload/RAG 제품을 추가하는 것이 아니다.

> **기존 기능과 저장소를 유지한 채 LightRAG가 retrieval 품질과 context efficiency를 개선하는지, 그리고 Mem0/OpenViking과의 단독 또는 조합이 정당한지 판단한다.**

조사 범위는 다음과 같다.

1. LightRAG의 실제 저장 구조와 기본 로컬 저장 경로
2. Qdrant, PostgreSQL, MinIO, Redis와의 구현상 결합성
3. 문서 업로드, 갱신, 삭제, 멀티테넌시의 제약
4. LightRAG 단독, LightRAG + Mem0, LightRAG + OpenViking의 역할 중복
5. 성능 개선을 입증할 PoC와 중단 기준

## 1. 핵심 결론

### 1.1 LightRAG는 Agent Memory provider가 아니라 graph RAG engine이다

LightRAG는 문서에서 entity/relation을 추출하고 graph와 vector index를 함께 질의하는 knowledge-graph RAG framework다. `local`, `global`, `hybrid`, `naive`, `mix` query mode를 제공하며, `mix`는 graph local/global 결과와 text chunk vector retrieval을 결합한다.

```text
문서
  -> chunking
  -> LLM entity/relation extraction
  -> graph node/edge merge
  -> entity / relation / chunk vector index
  -> local/global/naive/mix retrieval
```

따라서 LightRAG는 다음 병목에만 직접적인 후보다.

- 긴 문서 또는 여러 문서를 걸친 질의
- entity 관계, 의존성, 원인/영향, 다단계 연결을 찾아야 하는 질의
- flat top-k chunk가 상위 관계를 놓치거나 prompt에 너무 많은 chunk를 넣는 문제
- 사내 지식 문서의 cross-document reasoning

반면 LightRAG만으로는 user preference, 반복 정정, project convention 같은 durable agent memory를 해결하지 않는다. 개인 대화 사실을 organization graph에 넣으면 지식과 memory lifecycle이 섞인다.

### 1.2 기본 LightRAG Server/upload pipeline은 Chat Portal의 저장 원칙에 맞지 않는다

LightRAG의 기본 storage는 다음과 같다.

| 역할 | 기본 backend | 기본 위치 |
| --- | --- | --- |
| KV: full document, chunk, entity/relation metadata, LLM cache | `JsonKVStorage` | `working_dir`의 JSON/file |
| Vector | `NanoVectorDBStorage` | `working_dir`의 local data |
| Graph | `NetworkXStorage` | `working_dir`의 local data |
| Document status | `JsonDocStatusStorage` | `working_dir`의 JSON/file |

Built-in file processing pipeline은 업로드 원본을 `__parsed__`에 archive하고, MinerU/Docling parsing 결과, 이미지, layout, manifest를 working directory 하위에 보관한다. 공식 문서의 S3/MinIO content-store backend는 확인하지 못했고, remote S3/OSS image storage는 열린 feature request다. [LightRAG issue #3315](https://github.com/HKUDS/LightRAG/issues/3315)

따라서 다음 방식은 채택하면 안 된다.

```text
Browser -> LightRAG /documents/upload
        -> LightRAG local working_dir를 문서 원본/parse artifact의 영구 저장소로 사용
```

이는 MinIO 원본 보관, PostgreSQL 문서 lifecycle/ACL이라는 현재 Chat Portal 경계를 무너뜨리고, 로컬 persistent data 금지 요구와도 충돌한다.

### 1.3 가능한 경로는 "기존 ingestion + LightRAG Core index"다

```text
Chat Portal upload / existing knowledge ingestion
  -> MinIO: 원본, parse artifact, evidence
  -> PostgreSQL: document/version/ACL/status/citation mapping
  -> existing parser: text / section / page data
  -> LightRAG Core: 선택된 text를 graph + vector index로 생성
  -> Chat Portal retrieval gateway: 현재 RAG와 LightRAG를 A/B 비교
```

LightRAG는 원본 upload service가 아니라 **derived graph retrieval engine**으로 제한한다. 이 경로도 PostgreSQL+Apache AGE graph backend, Qdrant workspace, 삭제/reindex, tenant authorization을 검증해야 한다.

### 1.4 현재의 기본 추천은 조합이 아니라 단독 검증이다

1. 현재 RAG에 cross-document/long-document/context-bloat 문제가 실제로 있는지 baseline으로 확인한다.
2. 문제가 확인되면 **LightRAG 단독 shadow PoC**를 한다. Mem0나 OpenViking을 같은 request path에 넣지 않는다.
3. LightRAG가 RAG quality/context efficiency를 개선한 뒤에도 user/project durable fact 누락이 별도 병목이면 **Mem0를 별도 PoC**한다.
4. OpenViking은 Resource/Session/Memory/Skill context plane을 함께 소유하므로 LightRAG와 초기에 결합하지 않는다. 두 제품의 document retrieval 책임이 크게 겹친다.

`LightRAG + Mem0`는 조건부로 유효한 최종 조합이지만, 자동 시너지나 첫 도입 구조는 아니다. `LightRAG + OpenViking`은 현재 Chat Portal에 중복 data plane과 운영 복잡도를 먼저 만든다.

## 2. 출처와 버전

| 구분 | 확인 결과 | 신뢰도 |
| --- | --- | --- |
| 공식 GitHub | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | 1차 소스 |
| 공식 논문 | [LightRAG: Simple and Fast Retrieval-Augmented Generation](https://arxiv.org/abs/2410.05779) | 1차 연구 소스 |
| 공식 Core 문서 | [Programming with LightRAG Core](https://github.com/HKUDS/LightRAG/blob/main/docs/ProgramingWithCore.md) | 1차 소스 |
| 공식 파일 처리 문서 | [File Processing Pipeline](https://github.com/HKUDS/LightRAG/blob/main/docs/FileProcessingPipeline.md) | 1차 소스 |
| 조사 소스 commit | `44db36fe080645ba97ded719d44b42c7dee1f54a`, 2026-07-11 | 1차 소스 |
| 소스 version | `1.5.5` | 1차 소스 |
| GitHub stars | 약 37.6k, forks 약 5.3k, 2026-07-12 확인 | 보조 지표 |
| 라이선스 | MIT | 1차 소스 |

GitHub 이슈는 재현되지 않은 사용자 보고도 포함한다. 본문에서는 확정 결함이 아니라 **Chat Portal PoC에서 재현해야 할 위험 신호**로 사용한다.

## 3. LightRAG의 실제 구조

### 3.1 graph와 vector를 모두 가진 네 저장소 모델

LightRAG는 graph database 하나만 쓰는 제품이 아니다. LightRAG instance는 적어도 다음 네 계층을 동시에 사용한다.

```text
Full document / text chunks / extracted metadata / LLM cache
  -> KV storage

Entity vectors / relationship vectors / chunk vectors
  -> Vector storage

Entity nodes + relationship edges
  -> Graph storage

Document processing state
  -> Document-status storage
```

현재 초기화 코드는 full documents, text chunks, full entities/relations index, entity-to-chunk/relation-to-chunk index, graph, entity/relation/chunk vectors, document status, LLM response cache를 서로 다른 namespace로 만든다.

따라서 기존 Qdrant에 graph collection 하나를 추가하면 된다는 이해는 틀리다. LightRAG를 운영하면 source text copy, chunk metadata, graph, vector, processing state의 lifecycle을 함께 운영한다.

### 3.2 query mode와 성능 trade-off

| Mode | retrieval 대상 | 적합한 질문 | 성능 의미 |
| --- | --- | --- | --- |
| `naive` | text chunk vector | 특정 문장/절차/조항 | 현재 vector RAG와 가장 가까운 baseline |
| `local` | 특정 entity와 직접 관계 | 특정 시스템/조직/계약 | entity precision에 의존 |
| `global` | 관계 chain과 넓은 주제 | cross-document 요약, 영향 분석 | graph relationship 품질에 의존 |
| `hybrid` | local + global | 구체성과 큰 맥락을 함께 요구 | 후보가 증가 |
| `mix` | local + global + naive chunk | 일반 질의 | token/latency/cost가 가장 커질 수 있음 |

공식 README는 기본 mode를 `mix`로 소개하며, `mix`가 `naive`보다 약간 더 오래 걸린다고 설명한다. reranker는 retrieval 품질을 올릴 수 있지만 일반적으로 1~2초 지연을 추가한다고 명시한다. 성능 평가는 graph recall만 볼 수 없고 rerank를 포함한 end-to-end p95와 retrieved token을 함께 봐야 한다.

### 3.3 graph lifecycle은 문서 lifecycle보다 복잡하다

문서 하나를 넣으면 entity와 relation은 다른 문서의 같은 node/edge와 merge된다. 문서 하나를 삭제할 때 단순히 해당 문서의 vector point를 지우는 것으로 끝나지 않는다.

`adelete_by_doc_id()`는 full doc, chunks, graph elements, related indexes를 지우고 영향을 받은 entity/relation을 남은 문서의 LLM cache로 rebuild하려 한다. 코드 주석도 pipeline idle 또는 batch deletion 중에만 삭제하도록 동시성을 제한한다.

이 모델의 이점은 incremental graph update지만, Chat Portal에는 다음 비용이 생긴다.

- document update/delete가 즉시 O(1) vector delete가 아닐 수 있다.
- reprocess/resume가 graph merge와 LLM cache에 영향을 준다.
- ACL/retention 삭제는 LightRAG cleanup보다 먼저 PostgreSQL에서 retrieval을 차단해야 한다.
- graph merge 품질이 나쁘면 오래된 설명, duplicate entity/relation, wrong provenance가 검색에 남을 수 있다.

## 4. Chat Portal 인프라와의 실제 결합성

### 4.1 Qdrant: 지원됨, 그러나 기존 RAG collection 재사용은 권장하지 않음

LightRAG는 `QdrantVectorDBStorage`를 공식 지원한다. vector store에는 적어도 entity, relation, chunk의 서로 다른 namespace/collection이 필요하다. Qdrant adapter는 `workspace_id` payload로 workspace partition을 구현한다.

```text
Qdrant
  chat_portal_rag                  # 현재 production RAG, 그대로 유지
  lightrag_chunks_*                # LightRAG chunk vectors
  lightrag_entities_*              # LightRAG entity vectors
  lightrag_relationships_*         # LightRAG relation vectors
  chat_portal_mem0                 # Mem0를 별도로 쓸 때만
  chat_portal_mem0_entities        # Mem0 entity sidecar
```

collection exact name은 embedding model suffix와 LightRAG version/config에 따라 달라질 수 있으므로 PoC에서 명시적으로 확인한다. `chat_portal_rag`에 LightRAG payload를 혼합하면 LightRAG의 namespace/schema/delete lifecycle과 현재 RAG lifecycle이 충돌한다.

### 4.2 PostgreSQL: 가능하지만 graph를 위해 Apache AGE가 필요하다

LightRAG가 PostgreSQL을 사용할 수 있다는 말은 역할별로 나눠서 이해해야 한다.

| LightRAG 역할 | PostgreSQL backend | Chat Portal 현재 PostgreSQL만으로 가능한가 |
| --- | --- | --- |
| full docs/chunks/KV/LLM cache | `PGKVStorage` | 가능 |
| document processing status | `PGDocStatusStorage` | 가능 |
| vectors | `PGVectorStorage` | 가능하지만 Chat Portal은 Qdrant를 쓰므로 보통 선택하지 않음 |
| graph node/edge | `PGGraphStorage` | **Apache AGE plugin 필요** |

Qdrant + PostgreSQL 조합의 현실적인 설정은 다음과 같다.

```text
kv_storage         = PGKVStorage
doc_status_storage = PGDocStatusStorage
vector_storage     = QdrantVectorDBStorage
graph_storage      = PGGraphStorage    # PostgreSQL + Apache AGE
```

현재 PostgreSQL에 AGE가 없거나 운영 표준상 extension 도입이 불가하다면, LightRAG graph를 위해 Neo4j/Memgraph/OpenSearch 같은 새 graph backend를 추가해야 한다. 이는 기존 인프라 재사용이라는 장점을 크게 잃는 하드 게이트다.

PostgreSQL의 LightRAG table은 Portal business table과 분리한 schema/database 또는 최소한 별도 ownership/migration으로 관리해야 한다. LightRAG의 full document/chunk/LLM cache는 MinIO 원문을 대체하는 권위 데이터가 아니라 graph retrieval을 위한 파생 copy다.

### 4.3 MinIO: 원문은 유지할 수 있지만 LightRAG native object-store는 확인되지 않았다

LightRAG 공식 배포 문서에 나타나는 MinIO 설정은 bundled local Milvus 관련 구성이다. LightRAG 문서 원본/parse artifact를 S3/MinIO에 보관하는 AGFS 같은 native backend는 확인되지 않았다.

따라서 Chat Portal의 원칙은 다음이어야 한다.

```text
MinIO
  - authoritative original file
  - original transcript/attachment
  - existing parser output / page and section evidence
  - optional immutable parse artifact

LightRAG PGKV/Qdrant/AGE
  - derived text/chunk/graph/vector data
  - MinIO URI + document_id + version reference
```

LightRAG built-in `/documents/upload`, `scan`, MinerU/Docling artifact cache는 쓰지 않는 것이 안전하다. 기존 parser 결과를 Core API로 입력할 때도 `ainsert_custom_chunks` path의 graph merge 동작을 target version에서 반드시 검증해야 한다. 현재 해당 path의 KG merge에 관한 열린 버그 보고가 있다. [#3352](https://github.com/HKUDS/LightRAG/issues/3352)

### 4.4 Redis: durable document store가 아니라 coordination/cache 후보

LightRAG는 `RedisKVStorage`를 제공하지만 KV에는 full docs/chunks/LLM cache 같은 durable data가 들어간다. Chat Portal이 Redis를 transient 운영 store로 보는 한, `RedisKVStorage`를 primary LightRAG KV backend로 선택하면 안 된다.

Redis는 다음 Portal-level 용도에 한정한다.

- graph indexing task idempotency key
- per-document/per-workspace ingestion lock
- request-local retrieval result cache
- rate limiting, job progress cache
- circuit breaker/fallback state

LightRAG pipeline 자체의 durable state는 PGKV/PGDocStatus/PGGraph과 PostgreSQL outbox가 맡아야 한다.

### 4.5 workspace는 저장소 격리 기능이지 Chat Portal authorization이 아니다

LightRAG는 workspace를 각 storage backend에 전달한다. Qdrant에서는 payload partition, PGKV/PGDocStatus에서는 `workspace` field, PGGraph에서는 workspace-aware graph namespace가 사용된다.

그러나 이 기능만으로 multi-tenant authorization이 끝나지 않는다.

- workspace 문자열을 client request header/body에서 신뢰하면 안 된다.
- Portal backend가 authenticated tenant/workspace에서 workspace를 계산해야 한다.
- LightRAG API를 browser에 직접 노출하지 않는다.
- document ACL은 workspace보다 더 세밀할 수 있으므로 PostgreSQL ACL filter가 추가로 필요하다.

특히 [#2904](https://github.com/HKUDS/LightRAG/issues/2904)는 server `/query`가 `LIGHTRAG-WORKSPACE` header를 무시하고 default workspace context를 조립해 cross-workspace context를 섞을 수 있다는 보고다. 보고된 환경은 v1.4.13이지만 2026-07-12에도 open 상태이므로, target 1.5.5에서 재현 여부와 workspace routing을 가장 먼저 검증해야 한다.

## 5. 기존 기능별 적합성

### 5.1 업로드 문서 대화

LightRAG가 가장 유효할 수 있는 영역이다. 단, 업로드 문서를 LightRAG에 맡긴다는 뜻이 아니라 기존 upload source of truth를 유지한 뒤 LightRAG graph index를 추가하는 의미다.

#### 개선 가설

- 긴 매뉴얼/계약서/보고서에서 chunk 단위만으로 놓치던 entity relation을 찾는다.
- 두 개 이상의 업로드 문서에서 원인-영향, 의존성, 비교 관계를 더 잘 회수한다.
- 모든 top-k chunk를 prompt에 넣는 대신 graph candidate와 필요한 chunk만 넣어 token을 줄인다.

#### 실패 가능성

- 한 문서의 특정 조항/page를 찾는 질문은 기존 vector RAG가 더 빠르고 충분할 수 있다.
- entity extraction 품질이 낮으면 graph가 noise를 키운다.
- upload 직후 graph extraction은 LLM 비용/시간을 추가한다.
- document update/reprocess가 잦으면 graph merge/delete 비용이 커진다.

**판정:** existing document chat failure set에 multi-hop/cross-document 문제가 있을 때만 LightRAG PoC 가치가 있다. 그렇지 않다면 chunking, metadata filter, reranker, citation mapping 개선이 먼저다.

### 5.2 사내 지식 RAG

LightRAG의 가장 강한 후보 영역이다. 여러 부서/프로젝트/정책 문서에 entity/relationship가 반복되며, "A 정책이 B 시스템과 C 조직에 어떤 영향을 주는가" 같은 질문이 실제로 있다면 graph retrieval을 평가할 이유가 있다.

그러나 graph는 조직 지식의 authority가 아니다. 정책 원문과 version/ACL은 MinIO/PostgreSQL가 authority이고, LightRAG graph는 파생 retrieval index다.

### 5.3 일반 대화

LightRAG를 일반 대화의 long-term memory로 쓰면 안 된다.

- 개인 대화 사실을 조직 graph에 합치면 privacy/retention/lifecycle이 달라진다.
- 일반 대화의 preference recall은 graph traversal보다 small fact retrieval이 더 싸고 예측 가능하다.
- DeepAgents의 thread state/working files와 LightRAG graph는 목적이 다르다.

일반 대화에서 LightRAG를 호출하는 경우는 사용자가 사내 knowledge 또는 업로드 문서를 질문할 때뿐이다.

### 5.4 회의록 생성

회의록 생성 자체의 source of truth는 기존 MinIO transcript + PostgreSQL meeting/action state여야 한다. LightRAG는 승인된 회의록/결정문을 사내 지식으로 publish한 뒤, 이후 회의에서 cross-meeting relation을 찾는 용도라면 후보가 된다.

```text
"A 프로젝트의 지난 세 회의에서 배포 지연 원인과 결정 사항을 요약해줘"
  -> meeting documents를 대상으로 LightRAG graph retrieval
  -> MinIO transcript/page/timestamp evidence를 citation으로 확인
```

담당자, 마감일, action item status는 PostgreSQL current-state를 직접 질의해야 한다. LightRAG graph 또는 Mem0 fact가 업무 상태 authority가 되어서는 안 된다.

## 6. LightRAG 단독, Mem0 조합, OpenViking 조합

### 6.1 선택지 A: LightRAG 단독

#### 맡기는 역할

- 사내 지식/업로드 문서의 graph + vector retrieval
- cross-document, relationship, global/local context 질의
- 기존 RAG의 shadow 또는 replacement candidate

#### 장점

- MIT 라이선스다.
- Qdrant와 PostgreSQL backend를 공식 지원한다.
- graph RAG 성능 가설을 가장 깨끗하게 검증할 수 있다.
- Mem0/OpenViking와 retrieval 결과를 합치는 ranking 문제를 만들지 않는다.

#### 한계

- user/project durable fact memory를 해결하지 않는다.
- PostgreSQL AGE, workspace isolation, local file pipeline 회피가 필요하다.
- document graph extraction/merge/delete의 운영 비용이 있다.

#### 언제 맞는가

현재 가장 큰 실패가 사내 RAG/문서 질의의 cross-document reasoning, context bloat, citation quality라면 이 선택지가 맞다.

### 6.2 선택지 B: LightRAG + Mem0

이 조합은 역할을 엄격히 분리할 때만 시너지가 있다.

```text
LightRAG
  - approved organization/project document knowledge
  - entity/relation graph + chunks
  - document evidence retrieval

Mem0
  - user/project/agent durable preferences and conventions
  - correction memory
  - small fact recall

PostgreSQL / MinIO
  - ACL, document and meeting authority, action current-state, audit
```

#### 실제 시너지

- LightRAG가 "무슨 근거 문서가 맞는가"를 해결하고, Mem0가 "이 사용자의 프로젝트/선호에 맞춰 어떤 문맥을 우선할지"를 돕는다.
- 과거 대화 전체를 넣지 않고 Mem0의 작은 fact와 LightRAG evidence를 함께 쓰므로 prompt budget을 통제할 수 있다.
- organization graph와 개인 memory의 보존/삭제/권한 정책을 분리할 수 있다.

#### 시너지가 아닌 부분

- Mem0가 LightRAG graph traversal을 더 잘하게 만들지는 않는다.
- LightRAG가 Mem0의 stale fact/update/tenant authorization 문제를 해결하지 않는다.
- 두 retrieval을 무조건 매 요청에 직렬 호출하면 latency가 커질 수 있다.
- Mem0 entity linking은 graph database가 아니다. Mem0 V3는 graph-store support를 제거했고 vector sidecar entity linking만 남겼다. LightRAG graph와 통합/동기화하면 duplicate entity authority가 생긴다.

#### 반드시 지킬 경계

1. Mem0 facts를 LightRAG graph에 자동 ingestion하지 않는다.
2. LightRAG entity/relation을 Mem0 memory로 복제하지 않는다.
3. `document_id`, `version`, `evidence_uri`는 PostgreSQL/MinIO reference로만 연결한다.
4. 일반 대화는 Mem0만, document/RAG 질의는 LightRAG만 먼저 호출한다. 둘 다 필요한 질문에만 gateway가 제한된 결과를 결합한다.
5. Qdrant collection, ingestion outbox, retry queue, metrics를 완전히 분리한다.

#### 결론

장기적으로는 가장 논리적인 조합 후보지만, **첫 PoC의 대상이 아니다.** 먼저 LightRAG가 RAG 품질을 개선하는지, 그 다음 Mem0가 별도 personal-memory 병목을 개선하는지 독립적으로 증명해야 한다.

### 6.3 선택지 C: LightRAG + OpenViking

현재 단계에서는 권장하지 않는다.

| 영역 | LightRAG | OpenViking | 중복/충돌 |
| --- | --- | --- | --- |
| 문서 Resource | document/chunk/KG/vector | Resource URI, hierarchy, L0/L1/L2 | 둘 다 문서 retrieval plane을 소유 |
| Vector index | chunk/entity/relation index | context URI/index | Qdrant collection과 retrieval policy 이중화 |
| 문서 원문/파생 데이터 | KV + graph/vector, built-in local file pipeline | AGFS/MinIO + abstract/index | source of truth 경계가 복잡 |
| Session/meeting | 문서를 graph knowledge로 indexed 가능 | session archive와 memory commit이 first-class | 일부 보완 가능하지만 data duplication 큼 |
| Durable fact | 본래 역할 아님 | memory template으로 제공 | OpenViking이 더 넓게 포함 |

두 제품을 함께 쓰려면 "LightRAG는 승인된 organization knowledge graph, OpenViking은 agent session/skill/context filesystem"처럼 범위를 칼같이 나눠야 한다. 하지만 Chat Portal에는 이미 MinIO, PostgreSQL, DeepAgents가 있고, 이 조합은 별도 Qdrant index와 두 async ingestion pipeline을 운영하게 한다.

LightRAG와 OpenViking을 결합해야만 해결되는 명확한 use case와 평가 지표가 나오기 전까지는 도입하지 않는다.

### 6.4 선택지 D: OpenViking 단독 대 LightRAG 단독

이 둘은 조합보다 대안 비교가 먼저다.

| 질문 | LightRAG가 더 맞는 경우 | OpenViking이 더 맞는 경우 |
| --- | --- | --- |
| 핵심 retrieval 문제 | entity/relation, multi-hop, graph reasoning | filesystem hierarchy, session/resource/skill context browsing |
| 기존 저장소 | Qdrant + PostgreSQL(+AGE)를 적극 활용 | MinIO + Qdrant을 provider가 자체 context plane으로 소유 |
| document source lifecycle | Portal이 MinIO/PostgreSQL authority를 계속 갖고 싶음 | OpenViking AGFS를 context source of truth로 허용 가능 |
| memory 요구 | 별도 Mem0/Portal memory로 분리 가능 | session/memory/skill을 통합하고 싶음 |
| 라이선스 | MIT | AGPL-3.0 |
| local persistence 기본값 | 네 storage가 local, remote backend를 모두 설정해야 함 | QueueFS SQLite가 기본 |

Chat Portal이 graph 기반 사내 지식 RAG를 우선 검토하는 상황이라면 LightRAG는 OpenViking보다 직접적인 후보다. 반대로 문서 graph보다 agent session/skill/hierarchy context management가 본질이면 OpenViking이 대안이다.

## 7. 문서 업로드를 LightRAG에 연결할 때의 올바른 모델

### 7.1 하지 말아야 할 모델

```text
Browser -> LightRAG native upload
        -> local input / __parsed__ / mineru_raw
        -> LightRAG own document lifecycle
```

문제:

- 원본/parse artifact가 local disk에 남는다.
- Chat Portal document_id/version/ACL과 LightRAG file path가 이중 authority가 된다.
- remote object-store support가 native하게 확인되지 않았다.
- built-in file lifecycle과 MinIO deletion/retention이 충돌한다.

### 7.2 권장 모델: Portal-controlled ingestion adapter

```text
1. Upload
   Browser -> Chat Portal API -> MinIO original object
   PostgreSQL document/version/ACL/status = UPLOADED

2. Parse
   Existing parser worker -> normalized text, page/section mapping
   MinIO/PG에 parse artifact와 evidence locator 보관

3. Index command
   PostgreSQL outbox -> LightRAG adapter
   adapter -> target workspace에 document version을 index
   PostgreSQL status = GRAPH_INDEXING / GRAPH_READY / GRAPH_FAILED

4. Retrieval
   Chat Portal ACL check -> current RAG control 또는 LightRAG treatment
   answer에는 Portal citation mapper가 만든 MinIO/document version reference만 노출

5. Update/Delete
   PostgreSQL document state를 먼저 changed/deleted로 변경하고 query gateway에서 즉시 block
   outbox -> LightRAG delete/reindex
   completion audit 후 derived graph/vector 상태 확인
```

### 7.3 `ainsert`와 `ainsert_custom_chunks` 선택은 별도 검증 대상

기존 parser가 이미 높은 품질의 chunk/section/page mapping을 만든다면 그 결과를 재사용하고 싶을 것이다. 그러나 `ainsert_custom_chunks` path는 entity extraction을 실행하고도 KG merge를 하지 않는다는 열린 이슈가 있다. [#3352](https://github.com/HKUDS/LightRAG/issues/3352)

반대로 plain text `ainsert`는 LightRAG 자체 chunking을 다시 수행할 수 있어 현재 citation mapping과 chunk boundary가 달라질 수 있다.

따라서 PoC는 다음 두 방법을 같은 golden set에서 비교해야 한다.

| 입력 방법 | 장점 | 위험 |
| --- | --- | --- |
| `ainsert` with normalized document text | LightRAG의 표준 graph pipeline에 가까움 | 기존 page/section citation과 chunking을 잃거나 재구현 필요 |
| `ainsert_custom_chunks` with existing chunks | 현재 parser/citation 재사용 가능 | KG merge/재처리 정합성의 target-version 검증이 필수 |

현재 open issue 상태만으로 어느 path가 production-safe하다고 결론 내리면 안 된다.

## 8. 현재 확인된 위험과 issue

| 위험 | 근거 | Chat Portal 영향 | PoC 대응 |
| --- | --- | --- | --- |
| 기본 local storage | 공식 Core 문서의 기본값: JsonKV, NanoVectorDB, NetworkX, JsonDocStatus | local disk에 durable data가 남음 | 네 storage를 모두 remote backend로 명시 설정하고 local write audit |
| built-in upload artifact local persistence | 공식 file pipeline이 `__parsed__`, `*.mineru_raw`, `*.docling_raw`를 보관 | MinIO source of truth와 충돌 | native upload pipeline 사용 금지, Portal adapter 사용 |
| remote object storage 부재 | [#3315](https://github.com/HKUDS/LightRAG/issues/3315) remote S3/OSS image storage 요청이 open | parse image/artifact를 MinIO에 native 연결할 수 없음 | existing parser + MinIO artifact를 유지 |
| workspace isolation | [#2904](https://github.com/HKUDS/LightRAG/issues/2904) query context가 default workspace를 쓸 수 있다는 open report | tenant data leakage 위험 | target version multi-workspace negative test, direct server exposure 금지 |
| reprocess graph idempotency | [#3367](https://github.com/HKUDS/LightRAG/issues/3367) latest main에서 reprocess/resume 후 node/edge description accumulate 보고 | update/retry 뒤 graph noise, token/LLM cost 증가 | duplicate document/retry/reindex test 및 release pin/fork 판단 |
| custom chunk KG merge | [#3352](https://github.com/HKUDS/LightRAG/issues/3352) custom chunks entity extraction과 KG merge 불일치 보고 | 기존 parser chunk 재사용 시 graph가 비어 있거나 불완전할 위험 | target version end-to-end assertion 필요 |
| entity/relation conflict | [#2528](https://github.com/HKUDS/LightRAG/issues/2528) incremental ingestion conflict/duplicate 처리 질문 | 같은 명칭 entity가 다른 문서/tenant 의미를 섞을 수 있음 | workspace 분리, entity canonicalization, graph provenance evaluation |
| citation 안정성 | [#3346](https://github.com/HKUDS/LightRAG/issues/3346) 근거가 간헐적으로 누락된다는 open report | Chat Portal 문서 답변의 citation contract 위반 | answer와 evidence URI를 별도로 검증하고 control fallback |
| graph lexical retrieval | [#3198](https://github.com/HKUDS/LightRAG/issues/3198) BM25 + vector + graph traversal seed가 RFC 상태 | 전문용어/약어가 많은 도메인에서 graph/vector만으로 precision 부족 가능 | 현재 RAG BM25/reranker와 fairness 있게 비교 |

## 9. 성능 PoC 설계

### 9.1 Phase 0: 도입 가능성 gate

다음 중 하나라도 통과하지 못하면 answer-quality A/B 이전에 LightRAG PoC를 중단한다.

1. `PGKVStorage`, `PGDocStatusStorage`, `QdrantVectorDBStorage`, `PGGraphStorage`를 사용하고 local persistent write가 없음을 확인한다.
2. 운영 PostgreSQL에 Apache AGE를 도입할 수 있거나, 별도 graph backend의 비용/운영 책임이 승인된다.
3. LightRAG Server workspace header를 직접 신뢰하지 않고 Portal gateway가 workspace를 강제하는 구조를 만든다.
4. tenant A/B, user/project ACL, deleted document에 대한 negative retrieval test가 0건 누출이다.
5. built-in upload/file scan/artifact archive 경로를 호출하지 않는다.

### 9.2 Phase 1: retrieval-only shadow PoC

#### Corpus

- 사내 knowledge와 representative upload document 100~500개
- 긴 문서, 다문서, multi-hop relation 질문을 의도적으로 포함
- 단순 page lookup 질문도 포함해 graph의 불필요한 overhead를 측정
- 문서 update/delete/reprocess fixture 포함

#### 비교군

```text
Control A: 현재 Chat Portal RAG

Treatment B: LightRAG naive
  - LightRAG chunk vector path만 사용

Treatment C: LightRAG mix
  - graph local/global + chunk vector path 사용

Shared conditions:
  - 동일 corpus version
  - 동일 authorization fixture
  - 동일 LLM and system prompt
  - 동일 최대 context token budget
  - 동일 citation output schema
```

`Control A`와 `Treatment B`를 비교해야 LightRAG graph가 아닌 chunking/embedding/reranker 차이로 생긴 이득을 분리할 수 있다. `B`와 `C` 비교로 graph retrieval의 순수 기여를 확인한다.

#### 지표

| 범주 | 지표 |
| --- | --- |
| Retrieval | document/page/section Recall@k, MRR, nDCG, relation evidence recall |
| Answer | faithfulness, correctness, human preference win-rate, citation precision |
| Context | input token, retrieved chars, irrelevant evidence ratio, tool-call count |
| Latency | retrieval p50/p95, rerank time, graph query time, TTFT, end-to-end p95 |
| Cost | extraction LLM token per document, reindex cost, query model token, storage growth |
| Freshness | update/delete/reprocess 후 stale result 제거 시간 |
| Security | tenant/workspace/document ACL negative tests |

#### 통과 기준

- graph-intensive query set에서 `mix`가 current RAG보다 사전 합의한 quality improvement를 보인다.
- 단순 lookup query에서는 `naive` 또는 control routing이 더 빠르다는 route policy를 만들 수 있다.
- `mix`의 p95 latency/token 증가가 quality 이득을 상쇄하지 않는다.
- update/delete/retry가 graph duplicate, stale citation, cross-tenant result를 만들지 않는다.
- extraction/reindex 실패는 관측 가능하고 control RAG fallback이 동작한다.

### 9.3 Phase 2: routing PoC

LightRAG가 모든 RAG 질의에 좋은지 확인하지 말고 query class별 route를 평가한다.

```text
specific page / exact policy / short question
  -> current RAG or LightRAG naive

cross-document relation / impact / dependency / summary
  -> LightRAG mix

general chat without knowledge request
  -> no LightRAG
```

이 routing이 없으면 `mix`의 graph/rerank overhead가 단순 질의 latency를 악화시킬 수 있다.

### 9.4 Phase 3: Mem0는 조건부로 별도 PoC

LightRAG가 통과한 뒤 아래가 사실일 때만 Mem0 PoC를 한다.

- RAG quality와 별개로 사용자가 preference/project convention을 반복 설명한다.
- 이전 대화의 정정/결정 fact 누락이 agent failure의 유의미한 원인이다.
- LightRAG document retrieval만으로는 해결되지 않는다.

Mem0 PoC는 general chat/meeting follow-up에서만 수행하고, LightRAG graph와 같은 query path에 처음부터 넣지 않는다.

## 10. 최종 선택 규칙

### LightRAG 단독을 선택할 조건

- 현재 문서/RAG에서 cross-document, entity relation, multi-hop failure가 실제로 크다.
- PostgreSQL AGE와 Qdrant multi-workspace를 운영할 수 있다.
- Portal-controlled ingestion adapter로 local file pipeline을 피할 수 있다.
- shadow PoC에서 graph `mix`가 기존 RAG보다 quality/context efficiency 이득을 보인다.

### LightRAG + Mem0를 선택할 조건

- LightRAG가 조직 문서 RAG에서 독립적으로 통과했다.
- Mem0가 general chat/meeting durable fact에서 독립적으로 통과했다.
- 두 계층의 source of truth와 query routing을 분리할 수 있다.

```text
organization/document knowledge -> LightRAG
user/project durable fact        -> Mem0
business state/ACL/audit         -> PostgreSQL
original/evidence                -> MinIO
runtime lock/cache               -> Redis
```

### OpenViking을 LightRAG와 함께 선택하지 않을 조건

아래 중 하나라도 해당하면 LightRAG + OpenViking은 피한다.

- 둘 다 업로드/사내 문서 retrieval을 맡도록 설계하려 한다.
- 둘 다 MinIO/Qdrant에서 같은 원문/문맥을 index하려 한다.
- 아직 LightRAG와 OpenViking 각각의 standalone improvement를 측정하지 않았다.
- 팀이 두 async ingestion pipeline, 두 vector schema, 두 lifecycle을 운영할 수 없다.

### 아무 provider도 선택하지 않을 조건

- current RAG의 failure가 graph relation이 아니라 chunking, metadata filter, reranking, ACL, citation, stale invalidation에 있다.
- graph `mix`가 quality를 개선하지 못하거나 p95/token/cost가 이득을 상쇄한다.
- AGE 또는 local-data-free ingestion 조건을 충족할 수 없다.

이 경우 현재 RAG pipeline을 개선하는 것이 더 낫다. graph RAG는 일반 vector RAG의 보편적 상위호환이 아니다.

## 11. Chat Portal에 대한 최종 권고

1. **먼저 LightRAG를 현재 RAG의 대체제가 아니라 graph-retrieval shadow candidate로만 PoC한다.**
2. **LightRAG native upload pipeline은 사용하지 않는다.** 원본/parse artifact/ACL/version은 현재 MinIO/PostgreSQL 흐름에 남긴다.
3. **LightRAG Core는 Qdrant + PostgreSQL KV/doc status + PostgreSQL AGE graph로 구성 가능한지 먼저 검증한다.** AGE가 불가하면 graph backend 추가 비용을 명시적으로 승인받아야 한다.
4. **workspace는 authorization이 아니므로 Portal gateway가 tenant/document scope를 강제한다.** #2904류 multi-tenant issue가 해소되었다고 가정하지 않는다.
5. **Mem0는 LightRAG와 경쟁하지 않는다.** LightRAG가 조직 지식 RAG에서 통과하고 personal durable memory가 별도 병목일 때만 두 번째로 추가한다.
6. **OpenViking은 LightRAG와 결합 후보가 아니라 대안 후보로 둔다.** graph relation이 필요한지, hierarchy/session/skill context가 필요한지 먼저 선택한다.

현재 Chat Portal의 조사 목적에 가장 맞는 초기 질문은 이것이다.

> 현재 RAG의 실제 실패 중 graph retrieval로만 해결 가능한 비율은 얼마이며, LightRAG `mix`가 같은 token/latency 예산에서 이를 개선하는가?

이 질문에 "예"라고 측정되기 전에는 Mem0나 OpenViking과의 조합을 논의해도 근거가 부족하다.

## 12. 공개된 제품/플랫폼 사례: Agent Memory 구성 패턴

아래 표는 각 회사가 공개 문서에서 설명한 제품/플랫폼의 구성만 정리한다. 내부 DB, embedding model, ranking pipeline을 공개하지 않은 경우에는 추측하지 않고 `비공개`로 표기했다. 따라서 구현을 그대로 복제하기 위한 표가 아니라, **실제 제품이 memory를 어떤 책임 단위로 분리하는지**를 보는 사례다.

| 제품/회사 | 공개된 memory/context 구성 | 실제 제품에서의 동작 | 저장소/처리 공개 범위 | Chat Portal에 주는 설계 시사점 | 출처 |
| --- | --- | --- | --- | --- | --- |
| ChatGPT / OpenAI | `Saved Memories` + `Reference chat history` + `Projects`의 project chat/file context | Saved memory는 명시적 또는 자동으로 보존되는 선호/목표 등의 durable 정보, chat history는 유용한 과거 대화 회수, Project는 project 내부 chats/files와 instructions에 context를 한정 | 내부 DB/retrieval 구현은 비공개. 사용자는 memory와 chat history를 별도 on/off/delete할 수 있고 project-only memory boundary를 설정 | durable fact, past-session recall, project knowledge를 하나의 저장소/retention 정책으로 섞지 말 것. scope를 먼저 분리하고 삭제 UX도 각각 제공할 것 | [Memory](https://help.openai.com/en/articles/11146739-how-does-reference-saved-memories-work), [Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt) |
| Amazon Bedrock AgentCore Memory / AWS | short-term raw events + long-term memory records + strategy/namespace | session/actor ID로 raw event를 보관하고, background extraction/consolidation이 semantic, preference, summary, episodic 또는 custom strategy의 long-term record를 만든 뒤 semantic retrieval | fully managed service. event, actor/session, strategy, namespace, retrieval API는 공개하지만 내부 storage implementation은 비공개 | raw transcript/event와 durable fact를 분리하고, extraction/consolidation을 request critical path가 아닌 비동기 처리로 둘 것. tenant/user scope는 actor와 namespace만으로 끝내지 말고 제품 authz와 결합 | [Memory types](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-types.html), [Memory strategies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-strategies.html), [Memory organization](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-organization.html) |
| Vertex AI Agent Engine Memory Bank / Google Cloud | Agent Engine Sessions + Memory Bank | Sessions가 개별 session conversation history를 관리하고, Memory Bank가 대화에서 facts/preferences/context를 생성해 session 간 long-term memory로 retrieve. ADK 기본 service 또는 다른 runtime에서 API로 사용 가능 | managed service. memory generate/retrieve API, IAM 권한, Agent Engine integration은 공개하지만 내부 DB/검색 engine은 비공개 | session store와 cross-session fact memory를 구분한 managed platform 사례. Chat Portal도 DeepAgents thread state와 durable memory candidate를 같은 테이블/collection에 합치지 않는 편이 맞음 | [Memory Bank setup](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/set-up), [Google Cloud announcement](https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-memory-bank-in-public-preview) |
| Letta API / Letta | in-context Memory Blocks + Files + Archival Memory + conversation search + external RAG tools | small/critical state는 항상 prompt에 보이는 editable block, 큰/덜 중요한 memory는 archival semantic search, files는 partial read/search, 대규모 corpus는 external RAG tool로 분리. block은 multi-agent shared memory로도 사용 | abstraction/API와 archival vector memory 사용은 공개. self-host/managed deployment의 구체 storage topology는 배포 선택에 따라 다름 | 항상 주입할 작은 정책/선호와 on-demand retrieval을 분리해야 함. shared state는 read-only default와 concurrent last-write-wins 위험을 고려해야 함 | [Context hierarchy](https://docs.letta.com/guides/core-concepts/memory/context-hierarchy), [Memory blocks](https://docs.letta.com/guides/core-concepts/memory/memory-blocks), [Agent memory tools](https://docs.letta.com/guides/get-started/for-agents) |
| Zep / Graphiti | user별 temporal Context Graph + time/full-text/semantic/graph retrieval | Zep은 사용자별 entity, relation, fact의 시간 변화를 graph로 만들고 historical context와 fact invalidation을 처리한다. Graphiti는 단일 subject graph의 OSS engine, Zep은 이를 운영형 Context Lake로 확장 | Graphiti의 temporal graph 개념과 Zep의 제품 경계는 공개. Zep managed engine의 세부 storage/LLM pipeline은 proprietary | graph memory는 문서 RAG의 관계뿐 아니라 변경되는 user/business state에도 쓸 수 있지만, 시간/invalidity/provenance가 핵심이다. 단순 vector entity sidecar를 graph memory로 오해하면 안 됨 | [Zep graph overview](https://help.getzep.com/graph-overview), [Zep vs Graphiti](https://help.getzep.com/zep-vs-graphiti) |
| DeepAgents / LangChain | short-term agent state + filesystem-backed persistent memory + skills + StoreBackend namespace | current thread에서는 state/filesystem으로 context를 관리하고, `/memories/` 경로는 StoreBackend에 routing해 cross-thread memory로 저장. agent/user/org namespace와 read-only policy, background consolidation을 제공 | SDK abstraction과 backend routing은 공개. 실제 production store는 사용자가 선택/구현 | runtime working context, durable files/facts, procedural skills, organization policy를 별도 scope와 권한으로 분리하는 직접적인 참조 모델. 그러나 vector RAG, audit, external knowledge lifecycle은 별도 시스템이 필요 | [DeepAgents Memory](https://docs.langchain.com/oss/python/deepagents/memory), [Context engineering](https://docs.langchain.com/oss/python/deepagents/context-engineering) |
| Cursor / Anysphere | versioned Project Rules + global User Rules + project-scoped auto Memories | project rule은 repository 안에서 version control되고 file/path relevance로 attach. user rule은 모든 project에 항상 적용. Memory는 chat을 sidecar model이 관찰해 생성하는 project-scoped rule이며 user approval 후 저장 | rules/memory의 prompt-level 동작과 scope는 공개. internal storage/model/retrieval은 비공개 | code agent에서 durable fact를 별도 vector DB로만 다루지 않고, 재사용 instruction을 versioned/project-scoped policy로 승격하는 사례. 자동 추출 결과는 승인 가능한 candidate여야 함 | [Cursor Rules](https://docs.cursor.com/context/rules), [Cursor Memories](https://docs.cursor.com/en/context/memories) |

### 사례에서 반복되는 공통 구조

제품마다 명칭은 달라도 공개된 설계는 대체로 아래 네 책임을 분리한다.

| 책임 | 사례 | Chat Portal에서 확인할 질문 |
| --- | --- | --- |
| 현재 session/event | AgentCore events, Vertex Sessions, DeepAgents state, ChatGPT project chats | 원문 대화/회의를 어떤 보존 기간과 ACL로 저장할 것인가 |
| durable facts/preferences | ChatGPT Saved Memories, AgentCore long-term records, Memory Bank, Letta blocks, Cursor Memories | 자동 추출 결과를 언제 active memory로 승격하고, 정정/삭제를 어떻게 처리할 것인가 |
| procedural/shared instructions | Letta read-only/shared blocks, DeepAgents skills/org memory, Cursor project/user rules | 사용자 입력이 shared instruction을 오염시키지 않게 write 권한과 review를 어떻게 제한할 것인가 |
| external knowledge retrieval | Letta external RAG, Zep graph, LightRAG graph RAG, ChatGPT project files | 문서 원문/version/ACL authority와 derived retrieval index를 어떻게 분리할 것인가 |

공개 제품 사례가 공통으로 보여 주는 결론은 하나의 "memory DB"가 모든 문제를 해결한다는 것이 아니다. session 원문, durable facts, procedural instructions, external knowledge는 서로 다른 retention, 권한, update, retrieval 비용을 가지므로 분리한다. Chat Portal도 provider 선택 전에 이 네 책임 중 현재 품질 병목이 어디인지 측정해야 한다.

## 참고 자료

- [LightRAG README](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/README.md): query modes, rerank latency statement, multimodal/file pipeline 개요.
- [LightRAG Core programming guide](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/docs/ProgramingWithCore.md): 네 storage backend, workspace isolation, Qdrant/PGGraph/PGKV/PGDocStatus 설정.
- [LightRAG file processing pipeline](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/docs/FileProcessingPipeline.md): `__parsed__`, MinerU/Docling raw artifact, local file lifecycle.
- [LightRAG core implementation](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/lightrag/lightrag.py): storage initialization, workspace, `adelete_by_doc_id` pipeline coordination.
- [Qdrant storage implementation](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/lightrag/kg/qdrant_impl.py): workspace payload filter/partition behavior.
- [Mem0 V3 migration](https://docs.mem0.ai/migration/oss-v2-to-v3): Mem0 graph-store removal과 entity linking 경계.
- [Mem0 Deep Dive](mem0.md): Chat Portal durable fact memory와 SQLite/tenant authorization 제약.
- [OpenViking Deep Dive](openviking.md): URI/L0-L1-L2 context DB와 storage/queue 운영 제약.
- [LightRAG #2904](https://github.com/HKUDS/LightRAG/issues/2904): workspace header/query context isolation 위험 신호.
- [LightRAG #3367](https://github.com/HKUDS/LightRAG/issues/3367): reprocess/resume graph description accumulation 위험 신호.
- [LightRAG #3352](https://github.com/HKUDS/LightRAG/issues/3352): custom chunks KG merge 위험 신호.
- [LightRAG #3315](https://github.com/HKUDS/LightRAG/issues/3315): remote S3/OSS image storage feature request.
- [LightRAG #2528](https://github.com/HKUDS/LightRAG/issues/2528): incremental entity/relation conflict 질문.
- [LightRAG #3346](https://github.com/HKUDS/LightRAG/issues/3346): citation/evidence output 위험 신호.
