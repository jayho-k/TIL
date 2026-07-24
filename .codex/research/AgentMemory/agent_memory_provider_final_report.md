# Chat Portal Agent Memory / Context Provider 최종 리포트
작성일: 2026-07-12

## 1. 목적과 현재 전제

이 조사의 목적은 새 chat/RAG 기능을 만드는 것이 아니다. Chat Portal은 이미 다음 기능을 제공한다.

- 업로드 문서 대화
- 일반 대화
- 회의록 생성
- 사전 parsing/embedding한 사내 지식 RAG

운영 중인 기반 인프라는 Qdrant, PostgreSQL, MinIO, Redis이며, Agent runtime으로 DeepAgents 도입을 검토한다.

따라서 최종 질문은 다음이다.

> **현재 기능을 유지한 상태에서 어떤 memory/context engine이 retrieval 품질, context token, 응답 지연, 반복 정정을 실제로 개선하는가?**

provider를 도입하기 위해 기존 RAG를 교체하거나, 모든 데이터를 하나의 memory DB에 넣는 것은 이 리포트의 권고가 아니다.

## 2. 최종 결론

### 2.1 지금 하나의 provider를 확정하지 않는다

현재 정보만으로는 Mem0, OpenViking, LightRAG 중 하나를 전체 Chat Portal provider로 확정하면 안 된다. 세 제품의 책임이 다르고, 현재 성능 병목이 문서 retrieval인지 personal memory인지 session/context management인지 아직 baseline으로 입증되지 않았기 때문이다.

```text
문서/사내 지식 RAG의 관계·다문서 문제
  -> LightRAG 단독 shadow PoC

일반 대화의 preference/project convention/반복 정정 문제
  -> Mem0 단독 PoC

문서·세션·스킬을 URI 계층의 한 context plane으로 다뤄야 하는 문제
  -> OpenViking 단독 대안 PoC
```

**두 provider를 처음부터 함께 넣는 방식은 권장하지 않는다.** 품질/latency 변화의 원인을 알 수 없고, source of truth와 장애 경로가 중복된다.

### 2.2 현재 기능 구성에서 가장 중요한 1차 가설

Chat Portal에는 문서 대화, 회의록, 사내 지식 RAG가 이미 있으므로 아래 가설의 정보 가치가 가장 크다.

> 현재 RAG의 실제 실패 중 cross-document, entity relation, multi-hop, context bloat 문제가 유의미한가? 그렇다면 LightRAG `mix`가 동일 token/latency 예산에서 현재 RAG보다 개선하는가?

이 문제가 baseline에서 확인되면 **LightRAG 단독 shadow PoC가 첫 순서**다. 반대로 RAG는 충분하고 사용자의 반복 설명/정정 누락이 주 문제라면 **Mem0 단독 PoC가 첫 순서**다.

## 3. 역할별 최종 판단

| 후보 | 정확한 역할 | 현재 Chat Portal에서의 판단 | 기본 도입 여부 |
| --- | --- | --- | --- |
| DeepAgents | runtime, short-term state, filesystem, subagent, skills | 모든 선택지의 runtime. 장기 RAG/memory source of truth는 아님 | 사용 |
| LightRAG | graph + vector document retrieval | 문서 업로드/사내 지식 RAG의 성능 후보. graph 문제에만 검증 | 조건부 1차 PoC |
| Mem0 | durable fact extraction/retrieval | user/project preference, convention, correction memory 후보 | 조건부 1차 PoC |
| OpenViking | Resource/Session/Memory/Skill Context Database | LightRAG와 결합 대상이 아니라 hierarchy/session/skill 중심의 대안 | 조건부 대안 PoC |
| Hindsight | observation/temporal memory engine | PostgreSQL 중심 memory 연구 후보이나 현재 RAG 성능 개선의 직접 후보는 아님 | 보류 |
| Honcho | peer/session/sub-agent representation | multi-agent state modeling이 실제 병목일 때만 검토 | 보류 |
| ByteRover, Holographic, RetainDB, Supermemory | 각각 context/memory platform | 현재 Qdrant/PostgreSQL/MinIO 요구와 기능 병목에 대한 우선 근거 부족 | 보류 |

Hindsight와 Honcho의 조사를 폐기하는 뜻은 아니다. 다만 현재 목표가 기존 Chat Portal 성능 개선이므로, 문서 graph retrieval과 personal durable memory보다 먼저 PoC할 근거는 없다.

## 4. provider별 저장 책임과 하드 게이트

### 4.1 LightRAG: graph RAG 후보

LightRAG는 Agent Memory provider가 아니라 document knowledge graph + vector retrieval engine이다. full document/chunk/KV, entity/relation/chunk vector, graph node/edge, document status를 함께 관리한다.

| 데이터 | 권위 저장소 | LightRAG의 위치 |
| --- | --- | --- |
| 원본 문서, transcript, attachment | MinIO | URI/reference만 사용 |
| document version, ACL, lifecycle, citation mapping | PostgreSQL | query 전 권한 판단과 index command authority |
| derived full text/chunk, graph metadata, LLM cache | LightRAG `PGKVStorage` | 파생 copy |
| graph node/edge | `PGGraphStorage` + Apache AGE | 파생 graph |
| entity/relation/chunk vectors | LightRAG 전용 Qdrant collection | 파생 index |

**하드 게이트**

1. LightRAG 기본 upload/file pipeline은 쓰지 않는다. 기본 JSON/NetworkX/NanoVector와 `__parsed__`, MinerU/Docling artifact는 local working directory를 사용한다.
2. Qdrant만으로는 충분하지 않다. PostgreSQL graph backend에는 Apache AGE가 필요하다.
3. LightRAG workspace는 storage partition이며 Chat Portal tenant authorization을 대체하지 않는다.
4. `ainsert`와 `ainsert_custom_chunks`의 graph merge/citation behavior를 현재 parser output으로 직접 검증한다.

### 4.2 Mem0: durable fact 후보

Mem0 최신 OSS V3는 대화/agent output에서 fact를 추출하고 Qdrant 등에서 recall하는 vector-first engine이다. automatic path는 `ADD-only`이며, 최신 상태의 update/delete/approval은 Portal이 맡아야 한다.

| 데이터 | 권위 저장소 | Mem0의 위치 |
| --- | --- | --- |
| user/project fact의 active/superseded state, tenant policy, audit | PostgreSQL | lifecycle command/result 기록 |
| fact vector/payload, entity sidecar | Mem0 전용 Qdrant collection | recall index |
| transcript/evidence | MinIO + PostgreSQL | payload에는 reference만 |
| history/recent messages | vanilla Mem0 SQLite | PostgreSQL adapter/fork가 필요한 공백 |

**하드 게이트**

1. vanilla OSS는 remote Qdrant/PostgreSQL을 써도 SQLite history/recent message path를 연다. local persistent data 금지면 PostgreSQL history adapter/fork가 필요하다.
2. self-host API auth는 data-plane tenant authorization을 자동 강제하지 않는다. Portal `MemoryService`가 모든 scope filter를 강제한다.
3. 한국어 BM25/entity extraction은 English spaCy 의존 이슈가 있어 semantic-only baseline과 비교해야 한다.
4. Mem0 fact를 LightRAG graph에 자동 반영하지 않는다.

### 4.3 OpenViking: LightRAG의 조합이 아닌 대안

OpenViking은 Resource, Session, Memory, Skill을 URI filesystem과 L0/L1/L2 context tier로 관리하는 Context Database다. durable fact도 memory template으로 관리할 수 있으므로 Mem0가 기능상 필수인 것은 아니다.

| 강점 | Chat Portal에서의 제약 |
| --- | --- |
| 문서/세션/스킬을 같은 URI context plane에서 browse/search/read | 자체 AGFS/URI/schema/queue/index lifecycle을 소유해야 함 |
| MinIO S3-compatible AGFS와 Qdrant 공식 backend | 기존 RAG/Qdrant collection과 bucket prefix를 재사용할 수 없음 |
| custom memory template과 session commit | QueueFS SQLite, async semantic pipeline, restart/retry를 운영해야 함 |
| hierarchy-aware context loading | AGPL-3.0 및 별도 Context DB service 운영 검토 필요 |

OpenViking과 LightRAG은 모두 문서 retrieval/context plane을 소유한다. `LightRAG + OpenViking`은 명확한 성능 증거가 나오기 전에는 배제한다.

## 5. 권장 아키텍처 선택지

### 선택지 A: 현재 RAG 개선만 수행

다음 상황이면 새 provider를 도입하지 않는다.

- failure가 graph relation이 아니라 chunking, metadata filter, reranker, ACL, citation, stale invalidation에 있음
- graph RAG가 동일 token/latency 예산에서 quality를 개선하지 못함
- AGE 또는 local-data-free LightRAG ingestion 조건을 충족할 수 없음

이 경우 현재 Qdrant RAG pipeline을 고도화하는 것이 최선이다.

### 선택지 B: LightRAG 단독

```text
DeepAgents
  -> Chat Portal authorization / retrieval gateway
  -> current RAG control path
  -> LightRAG shadow or selected graph path
       -> PostgreSQL: PGKV + PGDocStatus + PGGraph(AGE)
       -> Qdrant: LightRAG chunk/entity/relation collections

MinIO + PostgreSQL
  -> original/evidence/document ACL/version authority
```

선택 조건:

- 다문서, 관계, 영향 분석, meeting evidence 질문에서 graph retrieval이 개선됨
- LightRAG `mix`가 current RAG 대비 quality/context efficiency 이득을 보임
- update/delete/retry 뒤 graph duplicate, stale citation, tenant leak이 없음

### 선택지 C: Mem0 단독

```text
DeepAgents
  -> Portal MemoryService
  -> Mem0 fact recall
       -> Qdrant: chat_portal_mem0, chat_portal_mem0_entities

PostgreSQL
  -> history adapter, policy, current fact state, audit/outbox

MinIO
  -> transcript/evidence reference
```

선택 조건:

- 현재 RAG 품질은 충분함
- user/project preference, convention, correction 누락이 반복됨
- PostgreSQL history adapter와 tenant filter 강제를 유지할 수 있음
- 한국어 recall이 baseline 이상임

### 선택지 D: LightRAG + Mem0

이것은 두 standalone PoC가 통과한 뒤에만 가능한 최종 조합이다.

```text
organization/document knowledge -> LightRAG
user/project durable facts      -> Mem0
thread/scratch/skills           -> DeepAgents
ACL/current state/audit         -> PostgreSQL
original/evidence               -> MinIO
lock/cache/idempotency          -> Redis
```

필수 경계:

- LightRAG graph와 Mem0 entity sidecar를 통합하지 않는다.
- document chunk/relationship을 Mem0에 대량 저장하지 않는다.
- 모든 request에서 두 provider를 호출하지 않는다. query class router가 필요하다.
- 각각 전용 Qdrant collection, outbox, retry/metric을 사용한다.

## 6. PoC의 최종 순서

### Phase 0: baseline과 공통 보안 gate

provider 전에 현재 기능의 representative golden set과 trace를 만든다.

| 기능 | 확인할 실패 | 핵심 지표 |
| --- | --- | --- |
| 업로드 문서 대화 | long document/다문서에서 근거 누락 | Recall@k, citation precision, faithfulness, token, p95 |
| 사내 지식 RAG | cross-document/multi-hop failure | MRR, nDCG, relation evidence recall, p95 |
| 일반 대화 | preference/convention 반복 설명 | correction rate, expected default action accuracy |
| 회의 follow-up | 이전 결정 근거 또는 최신 상태 누락 | evidence recall, stale recall, current-state correctness |

모든 provider path에서 `tenant_id`, workspace, user/project/document ACL을 Portal backend가 결정하며, cross-tenant negative test는 0건 누출이어야 한다.

### Phase 1A: graph 병목이면 LightRAG 단독 shadow PoC

```text
Control A: current Chat Portal RAG
Treatment B: LightRAG naive
Treatment C: LightRAG mix
```

동일 corpus version, authorization fixture, model, system prompt, max context token, citation schema로 비교한다. `A` 대 `B`는 graph 이외의 차이를, `B` 대 `C`는 graph의 순수 기여를 분리하기 위해 필요하다.

통과 기준:

- graph-intensive set에서 `mix` quality가 사전 합의한 수준 이상 개선
- `mix`의 token/p95/cost 증가가 이득을 상쇄하지 않음
- update/delete/retry, workspace/ACL negative test 통과
- local working directory에 영구 document/artifact가 남지 않음

### Phase 1B: personal-memory 병목이면 Mem0 단독 PoC

Control은 current conversation/RAG, treatment는 strict scope filter를 가진 top-N Mem0 fact recall이다.

통과 기준:

- preference/convention을 다음 행동에 실제 반영
- superseded/deleted fact가 active prompt에 0회 주입
- tenant/project negative test 0건 누출
- 한국어 semantic/hybrid retrieval이 baseline 이상
- Mem0/Qdrant 오류에서 일반 chat이 fallback으로 계속 동작

### Phase 2: 두 결과가 각각 통과했을 때만 LightRAG + Mem0

두 provider를 결합하는 목적은 하나의 답변을 더 많은 context로 만들기 위함이 아니다. document evidence와 personal durable fact가 둘 다 필요한 query에서 제한된 context를 합치는 것이다.

## 7. 현재 조사 결과로 바뀐 과거 결론

이전 리포트의 "Mem0와 Hindsight를 1차 PoC"와 "OpenViking은 설계 참고"라는 일괄 순위는 더 이상 현재 목적에 맞지 않는다.

변경 이유:

1. Chat Portal의 기능은 이미 있고, 목적은 provider 기능 비교가 아니라 성능 개선이다.
2. LightRAG는 graph RAG라는 별도 축이며, 문서/사내 지식 retrieval 병목을 직접 검증할 수 있다.
3. OpenViking에도 durable fact memory가 있으므로 Mem0를 durable fact의 유일한 해법으로 볼 수 없다.
4. LightRAG와 OpenViking은 문서/context retrieval 책임이 겹치므로 결합보다 대안 비교가 먼저다.
5. Mem0와 LightRAG은 역할 분리가 가능하지만, 각각의 독립 성능 이득이 먼저 증명돼야 한다.

## 8. 최종 권고

1. **현재 RAG baseline을 먼저 측정한다.** graph 문제가 입증되지 않으면 LightRAG를 도입하지 않는다.
2. **graph 문제가 확인되면 LightRAG Core를 기존 ingestion의 shadow index로 PoC한다.** native upload/file pipeline은 사용하지 않는다.
3. **personal durable memory가 별도 병목일 때만 Mem0를 독립 PoC한다.** Mem0는 LightRAG graph와 통합하지 않는다.
4. **OpenViking은 LightRAG와 함께 쓰지 않는다.** graph RAG가 아니라 session/resource/skill hierarchy가 본질적 병목일 때 LightRAG의 대안으로 단독 검토한다.
5. **Hindsight/Honcho 등은 현 단계에서 보류한다.** 현재 기능의 병목과 직접 연결되는 증거가 나오면 재평가한다.

가장 중요한 결정 기준은 provider 기능 목록이 아니라 다음 질문이다.

> 현재 Chat Portal의 어떤 실패가 측정 가능한 비용/품질 문제를 만들고 있으며, 단일 provider가 동일 token, latency, 보안 경계 안에서 그 실패를 개선하는가?

## 참고 조사 자료

- [LightRAG Deep Dive](providers/lightrag.md): graph RAG storage, local file pipeline, PostgreSQL AGE/Qdrant, workspace/issue, standalone/combination PoC.
- [Mem0 Deep Dive](providers/mem0.md): V3 add-only, Qdrant, SQLite history, PostgreSQL adapter 필요성, tenant authorization.
- [OpenViking Deep Dive](providers/openviking.md): URI/L0-L1-L2, MinIO/Qdrant, QueueFS, multi-tenancy, DeepAgents 결합.
- [DeepAgents Memory](https://docs.langchain.com/oss/python/deepagents/memory): runtime memory files, namespace, skills, store boundary.
- [LightRAG Core programming guide](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/docs/ProgramingWithCore.md): supported storage backend와 workspace isolation.
- [LightRAG file processing pipeline](https://github.com/HKUDS/LightRAG/blob/44db36fe080645ba97ded719d44b42c7dee1f54a/docs/FileProcessingPipeline.md): built-in local artifact lifecycle.
- [LightRAG #2904](https://github.com/HKUDS/LightRAG/issues/2904), [#3367](https://github.com/HKUDS/LightRAG/issues/3367), [#3352](https://github.com/HKUDS/LightRAG/issues/3352), [#3315](https://github.com/HKUDS/LightRAG/issues/3315): workspace, reprocess, custom chunk, object storage risk signals.

