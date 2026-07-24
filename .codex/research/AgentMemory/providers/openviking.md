# OpenViking Deep Dive: Context Database 설계와 Chat Portal 적합성

조사일: 2026-07-12

## 조사 범위와 판정 기준

이 문서는 OpenViking의 사용법 튜토리얼이 아니다. Chat Portal의 Agent Memory를 설계하기 위해 다음을 확인한다.

1. OpenViking이 메모리, 리소스, 스킬을 어떤 데이터 모델로 표현하는가
2. 실제 저장소와 인덱스는 어디에 무엇을 저장하는가
3. 계층형 컨텍스트, 세션 압축, 메모리 추출, 검색, 정합성 회복이 어떻게 이어지는가
4. 현재 운영 중인 Qdrant, PostgreSQL, MinIO, Redis와 어떤 경계로 결합할 수 있는가
5. OpenViking 자체를 도입할지, 설계만 차용할지 판단하려면 무엇을 PoC로 검증해야 하는가

## 핵심 결론

OpenViking은 단순한 "장기 메모리 저장 라이브러리"가 아니다. `viking://` URI를 중심으로 Memory, Resource, Skill, Session을 파일시스템처럼 조직하고, 원문 저장(AGFS/RAGFS), 벡터 인덱스, 비동기 요약/임베딩, 검색, 세션 커밋, 메모리 추출, 멀티테넌시를 한 시스템으로 묶은 **self-host 가능한 Context Database**다.

이전 조사에서 Qdrant와 MinIO 결합이 불명확하다고 적은 부분은 최신 공식 문서와 소스 기준으로 수정해야 한다.

- Qdrant: 공식 VectorDB backend다. 단, OpenViking 전용 컬렉션과 전용 metadata sidecar를 사용해야 한다.
- MinIO: 공식 S3-compatible AGFS backend로 직접 지원한다. Path-style S3가 기본이며 문서가 MinIO를 명시한다.
- PostgreSQL: 일반 PostgreSQL/pgvector backend는 현재 공식 지원 목록에 없다. `openGauss` 지원을 PostgreSQL 지원으로 해석하면 안 된다.
- Redis: QueueFS의 기본 영속 백엔드는 SQLite다. 공식 Redis queue/backend는 이번 소스와 문서 기준으로 확인하지 못했다.

따라서 Chat Portal에 OpenViking을 도입한다면 "기존 저장소 위에 얇게 얹는 provider"가 아니라, `MinIO(원문) + Qdrant(전용 인덱스) + OpenViking Server(문맥 엔진)`이라는 독립 Context DB 서비스로 보는 것이 정확하다. PostgreSQL은 Chat Portal의 업무 데이터, 권한 원장, OpenViking과의 매핑/감사 정보에 계속 남긴다.

## 출처와 버전

| 구분 | 확인 결과 | 신뢰도 |
| --- | --- | --- |
| 공식 GitHub | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) | 1차 소스 |
| 공식 문서 | [OpenViking Docs](https://docs.openviking.ai/en/) | 1차 소스 |
| 소스 스냅샷 | `main` commit `5bfa9b617ecff478f825ca435a35bc4222b30582`, 2026-07-11 | 1차 소스 |
| GitHub 최신 릴리스 | `v0.4.9`, 2026-07-10 기준 | 1차 소스 |
| GitHub stars | 약 26.6k, 2026-07-12 확인 | 지표성 참고 |
| 메인 프로젝트 라이선스 | AGPL-3.0. CLI와 examples에는 별도 Apache-2.0 구성 요소가 있다. | 1차 소스 |
| 관련 연구 | [VikingMem 논문](https://arxiv.org/abs/2605.29640) | 연구 논문, 제품 구현과 동일하다고 단정하면 안 됨 |

공식 문서와 현재 소스 사이에는 메모리 카테고리 표기 차이가 있다. 이 문서에서는 문서의 개념 모델과 `main` 소스의 템플릿/구현 모델을 분리해서 다룬다.

## 1. 문제 정의: Vector DB를 Context DB로 확장한다

OpenViking의 출발점은 단순 벡터 검색의 한계다.

- 청크 단위 벡터만으로는 문서나 대화의 전체 구조를 잃기 쉽다.
- 메모리, RAG 리소스, 스킬 정의가 서로 다른 저장소와 코드에 흩어진다.
- 검색 결과가 어떤 상위 문맥에 속하는지, 왜 선택되었는지 추적하기 어렵다.
- 과거 실행 결과를 단순 대화 로그로만 남기면 재사용 가능한 Agent 행동 규칙으로 바뀌지 않는다.

OpenViking의 답은 모든 컨텍스트를 URI 트리로 표현하고, 원문과 인덱스를 분리하며, 먼저 좁은 요약을 탐색한 뒤 필요한 경우에만 원문으로 내려가는 것이다. 즉 핵심 추상화는 `chunk`가 아니라 **주소를 가진 context node와 그 계층**이다.

## 2. 전체 아키텍처

```text
                        OpenViking Server / Embedded Runtime

  add resource ─┐       Session commit ──────────┐       search / read
                v                                v             ^
        Parser + TreeBuilder              Session compressor    |
                |                         + Memory extractor    |
                v                                |             |
  AGFS/RAGFS: L2 원문, L1/L0, 관계, 세션, 메모리 <──────────────┤
                |                                |             |
                v                                v             |
        SemanticQueue / EmbeddingQueue ──> Vector Index ────────┘
                                           URI, vector, metadata
```

공식 구조에서 AGFS는 source of truth다. Vector Index는 원문을 보관하지 않고 URI, 벡터, 필터용 metadata, L0 abstract만 보관하는 파생 인덱스다. 인덱스를 잃으면 AGFS에서 재구축할 수 있지만, AGFS 원문을 잃으면 복원할 수 없다.

이 구분은 Chat Portal 설계에도 중요하다. Qdrant를 원문 DB처럼 쓰지 않고, MinIO 또는 AGFS가 원문과 계층 메타데이터의 권위 있는 위치가 되도록 둬야 한다.

## 3. 논리 주소 체계: Viking URI와 Namespace

OpenViking은 내부 저장 경로를 직접 노출하지 않고 `viking://{scope}/{path}`라는 가상 URI를 사용한다.

대표 namespace는 다음과 같다.

```text
viking://resources/...                         # account 안에서 공유 가능한 지식/문서/코드
viking://user/{user_id}/resources/...          # 특정 사용자의 비공개 리소스
viking://user/{user_id}/memories/...           # 사용자 또는 peer 범위의 장기 메모리
viking://user/{user_id}/skills/...             # 사용자 범위의 스킬 정의
viking://user/{user_id}/sessions/{session_id}/ # 세션 메시지와 archive
viking://agent/skills/...                      # account 범위의 공유 agent skill
```

서버의 멀티테넌시 모드에서는 public URI 앞에 `account_id`를 쓰지 않는다. 요청 인증 정보에서 account/user를 해석한 뒤 저장소 내부에 account prefix를 붙인다. 예를 들어 `viking://resources/project-a`는 논리적으로 account 공유 리소스이고, 내부적으로는 `/local/{account_id}/resources/project-a` 계열로 매핑된다.

이 모델의 장점은 동일한 검색, browse, read 인터페이스가 리소스/메모리/스킬에 적용된다는 점이다. 단점은 URI와 권한 문맥이 저장/검색/삭제의 핵심 키가 되므로, Chat Portal의 `tenant_id`, `workspace_id`, `user_id`, `agent_id` 매핑을 처음부터 명확히 고정해야 한다는 점이다.

## 4. Context Type: Resource, Memory, Skill

공식 개념 문서는 context를 세 종류로 나눈다.

| 타입 | 의미 | 주된 생성자 | 변경 성격 |
| --- | --- | --- | --- |
| Resource | 문서, 코드, 매뉴얼 등 외부 지식 | 사용자/시스템 ingestion | 비교적 정적 |
| Memory | 사용자/Agent가 학습한 사실과 실행 지식 | 세션 커밋의 추출기 | 지속적으로 업데이트 |
| Skill | 호출 가능한 절차/도구/능력 정의 | 사용자/시스템 | 상대적으로 정적 |

여기서 Skill 자체와 "스킬을 어떻게 사용했는가"는 분리된다. `SKILL.md` 같은 정의는 Skill이고, 어떤 조건에서 성공/실패했는지는 memory의 `tools`, `skills`, `experiences` 류가 된다. 이는 Hermes의 durable fact / skill 구분과 비슷하지만, OpenViking은 둘을 한 URI filesystem 안에서 검색하고 참조한다.

## 5. L0/L1/L2: 계층은 Memory Type이 아니라 정보 밀도다

OpenViking의 가장 중요한 설계는 모든 context directory에 적용되는 정보 계층이다.

| 층 | 파일/대상 | 대략적 크기 | 역할 |
| --- | --- | --- | --- |
| L0 | `.abstract.md` | 약 100 tokens | 벡터 recall, 빠른 필터링, 목록 표시 |
| L1 | `.overview.md` | 약 1k~2k tokens | rerank, 상위 구조와 하위 탐색 안내 |
| L2 | 원문 파일과 하위 directory | 제한 없음 | 필요한 때만 읽는 실제 세부 내용 |

예를 들어 한 프로젝트 리소스 directory에는 L0/L1과 여러 L2 파일이 함께 존재한다.

```text
viking://resources/projects/chat-portal/
├── .abstract.md       # "Chat Portal agent memory architecture ..."
├── .overview.md       # 하위 문서, 핵심 결정, 읽을 경로를 설명
├── .relations.json    # 다른 context URI와의 관계
├── architecture.md    # L2
├── adr/
│   ├── .abstract.md
│   ├── .overview.md
│   └── 001-memory.md  # L2
└── runbook/
    └── ...
```

핵심은 L0/L1이 원문을 축약한 별도 캐시이자 navigation index라는 점이다. "요약 하나를 프롬프트에 넣는다"가 아니라, 상위 directory부터 하위 directory까지 점진적으로 탐색할 수 있는 파일시스템 표현이다.

### L0/L1 생성 방식

리소스를 넣으면 Parser는 포맷 변환과 트리 생성만 수행한다. LLM 호출은 Parser와 분리되어 있으며, SemanticQueue가 비동기로 leaf directory에서 root로 올라가며 L1을 만들고 L0를 추출한다.

```text
Input -> Parser -> temporary tree -> TreeBuilder -> AGFS
                                                  -> SemanticQueue
                                                     leaf -> parent -> root
                                                     L1 -> L0 -> embedding
```

이 분리는 ingestion 요청의 응답 시간을 줄이지만, 새 리소스가 즉시 검색 가능한 상태가 아닐 수 있다는 뜻이기도 하다. Chat Portal에서는 "원문 저장 완료", "요약 생성 완료", "벡터 색인 완료"를 동일한 완료 상태로 취급하면 안 된다.

## 6. Memory 모델: 문서 모델과 구현 모델을 구분해야 한다

### 6.1 공식 개념 문서의 분류

공식 context type 문서는 `profile`, `preferences`, `entities`, `events`, `trajectories`, `experiences`, `tools`, `skills`를 메모리 카테고리로 제시한다. 이 표는 "사실/사용자 상태/실행 지식"을 한 namespace 안에 분리한다는 설계 의도를 설명하는 데 유용하다.

### 6.2 현재 `main` 구현의 템플릿 기반 분류

2026-07-11 `main` 소스의 기본 YAML template 디렉터리에는 `profile`, `preferences`, `entities`, `events`, `cases`, `trajectories`, `experiences`, `tools`, `skills`, `identity`, `soul`이 존재한다. 세션 문서에는 user/agent stage로 나뉜 별도 8-category 표도 있다. 따라서 카테고리 명칭과 소유 범위를 제품의 안정된 외부 계약이라고 가정하면 위험하다.

구현상 더 근본적인 모델은 다음이다.

```text
MemoryTypeSchema
  - memory_type
  - directory URI template
  - filename template
  - fields + field-level merge_op
  - embedding template
  - operation_mode: upsert | add_only | update_only
  - stage: user | agent
  - peer_enabled
```

즉 "카테고리가 8개"가 본질이 아니라 **YAML schema로 memory type을 정의하고, type마다 경로, 파일 이름, 추출 규칙, merge 규칙, 임베딩 문장을 바꿀 수 있다**는 점이 본질이다.

### 6.3 세 가지 다른 시간 모델

OpenViking의 기본 템플릿은 적어도 세 가지 시간 모델을 갖는다.

| 시간 모델 | 예 | 의도 |
| --- | --- | --- |
| 단일 문서 upsert/merge | `profile`, `preferences`, `entities`, `experiences`, `tools` | 사실을 수정하고 정제한다 |
| append-only event | `events` | 발생 사실을 이력으로 보존한다 |
| add-only trajectory/case | `trajectories`, `cases` | 특정 실행 사례를 새 레코드로 남긴다 |

이 구분은 Chat Portal이 OpenViking 설계를 차용할 때 가장 가치 있다. "모든 기억을 하나의 vector collection에 append"하는 대신, stateful fact, immutable event, reusable procedure를 서로 다른 lifecycle로 관리할 수 있다.

### 6.4 Field-level merge

각 schema field에는 `immutable`, `patch`, `sum` 등 merge operation을 둔다. 예를 들어 tool/skill 실행 통계는 누적하고, 이름 같은 identity field는 고정하며, 본문은 patch/merge한다. 메모리를 텍스트 blob이 아니라 **타입이 있는 파일 + 구조화 metadata**로 관리하려는 설계다.

## 7. Session은 단순 chat history가 아니다

세션은 메시지 컨테이너이면서 장기 메모리 생성의 입력 파이프라인이다.

```text
viking://user/{user_id}/sessions/{session_id}/
├── messages.jsonl               # 현재 대화
├── .abstract.md                 # 현재 세션 L0
├── .overview.md                 # 현재 세션 L1
├── history/archive_001/
│   ├── messages.jsonl            # 압축 전 archive L2
│   ├── .abstract.md
│   ├── .overview.md
│   ├── memory_diff.json          # 메모리 변경 감사 기록
│   └── .done                     # 비동기 후처리 완료 marker
└── tools/{tool_id}/tool.json     # tool use 기록
```

`session.commit()`은 두 단계다.

1. 동기 단계: 현재 메시지를 archive에 저장하고 active message를 비운 뒤 task id를 돌려준다.
2. 비동기 단계: archive summary 생성, 장기 memory 추출, memory diff 기록, usage/active count 갱신, semantic/vector queue 등록을 수행한다.

따라서 "사용자가 말한 직후 메모리에 완전히 반영된다"가 아니라, 커밋 후 background task가 완료되어야 durable memory와 검색 인덱스가 최신 상태가 된다.

### 추출과 중복 제거

공개 문서가 설명하는 흐름은 다음과 같다.

```text
archive messages
  -> LLM candidate extraction
  -> vector pre-filter for similar memories
  -> LLM decision: skip/create/merge/delete
  -> AGFS write
  -> semantic/vector indexing
```

후보별로 `skip`, `create`, 기존 항목별 `merge`, `delete` 결정을 낸다. 이는 "LLM이 항상 새 memory를 추가"하는 구조가 아니라 기존 기억과 비교해 교정/병합하려는 구조다. 하지만 최종 정책 품질은 template prompt, embedding, reranker, candidate recall에 크게 좌우된다.

### 중요한 한계: 기본 템플릿을 그대로 쓰면 안 되는 이유

기본 template에는 범용 개인 assistant 성격의 `identity`, `soul`도 포함된다. Chat Portal의 업무/멀티테넌트 서비스에 그대로 켜면 제품의 memory taxonomy와 충돌할 가능성이 높다. `custom_templates_dir`가 공식 설정으로 제공되므로, Chat Portal에서는 기본 type을 그대로 신뢰하지 말고 아래처럼 서비스 용어에 맞춘 schema를 별도로 설계해야 한다.

```text
profile             # 장기 사용자/조직 특성
preferences         # 응답/작업 선호
project_facts       # 지속되는 프로젝트 사실과 제약
decisions           # append-only ADR/합의/결정
entities            # 사람, 서비스, 저장소, repository
task_trajectories   # add-only 실행 경로와 결과
agent_experiences   # 재사용 가능한 행동 규칙
tool_knowledge      # 도구별 안정적인 사용 지식
```

## 8. 검색은 단일 Vector Similarity가 아니다

OpenViking의 `find`와 `search`는 구분된다.

- `find`: 기본 semantic retrieval에 가깝다.
- `search`: query intent를 분석해 0~5개의 typed query를 만들고, 계층 탐색과 rerank를 수행하는 더 무거운 경로다.

개념적 검색 흐름은 다음과 같다.

```text
query
  -> intent analysis / query plan
  -> candidate directories from vector index
  -> priority-queue based directory-recursive retrieval
  -> scalar filter + rerank
  -> matched contexts (URI, type, L0, score, relations)
  -> agent reads L1, then only needed L2
```

검색 결과는 raw chunk가 아니라 URI, context type, leaf 여부, L0, 점수, relation을 가진 context node다. Agent는 `search -> browse -> read`로 더 깊이 들어갈 수 있다. 이 구조는 DeepAgents에서 subagent가 탐색 범위를 좁히고, 필요한 파일만 context에 올리는 방식과 개념적으로 잘 맞는다.

## 9. 실제 저장 구조

### 9.1 AGFS/RAGFS: 원문과 계층 메타데이터

AGFS는 OpenViking의 content store다. 현재 구현은 Rust 기반 RAGFS binding을 in-process로 사용한다. 여기에는 다음이 저장된다.

- L2 원문: Markdown, 코드, PDF/이미지/음성/비디오 등 ingestion 결과
- L1 `.overview.md`, L0 `.abstract.md`
- `.relations.json`
- 세션 메시지, archive, `memory_diff.json`, 완료 marker
- memory file 본문과 `MEMORY_FIELDS` metadata
- 내부 queue/redo/lock 관련 metadata

AGFS backend는 `local`, `s3`, `memory`를 지원한다. `s3`는 S3-compatible backend이며 bucket, endpoint, access key, secret key, prefix, path-style 여부를 받는다.

### 9.2 MinIO: 직접 결합 가능

MinIO는 S3-compatible backend로 직접 설정 가능하다. 공식 설정 문서는 MinIO/SeaweedFS의 Path-style을 명시하고 `use_path_style: true`를 기본값으로 둔다. 즉 MinIO URL을 단순 ingestion source로만 쓰는 것이 아니라 AGFS의 실제 content backend로 쓸 수 있다.

Chat Portal 관점의 권장 배치는 다음과 같다.

```text
MinIO bucket: openviking-context
prefix: chat-portal/prod/
  /{account_id}/resources/...
  /{account_id}/user/{user_id}/memories/...
  /{account_id}/user/{user_id}/sessions/...
  /_system/...                  # 내부 queue/redo/lock 관련 경로
```

주의할 점은 OpenViking이 directory marker, object key normalization, `.abstract.md` 등 sidecar 파일을 직접 관리한다는 것이다. 같은 bucket/prefix를 Chat Portal 애플리케이션이 임의로 수정하면 계층과 인덱스 정합성이 깨질 수 있다. 따라서 **전용 bucket 또는 최소한 전용 prefix**가 필요하다.

### 9.3 Vector Index: Qdrant에 저장되는 것

Vector index에는 원문이 아니라 다음과 같은 index record가 들어간다.

| 필드 | 용도 |
| --- | --- |
| `id` | context node 식별자 |
| `uri`, `parent_uri` | URI 트리와 하위 탐색 |
| `context_type` | resource / memory / skill |
| `is_leaf` | 파일 또는 directory 여부 |
| dense/sparse vector | semantic/hybrid recall |
| `abstract` | L0 text |
| `name`, `description` | display/filter/rerank 보조 |
| `created_at`, `active_count` | lifecycle와 usage 신호 |

중요한 점은 Qdrant에 L2 원문을 넣지 않는다는 것이다. 검색 후보를 찾은 뒤 실제 내용은 AGFS(MinIO)에서 URI로 읽는다.

## 10. Qdrant backend: 지원하지만 전용 컬렉션이 필요하다

최신 공식 설정과 `qdrant_adapter.py` 소스를 확인했다. Qdrant는 공식 backend이며 URL, API key, timeout, dense/sparse vector field name, metadata sidecar collection name을 설정할 수 있다.

구현상 물리 컬렉션 이름은 다음 형식이다.

```text
{project_name}__{collection_name}
```

기본값은 `project_name=default`, `collection_name=context`이므로 `default__context`가 된다. 또한 OpenViking collection/index metadata는 기본적으로 `__openviking_meta`라는 별도 Qdrant collection에 둔다.

### 기존 Qdrant collection 재사용이 위험한 이유

OpenViking은 기존 물리 collection이 존재하는 경우 metadata sidecar에서 해당 collection의 OpenViking schema를 찾는다. metadata가 없으면 오류를 내며 다른 project/name을 쓰거나 metadata를 복원하거나 stale collection을 삭제하라고 안내한다. 즉 Chat Portal에서 이미 쓰는 일반 RAG/memory collection을 OpenViking collection으로 지정하는 것은 지원되는 결합 방식이 아니다.

권장 namespace는 다음과 같다.

```text
Qdrant
  chat_portal_rag                  # 기존 Chat Portal RAG
  chat_portal_mem0                 # Mem0을 별도로 쓸 때의 전용 collection
  openviking__context              # OpenViking의 전용 context index
  __openviking_meta                # OpenViking의 전용 metadata sidecar
```

`project_name=openviking`, `name=context`처럼 명시적인 이름을 설정해 `openviking__context`를 만들고, OpenViking만 해당 collection과 meta collection을 소유해야 한다.

### Qdrant 구현상 확인한 제약

- Qdrant adapter는 `qdrant-client`가 아닌 자체 경량 REST client를 사용한다.
- dense vector field 기본 이름은 `vector`, sparse vector field 기본 이름은 `sparse_vector`다.
- metadata/payload index를 만들고, text index 옵션도 지원한다.
- 일부 aggregate/scan 경로는 Qdrant server-side 연산 대신 client-side scroll/full scan을 사용하며, 소스에서 대형 collection에 비용 경고를 남긴다.
- path scope 지원 깊이에 제약이 있으며, adapter 소스는 `0/1/-1` 이외 깊이를 지원하지 않는다고 명시한다.

따라서 Qdrant 지원은 "기존 collection 어디에나 연결하면 OpenViking 검색이 즉시 동작한다"는 의미가 아니다. OpenViking이 요구하는 URI/payload/schema를 가진 **전용 index**에 대해 지원한다는 뜻이다. 대규모 tenant 수와 hot directory에서 retrieval latency, scroll 비용, payload index 설계는 반드시 측정해야 한다.

## 11. PostgreSQL과 Redis의 위치

### PostgreSQL

현재 공식 VectorDB backend 목록은 local, HTTP, Volcengine/VikingDB, private VikingDB, cuVS, Qdrant, openGauss다. 일반 PostgreSQL 또는 pgvector backend는 확인되지 않았다. openGauss가 PostgreSQL wire protocol과 유사해 보여도 별도 제품/adapter이므로 Postgres 대체 지원으로 간주하면 안 된다.

Chat Portal의 PostgreSQL은 다음 용도로 유지하는 편이 맞다.

- Chat Portal account/workspace/user/agent의 source of truth
- OpenViking `account_id`, `user_id`, `peer_id`, session id 매핑
- 서비스 권한, billing, retention policy, 삭제 요청의 업무 audit
- OpenViking task 상태를 서비스 관점에서 추적해야 할 때의 outbox/audit
- OpenViking 메모리의 승인/차단/보류 상태 같은 제품 정책 metadata

OpenViking 내부 content/index의 권위 데이터를 Postgres에 이중 기록하려 하면 source of truth가 둘이 된다. Postgres에는 OpenViking URI와 lifecycle reference를 두고, 본문/요약/벡터를 별도 복제하지 않는 경계가 현실적이다.

### Redis

OpenViking 자체의 durable queue 기본값은 SQLite QueueFS다. Redis backend는 공식 configuration과 현재 소스에서 확인하지 못했다. 따라서 Redis를 OpenViking 내부 queue의 HA 대체재로 가정하면 안 된다.

Chat Portal이 이미 운영하는 Redis는 OpenViking 바깥에서 다음 용도로는 유효하다.

- 사용자 요청과 OpenViking background task 상태의 짧은 TTL cache
- recall 결과 또는 materialized context bundle cache
- 동일 세션 commit 중복 제출을 막는 idempotency key
- 서비스 레벨 rate limit, distributed coordination, event delivery

하지만 Redis를 장기 memory, AGFS 원문, 세션 archive, memory diff의 영속 저장소로 두면 안 된다.

## 12. 정합성, 실패 복구, 이중화

### 12.1 기본 철학

OpenViking은 "나쁜 검색 결과를 반환하는 것보다 일시적으로 검색을 놓치는 편이 낫다"는 방향을 갖는다. AGFS가 source of truth이고 VectorDB는 파생 인덱스이므로, 파일과 벡터 간 실패 순서를 다르게 설계한다.

- 삭제: vector index를 먼저 삭제하고 파일을 삭제한다. 파일 삭제가 실패하면 검색에서는 사라지지만 원문은 남아 재시도가 가능하다.
- 이동: 새 위치 복사 후 vector URI를 갱신하고 마지막에 원본을 지운다.
- resource ingestion: 임시 트리와 lifecycle tree lock을 사용해 summary/index 작업 중 삭제와 충돌하지 않게 한다.
- memory commit: memory extraction 전에 redo marker를 기록하고, 프로세스 재시작 때 남은 marker를 재실행한다.

### 12.2 Path lock과 redo log

`rm`, `mv`, `add_resource`, `session.commit`에는 file-based path lock이 적용된다. exact lock과 tree lock을 구분하고 fencing token, stale lock cleanup을 사용한다. `session.commit`의 memory extraction은 redo log로 재시도한다. queue 작업은 idempotent/retriable하게 설계된다.

이것은 단일 writer 또는 제한된 동시성에서 꽤 구체적인 정합성 설계다. 다만 분산 환경의 완전한 transaction coordinator는 아니다.

### 12.3 Multi-write는 AGFS 복제 기능이다

AGFS는 primary backend와 backup backend를 두는 multi-write를 지원한다.

- primary: authoritative write target, 최종 read fallback
- backup: replica, migration, read acceleration 용도
- async: primary 성공 뒤 즉시 반환, backup은 eventual consistency
- sync: backup acknowledgement를 일정 수 기다림
- redirect: 대형 파일/특정 확장자를 primary 대신 지정 backup으로 보냄

이 기능은 MinIO replica 또는 다른 S3 backend에 AGFS 콘텐츠를 복제하는 데 유용할 수 있다. 하지만 다음 한계가 있다.

- multi-write를 켠 이전의 과거 파일은 자동 backfill되지 않는다.
- async backup은 지연될 수 있다.
- redirect/sync 상태는 내부 metadata에 의존한다.
- 공식 문서는 동일 primary에 대한 multi-process concurrent write의 distributed metadata locking을 미래 과제로 명시한다.

따라서 "OpenViking이 이중화를 제공하므로 서비스 전체가 HA"라는 결론은 성립하지 않는다. 고가용성은 아래 계층별로 따로 설계해야 한다.

| 계층 | 책임 | Chat Portal 운영 판단 |
| --- | --- | --- |
| MinIO/AGFS | 원문과 sidecar의 durability/replication | MinIO 자체 erasure coding/replication과 backup policy 사용 |
| Qdrant | vector index HA/replication | Qdrant cluster/replication을 별도로 운영 |
| QueueFS SQLite | async 작업 지속성 | shared/worker 배치와 SQLite 경로의 단일 장애점 PoC 필요 |
| OpenViking Server | HTTP/API/worker process | 다중 instance가 동일 AGFS/queue에서 안전한지 부하/장애 PoC 필요 |
| PostgreSQL | 제품 원장/권한/audit | OpenViking 데이터의 secondary source가 되지 않도록 경계 유지 |

## 13. 멀티테넌시와 보안 모델

OpenViking Server의 identity 계층은 다음과 같다.

```text
account_id  -> tenant / workspace / customer 경계
user_id     -> account 내부의 개인 memory/session 경계
peer_id     -> user 아래의 대화 상대 또는 runtime actor 범위
role        -> ROOT / ADMIN / USER
```

동일 account의 `resources`는 공유할 수 있지만 memory, skill, session은 기본적으로 user 또는 peer 경계로 분리된다. `api_key` mode에서는 user/admin key에서 identity를 해석하고, trusted mode에서는 신뢰된 gateway가 account/user header를 주입한다.

저장 시 암호화도 제공한다. VikingFS 계층에서 account별 key를 유도하는 envelope encryption 구조이며, AGFS/MinIO에는 ciphertext만 보이게 할 수 있다. local key, Vault, Volcengine KMS 옵션이 문서에 있다.

Chat Portal에는 trusted mode가 특히 검토 대상이다. Portal backend가 이미 인증과 tenant authorization을 책임지고 있다면, 외부 클라이언트가 OpenViking API key를 직접 들고 다니게 하기보다 Portal 내부 gateway만 trusted header를 주입하는 방식이 권한 모델을 단순하게 만들 수 있다. 단, gateway가 보안 경계가 되므로 network policy와 header spoofing 방지가 전제다.

## 14. 커스터마이즈 가능한 범위

OpenViking은 고정된 memory provider가 아니다. 다음 레벨에서 커스터마이즈할 수 있다.

| 대상 | 커스터마이즈 수단 | Chat Portal 의미 |
| --- | --- | --- |
| Memory taxonomy | `custom_templates_dir`의 YAML schema | 서비스 전용 memory type, URI, lifecycle 정의 |
| 추출 정책 | type별 prompt/fields/merge operation/operation mode | durable fact와 event/procedure를 분리 |
| 임베딩 문장 | `embedding_template` | 검색 대상 문장을 memory type별로 최적화 |
| L1 overview | `overview_template` | directory navigation 품질 제어 |
| 모델 | embedding, VLM/LLM, reranker provider 설정 | 비용/지연/데이터 경로 선택 |
| Content store | local/S3-compatible/memory AGFS | MinIO 직접 사용 |
| Vector index | Qdrant 등 backend 설정 | Qdrant 전용 collection 사용 |
| 접근 경계 | account/user/peer, API key/trusted mode | Portal tenant 모델과 연결 |

반대로 다음은 별도 검증 없이는 커스터마이즈 가능하다고 보면 안 된다.

- PostgreSQL/pgvector를 OpenViking의 native storage backend로 쓰는 것
- Redis를 OpenViking QueueFS backend로 교체하는 것
- 기존 Qdrant RAG collection을 OpenViking collection으로 그대로 재사용하는 것
- 대규모 multi-instance write에서 distributed lock을 제공하는 것

## 15. DeepAgents와의 결합성

OpenViking은 현재 LangChain/LangGraph integration을 공식 제공하며 retriever, chat history, durable store, context wrapper, tools, middleware를 지원한다. 이는 DeepAgents의 기반인 LangGraph와 연결할 수 있는 표면이 있다는 뜻이다.

그러나 DeepAgents에 가장 자연스러운 적용은 "기본 store를 OpenViking으로 바꾸면 모든 memory 문제가 해결된다"가 아니다. OpenViking의 장점은 탐색 가능한 context filesystem이므로, 다음 역할로 보는 편이 맞다.

```text
DeepAgent execution
  -> pre-run recall: L0/L1 후보를 좁은 working context로 제공
  -> tool-driven exploration: search -> browse -> read(L2)
  -> turn capture: messages + used context/skill 기록
  -> commit: archive -> memory extraction -> background vectorization
```

특히 DeepAgent의 subagent가 무제한으로 과거 내용을 받는 대신, OpenViking에서 L0/L1로 후보를 탐색하고 L2는 필요한 subagent에만 제공하도록 설계하면 context budget을 제어할 수 있다.

다만 이 결합은 OpenViking middleware의 동작 시점, DeepAgents의 subagent lifecycle, commit이 비동기라는 점을 함께 검증해야 한다. 단일 root agent만 memory를 commit할지, subagent별 peer/session을 둘지, 성공한 trajectory만 promotion할지 같은 제품 정책은 OpenViking이 대신 결정해 주지 않는다.

## 16. Chat Portal용 권장 배치안

OpenViking을 실제 도입하는 경우의 최소한의 경계는 아래와 같다.

```text
Chat Portal API / DeepAgents
  |  tenant authorization + business policy
  v
OpenViking Server (separate service)
  |-- AGFS/RAGFS -> MinIO: openviking 전용 bucket/prefix
  |-- VectorDB   -> Qdrant: openviking 전용 collection + meta collection
  |-- QueueFS    -> SQLite persistent volume: PoC에서 worker/scale 검증
  '-- HTTP/MCP/LangChain-LangGraph integration

PostgreSQL
  '-- Chat Portal source of truth, identity mapping, audit/outbox, retention state

Redis
  '-- request/task cache, idempotency, short-lived materialized context cache
```

### 직접 도입이 맞는 경우

- RAG 문서, 장기 memory, skill, session archive를 같은 namespace와 browse/read UX로 통합해야 한다.
- `search -> browse -> read`와 L0/L1/L2 progressive loading이 제품의 핵심 행동이어야 한다.
- MinIO와 Qdrant를 OpenViking 전용 리소스로 분리해 운영할 수 있다.
- AGPL-3.0 의무와 별도 Context DB 운영 비용을 수용할 수 있다.

### 설계만 차용하는 편이 맞는 경우

- Chat Portal의 memory를 Qdrant/PostgreSQL/MinIO의 기존 스키마에 완전히 통합해야 한다.
- PostgreSQL을 memory lifecycle의 중심 source of truth로 강하게 유지해야 한다.
- OpenViking의 QueueFS/AGFS 운영 모델을 새로 들이는 비용이 크다.
- Mem0 등을 extraction engine으로 쓰되 memory node/edge/version을 제품 DB에서 직접 관리하려 한다.

후자의 경우에도 OpenViking에서 차용할 핵심은 충분히 크다.

- URI/path 기반 namespace
- memory type별 lifecycle과 merge rule
- L0/L1/L2의 progressive context loading
- 원문(MinIO)과 검색 인덱스(Qdrant)의 분리
- archive + memory diff + promotion이라는 추적 가능한 memory write
- content write와 semantic/vectorization의 비동기 분리

## 17. 도입 전 반드시 검증할 PoC

### P0: 저장소 정합성

1. MinIO 전용 bucket/prefix에 resource, memory, session을 저장한다.
2. OpenViking 전용 Qdrant collection과 `__openviking_meta`를 만든다.
3. resource 추가 -> L0/L1 생성 -> Qdrant index -> URI read의 전체 흐름을 확인한다.
4. 파일 이동/삭제 후 Qdrant의 `uri`, `parent_uri`와 MinIO object가 함께 정리되는지 확인한다.
5. Qdrant 장애, MinIO 장애, semantic worker 재시작 각각에서 어떤 상태가 남는지 기록한다.

### P1: Memory taxonomy 품질

1. 기본 YAML 대신 Chat Portal 전용 template 5~8개만 정의한다.
2. profile/preference/project fact/decision/trajectory/experience를 서로 다른 operation mode로 둔다.
3. 동일 사실의 정정, 상충 사실, 단기 TODO, 민감 정보, tool failure를 포함한 대화 set으로 추출 결과를 평가한다.
4. `memory_diff.json`을 기준으로 add/update/delete가 설명 가능하고 되돌릴 수 있는지 본다.

### P2: DeepAgents lifecycle

1. root agent와 subagent의 session/peer 경계를 정한다.
2. pre-run recall, tool-driven deep read, post-run capture, commit 시점을 명시한다.
3. background commit이 끝나기 전 다음 turn이 들어왔을 때 stale memory를 어떻게 다룰지 정한다.
4. subagent의 실패한 시도는 trajectory로 남길지, 성공한 결과만 experience로 promotion할지 정책을 시험한다.

### P3: 운영과 확장성

1. 한 tenant의 hot directory에 동시 write/commit을 걸어 path lock 충돌과 지연을 측정한다.
2. QueueFS SQLite가 배포 방식에서 shared인지 worker isolated인지, persistent volume 장애 시 어떤 복구가 되는지 확인한다.
3. Qdrant collection 규모 증가 시 client-side scroll 경로가 latency를 악화시키는지 측정한다.
4. MinIO replication과 OpenViking multi-write를 동시에 쓸 때 중복 복제/복구 책임을 명확히 한다.
5. AGPL-3.0 배포 의무를 법무/제품 정책과 검토한다.

## 최종 판단

OpenViking은 "OpenViking식 계층형 메모리"라는 아이디어만 제공하는 미완성 개념 프로젝트가 아니다. 현재는 Qdrant와 MinIO를 공식 backend로 연결할 수 있고, server mode, multi-tenant identity, encryption, session/memory pipeline, recovery, LangChain/LangGraph integration까지 갖춘 별도 Context DB다.

다만 Chat Portal의 기존 Qdrant/PostgreSQL/MinIO에 단순히 붙는 provider도 아니다. Qdrant와 MinIO는 사용할 수 있지만 OpenViking이 그 위의 URI, sidecar, queue, schema, lock, lifecycle을 소유해야 한다. PostgreSQL과 Redis는 OpenViking 내부 저장소를 대체하기보다 Portal의 business control plane과 runtime support layer로 남는다.

그러므로 현 시점 권고는 다음이다.

1. OpenViking을 계층형 memory/context 설계의 가장 강한 참고 모델로 채택한다.
2. 실제 도입 여부는 MinIO + 전용 Qdrant collection + 단일 OpenViking Server PoC로 먼저 검증한다.
3. PoC에서 QueueFS/다중 인스턴스/AGPL/메모리 템플릿 품질이 만족스럽지 않으면, OpenViking의 URI/L0-L1-L2/lifecycle만 차용해 DeepAgents + Mem0 + Qdrant + PostgreSQL + MinIO 구조로 직접 구현한다.

## 참고 자료

### 공식 문서

- [Architecture Overview](https://docs.openviking.ai/en/concepts/01-architecture): Context DB의 구성 요소, AGFS와 vector index의 분리, write/retrieve/session 흐름. 신뢰도: 높음.
- [Context Types](https://docs.openviking.ai/en/concepts/02-context-types): Resource/Memory/Skill 개념 분리. 신뢰도: 높음.
- [Context Layers](https://docs.openviking.ai/en/concepts/03-context-layers): L0/L1/L2와 directory sidecar 구조. 신뢰도: 높음.
- [Storage Architecture](https://docs.openviking.ai/en/concepts/05-storage): VikingFS, AGFS, index schema, delete/move synchronization. 신뢰도: 높음.
- [Context Extraction](https://docs.openviking.ai/en/concepts/06-extraction): Parser/TreeBuilder/SemanticQueue 분리와 bottom-up generation. 신뢰도: 높음.
- [Session Management](https://docs.openviking.ai/en/concepts/08-session): archive, memory extraction, memory diff. 신뢰도: 높음.
- [Path Locks and Crash Recovery](https://docs.openviking.ai/en/concepts/09-transaction): lock, redo log, failure order. 신뢰도: 높음.
- [Multi-Tenant](https://docs.openviking.ai/en/concepts/11-multi-tenant): account/user/peer isolation과 auth mode. 신뢰도: 높음.
- [Multi-Write Storage](https://docs.openviking.ai/en/concepts/14-multi-write-storage): primary/backup, consistency, 한계. 신뢰도: 높음.
- [Configuration](https://docs.openviking.ai/en/guides/01-configuration): Qdrant, S3-compatible/MinIO, QueueFS, custom memory template 설정. 신뢰도: 높음.
- [LangChain and LangGraph](https://docs.openviking.ai/en/agent-integrations/07-langchain-langgraph): retriever, store, middleware, tools integration. 신뢰도: 높음.

### 소스 코드 확인 지점

- [QdrantConfig](https://github.com/volcengine/OpenViking/blob/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking_cli/utils/config/vectordb_config.py): Qdrant URL/API key/vector field/meta collection 설정.
- [QdrantCollectionAdapter](https://github.com/volcengine/OpenViking/blob/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking/storage/vectordb_adapters/qdrant_adapter.py): 물리 collection 명명과 OpenViking metadata 검증.
- [QdrantCollection](https://github.com/volcengine/OpenViking/blob/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking/storage/vectordb/collection/qdrant_collection.py): vector schema, payload/index, scroll 경로.
- [MemoryTypeRegistry](https://github.com/volcengine/OpenViking/blob/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking/session/memory/memory_type_registry.py): built-in/custom YAML schema loading.
- [Memory templates](https://github.com/volcengine/OpenViking/tree/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking/prompts/templates/memory): 기본 memory taxonomy와 type별 lifecycle prompt.

### 논문

- [VikingMem: A Memory Base Management System for Stateful LLM-based Applications](https://arxiv.org/abs/2605.29640): event/entity 기반 추출, 업데이트, 시간 압축의 연구 설계. OpenViking OSS가 이 논문의 모든 production capability를 그대로 공개했다는 뜻은 아니다.
