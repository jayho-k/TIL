# OpenViking 분석 초안

조사일: 2026-07-03  
목적: 이미 MinIO를 사용 중인 상황에서 OpenViking을 추가로 도입할 이유가 있는지 판단한다.

## 1. 한 줄 결론

OpenViking은 MinIO 같은 오브젝트 스토리지를 대체하거나 감싸는 저장소라기보다, AI Agent가 사용하는 memory, resource, skill을 `viking://` 경로 체계로 조직하고 검색하는 **context database / context filesystem**에 가깝다.

따라서 판단 기준은 "MinIO에 같은 구조로 파일을 저장할 수 있는가?"가 아니라, "파일/문서/메모리/스킬을 계층형 context로 만들고, 요약 계층과 recursive retrieval, memory extraction까지 제품화된 형태로 쓸 필요가 있는가?"이다.

## 2. OpenViking이 풀려는 문제

공식 README는 Agent 개발에서 다음 문제를 강조한다.

- memory, resource, skill이 서로 다른 저장소/코드/벡터 DB에 흩어져 관리가 어렵다.
- 긴 실행 과정에서 context가 계속 쌓이는데 단순 truncation/compression은 정보 손실을 만든다.
- 일반 RAG는 flat chunk 중심이라 문서나 repo의 디렉터리 구조를 잘 활용하지 못한다.
- retrieval 과정이 불투명해서 왜 특정 context가 들어갔는지 디버깅하기 어렵다.
- memory가 단순 대화 기록에 머물고, agent의 task 경험까지 축적하기 어렵다.

OpenViking의 핵심 아이디어는 모든 context를 파일 시스템처럼 다루는 것이다.

```text
viking://
  resources/
  user/{user_id}/memories/
  user/{user_id}/resources/
  user/{user_id}/skills/
  user/{user_id}/peers/
```

Agent는 `ls`, `tree`, `find`, `grep` 같은 조작 방식으로 context를 탐색하고, 내부적으로는 embedding/vector search와 계층 구조를 결합해 검색한다.

## 3. MinIO와의 관계

현재 공개 README와 `docker-compose.yml` 기준으로 OpenViking의 기본 저장 설정은 S3/MinIO가 아니라 로컬 workspace다.

```json
{
  "storage": {
    "workspace": "/home/your-name/openviking_workspace"
  }
}
```

Docker Compose도 `~/.openviking:/app/.openviking` 볼륨을 붙이는 단순 구성이고, 별도 MinIO/S3 서비스는 없다.

즉 현재 확인한 범위에서는:

- OpenViking을 쓰기 위해 MinIO가 필수는 아니다.
- OpenViking이 MinIO 위에 object layout을 강제하는 구조도 아니다.
- 이미 MinIO가 있다면 원본 문서, 이미지, 첨부 파일, artifact 저장소로 계속 쓰고, OpenViking은 그 위의 context index/memory layer로 붙이는 식이 더 자연스럽다.

직접 MinIO에 OpenViking과 비슷한 구조를 만들 수는 있다. 예를 들어 `resources/project/docs/api/auth.md`, `resources/project/docs/.overview.md` 같은 prefix convention을 정하고, 메타데이터 DB와 벡터 DB를 별도로 붙이면 된다. 하지만 MinIO 자체는 object key-value 저장소라서 directory semantics, recursive retrieval, memory extraction, retrieval trajectory 관찰성은 직접 구현해야 한다.

## 4. OpenViking의 주요 기능

### 4.1 Filesystem Management Paradigm

context를 flat chunk가 아니라 URI 기반 가상 파일 시스템으로 본다.

- `viking://resources/...`
- `viking://user/{id}/memories/...`
- `viking://user/{id}/skills/...`

이 방식의 장점은 사람이 이해하기 쉬운 구조와 agent가 조작하기 쉬운 command interface를 동시에 제공한다는 점이다.

### 4.2 Tiered Context Loading

OpenViking은 context를 L0/L1/L2 계층으로 나눈다.

- L0 Abstract: 짧은 요약, relevance check 용도
- L1 Overview: 계획/탐색에 쓸 핵심 정보
- L2 Details: 원문 전체

이 구조는 "모든 chunk를 벡터 검색해서 바로 prompt에 넣는 방식"보다 token 사용량을 줄이고, agent가 먼저 개요를 보고 필요한 상세만 열람하게 만드는 데 초점이 있다.

### 4.3 Directory Recursive Retrieval

공식 설명의 retrieval 흐름은 다음과 같다.

1. intent analysis로 retrieval condition을 만든다.
2. vector retrieval로 high-score directory를 먼저 찾는다.
3. 해당 directory 내부에서 2차 검색한다.
4. 하위 directory가 있으면 재귀적으로 탐색한다.
5. 결과를 합쳐 최종 context로 반환한다.

이는 "문서 조각 하나의 유사도"보다 "그 조각이 속한 디렉터리/문서 구조"를 활용하려는 전략이다.

### 4.4 Automatic Session Management

대화나 task 실행 결과에서 user memory와 agent experience memory를 추출해 장기 기억으로 축적한다.

이 부분은 단순 RAG 저장소와의 가장 큰 차이다. 단순히 문서를 검색하는 것이 아니라, agent가 사용하면서 memory base가 계속 갱신되는 것을 목표로 한다.

## 5. 연구/논문 기반

OpenViking README는 VikingMem 논문을 기반으로 한다고 설명한다.

VikingMem은 장기 상호작용 상태를 관리하기 위한 Memory Base 개념을 제안한다. 핵심은 원시 이벤트 스트림에서 가치 있는 memory를 선택적으로 추출하고, entity/event abstraction으로 memory를 점진적으로 요약/수정/시간 가중하는 것이다.

또 다른 2026년 논문은 vector DB에서 디렉터리 구조를 first-class semantic으로 다루는 문제를 다룬다. 기존 vector DB의 metadata filter는 flat attribute에는 적합하지만, `/docs/v2/`, `/archive/` 같은 계층형 scope를 자연스럽게 표현하기 어렵다는 문제를 지적한다. 이 논문에서는 Directory-Semantic Query(DSQ), Directory-Semantic Maintenance(DSM), Trie-based Hierarchical Index(TrieHI)를 제안하고, OpenViking에 TrieHI가 통합되었다고 설명한다.

정리하면 OpenViking의 방향은 일반 vector DB보다 "agent context는 파일 시스템처럼 조직되어야 한다"는 주장에 가깝다.

## 6. 실제 사용 사례

공식 README 기준으로 OpenViking은 다음 연동/평가를 제시한다.

- OpenClaw + OpenViking
- Hermes + OpenViking
- Claude Code + OpenViking
- VikingBot
- OpenViking Studio hosted demo

GitHub 검색 기준으로도 OpenViking 관련 MCP server, Claude Code plugin, OpenClaw memory backend, Rust/Go rewrite 계열 repo가 보인다. 다만 이들은 대부분 생태계 주변 도구나 fork로 보이며, 대규모 상용 production 도입 사례가 공개적으로 충분히 축적된 상태라고 보기는 어렵다.

README의 benchmark는 유용한 참고 자료지만, 프로젝트 자체가 제시한 수치이므로 독립 재현 여부를 따로 확인해야 한다.

## 7. OpenViking을 쓰지 않으면 무엇을 쓰는가?

### 7.1 일반 RAG 스택

가장 흔한 대안은 다음 조합이다.

- 원본 파일 저장: MinIO/S3
- 메타데이터 저장: PostgreSQL/MySQL
- 벡터 검색: Milvus, Qdrant, Weaviate, Chroma, pgvector, OpenSearch vector search
- orchestration: LangChain, LlamaIndex, Haystack 등
- agent memory: LangGraph Store, Mem0, Letta, custom memory service

Milvus standalone도 의존 구성으로 etcd, MinIO, Pulsar를 자동 구성한다고 문서화되어 있다. 즉 MinIO는 이미 vector DB 생태계에서 원본/세그먼트/오브젝트 저장 계층으로 쓰일 수 있다.

### 7.2 Agent memory 특화 도구

OpenViking과 직접 비교할 만한 축은 "agent memory"다.

- Mem0: LLM application을 위한 memory layer. hosted와 open-source/self-host 옵션을 제공한다.
- Letta: memory-first agent 플랫폼. memory blocks, archival memory, context hierarchy, folders/files/passages API를 제공한다.
- LangGraph memory/store: short-term checkpoint와 long-term namespace 기반 JSON document store를 제공한다.

이 도구들은 memory abstraction에는 강하지만, OpenViking처럼 resource, memory, skill을 하나의 virtual filesystem으로 통합하는 방향은 상대적으로 약하거나 직접 설계가 필요하다.

### 7.3 직접 설계

MinIO를 이미 사용하고 있고 scope가 좁다면 직접 설계도 가능하다.

기본 구성 예:

```text
MinIO
  raw/{tenant}/{project}/...
  processed/{tenant}/{project}/...
  context/{tenant}/{project}/.abstract.md
  context/{tenant}/{project}/.overview.md

PostgreSQL
  documents(id, uri, object_key, parent_uri, type, version, metadata)
  context_nodes(id, uri, parent_id, l0, l1, l2_ref, updated_at)
  memories(id, user_id, agent_id, type, content, source_event_id, confidence)

Vector DB
  embedding(id, node_id, uri, parent_uri, depth, text, vector, metadata)
```

이 방식은 기존 인프라와 맞추기 쉽고 lock-in이 작다. 대신 다음을 직접 만들어야 한다.

- ingestion pipeline
- L0/L1/L2 요약 생성 정책
- parent/child directory index
- recursive retrieval
- memory extraction/update policy
- retrieval trace logging
- prompt injection/sensitive data 방어
- reindex/versioning/migration

## 8. 도입 판단 기준

OpenViking을 도입할 이유가 강한 경우:

- Agent가 장기 task를 수행하고, task 경험을 다음 실행에 재사용해야 한다.
- context가 단순 문서 검색이 아니라 memory, resource, skill, user preference까지 포함한다.
- repo, 문서, wiki처럼 계층 구조가 retrieval 품질에 중요하다.
- "왜 이 context가 선택됐는지" 관찰하고 디버깅해야 한다.
- 빠르게 실험해야 하고, 직접 memory/RAGFS 계층을 만들 시간이 없다.

OpenViking 없이 직접 설계가 나은 경우:

- 현재 필요한 것이 단순 문서 검색/QA다.
- MinIO에 저장된 객체를 embedding해서 검색하는 수준이면 충분하다.
- memory extraction이나 agent experience accumulation이 아직 필요 없다.
- 저장소 구조, 보안, 권한, 감사 로그를 이미 사내 표준으로 통제해야 한다.
- AGPLv3 라이선스가 제품/배포 방식과 충돌할 수 있다.
- OpenViking의 내부 구현과 운영 안정성을 충분히 검증하기 어렵다.

## 9. 현재 상황에 대한 임시 결론

이미 MinIO를 쓰고 있다면, OpenViking을 "MinIO를 더 잘 쓰기 위한 도구"로 보는 것은 맞지 않다. MinIO는 원본/대용량 객체 저장 계층이고, OpenViking은 agent가 읽고 갱신하는 context/memory 계층이다.

따라서 지금 단계의 합리적인 판단은 다음이다.

1. MinIO는 계속 raw artifact 저장소로 둔다.
2. OpenViking은 별도 PoC로 설치해 `resources/`, `memories/`, `skills/` 구조와 retrieval 품질을 확인한다.
3. PoC에서 확인할 핵심은 storage 성능이 아니라 다음 세 가지다.
   - 같은 문서를 MinIO + 일반 vector DB로 검색했을 때보다 답변 품질이 좋아지는가?
   - directory recursive retrieval이 실제 프로젝트 문서 구조에서 도움이 되는가?
   - memory extraction/update가 직접 구현할 가치보다 충분히 편한가?

만약 PoC에서 위 세 가지가 뚜렷하지 않다면, OpenViking을 도입하기보다 MinIO + PostgreSQL + vector DB + 직접 memory policy로 가는 편이 더 단순하다.

## 10. 다음 실습 계획

1. OpenViking을 로컬에서 실행한다.
2. MinIO에 이미 있는 문서 일부를 샘플로 export하거나 URL/resource 형태로 OpenViking에 ingest한다.
3. 동일 질의를 두 방식으로 비교한다.
   - Baseline: MinIO 원본 + 일반 vector DB/RAG
   - OpenViking: `viking://resources/...` 기반 recursive retrieval
4. 비교 항목:
   - 검색된 context의 정확도
   - 답변 품질
   - retrieval trace 해석 가능성
   - indexing/reindexing 복잡도
   - 운영 구성 요소 수

## 11. 현재 로컬 PoC 상태

2026-07-03 현재 로컬 환경에서 확인한 내용:

- Docker CLI 설치 확인: `Docker version 28.1.1`
- Docker Compose 설치 확인: `Docker Compose version v2.35.1-desktop.1`
- OpenViking 이미지 실행 전 확인 결과: Docker Desktop Linux engine pipe가 없어 Docker daemon이 실행 중이 아님

따라서 아직 `ghcr.io/volcengine/openviking:latest` 이미지를 pull하거나 컨테이너를 실행하지는 못했다.

Docker Desktop을 실행한 뒤 다음 절차로 PoC를 진행하면 된다.

```powershell
docker pull ghcr.io/volcengine/openviking:latest

docker run --name openviking `
  -p 1933:1933 `
  -v ${PWD}\.codex\research\OpenViking\openviking_home:/app/.openviking `
  ghcr.io/volcengine/openviking:latest
```

실행 후 확인:

```powershell
curl http://127.0.0.1:1933/health
```

주의할 점:

- OpenViking은 embedding model과 VLM 설정이 필요하다.
- 공식 README 기준으로 `openviking-server init` / `openviking-server doctor`가 권장 초기화 흐름이다.
- MinIO는 기본 의존성이 아니므로 PoC에서는 먼저 OpenViking 자체 ingest/retrieval 품질을 확인하고, 이후 MinIO 객체를 resource source로 연결하는 방식을 검토한다.

## 12. API 호출 기준 내부 동작 분석

### 12.1 결론: 파일 저장만 하는가?

아니다. 파일 저장 자체는 OpenViking의 일부일 뿐이다. 실제 기능은 크게 네 가지다.

1. 외부 문서/파일/repo를 `viking://` 계층 구조로 ingest한다.
2. 비동기 queue에서 L0 `.abstract.md`, L1 `.overview.md`를 만들고 vector index에 넣는다.
3. 검색 시 단순 vector top-k가 아니라 directory 기반 hierarchical retrieval을 수행한다.
4. session commit 시 대화/도구 사용 이력을 archive하고 long-term memory를 추출한다.

다만 이 기능들이 모두 항상 자동으로 동작하는 것은 아니다. 어떤 API를 호출하느냐에 따라 다르다.

### 12.2 `POST /api/v1/resources`: resource 추가

HTTP 예시:

```bash
curl -X POST http://localhost:1933/api/v1/resources \
  -H "Content-Type: application/json" \
  -d '{
    "path": "https://raw.githubusercontent.com/volcengine/OpenViking/refs/heads/main/README.md",
    "parent": "viking://resources/openviking",
    "wait": true,
    "reason": "OpenViking 분석용 공식 README"
  }'
```

라우터 흐름:

```text
server/routers/resources.py
  AddResourceRequest
  -> service.resources.add_resource(...)
```

서비스 흐름:

```text
ResourceService.add_resource
  -> target URI 결정
  -> ResourceProcessor.process_resource(...)
  -> Parser가 원본을 temp 구조로 변환
  -> TreeBuilder가 AGFS/VikingFS로 이동
  -> SemanticQueue에 L0/L1 생성 및 vectorization 작업 등록
  -> wait=true면 queue 완료까지 대기
  -> wait=false면 task_id 반환 후 background 처리
```

문서 기준 추출 흐름:

```text
Input File
  -> Parser
  -> TreeBuilder
  -> SemanticQueue
  -> L0/L1 Generation
  -> Vector Index
```

여기서 OpenViking이 실제로 해주는 것은 단순 저장보다 많다.

- URL/local upload/repo를 받아 parser로 구조화한다.
- 큰 문서는 header 기반으로 나누고, code repo는 `.gitignore`와 일반 non-code directory를 고려한다.
- `.abstract.md`, `.overview.md`를 생성한다.
- vector index에는 URI, parent_uri, context_type, vector, sparse_vector, abstract, active_count 같은 검색용 metadata를 저장한다.
- 원문은 AGFS/VikingFS에 두고 vector index에는 원문 전체를 넣지 않는다.

### 12.3 `POST /api/v1/search/find`: 단순 semantic search

HTTP 예시:

```bash
curl -X POST http://localhost:1933/api/v1/search/find \
  -H "Content-Type: application/json" \
  -d '{
    "query": "OpenViking이 MinIO와 어떻게 다른가",
    "target_uri": "viking://resources/openviking",
    "limit": 10,
    "include_provenance": true
  }'
```

라우터 흐름:

```text
server/routers/search.py
  /api/v1/search/find
  -> service.search.find(...)
  -> viking_fs.find(...)
```

`find()`의 특징:

- session context를 사용하지 않는다.
- intent analysis를 하지 않는다.
- 단일 query로 빠르게 검색한다.
- 그래도 내부 retrieval은 hierarchical retriever를 탄다.

문서상 `find()`와 `search()` 차이:

```text
find()
  - session context 없음
  - intent analysis 없음
  - single query
  - 낮은 latency

search()
  - session context 필요
  - LLM intent analysis 사용
  - 0~5 TypedQueries 생성 가능
  - 복잡한 task용
```

### 12.4 `POST /api/v1/search/search`: session-aware search

HTTP 예시:

```bash
curl -X POST http://localhost:1933/api/v1/search/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "이 프로젝트에 맞는 context를 찾아줘",
    "session_id": "analysis_001",
    "target_uri": "viking://resources/",
    "limit": 10,
    "telemetry": true
  }'
```

라우터 흐름:

```text
server/routers/search.py
  /api/v1/search/search
  -> session load
  -> service.search.search(...)
  -> session.get_context_for_search(query)
  -> viking_fs.search(...)
```

IntentAnalyzer 흐름:

```text
Session compression summary
  + 최근 5개 message
  + 현재 query
  -> query_planner/VLM 호출
  -> 0~5 TypedQuery 생성
```

TypedQuery는 다음 정보를 가진다.

```python
TypedQuery(
  query="rewritten query",
  context_type="memory/resource/skill",
  intent="query purpose",
  priority=1~5,
)
```

즉 `search()`는 query 하나를 그대로 날리는 것이 아니라, 대화 맥락을 보고 "memory를 찾아야 하는지, resource를 찾아야 하는지, skill을 찾아야 하는지"를 나눠 검색할 수 있다.

### 12.5 hierarchical retrieval 내부

핵심 구현 파일:

```text
openviking/retrieve/hierarchical_retriever.py
```

흐름:

```text
1. query embedding 생성
2. target_uri가 있으면 root_uris로 사용
   없으면 context_type별 기본 root directory 선택
3. global vector search로 시작 directory 후보 탐색
4. directory 후보와 root directory를 merge
5. priority queue로 child directory/file을 recursive search
6. L2 file은 terminal hit로 수집
7. L0/L1 directory는 계속 하위 탐색
8. rerank가 설정되어 있으면 directory/child score를 rerank
9. top-k가 일정 round 동안 변하지 않으면 convergence로 중단
10. MatchedContext로 변환
```

코드상 확인되는 주요 값:

```python
MAX_CONVERGENCE_ROUNDS = 3
GLOBAL_SEARCH_TOPK = 10
MAX_PARALLEL_CHILD_SEARCHES = 4
LEVEL_URI_SUFFIX = {0: ".abstract.md", 1: ".overview.md"}
```

score 계산에는 `score_propagation_alpha`가 들어간다.

```text
final_score = alpha * child_score + (1 - alpha) * parent_score
```

현재 문서상 기본값은 `retrieval.score_propagation_alpha = 1.0`이라 parent score를 섞지 않고 child score 중심으로 본다.

### 12.6 `POST /api/v1/search/grep`, `glob`, `ls`, `tree`

이쪽은 semantic retrieval이 아니다. 파일 시스템 조작에 가깝다.

```bash
curl -X POST http://localhost:1933/api/v1/search/grep \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "viking://resources/openviking",
    "pattern": "MinIO",
    "case_insensitive": true
  }'
```

흐름:

```text
server/routers/search.py
  /grep
  -> service.fs.grep(...)

server/routers/filesystem.py
  /fs/ls
  -> service.fs.ls(...)

server/routers/filesystem.py
  /fs/tree
  -> service.fs.tree(...)
```

이 기능들은 "agent가 context filesystem을 탐색한다"는 UX를 위해 중요하지만, 자체적으로 LLM memory나 recursive semantic search를 하는 것은 아니다.

### 12.7 `POST /api/v1/sessions/{session_id}/commit`: memory extraction

HTTP 예시:

```bash
curl -X POST http://localhost:1933/api/v1/sessions/analysis_001/commit \
  -H "Content-Type: application/json" \
  -d '{"keep_recent_count": 10}'
```

라우터 흐름:

```text
server/routers/sessions.py
  /sessions/{session_id}/commit
  -> service.sessions.commit_async(...)
  -> session.commit_async(...)
```

문서 기준 2-phase 처리:

```text
Phase 1: synchronous
  1. compression_index 증가
  2. messages를 archive directory에 messages.jsonl로 기록
  3. current messages 정리 또는 keep_recent_count만 남김
  4. task_id 반환

Phase 2: asynchronous background
  5. LLM으로 structured summary 생성
  6. .abstract.md, .overview.md 생성
  7. long-term memory 추출
  8. memory_diff.json 기록
  9. active_count 업데이트
  10. .done marker 기록
```

memory extraction 흐름:

```text
Messages
  -> LLM Extract
  -> Candidate Memories
  -> Vector Pre-filter로 유사 memory 검색
  -> LLM Dedup Decision
  -> create / skip / merge / delete
  -> AGFS에 memory write
  -> Vectorize
```

지원한다고 문서화된 memory category:

- user: profile, preferences, entities, events
- agent: cases, patterns, tools, skills

감사/추적용으로 archive directory에 `memory_diff.json`을 남긴다고 되어 있다. 이 파일은 adds/updates/deletes를 기록하므로, 최소한 memory 변경 trace는 존재한다.

### 12.8 `POST /api/v1/content/reindex`: reindex

HTTP 예시:

```bash
curl -X POST http://localhost:1933/api/v1/content/reindex \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "viking://resources/openviking",
    "mode": "vectors_only",
    "wait": true
  }'
```

라우터 흐름:

```text
server/routers/content.py
  /content/reindex
  -> service.reindex(uri, mode, wait, ctx)
```

README 기준 mode:

- `vectors_only`: 기존 semantic artifact는 유지하고 vector만 재생성
- `semantic_and_vectors`: `.abstract.md`, `.overview.md` 같은 semantic artifact를 다시 만들고 vector도 재생성

주의:

- 라우터는 root/admin role을 요구한다.
- 공개 README에는 `semantic` 또는 `full` alias는 없다고 되어 있다.

### 12.9 trace / observability

완전한 "retrieval trace API"가 명확히 어떤 형태로 반환되는지는 추가 검증이 필요하다. 다만 코드와 문서상 다음은 확인된다.

- `FindRequest`, `SearchRequest`에 `telemetry` 옵션이 있다.
- 응답에 `telemetry=execution.telemetry`가 포함될 수 있다.
- `include_provenance` 옵션이 있고, result의 `to_dict(include_provenance=...)`에 전달된다.
- `observer/retrieval` API가 retrieval quality metrics를 제공한다.
- task API가 background 작업 상태를 조회한다.

따라서 최소한 operation telemetry, provenance, task status, observer metrics는 있다. 하지만 사용자가 기대하는 "검색 과정 전체를 UI나 API에서 directory-by-directory로 보여주는 trace"가 어느 정도 상세한지는 실제 실행으로 확인해야 한다.

### 12.10 최종 판단

OpenViking의 역할은 "파일 저장소"가 아니라 다음 조합이다.

```text
Context ingest
  + virtual filesystem
  + L0/L1/L2 semantic artifact generation
  + vector index
  + hierarchical retrieval
  + session archive
  + memory extraction / dedup / merge
  + reindex / watch / task tracking
```

하지만 사용자가 이미 MinIO + DB + vector DB + 자체 pipeline을 가지고 있다면, OpenViking이 반드시 필요한 것은 아니다. 특히 다음 기능이 필요하지 않다면 도입 가치가 낮다.

- session commit 기반 memory extraction
- memory_diff audit
- resource/memory/skill 통합 URI
- directory recursive semantic retrieval
- L0/L1 자동 생성
- agent가 `ls/tree/read/find/grep`로 context를 탐색하는 인터페이스

반대로 이 기능들을 직접 만들 생각이라면, OpenViking은 그 구현체를 제공하는 후보로 볼 수 있다.

## 참고 자료

- OpenViking GitHub: https://github.com/volcengine/OpenViking
- OpenViking README raw: https://raw.githubusercontent.com/volcengine/OpenViking/main/README.md
- OpenViking docker-compose: https://raw.githubusercontent.com/volcengine/OpenViking/main/docker-compose.yml
- VikingMem paper: https://arxiv.org/abs/2605.29640
- Directory-Aware Query and Maintenance in Vector Databases: https://arxiv.org/abs/2606.16903
- MinIO AIStor docs: https://docs.min.io/aistor/
- Milvus standalone requirements: https://milvus.io/docs/prerequisite-docker.md
- Mem0 docs: https://docs.mem0.ai/introduction
- Letta docs: https://docs.letta.com/
- LangGraph memory docs: https://docs.langchain.com/oss/python/concepts/memory
