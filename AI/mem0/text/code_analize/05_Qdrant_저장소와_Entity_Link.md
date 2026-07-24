# Qdrant 저장소와 Entity Link 구현

> 분석 대상: `mem0/vector_stores/qdrant.py`, `mem0/memory/main.py`  
> 기준 snapshot: `mem0ai 2.0.12` (upstream commit 미확인)

## 결론

Mem0의 Qdrant 어댑터는 dense vector만 쓰는 단순 wrapper가 아니다. 하나의 주 메모리 collection에 dense vector와 optional BM25 sparse vector를 같이 저장하고, 별도 `{collection}_entities` collection으로 엔티티와 main memory ID의 연결을 유지한다.

다만 metadata filtering 문서의 모든 의미가 Qdrant 구현에서 완전히 동일하게 보장되지는 않는다. 특히 wildcard `"*"`는 field 존재 조건이 아니라 필터를 생략하며, `icontains`의 대소문자 구분 여부는 Qdrant full-text index 설정에 의존한다.

## 1. collection 구조

### 주 메모리 collection

`Qdrant.create_col()`은 collection 생성 시 아래 vector slot을 만든다.

```text
""     : dense vector (기본 unnamed vector)
"bm25" : sparse vector (Qdrant/bm25, optional 실제 값)
```

메모리 하나의 payload에는 V3 add path 기준으로 다음이 들어간다.

| payload key | 생성 위치 | 용도 |
| --- | --- | --- |
| `data` | `main.py` Phase 4 | 사람이 읽는 fact 본문 |
| `text_lemmatized` | `lemmatize_for_bm25()` | sparse BM25 vector 인코딩 입력 |
| `hash` | `md5(text)` | exact duplicate 억제 |
| `created_at`, `updated_at` | V3 add/update | lifecycle·응답 표시 |
| `user_id`, `agent_id`, `run_id` | `add()` scope | tenant/session 경계 |
| 사용자 metadata | `add(..., metadata=...)` | category, source_id, confidence 등 애플리케이션 속성 |

`insert()`는 각 payload의 `text_lemmatized`(없으면 `data`)를 모아 fastembed BM25 encoder로 batch 처리한다. encoder 또는 sparse slot이 없으면 해당 point는 dense vector만 저장되어도 정상이다.

### entity collection

`Memory.entity_store`는 처음 엔티티 연결이 필요할 때만 생성된다. Qdrant 기본 명명은 다음과 같다.

```text
main collection:     mem0
entity collection:   mem0_entities
```

entity point payload는 다음 구조다.

```json
{
  "data": "엔티티 문자열",
  "entity_type": "PERSON 또는 다른 추출 타입",
  "linked_memory_ids": ["main-memory-uuid-1", "..."],
  "user_id": "..."
}
```

Qdrant embedded mode(`path=...`)에서는 entity store가 별도 client를 열지 않고 main vector store의 client를 공유한다. 코드 주석의 목적은 RocksDB lock contention 방지다.

## 2. scope filter index

remote Qdrant일 때 `_create_filter_indexes()`가 자동 생성하려는 keyword payload index는 네 개다.

```text
user_id / agent_id / run_id / actor_id
```

local Qdrant (`path`)에서는 payload index 생성을 건너뛴다. 또한 사용자 정의 metadata(`category`, `source_id`, `status`, `project_id` 등)는 자동으로 index하지 않는다.

따라서 우리 서비스에서 자주 filter할 필드가 있다면 Qdrant collection에 별도 payload index를 인프라 코드로 만들어야 한다. `QdrantConfig`는 extra field를 거부하며 `indexed_fields` 설정도 없다. Mem0 `MemoryConfig`만으로 임의 metadata field의 index 목록을 선언해 자동 생성하는 코드는 이 snapshot에서 확인되지 않는다.

## 3. metadata filter의 실제 변환

`Qdrant._create_filter()`는 Mem0 filter dict를 Qdrant `Filter(must, should, must_not)`로 변환한다.

| Mem0 표현 | Qdrant 변환 |
| --- | --- |
| `{key: value}`, `{key: {eq: value}}` | `MatchValue` |
| `{key: [a, b]}`, `{key: {in: [a, b]}}` | `MatchAny` |
| `{key: {ne: x}}`, `{key: {nin: [...]}}` | `MatchExcept` |
| `gt/gte/lt/lte` | `Range`, ISO-8601 문자열이면 `DatetimeRange` |
| `contains` / `icontains` | `MatchText` |
| `AND` | `must` |
| `OR` | `should` |
| `NOT` | `must_not` |

### 구현과 문서 사이의 주의점

1. **wildcard `"*"`**: `_build_field_condition()`은 Qdrant에 field-exists condition이 없다는 이유로 `None`을 반환한다. 즉 `{ "category": "*" }`는 category가 존재하는 record만 고르는 것이 아니라 이 조건을 아예 적용하지 않는다.
2. **`icontains`**: 코드도 Qdrant `MatchText`의 case sensitivity는 full-text index 설정에 따라 다르며, index가 없으면 case-sensitive substring처럼 동작할 수 있다고 로그를 남긴다. 기본 자동 index는 full-text가 아니라 scope keyword index뿐이다.
3. **지원하지 않는 연산자**: Qdrant adapter는 오류를 내지만, vector store 구현체마다 동일한 동작이라고 단정할 수 없다. 실제 provider별 테스트가 필요하다.

이 세 사항은 filter를 권한 경계로 사용해서는 안 된다는 뜻이기도 하다. 접근 제어는 PostgreSQL/API 계층에서 먼저 강제하고, Mem0 filter는 검색 범위 축소로 사용한다.

## 4. Entity link가 만들어지는 방식

V3 add의 Phase 7은 새 fact들에서 `extract_entities_batch()`로 엔티티를 뽑는다.

```text
새 fact들
  → spaCy entity candidate 추출
  → 문자열 normalize(lowercase + 공백 정리) 후 batch 내 dedup
  → entity text batch embedding
  → 같은 scope의 entity collection exact text lookup
  → 없으면 semantic top-1 (score >= 0.95)도 같은 entity로 간주
  → 기존 entity update 또는 새 entity insert
```

기존 entity이면 `linked_memory_ids` 집합에 새 memory ID를 합친다. 없으면 새 entity point를 만든다. 이 연결은 main memory 간 edge를 별도 relation table에 저장하는 graph DB 구조가 아니라, entity payload 안의 ID 배열이다.

### 삭제·수정 시 정리

`Memory._remove_memory_from_entity_store()`는 update/delete lifecycle path에서 호출될 수 있도록 구현되어 있다.

- memory ID를 가진 entity record를 scope 내에서 찾는다.
- ID를 제거하고, 빈 배열이면 entity record 자체를 삭제한다.
- ID가 남으면 entity text를 재임베딩하여 payload를 update한다.

다만 entity cleanup은 예외를 경고/디버그 로그로 삼키는 non-fatal 보조 작업이다. main memory delete 성공과 entity 정리 성공은 원자적이지 않다.

### list/scroll pagination 한계

Qdrant adapter의 `list(filters, top_k=100)`는 `client.scroll(..., limit=top_k)`를 **한 번만** 호출하고 `(points, next_page_offset)`를 그대로 반환한다. 다음 offset을 따라가는 pagination loop가 없다.

이 구현은 다음 API에 직접 영향을 준다.

| 호출 경로 | 실제 상한/영향 |
| --- | --- |
| `Memory.delete_all(scope)` | 기본 `list()`를 써 Qdrant main memory를 최대 100개만 조회·삭제 |
| entity exact-text lookup | `top_k=10000` 한 페이지 안에서만 exact match 탐색 |
| entity cleanup/bulk clear | `top_k=10000` 한 페이지 안에서만 정리 |

즉 `delete_all()`의 이름만 보고 scope 전체 삭제를 보장하면 안 된다. 특히 100개가 넘는 사용자 memory에서는 잔존 point가 생긴다. 운영 전에는 wrapper에서 Qdrant scroll pagination을 직접 구현하거나 upstream/fork를 수정하고, 삭제 뒤 잔존 count를 검증해야 한다.

entity add 단계의 exact match도 매 batch마다 scope의 entity를 최대 10,000개 list해 Python에서 normalize/lookup한다. 대규모 scope에서는 entity collection 크기에 따라 latency와 메모리 사용량이 커질 수 있으므로 별도 benchmark가 필요하다.

## 5. BM25 의존성과 migration 제약

Qdrant adapter는 기존 collection을 발견하면 sparse vector 설정에 `bm25` slot이 있는지 검사한다.

- slot이 있으면 BM25 sparse insert/search 가능
- slot이 없으면 “pre-v3 collection” 경고 후 semantic search만 수행
- `fastembed`가 없으면 BM25 encoder 로드에 실패하고 keyword search는 `None` (`pyproject.toml`의 `extras` optional dependency에 포함)

기존 collection을 그대로 쓰면서 hybrid를 켜려면, 이 구현상 새 collection을 만드는 전략이 필요하다. 운영 이전에는 collection naming, 재임베딩, cutover 및 rollback 계획을 마련해야 한다.

여기서 “hybrid”는 Qdrant Native Hybrid와 구분해야 한다. 이 adapter는 dense `search()`와 sparse `keyword_search()`를 각각 `query_points()`로 호출하며, Qdrant의 `prefetch`·`FusionQuery`·RRF/DBSF를 사용하지 않는다. Mem0 상위 계층이 semantic candidate에 BM25와 entity 점수를 가산한다. 따라서 sparse 검색은 순위 boost에는 참여하지만 sparse-only 결과를 최종 후보에 추가하지 않는다. 비교 근거와 PoC 확장안은 `04_읽기와_Hybrid_Retrieval.md`에 정리했다.

## 6. 우리 Qdrant 설계에 적용

```text
Mem0 main collection       : user/agent durable facts 전용
Mem0 entity collection     : Mem0가 자동 관리
Research RAG collection    : 원문 chunk / citation / source version 전용 (Mem0와 분리)
```

- `source_id`, `source_version`, `memory_kind`, `confidence`, `status`처럼 운영에 필요한 metadata schema를 먼저 정한다.
- Qdrant filter index는 `user_id` 외에도 실제 query pattern이 확정된 후 별도 생성한다.
- `"*"`와 `icontains`는 문서 예시만 믿지 말고 우리 Qdrant 버전에서 integration test로 검증한다.
- entity linking은 한국어 spaCy 품질에 직접 영향을 받으므로, PoC에서 boost 유무를 비교한다.
- Mem0 기본 boost-only 검색과 Qdrant Native dense∪sparse fusion을 exact ID·기술 용어 질의에서 비교한다.
- `delete_all()` 뒤 main/entity 잔존 point 수를 scope별로 검증하고, 100개 초과 데이터셋을 반드시 포함한다.

다음 문서는 stock Mem0 내부 SQLite가 정확히 무엇을 보관하는지, 설정만으로 교체할 수 있는지, 우리 운영 구성에서 PostgreSQL adapter로 대체하려면 어떤 경계가 필요한지 정리한다.
