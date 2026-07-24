# Mem0 Deep Dive: 최신 OSS 메모리 엔진 구조와 Chat Portal 적합성

조사일: 2026-07-12

## 조사 범위와 판정 기준

이 문서는 Mem0 사용법 요약이 아니라 Chat Portal의 DeepAgents용 Agent Memory를 설계하기 위한 구현 조사다.

확인 대상은 다음과 같다.

1. 최신 Mem0 OSS가 어떤 memory algorithm과 데이터 모델을 실제로 사용하는가
2. memory, entity index, history, session message, server 운영 정보가 어디에 저장되는가
3. Qdrant, PostgreSQL, MinIO, Redis 각각과 어떤 경계로 결합되는가
4. library mode와 self-hosted REST server mode가 운영상 어떻게 다른가
5. tenant isolation, update/delete, audit, 고가용성에 어떤 공백이 있는가
6. OpenViking식 계층형 설계를 Mem0 위에 구현할 수 있는가

## 핵심 결론

Mem0는 OpenViking과 같은 Context Database가 아니다. 최신 OSS 기준 Mem0는 대화/실행 입력에서 독립적인 사실을 추출하고, Qdrant 같은 vector store에 저장하며, semantic + BM25 + entity signal로 검색하는 **vector-first long-term memory engine**이다.

Chat Portal에 가장 중요한 결론은 네 가지다.

1. Qdrant는 공식 backend이며 현재 소스에서 dense vector, BM25 sparse vector, entity sidecar collection까지 사용한다.
2. Mem0 OSS의 자동 추출은 최신 V3에서 `ADD-only`다. 자동으로 기존 사실을 LLM이 update/delete하는 모델이 아니다.
3. Qdrant를 remote로 설정해도 `history.db`와 최근 message context는 SQLiteManager가 관리한다. vanilla OSS는 history store를 PostgreSQL로 교체하는 설정을 제공하지 않는다.
4. self-hosted server의 API key는 서버 접근 인증이지 `tenant_id`/`user_id`를 자동 강제하는 data-plane authorization이 아니다. Chat Portal gateway 또는 `MemoryService`가 scope filter를 강제해야 한다.

따라서 Mem0는 여전히 Qdrant 기반 durable fact memory의 강력한 PoC 후보지만, "Mem0만 붙이면 장기 메모리의 저장, 이력, 계층, 권한, 감사가 모두 해결된다"고 보면 안 된다. Chat Portal은 PostgreSQL control plane과 MinIO evidence/archive, Redis runtime coordination을 별도로 가져야 하며, 로컬 SQLite를 전혀 허용하지 않는다면 Mem0 OSS에 adapter/fork 또는 대체 history 설계가 필요하다.

## 출처와 버전

| 구분 | 확인 결과 | 신뢰도 |
| --- | --- | --- |
| 공식 GitHub | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 1차 소스 |
| 공식 문서 | [Mem0 Docs](https://docs.mem0.ai/) | 1차 소스 |
| 소스 스냅샷 | `main` commit `17836748d7afe0521516c6a73c6a256680f05527`, 2026-07-11 | 1차 소스 |
| GitHub stars | 약 60.6k, forks 약 7.1k, 2026-07-12 확인 | 지표성 참고 |
| 라이선스 | Apache-2.0 | 1차 소스 |
| 최신 OSS 알고리즘 문서 | V3 add-only extraction, hybrid retrieval, entity linking migration guide | 1차 소스 |

주의: Mem0 문서에는 과거 graph-memory 또는 이전 update algorithm을 설명하는 페이지가 남아 있다. 이 문서는 최신 migration guide와 2026-07-11 `main` 소스 구현을 우선한다. 문서와 코드가 충돌하는 부분은 별도 표기한다.

## 1. Mem0의 정확한 역할

Mem0의 기본 단위는 filesystem node나 session archive가 아니라 **독립적인 memory text**다.

```text
conversation / agent output
  -> extract reusable facts
  -> embed each fact
  -> store vector + payload
  -> retrieve relevant facts on a later query
```

Mem0가 잘하는 영역은 다음과 같다.

| 역할 | 설명 |
| --- | --- |
| Fact extraction | 대화에서 재사용 가능한 사실, 선호, 제약을 추출 |
| Long-term recall | 새로운 query와 관련된 memory를 검색 |
| Explicit correction | memory id 기준 update/delete/history |
| Metadata filtering | user/agent/run 범위와 사용자 metadata 기반 검색 |
| Hybrid ranking | semantic, keyword/BM25, entity linking signal을 결합 |
| REST wrapping | SDK 기능을 self-hosted HTTP API로 노출 |

Mem0가 기본적으로 책임지지 않는 영역은 다음과 같다.

| 영역 | 이유 |
| --- | --- |
| 계층형 context filesystem | URI tree, L0/L1/L2, browse/read abstraction이 없다 |
| 원문/첨부 object storage | MinIO/S3를 native content store로 쓰지 않는다 |
| full transcript archive | SQLite에는 최근 메시지 context를 두지만 transcript archive system은 아니다 |
| agent skill repository | 일반 fact와 procedural summary는 만들 수 있어도 skill lifecycle/파일/검증을 관리하지 않는다 |
| tenant authorization | identifier filtering을 지원하지만 호출자 identity를 memory scope에 자동 결속하지 않는다 |
| distributed workflow/queue | background promotion, approval, retry, outbox를 제공하지 않는다 |

즉 Mem0는 Chat Portal memory architecture의 한 계층이지, memory architecture 전체가 아니다.

## 2. 최신 OSS 알고리즘: V3 ADD-only

이전 Mem0 방식은 기존 memory를 찾은 뒤 LLM이 `ADD`, `UPDATE`, `DELETE` 중 하나를 선택하는 구조였다. 최신 OSS migration guide와 현재 `mem0/memory/main.py`의 V3 경로는 이를 변경했다.

```text
Input messages
  -> 같은 user/agent/run scope에서 기존 memory top-10 semantic retrieval
  -> LLM 1회 호출로 새로운 fact들을 추출
  -> batch embedding
  -> exact MD5 hash deduplication
  -> vector store batch insert
  -> entity extraction/linking
  -> SQLite history와 recent messages 기록
```

자동 write의 결과 이벤트는 `ADD`뿐이다. 이미 존재하는 memory를 retrieval context로 LLM에 보여 중복 생성을 줄이지만, 기존 memory를 자동으로 수정하거나 삭제하지 않는다.

### 이 변경이 Chat Portal에 의미하는 것

| 요구 | 최신 Mem0 OSS의 기본 행동 | Chat Portal이 추가할 책임 |
| --- | --- | --- |
| 사용자가 선호를 정정 | 새 fact가 추가될 수 있음 | 기존 memory 찾기, 승인된 `update()` 또는 supersede 처리 |
| 오래된 project rule 폐기 | 자동 삭제되지 않음 | status/archive/expiration 또는 explicit delete 정책 |
| 사실 충돌 | LLM retrieval context가 완화할 수 있으나 보장하지 않음 | conflict detection, version, effective date 관리 |
| 반복되는 사실 dedup | 같은 텍스트 MD5는 차단 | 의미적으로 유사하지만 표현이 다른 사실의 merge 정책 |

따라서 Mem0를 "self-improving memory"라고 부를 때는 주의가 필요하다. 최신 OSS는 자동 state merge engine보다 **추가 중심의 memory ingestion engine**에 가깝다. Chat Portal의 durable fact는 append-only evidence와 current-state projection을 분리하는 편이 더 안전하다.

## 3. 데이터 모델과 실제 저장 위치

### 3.1 Primary memory record

각 memory는 vector store에 point/row로 저장된다. 주요 payload는 다음과 같다.

| 필드 | 생성 주체 | 의미 |
| --- | --- | --- |
| vector | embedder | memory text의 dense embedding |
| `data` | Mem0 | 추출된 memory text |
| `hash` | Mem0 | `data`의 MD5, exact dedup 용도 |
| `text_lemmatized` | Mem0 | BM25 keyword search용 정규화 text |
| `created_at`, `updated_at` | Mem0 | 생성/갱신 시점 |
| `user_id`, `agent_id`, `run_id` | 호출자 | 기본 scope filter |
| `actor_id`, role | 메시지/호출 문맥 | actor 단위 구분 보조 |
| custom metadata | 호출자 | tenant, project, tier, status 등 제품 정책 |
| `expiration_date` | 호출자 | expired memory 숨김 처리 |

`tenant_id`, `project_id`, `memory_tier`, `memory_path`는 Mem0의 first-class schema가 아니다. metadata payload로 저장하고 모든 query에서 filter로 강제해야 한다.

### 3.2 Qdrant collection은 하나가 아니다

현재 Qdrant adapter는 main memory collection에 dense vector와 `bm25` sparse vector slot을 만든다. entity linking을 처음 사용하면 별도 entity collection도 만든다.

```text
Qdrant
  chat_portal_mem0             # memory text: dense vector + optional bm25 sparse vector + payload
  chat_portal_mem0_entities    # entity text + linked_memory_ids + scope payload
```

기본 collection 이름은 `mem0`, entity collection은 `{collection_name}_entities`다. Qdrant에 이미 `chat_portal_mem0`이 존재하지만 `bm25` sparse slot이 없는 과거 collection이면, 최신 코드가 semantic search만 사용하고 hybrid keyword search를 비활성화한다. hybrid search가 필요하면 새 collection으로 migration하는 편이 안전하다.

### 3.3 SQLite history와 recent message store

`Memory`와 `AsyncMemory`는 Qdrant/pgvector 설정과 관계없이 `SQLiteManager(history_db_path)`를 생성한다. 기본 경로는 `~/.mem0/history.db`다.

SQLite에는 적어도 다음 테이블이 있다.

| 테이블 | 저장 내용 |
| --- | --- |
| `history` | `ADD`, explicit `UPDATE`, explicit `DELETE`의 old/new text, 시각, actor/role |
| `messages` | user/agent/run 조합으로 만든 session scope별 최근 메시지 context |

V3 extraction은 새 입력을 처리하기 전에 이 SQLite에서 같은 scope의 마지막 메시지 최대 10개를 읽어 extraction prompt에 넣는다. 즉 history SQLite는 단순 감사 부가 기능이 아니라 extraction 품질에 관여한다.

### 3.4 중요한 제약: history store provider가 없다

현재 `MemoryConfig`에는 `history_db_path: str`만 있고 history database provider/connection string이 없다. 현재 소스의 `SQLiteManager`는 `sqlite3`를 직접 사용한다.

따라서 다음 문장은 정확하지 않다.

> "Mem0 library mode에서 모든 데이터를 기존 Qdrant/PostgreSQL에 저장할 수 있다."

정확한 표현은 다음이다.

> "Memory vector/payload는 Qdrant 또는 pgvector로 보낼 수 있지만, Mem0 OSS의 history와 recent message context는 기본 구현상 local filesystem의 SQLite에 남는다."

Chat Portal이 local persistent data를 전혀 허용하지 않는 요구라면 vanilla Mem0 library mode는 그대로 채택할 수 없다. 선택지는 다음뿐이다.

1. Mem0를 fork/extension해 `SQLiteManager`를 PostgreSQL history adapter로 교체한다.
2. history SQLite를 영속 volume에 둔다는 예외를 명시적으로 허용한다. 이는 사용자 요구와 다르다.
3. Mem0의 `infer=False` raw insert 또는 외부 extraction을 사용해 SQLite의 session-context 의존도를 줄이고, 이력은 Chat Portal PostgreSQL에서 별도 관리한다. 그래도 Mem0 instance 자체는 SQLite를 연다.
4. Mem0를 fact retrieval engine으로 제한하고, history/compaction/curation은 Portal control plane에서 독립 운영한다.

## 4. Qdrant backend 구현 상세

### 4.1 Collection 생성과 vector 형태

Qdrant adapter는 collection이 없으면 다음을 생성한다.

```text
dense vector: unnamed default vector, cosine distance
sparse vector: named "bm25", IDF modifier
```

`fastembed`가 설치되어 있어야 BM25 sparse vector를 encode한다. 없거나 encode에 실패하면 Mem0는 오류로 멈추지 않고 semantic-only 또는 semantic + entity boost로 degraded operation을 수행한다.

### 4.2 Retrieval은 multi-signal ranking이다

```text
query
  -> lemmatize + entity extraction
  -> dense semantic search (후보 pool, top_k의 최대 4배 또는 60)
  -> BM25 sparse search
  -> entity collection search
  -> score fusion
  -> threshold + top_k 결과
```

중요한 한계는 BM25와 entity matching이 새로운 후보를 발굴하는 recall expansion이 아니라, **semantic result 후보의 ranking boost**라는 점이다. semantic search에서 빠진 memory를 keyword/entity signal만으로 되살리지는 않는다.

### 4.3 Filtering과 payload index

Mem0는 `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `nin`, `contains`, `icontains`, wildcard, `AND`/`OR`/`NOT` filter를 Qdrant query filter로 변환한다. Chat Portal의 hierarchy/scope query에는 충분히 강한 표현력이다.

그러나 adapter가 자동으로 만드는 Qdrant payload index는 현재 소스 기준 다음 네 필드뿐이다.

```text
user_id, agent_id, run_id, actor_id
```

`tenant_id`, `project_id`, `memory_tier`, `memory_type`, `status`를 많이 필터한다면 Chat Portal의 Qdrant migration/administration code에서 직접 payload index를 만들어야 한다.

공식 metadata filtering 문서는 `indexed_fields` Qdrant config 예시를 제시하지만, 현재 `QdrantConfig` 소스는 허용되지 않은 extra field를 validation error로 거부한다. 즉 이 문서/코드 조합으로는 `indexed_fields`가 동작한다고 보장할 수 없다. 이번 조사에서는 **직접 Qdrant client로 index를 provision하는 방식**을 안전한 운영 결론으로 둔다.

### 4.4 기존 Qdrant collection 재사용

Mem0는 OpenViking처럼 전용 sidecar metadata collection을 요구하지는 않는다. 하지만 Chat Portal 기존 RAG collection과 Mem0 collection을 공유하는 것은 권장하지 않는다.

- dense vector dimension과 embedding model이 다를 수 있다.
- Mem0는 `data`, `hash`, `text_lemmatized`, scope metadata와 BM25 sparse slot을 기대한다.
- entity collection lifecycle도 함께 관리해야 한다.
- retention/delete/reset이 RAG data에 영향을 줄 위험이 있다.

권장 namespace는 다음과 같다.

```text
Qdrant
  chat_portal_rag                 # 기존 문서 RAG
  chat_portal_mem0                # Mem0 memory only
  chat_portal_mem0_entities       # Mem0 entity linking
```

## 5. Entity linking은 Graph Memory가 아니다

과거 Mem0 OSS에는 Neo4j 등 graph store를 연결하는 graph memory 기능이 있었다. 최신 OSS migration guide는 graph store support를 제거하고, entity linking으로 대체했다고 명시한다.

현재 구현은 다음처럼 동작한다.

```text
new memory text
  -> noun/entity extraction
  -> entity collection에서 exact 또는 high-similarity match
  -> entity payload의 linked_memory_ids 누적
  -> query entity가 매칭되면 linked memory에 score boost
```

이는 관계 그래프를 직접 query/traverse하는 기능이 아니다. search response에 graph relation을 노출하거나 entity edge를 따라 탐색하는 설계가 필요하면 Mem0 OSS만으로는 부족하다.

Chat Portal이 entity graph를 원한다면 선택지는 다음이다.

- PostgreSQL에 `memory_entities`, `memory_entity_links`를 control plane으로 직접 유지한다.
- 별도 graph DB를 도입한다.
- Hindsight처럼 graph/observation 모델이 강한 후보를 비교한다.

## 6. Explicit update/delete/history의 의미

자동 extraction은 ADD-only지만 public API에는 explicit lifecycle operation이 남아 있다.

| API | 실제 행동 |
| --- | --- |
| `add()` | 추출 또는 raw memory insert. V3 자동 경로는 ADD-only |
| `update(memory_id, ...)` | Qdrant point vector/payload 갱신, SQLite history에 UPDATE 기록 |
| `delete(memory_id)` | vector point 삭제, SQLite history에 DELETE 기록, entity link 정리 시도 |
| `delete_all(user_id/agent_id/run_id)` | 해당 기본 scope의 memory를 반복 삭제 |
| `history(memory_id)` | SQLite `history` table 조회 |
| `reset()` | vector collection과 SQLite history를 reset |

여기서 audit의 한계가 있다. memory vector write와 SQLite history write는 하나의 distributed transaction이 아니다. Qdrant write가 성공한 뒤 SQLite history insert가 실패하거나 그 반대인 경우, Mem0가 두 저장소의 정합성을 복구하는 outbox/redo log를 제공하는 구조는 현재 소스에서 확인하지 못했다.

Chat Portal이 compliance/audit를 요구한다면 PostgreSQL에 별도 `memory_commands` 또는 outbox를 두고, Mem0 호출 전후 상태와 source evidence를 기록해야 한다.

## 7. Library mode와 self-hosted server mode

### 7.1 Library mode

```text
Chat Portal API/Worker process
  -> Memory 또는 AsyncMemory
    -> LLM / Embedder / Reranker
    -> Qdrant memory + entity collections
    -> local SQLite history.db
```

장점:

- Chat Portal authorization과 metadata policy를 코드에서 직접 강제할 수 있다.
- DeepAgents 실행 lifecycle과 같은 process 또는 worker job 안에서 제어하기 쉽다.
- remote Qdrant 연결과 custom `MemoryService` PoC가 빠르다.

단점:

- history SQLite가 application instance 또는 mounted volume에 결속된다.
- 여러 API replica가 각각 다른 `history.db`를 가지면 extraction context/history가 분산된다.
- Mem0 오류와 LLM/embedding 지연이 Chat Portal process resource에 직접 영향을 준다.
- 여러 서비스가 memory를 공유하려면 공통 wrapper와 policy를 모두 배포해야 한다.

### 7.2 Self-hosted REST server mode

```text
Chat Portal API / Worker / Bot
  -> HTTP
    -> Mem0 FastAPI server
      -> PostgreSQL app DB: user, API key, settings override, request log
      -> Qdrant or pgvector: memory vectors
      -> /app/history/history.db: Mem0 history + recent messages
```

공식 self-hosted compose의 default memory vector backend는 PostgreSQL + pgvector다. server default config는 `history_db_path=/app/history/history.db`를 사용하고 development compose는 `./history:/app/history` volume을 mount한다.

즉 self-hosted mode도 SQLite history 의존성을 없애지 않는다. 단지 history 파일의 위치가 library process의 `~/.mem0/history.db`에서 server container volume으로 옮겨진다.

장점:

- REST API, dashboard, API key, request log, configuration persistence를 분리된 서비스로 제공한다.
- 여러 언어/서비스가 같은 memory API를 사용할 수 있다.
- Mem0 process 장애를 Chat Portal API process와 분리할 수 있다.

단점:

- Qdrant/LLM/SQLite history/app PostgreSQL까지 여러 stateful dependency를 운영한다.
- multi-replica history SQLite의 공유/lock/consistency 모델이 기본 compose에 없다.
- Chat Portal의 tenant authorization을 서버 API key만으로 해결할 수 없다.

### 7.3 Server mode에서 Qdrant를 쓸 수 있는가

결론은 **코드 기준 가능하지만 reference deployment의 주 경로는 아니다**다.

근거:

- server는 `Memory.from_config()`로 현재 config를 재생성한다.
- `POST /configure`는 config override를 server PostgreSQL app DB에 저장하고 restart 후 다시 적용한다.
- Qdrant client는 core dependency에 포함되어 있다.
- `/configure`의 bundled-provider validation은 LLM/embedder provider만 제한하며 vector_store provider는 별도로 차단하지 않는다.

하지만 공식 self-hosted guide와 compose는 pgvector default만 다룬다. 따라서 production server mode + Qdrant는 다음을 PoC로 검증해야 한다.

1. `POST /configure` 후 Qdrant URL/API key/collection 설정이 restart 뒤에도 적용되는지
2. main collection과 entity collection이 기대한 namespace에 생성되는지
3. server의 history SQLite volume이 재배포/rollback 때 보존되는지
4. Qdrant/LLM outage가 API endpoint에서 어떻게 error mapping 되는지
5. custom LLM/embedder가 필요할 때 image rebuild와 provider allowlist 변경이 필요한지

## 8. Server 인증과 multi-tenancy의 실제 경계

self-hosted server는 JWT, per-user API key, legacy admin API key를 제공한다. 이는 "누가 Mem0 server API에 접속할 수 있는가"를 제어한다.

그러나 현재 endpoint 구현을 보면 일반 API key로도 요청 body/query의 `user_id`, `agent_id`, `run_id`, `filters`를 그대로 Mem0 core에 전달한다. `GET /memories/{memory_id}`, `PUT /memories/{memory_id}`, `DELETE /memories/{memory_id}`, `POST /search`는 authenticated server user와 memory payload scope를 자동 비교하지 않는다.

따라서 다음 가정은 위험하다.

> "Mem0 self-hosted에서 사용자별 API key를 발급하면 memory tenant isolation이 자동으로 된다."

정확한 역할 분리는 다음과 같다.

| 계층 | 책임 |
| --- | --- |
| Mem0 API key/JWT | Mem0 server access 인증 |
| Chat Portal authz | 호출자가 어떤 tenant/user/project memory를 읽고 쓸 수 있는지 판정 |
| MemoryService | 모든 add/search/get/update/delete에 required scope filter와 ownership check 부착 |
| Qdrant payload | 실제 retrieval pruning을 위한 `tenant_id` 등 metadata |
| PostgreSQL control plane | ownership, policy, audit, deletion ledger |

Mem0 REST API를 browser/client에 직접 노출하는 것보다, Chat Portal backend만 내부 네트워크에서 호출하는 구조가 더 안전하다.

## 9. PostgreSQL, MinIO, Redis와의 결합 경계

### 9.1 PostgreSQL

Mem0와 Postgres는 세 역할로 구분해야 한다.

| 역할 | Mem0 기본 제공 여부 | Chat Portal 권장 |
| --- | --- | --- |
| Memory vector store | pgvector provider로 가능 | 이미 Qdrant를 쓴다면 선택 사항 |
| Self-hosted server app DB | 제공 | users, API keys, config overrides, request log용 별도 schema/DB |
| Memory control plane | 제공하지 않음 | Portal PostgreSQL에 직접 구현 |
| Mem0 history/messages | 현재 SQLite only | 커스텀 adapter/fork 없이는 Postgres로 대체 불가 |

Portal PostgreSQL control plane에는 최소한 아래가 필요하다.

```text
memory_nodes            # Mem0 memory id와 business scope/path/current state
memory_commands         # add/update/delete 요청의 idempotency/audit
memory_evidence_refs    # MinIO source artifact와 line/turn reference
memory_promotions       # L1 -> L2/L3 승격 및 conflict 처리 상태
memory_provider_runs    # Mem0/LLM/vector 호출 결과와 재시도 상태
```

### 9.2 MinIO

Mem0에는 MinIO/object storage backend가 없다. MinIO에는 다음만 둔다.

- 동의된 raw transcript와 attachment
- memory 생성 근거 snapshot/evidence bundle
- offline evaluation dataset
- export, deletion/retention 작업의 artifact

Mem0 Qdrant payload에는 MinIO object 자체가 아니라 immutable `source_ref` 또는 evidence id만 저장한다. memory text와 evidence 원문을 Qdrant payload에 통째로 넣지 않는다.

### 9.3 Redis

Mem0 최신 OSS에는 Redis vector store provider가 있을 수 있지만, Chat Portal의 기존 Redis를 durable memory store로 전환하는 것은 권장하지 않는다. 이 문서에서 Redis의 적절한 위치는 runtime coordination이다.

| Redis 용도 | 이유 |
| --- | --- |
| retrieval cache | 같은 agent run에서 반복되는 search 결과 캐시 |
| materialized context cache | DeepAgent에 주입할 memory bundle의 짧은 TTL 보관 |
| idempotency key | session close/worker retry의 duplicate Mem0 add 방지 |
| distributed lock | 같은 fact/promotion을 동시 update하는 충돌 완화 |
| job queue/state | extraction review, promotion, audit outbox 처리 |

Redis는 Mem0 history SQLite의 대체물이 아니다. history는 재현 가능하고 감사 가능한 저장소가 필요하므로 PostgreSQL/MinIO control plane로 보강해야 한다.

## 10. OpenViking식 계층형 설계를 Mem0에 얹을 수 있는가

가능하다. 단, Mem0가 hierarchy를 제공해서가 아니라 Chat Portal이 hierarchy를 metadata와 PostgreSQL catalog로 구현하고 Mem0를 ingestion/retrieval engine으로 제한해야 한다.

### 10.1 책임 분리

```text
OpenViking에서 차용
  -> URI/path namespace, L0/L1/L2, promotion/compaction, source-of-truth 분리

Mem0
  -> fact extraction, embedding, hybrid search, explicit CRUD

Qdrant
  -> main memory + entity collection, vector retrieval, metadata pruning

PostgreSQL
  -> hierarchy catalog, version, policy, audit, ownership, current-state projection

MinIO
  -> transcript, evidence, attachment, snapshot

Redis
  -> cache, lock, queue, idempotency

DeepAgents
  -> task execution, working files, tool use, memory candidate proposal
```

### 10.2 추천 계층

| 계층 | 목적 | 권위 저장소 | Mem0 사용 여부 |
| --- | --- | --- | --- |
| L0 Runtime | 현재 실행의 scratchpad, task state, temporary decision | DeepAgent state / Redis | 보통 저장하지 않음 |
| L1 Working | 며칠 내 재사용 가능성이 높은 임시 작업 사실 | PostgreSQL catalog + Qdrant payload | 필요 시 TTL memory |
| L2 Project | project convention, repository rule, durable decision | PostgreSQL current-state + MinIO evidence | Mem0 recall 대상 |
| L3 User/Org | 장기 user preference, organization policy | PostgreSQL current-state + MinIO evidence | Mem0 recall 대상 |

핵심은 Mem0 `add()`가 L2/L3의 current state를 직접 결정하게 두지 않는 것이다. Mem0는 evidence-derived candidate를 생성하고, Portal job이 state/provenance/promotion을 결정해야 한다.

### 10.3 Path와 metadata contract

```text
memory://tenant/{tenant_id}/user/{user_id}/preferences/response-style
memory://tenant/{tenant_id}/project/{project_id}/facts/deploy-policy
memory://tenant/{tenant_id}/project/{project_id}/decisions/no-direct-vercel
memory://tenant/{tenant_id}/agent/{agent_id}/experiences/browser-qa
```

Qdrant/Mem0 metadata contract 예시:

```json
{
  "tenant_id": "t_123",
  "user_id": "u_456",
  "project_id": "p_chat_portal",
  "agent_id": "deepagent_default",
  "memory_path": "memory://tenant/t_123/project/p_chat_portal/facts/deploy-policy",
  "memory_tier": "L2_PROJECT",
  "memory_kind": "durable_fact",
  "status": "active",
  "source_evidence_id": "ev_789",
  "supersedes_memory_id": null,
  "created_at": "2026-07-12T00:00:00Z"
}
```

`tenant_id`, `project_id`, `memory_tier`, `memory_kind`, `status`에는 Qdrant payload index를 Mem0 밖에서 생성한다. 모든 search에는 `tenant_id`와 적어도 하나의 user/project/agent scope를 포함한다.

### 10.4 Correction과 conflict 정책

Mem0 자동 ADD-only는 evidence journal에는 잘 맞지만 current fact projection에는 부족하다. 예를 들어 "직접 Vercel 배포 금지"가 "이제 staging은 허용"으로 바뀌면 새 fact가 추가될 뿐 이전 fact가 자동 폐기되지 않는다.

권장 흐름은 다음과 같다.

```text
conversation/agent result
  -> candidate extraction by Mem0
  -> PostgreSQL command/audit row
  -> scope/path 기준 current memory 조회
  -> policy decision
       add new evidence
       explicit Mem0 update
       set old memory status=superseded
       keep both but mark conflict
  -> MinIO evidence reference persist
  -> Qdrant payload/index update
```

이 정책은 Mem0의 `update()`와 `delete()`를 사용할 수 있지만, 그 호출 자체를 LLM에게 맡기지 않는다.

## 11. DeepAgents 결합성

Mem0는 DeepAgents의 filesystem, planning, subagent orchestration을 대체하지 않는다. 가장 안정적인 결합은 Mem0를 직접 tool로 무제한 노출하는 대신 Portal `MemoryService`를 통해 retrieval 결과를 context file로 materialize하는 방식이다.

```text
request
  -> MemoryService retrieves L3, L2, then L1 with mandatory filters
  -> score/provenance/policy filtering
  -> DeepAgent working files materialized
       /context/memory/00_org_policy.md
       /context/memory/10_project_facts.md
       /context/memory/20_user_preferences.md
       /context/memory/30_working_recall.md
  -> DeepAgent execution
  -> candidate event emitted
  -> background review/promotion -> Mem0 explicit operation
```

이 구조의 장점은 다음과 같다.

- provider 교체가 DeepAgent prompt/filesystem contract를 깨지 않는다.
- 어떤 memory가 agent 행동에 영향을 줬는지 run record로 남길 수 있다.
- tenant filter와 privacy policy를 agent tool call 전에 강제한다.
- Mem0 extraction의 ADD-only 특성을 Portal curation workflow로 보완한다.

subagent 결과는 기본적으로 L0 runtime artifact로 취급한다. 성공/재사용성/evidence 기준을 통과한 결과만 L2/L3 candidate로 승격해야 memory pollution을 줄일 수 있다.

## 12. Library mode와 server mode의 재평가

| 관점 | Library mode | Self-hosted server mode |
| --- | --- | --- |
| primary fit | 단일 Chat Portal backend/worker PoC | 여러 runtime가 공용 memory API를 쓸 때 |
| Qdrant | 직접 config, 가장 단순 | 코드상 가능, pgvector default에서 override 검증 필요 |
| history/messages | local `history.db` | `/app/history/history.db` volume |
| tenant authz | Portal 코드에서 강제하기 쉬움 | API key만으로는 payload scope 강제 안 됨 |
| control plane | Portal PostgreSQL을 직접 사용 | Mem0 app DB + Portal control plane 둘 다 필요 |
| HA | process/volume에 결속 | API process는 분리되지만 SQLite history replica 전략 필요 |
| LLM/embedder choice | core provider dependency 범위에서 선택 | shipped image는 OpenAI/Anthropic/Gemini LLM, OpenAI/Gemini embedder allowlist 중심 |
| 추천 단계 | 첫 PoC | shared platform을 정말 요구할 때 |

초기 Chat Portal에는 library mode가 더 낫다. 다만 이는 "모든 데이터를 외부 DB에만 저장"하는 선택이 아니다. history SQLite를 어떻게 처리할지 먼저 결정하지 못하면 self-hosted server mode로 바꿔도 동일한 문제가 남는다.

## 13. 운영, 장애, 이중화 관점

### 13.1 State가 흩어진다

Mem0를 Qdrant self-hosted server mode로 운영하면 state는 최소 네 곳에 나뉜다.

```text
Qdrant                 -> memory vectors, BM25 sparse vectors, entity links
PostgreSQL (Mem0 app)  -> users, API keys, config override, request logs
SQLite history.db      -> history + recent extraction messages
PostgreSQL (Portal)    -> policy, ownership, audit, promotion/current-state
MinIO                  -> evidence/transcript/attachment
```

각 저장소의 backup/restore point가 다르면 memory id, history, evidence reference가 어긋날 수 있다. Mem0 자체가 이 전체를 하나의 transaction 또는 snapshot으로 묶지 않는다.

### 13.2 권장 장애 원칙

- Qdrant 장애: recall과 add가 실패한다. DeepAgent는 policy상 memory 없이 degraded 실행하거나 사용자에게 재시도를 알린다.
- LLM/embedding 장애: V3 `add()`는 LLM failure를 빈 결과로 숨기지 않고 error로 전파한다. background retry/outbox가 필요하다.
- SQLite history 장애: memory vector add 이후 history/message 기록이 어긋날 수 있다. Portal audit으로 감지하고 repair path를 둔다.
- MinIO 장애: evidence가 없는 durable promotion을 보류한다. evidence 없이 fact를 확정하지 않는 정책이 필요하다.
- PostgreSQL control plane 장애: Mem0 direct write를 하지 않고 command outbox를 재시도한다.

### 13.3 HA 결론

Mem0 Platform은 managed HA를 제공할 수 있지만 OSS self-hosted는 vector DB, app DB, history SQLite, API replica를 직접 운영해야 한다. 특히 SQLite history는 Mem0 OSS의 가장 명확한 horizontal scaling 제약이다. 여러 replica가 동일 history DB를 안전하게 공유하는 reference design은 이번 공식 compose와 소스에서 확인하지 못했다.

## 14. Chat Portal 권장 배치

```text
Chat Portal API / DeepAgent workers
  -> MemoryService
      - authorization and mandatory scope filters
      - hierarchy/promotion/conflict policy
      - provider abstraction
  -> Mem0 library mode (initial PoC)
      -> Qdrant: chat_portal_mem0 + chat_portal_mem0_entities
      -> local SQLite: explicitly accepted temporary limitation only
  -> PostgreSQL
      -> memory_nodes, commands, evidence refs, policy, audit, promotion state
  -> MinIO
      -> raw transcript, attachment, evidence, evaluation set
  -> Redis
      -> cache, lock, queue, idempotency
```

운영 목표가 "로컬 persistent storage 0"이라면 다음 중 하나를 먼저 결정해야 한다.

```text
A. Mem0 history SQLite adapter를 PostgreSQL로 교체하는 fork/extension
B. Mem0 OSS는 PoC에만 사용하고 production memory engine을 재선정
C. history SQLite persistent volume을 예외로 허용하고 HA 제한을 문서화
```

이 결정을 미루고 Qdrant만 remote로 바꾸는 것은 요구사항을 충족하지 못한다.

## 15. 도입 전 PoC

### P0: 최신 V3 behavior 확인

1. 동일 사실을 다른 표현으로 두 번 입력한다.
2. 결과가 ADD-only로 누적되는지, exact hash만 제거되는지 본다.
3. explicit `update()`와 `delete()` 후 Qdrant payload, entity collection, SQLite history를 함께 확인한다.
4. conflict/supersede decision을 Portal PostgreSQL policy로 처리할 수 있는지 검증한다.

### P1: Qdrant schema와 hybrid retrieval

1. main/entity collection을 전용 namespace로 만든다.
2. fastembed 설치/미설치에서 BM25 degradation을 확인한다.
3. `tenant_id`, `project_id`, `memory_tier`, `status` payload index를 외부 migration으로 생성한다.
4. semantic-only, semantic+BM25, entity boost의 latency와 precision을 측정한다.
5. 기존 Qdrant collection을 공유하지 않고 rollback 가능한 새 collection으로 migration한다.

### P2: local SQLite 요구사항

1. library mode의 `history_db_path` 생성 위치와 실제 table을 확인한다.
2. pod/container restart와 multi-worker에서 recent message context가 유지되는지 시험한다.
3. history SQLite를 제거/읽기 전용/ephemeral로 둘 때 extraction 품질과 history API가 어떻게 변하는지 측정한다.
4. PostgreSQL history adapter fork 비용을 추정한다.

### P3: tenant authorization

1. 서로 다른 Portal tenant의 memory를 같은 Mem0 server API key로 조회하지 못하도록 gateway test를 만든다.
2. memory id만 아는 요청이 다른 tenant의 get/update/delete에 실패하는지 MemoryService ownership check를 검증한다.
3. raw Mem0 REST endpoint를 외부 browser/client에 공개하지 않는 network policy를 적용한다.

### P4: DeepAgents lifecycle

1. L3 org/user -> L2 project -> L1 working 순서의 filtered recall을 구현한다.
2. materialized context file에 memory id, path, evidence id, score를 기록한다.
3. agent/subagent의 candidate를 바로 durable write하지 않고 outbox/review로 보낸다.
4. memory outage와 stale recall이 agent 행동에 미치는 영향을 측정한다.

## 최종 판단

Mem0는 Chat Portal 후보에서 제외할 제품이 아니다. Qdrant를 이미 운영하고 있고 Apache-2.0을 선호한다면, durable fact/preference retrieval의 첫 PoC 후보로 여전히 강하다.

하지만 OpenViking 조사 후 기준을 높이면 기존 결론은 수정해야 한다.

- Mem0는 계층형 context system이 아니라 vector-first memory engine이다.
- 최신 자동 ingestion은 ADD-only이며, current fact merge/retirement를 별도 control plane이 맡아야 한다.
- Qdrant backend는 강하지만, main collection과 entity collection을 전용으로 운영하고 custom payload index를 외부에서 provision해야 한다.
- PostgreSQL/MinIO/Redis와 결합할 수는 있지만, Mem0 내부 history는 SQLite라는 별도 local state를 남긴다.
- self-hosted server는 access auth와 dashboard를 주지만 tenant data authorization과 horizontal history scaling을 해결하지 않는다.

따라서 Chat Portal에서의 정확한 역할은 다음이다.

```text
Mem0        = durable fact candidate extraction + hybrid semantic recall engine
Qdrant      = memory/entity retrieval backend
PostgreSQL  = hierarchy, policy, ownership, audit, current-state control plane
MinIO       = transcript/evidence/archive source of truth
Redis       = runtime cache/lock/queue/idempotency
DeepAgents  = task runtime, skills, working filesystem, candidate producer
```

OpenViking의 URI/L0-L1-L2/lifecycle을 차용한 계층형 구조는 Mem0 위에 구현할 수 있다. 다만 그 구현 주체는 Mem0가 아니라 Chat Portal `MemoryService`와 PostgreSQL control plane이다. 그리고 "local storage를 쓰지 않는다"가 비타협 요구사항이면, Mem0 history SQLite를 대체할 방법을 먼저 PoC 또는 fork 설계로 확정해야 한다.

## 참고 자료

### 공식 문서

- [Configure the OSS Stack](https://docs.mem0.ai/open-source/configuration): vector store, LLM, embedder, reranker 설정. 신뢰도: 높음.
- [Qdrant](https://docs.mem0.ai/components/vectordbs/dbs/qdrant): Qdrant 연결 값과 기본 collection/path. 신뢰도: 높음.
- [Self-Hosted Setup](https://docs.mem0.ai/open-source/setup): REST server, dashboard, app PostgreSQL, auth 구성. 신뢰도: 높음.
- [REST API Server](https://docs.mem0.ai/open-source/features/rest-api): CRUD/API key/request log surface. 신뢰도: 높음.
- [Enhanced Metadata Filtering](https://docs.mem0.ai/open-source/features/metadata-filtering): filter 연산자와 Qdrant filter capability. 신뢰도: 높음. 단 `indexed_fields` 예시는 현재 소스와 충돌하므로 그대로 채택하지 않음.
- [OSS V3 Migration](https://docs.mem0.ai/migration/oss-v2-to-v3): ADD-only extraction, hybrid retrieval, entity linking, graph store 제거. 신뢰도: 높음.
- [Async Memory](https://docs.mem0.ai/open-source/features/async-memory): async API와 history/delete semantics. 신뢰도: 높음.

### 소스 코드 확인 지점

- [MemoryConfig](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/mem0/configs/base.py): `history_db_path`만 제공하며 history provider가 없음.
- [Memory V3 pipeline](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/mem0/memory/main.py): ADD-only, batch insert, entity link, explicit update/delete.
- [SQLiteManager](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/mem0/memory/storage.py): history/messages SQLite schema.
- [Qdrant adapter](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/mem0/vector_stores/qdrant.py): dense/BM25 sparse vector, auto index, Qdrant filtering.
- [REST server main](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/server/main.py): pgvector default, `/configure`, endpoint authorization behavior.
- [Server state](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/server/server_state.py): runtime config persistence와 Memory instance 재생성.
- [Server compose](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/server/docker-compose.yaml): history volume과 pgvector reference deployment.
