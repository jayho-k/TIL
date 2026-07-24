# 읽기와 Hybrid Retrieval: `Memory.search()`의 후보·점수 결합 방식

> 분석 대상: `mem0/memory/main.py`의 `search()`, `_search_vector_store()`, `_compute_entity_boosts()` 및 `mem0/utils/scoring.py`  
> 기준 snapshot: `mem0ai 2.0.12` (upstream commit 미확인)

## 결론

Mem0 V3 retrieval은 “Qdrant에서 top-k만 읽기”가 아니다. 의미 검색으로 후보를 넓게 가져온 다음, **BM25와 entity 연결은 후보를 새로 추가하지 않고 순위를 올리는 boost 신호**로 쓴다. 선택적으로 reranker가 마지막 순서를 다시 정한다.

```text
query + filters
  → query lemmatization / entity extraction
  → dense semantic search (후보 pool: max(top_k × 4, 60))
  ├─ BM25 sparse search (가능할 때)
  ├─ entity collection 검색 (가능할 때)
  └─ semantic 후보만 대상으로 score fusion
       → semantic threshold / hybrid top_k
       → 그 top_k 안에서 reranker (옵션)
```

이 설계의 핵심 제약은 명확하다. BM25 또는 entity 검색에서만 발견된 문서는 최종 결과 후보에 들어오지 못한다. dense semantic recall이 충분해야 hybrid boost도 의미가 있다.

## Mem0 Hybrid와 Qdrant Native Hybrid는 다르다

여기서 용어를 구분해야 한다. Mem0가 Hybrid Search를 사용하지 않는 것은 아니다. Mem0는 semantic, BM25, entity의 세 신호를 조합하는 방식을 **Multi-Signal Hybrid Search**라고 부른다. 그러나 Qdrant가 제공하는 `prefetch`와 `FusionQuery` 기반의 서버 측 Dense+Sparse Hybrid Search는 사용하지 않는다.

| 구분 | Qdrant Native Hybrid | Mem0 V3 Hybrid |
| --- | --- | --- |
| dense/sparse 실행 | 하나의 hybrid query에서 `prefetch` 가능 | `search()`와 `keyword_search()`로 별도 요청 |
| 후보군 | dense와 sparse 후보의 합집합 구성 가능 | semantic 결과만 최종 후보가 됨 |
| 결합 방식 | Qdrant의 RRF 또는 DBSF 등 | Mem0의 가산식 `score_and_rank()` |
| entity 신호 | 애플리케이션에서 별도 구현 필요 | 별도 entity collection의 boost를 함께 결합 |
| 결합 위치 | Qdrant 서버 | Mem0 애플리케이션 프로세스 |
| provider 종속성 | Qdrant 전용 | 공통 `keyword_search()` 인터페이스를 구현한 여러 vector store에서 사용 |

로컬 `mem0ai 2.0.12` snapshot에서는 다음 사실을 코드로 확인할 수 있다.

1. `mem0/vector_stores/qdrant.py`의 `search()`는 dense vector로 `client.query_points()`를 호출한다.
2. 같은 파일의 `keyword_search()`는 `using="bm25"`인 sparse query를 별도로 호출한다.
3. `prefetch`, `FusionQuery`, RRF, DBSF를 호출하는 코드는 없다.
4. `mem0/memory/main.py`는 semantic 결과로만 candidate를 만들고 BM25/entity 결과는 ID별 점수 map으로 전달한다.
5. `mem0/utils/scoring.py`는 semantic candidate를 순회하면서 BM25와 entity 점수를 가산한다.

공식 마이그레이션 문서도 이 동작을 명시한다. BM25는 recall을 확장하는 신호가 아니라 boost 신호이며, semantic search 결과만 후보가 된다. 2026-07-18 기준 upstream `main`의 Qdrant adapter에서도 `prefetch`나 `FusionQuery` 사용은 확인되지 않았다. 따라서 이는 우리가 받은 snapshot만의 누락이나 구버전 문제로 보기 어렵다.

### 왜 Qdrant의 기본 기능을 사용하지 않는가

Mem0 개발자가 “Qdrant Native Hybrid를 사용하지 않은 이유”를 직접 설명한 문서나 PR 코멘트는 확인하지 못했다. 따라서 아래 내용을 **공식적으로 확인된 설계 사실**과 **코드에서 추론한 이유**로 구분해야 한다.

공식 문서와 V3 도입 PR에서 확인되는 사실은 다음과 같다.

- Mem0는 15개 vector store adapter에 공통 `keyword_search()` 기능을 추가했다.
- semantic, BM25, entity 점수 결합은 vector store가 아니라 Mem0 중앙 검색 pipeline에서 수행한다.
- spaCy, Qdrant `fastembed`, entity store가 없어도 가능한 신호만 사용하도록 graceful degradation한다.
- Qdrant에서는 dense vector와 BM25 sparse vector를 같은 collection에 저장하지만 검색 호출과 fusion은 분리한다.

이 사실들로부터 다음 설계 이유를 추론할 수 있다.

1. **Provider 중립성:** Qdrant RRF에 결합 로직을 맡기면 Qdrant와 다른 vector store의 결과 및 score 의미가 달라진다. 중앙 결합은 provider별 동작 차이를 줄인다.
2. **Entity 점수 포함:** Mem0는 dense와 sparse뿐 아니라 별도 entity collection에서 계산한 연결 점수까지 포함한다. 따라서 Qdrant Dense+Sparse fusion만으로 검색 pipeline 전체를 대체할 수 없다.
3. **Graceful degradation:** BM25나 entity 기능 하나가 없어도 동일한 상위 pipeline에서 semantic-only로 계속 동작할 수 있다.
4. **Semantic precision 우선:** keyword만 일치하는 결과를 후보에 새로 넣지 않고 semantic 관련성을 기본 통과 조건으로 사용한다. 다만 이것이 개발자가 밝힌 직접적인 선택 이유라는 근거는 없으므로 추론으로만 취급한다.

### 이 선택으로 잃는 것

가장 큰 대가는 sparse-only recall이다. 문서 ID, 오류 코드, API·클래스명, 버전, 숫자, 고유명사처럼 정확 문자열 일치가 중요한 질의가 BM25에서는 높은 점수를 얻더라도 semantic candidate pool에 들지 못하면 최종 결과에서 사라진다. `threshold`까지 semantic 점수에 먼저 적용되므로 이후의 BM25, entity boost, reranker도 이를 복구하지 못한다.

예를 들어 `INC-2026-001924`를 포함한 memory가 dense top-60/80 밖에 있으면 BM25가 정확히 일치해도 Mem0 기본 검색은 이를 반환하지 못할 수 있다. Qdrant Native Hybrid의 dense/sparse 후보 합집합은 이런 항목을 sparse 경로로 후보에 포함시킬 수 있다.

우리처럼 Qdrant를 고정하고 한국어 연구 자료와 기술 식별자를 검색하는 구성에서는 Mem0의 provider 중립성보다 이 recall 차이가 더 중요할 수 있다. 따라서 Mem0 기본 방식을 그대로 전제하지 않고 다음 두 pipeline을 PoC에서 비교한다.

```text
[Mem0 기본]
dense 후보
  → BM25 점수 가산
  → entity boost
  → top_k
  → optional reranker

[Qdrant Native 확장안]
dense 후보 ∪ sparse 후보
  → Qdrant RRF 또는 DBSF
  → Mem0 entity boost
  → top_k
  → optional reranker
```

Native 확장안은 `Qdrant` adapter의 내부 구현만 바꾸면 끝난다고 단정할 수 없다. 현재 `Memory._search_vector_store()`가 semantic 결과를 기준으로 candidate와 threshold를 관리하기 때문이다. 구현한다면 별도 `hybrid_search()` 경로를 adapter와 MemoryService/fork에 추가하고, native fusion 결과 뒤에 entity boost와 reranker를 적용하는 편이 경계가 명확하다.

### 근거 자료

- Mem0 공식 문서, [Open Source: Migrating to the New Memory Algorithm](https://docs.mem0.ai/migration/oss-v2-to-v3): V3 retrieval 흐름, BM25 boost-only 후보 정책, vector store 호환성과 graceful degradation. 확인일 2026-07-18.
- Mem0 공식 GitHub, [PR #4805: V3 pipeline with hybrid search, entity extraction, and additive scoring](https://github.com/mem0ai/mem0/pull/4805): 15개 adapter의 keyword search와 중앙 additive scoring 도입 근거. 확인일 2026-07-18.
- Mem0 공식 GitHub, [현재 Qdrant adapter](https://github.com/mem0ai/mem0/blob/main/mem0/vector_stores/qdrant.py): dense와 sparse의 별도 `query_points()` 호출. 확인일 2026-07-18.
- Qdrant 공식 문서, [Hybrid Queries](https://qdrant.tech/documentation/search/hybrid-queries/): `prefetch`, RRF 및 DBSF를 사용하는 native hybrid 기능. 확인일 2026-07-18.
- Mem0 공식 GitHub, [Issue #4884](https://github.com/mem0ai/mem0/issues/4884): 영어 중심 BM25 lemmatization/entity extraction 문제 제기. 이는 문제 보고이며 Mem0 유지보수자의 Qdrant 설계 이유에 대한 공식 설명은 아니다. 확인일 2026-07-18.

## 1. `Memory.search()`의 입력 제약

```python
memory.search(
    "query",
    filters={"user_id": "alice"},
    top_k=20,
    threshold=0.1,
    rerank=False,
    explain=False,
)
```

- `filters`에는 `user_id`, `agent_id`, `run_id` 중 하나 이상이 필수다.
- entity ID를 `search(user_id="...")`처럼 최상위 인자로 넘기면 오류가 난다.
- 기본 `top_k=20`, 기본 `threshold=0.1`, 기본 `rerank=False`다.
- metadata comparison/logical filter는 `Memory._process_metadata_filters()`를 거쳐 vector store로 전달된다.
- `show_expired=False`이면 payload의 expiration date가 지난 메모리는 후보에서 제외한다.

`search()`는 `_search_vector_store()` 결과에, 요청에서 `rerank=True`이고 reranker가 설정되어 있을 때만 reranker를 적용한다. reranker 호출이 실패하면 경고 후 원래 hybrid 순위를 반환한다.

## 2. 후보 생성: semantic search가 유일한 recall 경로

`_search_vector_store()`의 순서는 다음과 같다.

1. query를 `lemmatize_for_bm25()`와 `extract_entities()`로 전처리한다.
2. query를 dense embedding한다.
3. `internal_limit = max(limit * 4, 60)`으로 계산한다.
4. `vector_store.search()`로 dense semantic 결과를 `internal_limit`개까지 가져온다.
5. `vector_store.keyword_search()`와 entity boost 계산을 순서대로 수행한다. entity별 store search만 thread pool 최대 4개로 병렬화한다.
6. 최종 candidate list는 **semantic 결과만**으로 만든다.

예를 들어 API `top_k=20`이면 semantic search는 최대 80개, `top_k=5`여도 최소 60개를 가져온다. 이후 점수 결합과 threshold를 거쳐 최종 top-k를 고른다.

## 3. BM25 keyword signal

### 입력과 저장

저장 시에는 `lemmatize_for_bm25(text)` 결과가 payload의 `text_lemmatized`에 들어간다. Qdrant 어댑터는 `fastembed`의 `Qdrant/bm25` sparse encoder로 이를 `bm25` named sparse vector에 기록한다.

검색 시에는 lemmatized query로 `keyword_search()`를 호출한다. raw BM25 점수는 query term 수에 따른 sigmoid로 `[0, 1]` 범위에 정규화된다.

| lemmatized term 수 | sigmoid midpoint / steepness |
| --- | --- |
| 1~3 | 5.0 / 0.7 |
| 4~6 | 7.0 / 0.6 |
| 7~9 | 9.0 / 0.5 |
| 10~15 | 10.0 / 0.5 |
| 16 이상 | 12.0 / 0.5 |

긴 query일수록 raw BM25가 높아지는 경향을 보정하려는 구현이다.

### graceful degradation

`fastembed`가 없거나, 기존 Qdrant collection에 `bm25` sparse slot이 없거나, vector store가 `keyword_search()`를 구현하지 않으면 BM25 결과는 `None`이 된다. search는 실패하지 않고 semantic-only 또는 entity 포함 검색으로 내려간다.

## 4. entity boost signal

`extract_entities()`는 spaCy 기반으로 query entity 후보를 만든다. 코드는 먼저 `query_entities[:8]`을 자른 뒤 중복을 제거하므로, 실제 고유 엔티티 수는 최대 8개보다 적을 수 있다. 각 엔티티를 임베딩해 entity collection에서 scope filter와 함께 검색한다.

```text
query entity
  → entity collection 검색 (각 entity top 500)
  → similarity >= 0.5인 entity record만 사용
  → record.linked_memory_ids에 있는 main memory에 boost 부여
```

boost 식은 다음과 같다.

```text
boost = entity_similarity × 0.5 × (1 / (1 + 0.001 × (linked_count - 1)^2))
```

- 최대 기본 가중치는 `ENTITY_BOOST_WEIGHT = 0.5`다.
- 한 엔티티에 너무 많은 메모리가 연결되면 `linked_count` 감쇠가 적용된다.
- 동일 memory에 여러 엔티티가 매칭되어도 합산이 아니라 **가장 큰 boost 하나**만 남긴다.

### 한국어 환경의 주의점

entity extraction과 lemmatization은 `mem0/utils/spacy_models.py`에서 `en_core_web_sm`을 로드한다. spaCy는 설치됐지만 모델이 없으면 첫 호출에서 model download를 자동 시도한다. 이는 폐쇄망에서 지연·실패를 만들 수 있다. 한 번 실패하면 process 내 failure flag가 설정되어 이후에는 빈 엔티티/원문 텍스트 fallback을 사용한다.

따라서 이 snapshot을 한국어 중심으로 Gemma 4 31B와 사용할 때:

- LLM fact extraction 언어 품질과,
- Python spaCy의 영어 기반 BM25 lemma/entity 추출 품질은

별개의 문제다. 한국어 entity boost와 lemmatized BM25 품질은 낮거나 사실상 비활성일 수 있으므로 PoC에서 semantic-only 대비 결과를 측정해야 한다.

## 5. 최종 점수 결합

`mem0/utils/scoring.py`의 `score_and_rank()`는 semantic 후보만 돌며 아래 점수를 계산한다.

```text
raw_combined = semantic_score + bm25_score + entity_boost
final_score = min(raw_combined / max_possible, 1.0)
```

분모 `max_possible`은 활성 신호에 따라 달라진다.

| 활성 신호 | 분모 |
| --- | --- |
| semantic만 | 1.0 |
| semantic + BM25 | 2.0 |
| semantic + entity | 1.5 |
| semantic + BM25 + entity | 2.5 |

중요하게도 `threshold`는 final score가 아니라 **semantic score에 먼저 적용**된다. semantic score가 `threshold` 미만인 후보는 BM25/entity 점수가 높아도 버려진다.

또 하나의 주의점은 신호 활성 여부가 candidate별이 아니라 query 전체 dict의 비어 있음으로 결정된다는 점이다. 예를 들어 BM25 match가 한 건이라도 있으면 모든 semantic candidate의 분모가 2.0 이상이 된다. BM25 score가 없는 candidate도 같은 큰 분모를 쓰므로 absolute score가 내려갈 수 있다. threshold는 결합 전에 적용되지만, 최종 `score`에 별도 cutoff를 두는 애플리케이션은 이 동작을 감안해 다시 보정해야 한다.

`explain=True`로 호출하면 `semantic_score`, `bm25_score`, `entity_boost`, 분모, final score가 `score_details`로 반환되어 디버깅할 수 있다.

## 6. reranker의 실제 위치

reranker는 hybrid candidate 생성이나 score fusion에 참여하지 않는다. `_search_vector_store()`가 결과를 만든 뒤 `Memory.search()`가 다음 조건에서만 호출한다.

```text
rerank=True AND MemoryConfig.reranker가 설정됨 AND 결과가 하나 이상 있음
```

따라서 reranker는 후보를 넓히지 않고, 이미 dense semantic candidate pool에서 살아남아 **hybrid top-k로 잘린 결과**의 순서만 바꾼다. `top_k` 밖으로 밀린 candidate를 reranker가 복구하지 못하므로 recall 문제는 해결하지 못한다.

## 7. 우리 PoC에서 확인할 항목

| 가설 | 비교 방법 |
| --- | --- |
| Korean query에서 BM25/entity가 이득인가 | semantic-only, BM25 설치, spaCy 활성 상태를 분리한 동일 데이터셋에서 비교 |
| dense candidate pool이 충분한가 | 정답 메모리가 semantic top-60 안에 드는 recall 측정 |
| boost가 의도와 맞는가 | `explain=True`로 query별 `score_details` 저장 및 검토 |
| reranker가 실질적으로 순위를 개선하는가 | rerank on/off의 MRR·정확도·latency 비교 |
| 0.1 threshold가 적절한가 | 업무 query별 false negative/false positive를 보고 재조정 |
| Native Hybrid가 sparse-only 정답을 복구하는가 | Mem0 기본 검색과 dense∪sparse Qdrant RRF/DBSF의 Recall@K·MRR 비교 |
| 기술 식별자 검색이 충분한가 | 문서 ID, 오류 코드, 버전, API·클래스명을 포함한 exact-match 질의군을 별도 평가 |

현재 public `search()`에는 BM25와 entity boost를 각각 끄는 request-level flag가 없다. 위 비교는 dependency가 다른 실험 환경/collection을 분리하거나, 우리 `MemoryService` wrapper 또는 fork에 feature gate를 추가해 수행해야 한다. `rerank`만 public flag로 제어할 수 있다.

Qdrant adapter의 sparse vector, filter 구현, entity collection 생성 방식은 다음 문서에서 더 자세히 분석한다.
