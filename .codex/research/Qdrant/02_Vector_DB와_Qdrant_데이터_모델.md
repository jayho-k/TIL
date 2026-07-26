Exit code: 0
Wall time: 2.6 seconds
Output:
# Vector DB와 Qdrant 데이터 모델 — 공개 설계 사례 기반

> 학습 단계: 1 / 9  
> 조사 기준일: 2026-07-24  
> 목적: 사용자별 subagent 메모리 시스템을 설계하기 전에, 공개된 기업·프레임워크·Qdrant 공식 문서가 실제로 어떤 데이터 경계와 scope 방식을 채택했는지 확인한다.

## 이 노트의 읽는 법

이 문서는 “이렇게 설계해야 한다”는 가상 예시나 단일 정답을 제시하지 않는다. 각 사례에서 확인되는 사실과, 그 사실만으로는 알 수 없는 점을 분리한다.

| 출처 등급 | 사용한 자료 | 신뢰도와 한계 |
| --- | --- | --- |
| 1차 기술 문서 | Qdrant 공식 문서 | 공개 API와 제품 동작을 확인하기 좋음. 특정 고객의 실제 운영 전체를 뜻하지는 않음 |
| 공개 고객 사례 | Dust, Fieldy AI, Deutsche Telekom 사례 | 구체적인 설계 선택을 볼 수 있음. Qdrant가 발행한 고객 사례이므로 성능·비용 수치는 독립 검증 자료가 아님 |

따라서 이후 설계 단계에서 이 사례들은 **후보와 검증 질문**의 근거로 쓰고, 우리 워크로드에서의 성능·보안·비용은 별도 실험으로 검증한다.

---

## 1. 핵심 개념: 정의와 공개 사례의 연결

### 1.1 Vector DB와 embedding

**Vector DB**는 텍스트·이미지·음성처럼 비정형 데이터를 embedding 모델이 만든 숫자 배열(vector)로 저장하고, 질의 vector와 가까운 Point를 찾는 저장·검색 시스템이다. Qdrant는 embedding 모델 그 자체가 아니라, 만들어진 vector와 metadata를 저장하고 검색하는 계층이다. Qdrant Cloud에는 embedding을 서버에서 생성하는 기능도 있지만, 일반적인 아키텍처에서는 애플리케이션 또는 별도 inference 계층이 embedding을 만든다.

```text
원문 또는 이벤트
  → embedding 모델
  → vector
  → Qdrant: 저장·유사도 검색·filter
```

이 구분은 실제 사례에서 중요하게 나타난다.

- **Fieldy AI**는 음성을 전사한 뒤 backend에서 embedding을 만들고 Qdrant에 저장한다. 즉 Qdrant는 “말을 이해해 기억을 만드는” 컴포넌트가 아니라 전사·embedding 결과의 검색 계층이다.
- **Dust**는 embedding model별로 Collection을 구성하는 방향을 택했다. 이 사례는 embedding model이 단순한 라이브러리 설정이 아니라 Collection topology를 결정할 수 있음을 보여 준다.

따라서 “에이전트 기억을 Qdrant에 저장한다”는 말은 대화 원문을 무조건 저장한다는 뜻이 아니다. 무엇을 memory record로 추출할지, 어떤 embedding 모델을 쓸지는 Qdrant 앞단의 설계 책임이다.

### 1.2 Point: Qdrant가 검색하는 최소 레코드

**Point**는 Qdrant의 기본 데이터 레코드다. Point는 `id`, 하나 이상인 `vector`, 선택적인 `payload`로 구성된다. ID는 64-bit unsigned integer 또는 UUID를 사용할 수 있다.

```json
{
  "id": "018f4b6c-1ef7-7d9d-a946-58f2ee7d6e76",
  "vector": [0.12, -0.04, 0.81],
  "payload": {
    "group_id": "tenant-42",
    "created_at": "2026-07-24T10:00:00Z"
  }
}
```

여기서 vector는 “어떤 Point가 질의와 의미상 가까운가”를 위한 값이고, payload는 “어떤 Point를 검색 후보에 넣어도 되는가”를 제한하거나 결과를 설명하는 JSON metadata다.

공개 사례에서는 Point의 실제 의미가 서로 다르다.

| 사례 | Point가 나타내는 것으로 공개된 단위 |
| --- | --- |
| Fieldy AI | 전사된 대화와 그 embedding. 이후 raw transcript 외 summary embedding도 검토 중 |
| Dust | 수천 데이터 소스에서 들어오는 vector record. 정확한 chunk schema는 비공개 |
| Qdrant 멀티테넌시 문서 | tenant를 나타내는 `group_id` payload를 가진 vector record |

즉 Point는 항상 “문서 chunk”를 뜻하지 않는다. 앞으로 **subagent memory를 설계할 때도 fact, decision, procedure, transcript segment 중 어느 것을 Point로 만들지 별도로 결정**해야 한다. 이 결정은 사례가 대신 내려주지 않는다.

### 1.3 Collection: 단순 폴더가 아니라 검색·운영 경계

**Collection**은 검색할 Point의 이름 있는 집합이다. 일반 dense vector를 쓰는 Collection에서는 모든 Point가 같은 vector 차원과 같은 distance metric을 공유한다. Collection은 또한 HNSW, optimizer, payload storage, shard 같은 검색·운영 설정의 단위다.

```text
Collection: text_embedding_v1
  ├─ Point 1: 768차원 text vector + payload
  ├─ Point 2: 768차원 text vector + payload
  └─ Point 3: 768차원 text vector + payload
```

그래서 Collection을 나누는 기준은 이름이나 소유자보다 다음과 같은 **계약의 차이**다.

| 분리 기준 | 같은 Collection에 둘 수 있는 경우 | 분리를 검토할 경우 |
| --- | --- | --- |
| vector contract | 같은 embedding model·차원·거리 함수 | 모델 또는 vector 형식이 다름 |
| 검색 경로 | 하나의 query에서 함께 후보가 됨 | 서로 절대 섞여 검색되면 안 됨 |
| payload/filter | 같은 metadata schema와 filter 패턴 | schema·filter·권한 규칙이 본질적으로 다름 |
| 운영 | 함께 index·백업·확장해도 됨 | 독립 scaling, 강한 물리 격리, 별도 보존 정책이 필요 |

**Dust의 실제 변화**가 이 개념의 좋은 근거다. Dust는 처음에 데이터 소스별 Collection을 만들었지만, 데이터 소스가 5,000개를 넘고 **Collection 수가 거의 1,000개에 이르자 RAM과 검색 성능 문제가 커졌다고 밝혔다.** 이후 Collection을 data source별이 아니라 **shared multi-tenant 및 embedding model 기준으로 통합했다.**

반대로 Qdrant 공식 문서는 사용자 수가 제한적이고 강한 격리가 필요할 때 여러 Collection을 고려할 수 있다고 설명한다. 따라서 “사용자별 Collection은 항상 틀리다”가 아니라, 수많은 작은 Collection은 비용이 크며 Collection 경계에 기술적 근거가 있어야 한다는 뜻이다.

### 1.4 Payload: metadata이자 검색 범위의 입력

**Payload**는 Point에 붙는 JSON metadata다. Qdrant는 payload condition을 vector query와 결합해 후보를 제한할 수 있고, 자주 필터하는 field에는 payload index를 만들 수 있다.

```json
{
  "group_id": "tenant-42",
  "source_id": "connector-slack",
  "created_at": "2026-07-24T10:00:00Z"
}
```

Qdrant의 공식 멀티테넌시 문서는 이 payload를 이용해 tenant를 partition한다. `group_id`를 keyword index로 만들고 `is_tenant=true`를 지정하면 동일 tenant vector를 함께 배치해 tenant-filtered query의 효율을 높일 수 있다. 이 기능은 tenant filter가 늘 존재하는 워크로드에 맞춘 최적화다. filter 없는 전역 검색은 오히려 더 느려질 수 있다.

이 사례에서 얻어야 할 개념은 “payload는 부가 설명”이 아니라는 점이다. `group_id` 같은 field는 데이터 격리와 검색 경로의 일부다. 다만 Qdrant filter는 데이터베이스 query의 조건이지, 호출자가 다른 tenant ID를 넣지 못하게 하는 authorization 계층은 아니다. 이 구분은 3단계 멀티테넌시에서 더 자세히 다룬다.

### 1.5 Dense Vector, Sparse Vector, MultiVector, Named Vector

네 용어는 같은 층위가 아니다. **Dense·Sparse·MultiVector는 한 vector field에 무엇을 저장하느냐**이고, **Named Vector는 한 Point에 그러한 field를 여러 개 둘 수 있게 하는 schema 방식**이다. 특히 MultiVector와 Named Vector를 같은 기능으로 이해하면 설계가 꼬이기 쉽다.

```text
하나의 Point
├─ vector field `semantic`        → Dense vector 1개
├─ vector field `lexical`         → Sparse vector 1개
├─ vector field `late_interaction`→ MultiVector 1개(선택)
└─ payload                         → 위 vector들이 공통으로 공유하는 metadata

`semantic`·`lexical`·`late_interaction`이라는 이름을 둘 수 있게 하는 것이 Named Vector다.
```

위 그림은 Qdrant가 지원하는 일반적인 schema를 보여 주기 위한 것이며, Fieldy나 Dust가 이 이름과 구조를 실제로 사용한다는 뜻은 아니다.

#### 1.5.1 Dense Vector — 의미가 비슷한 대상을 찾는 고정 길이 표현

**Dense vector**는 모든 Point가 같은 차원의 실수 배열을 하나씩 갖는 방식이다. 예를 들어 `size: 768`인 dense vector field라면 각 Point는 길이 768의 배열을 가져야 하며, 해당 field의 distance metric도 schema에서 정한다. 값 대부분이 0이 아니어도 되고, sparse vector와 달리 배열의 모든 위치를 순서대로 가진다.

```json
"semantic": [0.12, -0.04, 0.81, "... 총 768개 값 ..."]
```

문장 embedding 모델은 비슷한 뜻의 문장을 가까운 위치에 놓도록 학습된다. 그래서 dense retrieval은 표현이 달라도 의미가 비슷한 기억을 찾는 데 적합하다. 반면 에러 코드, 고객 ID, 제품 코드처럼 **정확한 토큰 자체가 중요한 질의**는 의미가 비슷하다는 이유만으로 충분히 회수되지 않을 수 있다. Qdrant의 dense 검색은 기본적으로 HNSW 근사 탐색을 사용하며, 필요하면 exact search로 바꿀 수 있다. 이 차이는 2단계에서 다룬다.

**공개 사례 연결 — Fieldy AI:** Fieldy는 전사문에 대한 embedding을 Qdrant에 저장하고 HNSW dense retrieval을 사용한다고 공개했다. 이는 dense vector가 장기 대화에서 의미 관련 후보를 찾는 역할을 하는 실제 사례다. 다만 Fieldy는 vector 차원, field 이름, Collection schema를 공개하지 않았으므로 그 내부 schema까지 추정하면 안 된다.

#### 1.5.2 Sparse Vector — 드문 단어·식별자를 보존하는 희소 표현

**Sparse vector**는 전체 차원 길이를 0으로 채워 저장하지 않고, 실제 값이 있는 위치만 `(index, value)`로 저장하는 표현이다. 따라서 Point마다 값의 개수가 달라도 된다.

```json
"lexical": {
  "indices": [42, 9182, 50101],
  "values":  [0.73, 1.20, 0.41]
}
```

여기서 `42` 같은 index는 tokenizer 또는 sparse model이 만든 vocabulary 위치이고, `0.73`은 그 항목의 가중치다. Qdrant에서 sparse vector는 **이름이 있는 vector field로만** 정의하며, dense vector와 별도의 sparse index에 저장된다. 공식 문서 기준 sparse query는 정확하게 수행되고 dot product로 점수를 계산한다.

BM25는 sparse vector 자체의 이름이 아니라, 단어 빈도와 희소성을 이용해 lexical score를 만드는 대표적인 검색 알고리즘이다. 따라서 “BM25를 쓴다”는 말은 대개 정확한 단어·용어 일치 신호를 dense 의미 검색에 보완한다는 뜻이지, 자동으로 특정 Qdrant schema를 뜻하지는 않는다.

**공개 사례 연결 — Fieldy AI:** Fieldy는 HNSW dense retrieval과 **BM25 term matching**을 함께 사용하고 RRF로 순위를 결합한다고 공개했다. 이는 사람 이름, 회의 제목, 고유 표현처럼 lexical signal이 필요한 제품에서 dense 단독 검색의 빈틈을 보완한 사례다. 하지만 Fieldy가 Qdrant의 native sparse vector를 어떤 이름·설정으로 썼는지는 공개하지 않았으므로, “BM25를 사용했다”를 “특정 `lexical` named sparse vector를 사용했다”로 단정할 수 없다.

#### 1.5.2-a 왜 Sparse는 단어·용어 일치 중심이고 Dense는 의미 유사성에 쓸 수 있는가?

앞의 “0이 아닌 위치만 저장한다”는 설명은 저장 공간 절약만 뜻하지 않는다. **어떤 차원이 0인지와 유사도 계산 방식이 sparse retrieval의 검색 특성을 만든다.**

Sparse vector는 먼저 tokenizer 또는 sparse model이 vocabulary의 토큰마다 고정된 index를 부여한다. 문서에 해당 토큰이 있거나 모델이 그 토큰을 중요한 검색 신호로 판단하면 그 index에 0이 아닌 가중치를 둔다. 없으면 논리적으로는 0이다. dot product는 같은 index의 값을 곱해 더하므로, query와 Point 양쪽에서 모두 0이 아닌 index만 점수에 기여한다.

```text
문서 Point: qdrant(index 42)=0.8, hnsw(index 9182)=1.2
질의 Query: qdrant(index 42)=0.6, hnsw(index 9182)=0, redis(index 77)=0.9

score = (0.8 × 0.6)      # qdrant: 양쪽에 있어 기여
      + (1.2 × 0)        # hnsw: query에는 없어 기여하지 않음
      + (0 × 0.9)        # redis: Point에는 없어 기여하지 않음
      = 0.48
```

따라서 sparse vector의 검색 특성은 다음 인과관계로 생긴다.

```text
토큰별 고정 index
  → 문서/질의에 없는 토큰은 0
  → 공통 non-zero index만 dot product에 기여
  → 같은 단어·용어·식별자(또는 sparse model이 확장한 관련 토큰) 중심으로 회수
```

여기서 **0은 새로운 특징을 만드는 값이 아니다.** 해당 token feature가 이 문서 또는 이 질의에 없어서 유사도에 기여하지 않게 하는 값이다. 반대로 0이 아닌 값과 공통 index의 존재가 lexical match라는 검색 특징을 만든다. BM25는 이러한 lexical signal의 가중치를 계산하는 대표적인 방법이며, SPLADE 같은 learned sparse model은 원문에 없는 관련 vocabulary token에도 0이 아닌 값을 둘 수 있다. 그렇더라도 각 차원이 vocabulary token에 연결되어 있다는 점은 유지된다.

Dense vector는 같은 방식으로 token index를 비교하지 않는다. embedding model이 문장 전체를 읽어 항상 같은 길이의 배열을 만들고, 학습 과정에서 의미가 비슷한 입력은 가까운 숫자 패턴이 되도록 학습한다. 그러므로 dense vector의 각 좌표는 보통 `환불`, `HNSW`처럼 사람이 이름 붙일 수 있는 한 단어가 아니라, 여러 문맥·의미 신호가 분산된 잠재 표현이다.

```text
"환불을 받고 싶어요"       ── embedding model ──→ dense pattern A
"결제한 돈을 돌려주세요"   ── embedding model ──→ dense pattern B

두 문장에 공통 단어가 거의 없어도,
모델이 두 문장을 비슷한 의도로 학습했다면 A와 B의 전체 패턴은 가까울 수 있다.
```

따라서 **“고정 길이” 자체가 dense vector를 의미 검색으로 만드는 것은 아니다.** 고정 길이는 schema·저장 형식의 성질이고, 의미 유사성을 만드는 원인은 embedding 모델의 학습 데이터와 objective다. 품질이 낮거나 업무 도메인에 맞지 않는 dense embedding 모델은 의미 검색을 잘하지 못할 수 있다. 이 때문에 Fieldy처럼 dense 신호와 BM25 lexical signal을 함께 평가하는 선택이 등장한다.

#### 1.5.3 MultiVector — 한 Point 안에 여러 dense vector를 담는 late-interaction 표현

**MultiVector**는 하나의 vector field 값이 vector 하나가 아니라 같은 차원의 dense vector 여러 개로 이루어진 행렬인 방식이다. 각 행의 차원은 고정이지만, 한 Point가 갖는 행의 수는 달라도 된다.

```json
"late_interaction": [
  [0.10, 0.21, "... 같은 차원의 값 ..."],
  [0.34, 0.05, "... 같은 차원의 값 ..."],
  [0.87, 0.19, "... 같은 차원의 값 ..."]
]
```

Qdrant의 현재 multivector comparator는 `max_sim`이다. query가 여러 sub-vector를 가질 때, query의 각 sub-vector마다 Point 내부에서 가장 유사한 sub-vector 하나를 고르고 그 점수를 합산한다. 즉 문서 전체를 vector 하나로 압축해 한 번 비교하는 dense retrieval과 달리, query의 여러 부분을 문서의 서로 다른 부분과 대응시킬 수 있다. ColBERT처럼 late interaction을 쓰는 모델이 대표적인 사용처다.

```text
점수 = query의 각 sub-vector마다
       Point 안에서 가장 높은 유사도 1개를 선택해 모두 더한 값
```

이는 **Named Vector와 다르다.** MultiVector는 `late_interaction`이라는 *한 field의 값 형식*이고, Named Vector는 `semantic`, `lexical`, `late_interaction`처럼 *field를 여러 개 두는 schema*다. MultiVector는 더 정교한 matching을 제공할 수 있지만 vector 수와 비교량이 늘어 storage·ingestion·query 비용을 별도 측정해야 한다.

현재 이 노트에서 조사한 Fieldy·Dust·Deutsche Telekom 공개 사례에는 MultiVector 사용 여부가 확인되지 않는다. 따라서 “에이전트 기억이면 MultiVector가 더 좋다”는 결론은 낼 수 없다. 실제로 late-interaction embedding 모델을 채택했을 때만 후보로 두고, 이후 실습에서 dense 단독 방식과 품질·지연시간을 비교할 대상이다.

#### 1.5.3-a MultiVector는 왜 필요한가 — 전체 요약에서 사라지는 세부 대응을 남기기 위해

일반 dense retrieval은 긴 문서나 memory record 전체를 vector 하나로 **압축**해 query vector 하나와 비교한다. 빠르고 단순하지만, 문서 안의 특정 문장·개념 하나가 전체 내용의 평균적인 표현에 묻힐 수 있다.

```text
일반 Dense
긴 문서 전체 ── embedding model ──→ dense vector 하나
query vector 하나 ── 유사도 비교 ──→ 문서 전체의 대략적인 관련성
```

MultiVector는 late-interaction 모델이 문서의 여러 부분에서 만든 sub-vector들을 한 Point에 보존한다. query도 여러 sub-vector로 표현한 뒤, query의 각 부분이 Point 내부의 어느 부분과 가장 잘 맞는지 비교한다.

```text
MultiVector
문서 Point
├─ 문서의 부분 A를 나타내는 sub-vector
├─ 문서의 부분 B를 나타내는 sub-vector
└─ 문서의 부분 C를 나타내는 sub-vector

query의 각 sub-vector
  → Point 내부에서 가장 잘 맞는 sub-vector를 선택
  → 선택된 점수를 모두 합산(max_sim)
```

따라서 MultiVector가 만드는 검색 특징은 “문서 전체가 대략 비슷한가?”보다 **“문서 안에 query의 각 부분과 잘 대응하는 부분이 있는가?”**를 더 세밀하게 보는 것이다. 예를 들어 하나의 긴 기술 문서 안에 payload filter, HNSW, snapshot 복구가 함께 있을 때, `HNSW 설정` 질의는 문서 전체의 평균이 아니라 HNSW 관련 부분과의 강한 대응을 얻을 수 있다. 이 예시는 원리를 보조하기 위한 가상 설명이며, 특정 기업의 공개 구현은 아니다.

이 방식은 다음과 같은 경우에 검토할 수 있다.

| 필요한 상황 | MultiVector가 해결하려는 문제 |
| --- | --- |
| 긴 문서·논문·매뉴얼 검색 | 문서 전체를 vector 하나로 압축하며 잃는 세부 문맥 보완 |
| ColBERT 같은 late-interaction retrieval 모델 사용 | 모델이 생성한 query/document sub-vector를 `max_sim` 방식으로 비교 |
| 코드·기술 자료처럼 여러 세부 개념의 대응이 중요한 검색 | query의 각 부분이 문서의 서로 다른 부분에 대응하는지 확인 |
| 이미지 patch 등 여러 지역 표현을 검색하는 멀티모달 모델 | 한 이미지의 여러 영역을 하나의 global vector로만 축약하지 않음 |

반대로 짧은 preference, fact, decision처럼 Point 자체가 이미 작은 memory 단위라면 dense vector 하나로 충분할 가능성이 있다. MultiVector는 vector 수가 늘어 storage·ingestion·query 비용도 증가하므로, 단지 Point에 vector를 여러 개 두고 싶다는 이유만으로 선택하지 않는다. 특히 **MultiVector의 입력은 임의로 잘라 만든 일반 embedding 여러 개가 아니라, late-interaction을 전제로 학습된 모델의 출력일 때 의미가 가장 분명하다.**

Named Vector와의 차이도 다시 정리하면 다음과 같다.

```text
Named Vector: 같은 memory record를 semantic / lexical처럼 서로 다른 검색 기준으로 둠
MultiVector: 하나의 검색 기준 안에서 문서·query의 여러 부분을 세밀하게 대응시킴
```

#### 1.5.4 Named Vector — 같은 Point를 여러 검색 공간으로 나타내는 schema

**Named Vector**는 한 Point의 `vector`를 배열 하나가 아니라 이름→vector의 map으로 만드는 방식이다. 각 이름은 서로 다른 차원, distance metric, vector type(dense/sparse/multivector)를 가질 수 있다.

```json
"vector": {
  "semantic": [0.12, -0.04, "..."],
  "lexical": {
    "indices": [42, 9182],
    "values": [0.73, 1.20]
  }
}
```

Named Vector가 필요한 이유는 **동일한 Point와 동일한 payload를 여러 표현으로 검색해야 하기 때문**이다. 예를 들어 하나의 memory record에 tenant·agent·시간·source payload를 한 번만 붙이고, 의미 검색은 `semantic`, 키워드 검색은 `lexical` field로 수행할 수 있다. 텍스트 embedding과 이미지 embedding처럼 서로 다른 modality를 같은 업무 레코드에 귀속시키는 경우도 같은 원리다.

그러나 Named Vector 자체가 결과를 합치거나 hybrid search를 자동 수행하지는 않는다. 어느 vector field를 query할지, 두 검색 결과를 `prefetch`와 RRF/DBSF로 어떻게 결합할지는 별도의 query 설계다. 이는 6단계 Hybrid Search에서 다룬다.

Qdrant 공식 FAQ는 같은 payload를 공유하고 하나의 요청에서 여러 vector space를 함께 질의해야 할 때 Named Vector를 권장한다. 반대로 payload schema·보존 주기·독립 scaling·질의 패턴이 다르면 Collection 분리가 더 자연스럽다.

**공개 사례와의 연결:** Fieldy의 dense + BM25 결합은 의미 신호와 lexical 신호를 분리해 다뤄야 하는 문제를 보여 준다. 다만 그 결합을 Named Vector로 구현했는지는 공개되지 않았다. Dust는 반대로 embedder별 shared Collection을 두었다고 공개했으며, 이는 embedding contract와 운영 경계가 다르면 field를 늘리기보다 Collection을 나눌 수 있음을 보여 준다. 두 사례를 Named Vector 사용 사실로 과장해서는 안 된다.

#### 1.5.5 네 개념을 한 표로 비교

| 구분 | Point 안의 형태 | 주된 검색 신호 | Qdrant에서 알아둘 제약·성질 | 도입을 검토할 조건 |
| --- | --- | --- | --- | --- |
| Dense vector | 고정 길이 실수 배열 1개 | 의미 유사도 | 같은 field는 차원·metric 계약을 공유, 기본적으로 HNSW 근사 검색 | 일반 text/image embedding으로 의미 검색을 할 때 |
| Sparse vector | 값이 있는 index와 값의 쌍 | 단어·식별자 등 lexical 일치 | 고정 길이 없음, 이름 필수, 별도 sparse index·exact query | 정확한 용어·코드·이름의 recall이 실제 요구일 때 |
| MultiVector | 같은 차원의 dense vector 여러 개(행렬) | query 부분과 Point 부분의 세밀한 대응 | `max_sim` comparator, vector 수 증가에 따른 비용 측정 필요 | ColBERT 등 late-interaction 모델 출력을 그대로 검색할 때 |
| Named Vector | 이름이 다른 vector field들의 map | 여러 검색 공간을 같은 Point/payload에 연결 | 각 field가 dense·sparse·multivector 및 각기 다른 설정을 가질 수 있음 | 하나의 memory record를 여러 표현으로 함께 검색해야 할 때 |

#### 1.5.6 사례를 바탕으로 확인할 설계 질문

이 단계에서는 아래 질문에 답해 어떤 기능을 켤지 결정하지 않는다. 단지 기능과 문제를 정확히 연결한다.

| 확인할 사실 | 우선 검토할 선택 | 사례·근거 |
| --- | --- | --- |
| 자연어로 의미가 비슷한 과거 기억을 찾는 것이 핵심인가? | Dense vector | Fieldy의 HNSW dense retrieval |
| 사람 이름, ticket ID, 에러 코드처럼 정확한 표현을 자주 놓치면 안 되는가? | Dense + sparse를 비교 평가 | Fieldy의 dense + BM25 결합. 정확한 Qdrant schema는 비공개 |
| 채택한 retrieval 모델의 출력이 query/document sub-vector들의 집합인가? | MultiVector | Qdrant 공식 late-interaction 지원. 현재 조사한 고객 사례에는 사용 공개 없음 |
| 같은 memory record·scope·payload를 semantic/lexical 등 여러 방식으로 한 query에서 검색해야 하는가? | Named Vector + hybrid query를 검토 | Qdrant 공식 FAQ. 결과 결합 방식은 6단계에서 학습 |
| 모델, payload schema, 수명주기, 독립 확장 요구가 서로 다른가? | 별도 Collection을 우선 검토 | Dust의 embedder별 shared Collection 운영 사례 |

### 1.6 거리 함수: embedding 모델의 계약

Qdrant dense vector Collection은 `Dot`, `Cosine`, `Euclid`, `Manhattan` metric을 지원한다. 무엇을 선택할지는 “Cosine이 일반적으로 많이 쓰인다”가 아니라 **embedding 모델이 어떤 metric으로 학습·평가됐는가**에 따라 결정한다.

| metric | 의미 | Qdrant에서 알아둘 점 |
| --- | --- | --- |
| Cosine | 방향이 비슷한 vector를 가깝게 봄 | 업로드 시 vector를 정규화하고 dot product로 계산 |
| Dot | 방향과 크기를 함께 반영 | 모델이 dot-product retrieval을 전제로 할 때 사용 |
| Euclid | 좌표 간 직선 거리가 짧을수록 가까움 | 모델의 retrieval 권장 방식이 L2일 때 사용 |
| Manhattan | 좌표 차이 절댓값의 합 | 지원하지만 text retrieval의 기본값으로 가정하지 않음 |

Dust가 Collection을 embedder별로 조직한 사례는 이 선택과 연결된다. embedding 모델이 바뀌면 차원 또는 metric이 달라질 수 있고, 기존 vector를 그대로 비교하면 안 될 수 있기 때문이다. Qdrant는 Named Vector를 추가해 background re-embedding 후 이전 vector를 제거하는 migration도 지원하지만, 실제 전환 순서와 품질 평가는 애플리케이션이 책임진다.

### 1.7 개념 요약

```text
embedding model
  └─ vector contract(차원·metric)
       └─ Collection 경계
            └─ Point(검색 최소 단위)
                 ├─ vector: 관련성 후보 탐색
                 └─ payload: tenant·source·시간 등 검색 범위 제한
```

이제 뒤의 사례는 이 용어들이 실제 제품에서 어떻게 조합됐는지를 보여 주는 자료다. 사례의 설계는 참고하되, 우리의 subagent memory Point와 scope를 그대로 결정하지는 않는다.

### 1.8 개념의 1차 출처

- Qdrant 공식 문서, [Overview](https://qdrant.tech/documentation/overview/)
- Qdrant 공식 문서, [Points](https://qdrant.tech/documentation/concepts/points/)
- Qdrant 공식 문서, [Vectors](https://qdrant.tech/documentation/manage-data/vectors/)
- Qdrant 공식 문서, [Search](https://qdrant.tech/documentation/concepts/search/)
- Qdrant 공식 문서, [Collections](https://qdrant.tech/documentation/manage-data/collections/)
- Qdrant 공식 문서, [Qdrant Fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/)

---

## 2. 사례 A — Qdrant 공식 멀티테넌시 설계

### 문제

Qdrant는 다수 tenant의 vector를 한 클러스터에서 처리할 때, tenant마다 Collection을 만드는 방식이 Collection 수에 비례하는 자원 오버헤드를 만든다고 설명한다. 공식 문서는 대부분의 경우 **embedding model별 단일 Collection + payload 기반 tenant partitioning**을 출발점으로 제안한다.

### 공개된 설계 방식

```text
shared collection (동일 embedding model)
  ├─ point A: payload.group_id = tenant-1
  ├─ point B: payload.group_id = tenant-1
  └─ point C: payload.group_id = tenant-2

모든 tenant 조회:
  vector query + group_id filter
```

Qdrant는 `group_id` 같은 keyword payload field에 `is_tenant=true` index를 만들 수 있게 한다. 이 설정은 같은 tenant vector가 물리적으로 함께 배치되도록 도와 tenant-filtered query의 순차 읽기 효율을 높이는 목적이다. 반대로 tenant filter가 없는 전역 검색은 더 느려질 수 있다고 명시한다.

tenant 크기가 매우 불균형한 경우에는 작은 tenant를 fallback shard에 함께 두고, 큰 tenant만 custom shard로 승격하는 tiered multitenancy도 제공한다. 이 경우에도 payload 기반 tenant filter는 계속 필요하다.

### 이 사례가 보여주는 점

- Collection 경계와 tenant 경계는 다를 수 있다.
- tenant scope는 검색의 선택 옵션이 아니라 모든 read/write에 함께 다뤄야 하는 데이터 경계다.
- 대형 tenant의 성능·격리 문제는 Collection 폭증 대신 shard 승격으로 다룰 수 있다.

### 이 사례만으로 알 수 없는 점

- `group_id`가 user인지 organization인지, subagent인지 결정해 주지 않는다.
- payload filter는 검색 범위를 줄이는 기능이지 애플리케이션 authorization을 대체하지 않는다.
- tenant index와 custom shard를 첫 배포부터 사용해야 한다는 뜻은 아니다.

### 출처

- Qdrant 공식 문서, [Multitenancy](https://qdrant.tech/documentation/tutorials/multiple-partitions/)
- Qdrant 공식 문서, [Collections](https://qdrant.tech/documentation/manage-data/collections/)

---

## 3. 사례 B — Dust: 데이터 소스별 Collection에서 공유 Collection으로

### 문제

Dust는 AI-native 기업용 에이전트 제품에서 처음에는 **데이터 소스마다 별도 vector Collection**을 만들었다. 데이터 소스가 5,000개를 넘자 Collection 수가 거의 1,000개에 이르고, RAM 사용량과 검색 성능 문제가 커졌다고 공개 사례에서 설명한다.

### 공개된 설계 변화

```text
초기
  data source A → collection A
  data source B → collection B
  data source C → collection C

변경 후
  embedding model A → shared multi-tenant collection
  embedding model B → shared multi-tenant collection
  tenant·data source 구분 → payload filter + sharding
```

Dust는 수천 Collection을 “몇 개의 shared multi-tenant Collection”으로 통합했고, sharding과 payload filtering을 사용했다. 또 `DustQdrantClient`라는 자체 client 계층을 두어 cluster version, embedding model, sharding logic의 차이를 애플리케이션 코드에서 감쌌다. 이후 Collection을 embedding model별로 구성해 model migration과 실험을 다루겠다고 밝혔다.

### 이 사례가 보여주는 점

- Collection을 data source, user, agent처럼 개별 엔티티에 1:1로 매핑하면 규모가 커질 때 운영 비용이 커질 수 있다.
- embedding model은 실제 Collection 분리 기준이 될 수 있다.
- Qdrant 호출을 직접 흩뿌리기보다, tenant filter·model 선택·shard routing을 강제하는 client/service 계층을 둘 수 있다.

### 이 사례만으로 알 수 없는 점

- Dust의 정확한 payload schema, authorization 규칙, shard 승격 기준은 공개되지 않았다.
- “몇 개의 Collection”이라는 선택은 Dust의 데이터 수·모델 수·지역 요구사항에 따른 것이므로 그대로 복제할 수 없다.
- 수치와 비용 절감 주장은 Qdrant가 발행한 고객 사례이므로 독립적으로 검증된 벤치마크는 아니다.

### 출처

- Qdrant 고객 사례, [How Dust Scaled to 5,000+ Data Sources with Qdrant](https://qdrant.tech/blog/case-study-dust-v2/)

---

## 4. 사례 C — Fieldy AI: 원문·검색 인덱스·메타데이터를 같은 저장소로 보지 않음

### 문제

Fieldy AI는 음성을 지속적으로 기록하고 전사해 사용자의 검색 가능한 개인 기억으로 만드는 제품이다. 공개 사례에서 핵심 제약은 “순간에 수집하지 못한 대화는 나중에 복원할 수 없다”는 수집 신뢰성이다.

### 공개된 아키텍처

```text
wearable device
  → mobile app
  → backend
  → speech-to-text
  → transcript + embedding
  → Qdrant

user query
  → retrieval agent
  → Qdrant: HNSW dense + BM25 sparse
  → RRF fusion
  → Firestore: conversation metadata 조회
  → context assembly
```

Fieldy는 Qdrant에 transcript와 embedding을 저장하고, 검색 때는 dense HNSW와 BM25를 Reciprocal Rank Fusion으로 결합한다. 컨텍스트 조립을 위한 conversation metadata는 Firestore에서 가져온다고 설명한다. 이후 개선 계획으로 location·datetime filtering, raw transcript 외 summary embedding을 추가하는 방안도 제시했다.

### 이 사례가 보여주는 점

- vector 검색 계층만으로 전체 memory system을 끝내지 않고, 검색 결과를 보완하는 metadata/원문 계층을 별도로 둘 수 있다.
- 장기 기억의 ingestion pipeline은 “embedding 생성”보다 앞단의 수집 실패, 재시도, 누락 방지가 더 중요할 수 있다.
- 같은 transcript라도 raw segment와 summary처럼 검색 목적이 다른 표현을 병행할 수 있다.

### 이 사례만으로 알 수 없는 점

- Fieldy의 사용자 격리 payload, collection topology, 삭제 정책은 공개되지 않았다.
- Fieldy의 hybrid search를 subagent memory에 바로 적용해야 한다는 근거는 아니다. 이는 정확한 단어와 긴 transcript를 검색하는 제품 특성에서 나온 선택이다.
- 고객 사례의 신뢰성·비용 수치는 Qdrant가 발행한 자료임을 고려해야 한다.

### 출처

- Qdrant 고객 사례, [How Fieldy AI Achieved Reliable AI Memory with Qdrant](https://qdrant.tech/blog/case-study-fieldy/)

---

## 5. 사례 D — Deutsche Telekom LMOS: memory는 vector DB 하나의 문제가 아니라 플랫폼 책임

### 문제

Deutsche Telekom의 AI Competence Center는 10개 유럽 국가에서 agent를 운영하는 PaaS를 만들며, tenancy와 memory management, context sharing, 비결정적인 agent 협업을 주요 과제로 제시했다.

### 공개된 설계 방향

```text
LMOS PaaS
  ├─ agent lifecycle / deployment / monitoring / horizontal scaling
  ├─ tenancy와 compliance
  ├─ context sharing과 state management
  └─ Qdrant: vector retrieval 계층
```

공개 사례에서 Arun Joseph는 이를 단순한 AI 문제가 아니라 distributed systems 문제로 설명하며 feedback loop, state management, lifecycle orchestration, routing이 필요하다고 말했다. LMOS는 agent가 사용할 플랫폼 책임을 한 계층에 두고 Qdrant를 그 안의 vector retrieval 구성요소로 선택했다.

### 이 사례가 보여주는 점

- subagent의 memory 설계에는 vector 검색뿐 아니라 lifecycle, approval, state, routing의 책임 경계가 필요하다.
- tenant 격리와 context 공유는 서로 반대가 아니라, scope와 orchestration을 명확히 해야 동시에 다룰 수 있는 요구다.
- agent에게 Qdrant client를 직접 노출하는 구조보다, 플랫폼/service 계층이 scope와 lifecycle을 관리하는 구조를 검토할 이유가 생긴다.

### 이 사례만으로 알 수 없는 점

- LMOS의 Qdrant Collection·Payload·Shard schema는 이 공개 사례에 나오지 않는다.
- Qdrant가 ownership state나 approval workflow의 원장이라는 뜻은 아니다.

### 출처

- Qdrant 고객 사례, [How Deutsche Telekom Built a Multi-Agent Enterprise Platform Leveraging Qdrant](https://qdrant.tech/blog/case-study-deutsche-telekom/)
- Eclipse Foundation, [LMOS 프로젝트](https://projects.eclipse.org/projects/technology.lmos)

---

## 6. 사례 비교: 실제 선택과 적용 전 확인할 질문

| 사례 | 공개된 실제 선택 | 해결하려던 문제 | 우리 설계 전에 확인할 질문 |
| --- | --- | --- | --- |
| Qdrant 공식 멀티테넌시 | shared Collection + payload partition, 필요 시 tiered shard | 많은 tenant의 Collection 폭증과 성능 | tenant는 user, 조직, app 중 무엇인가? 모든 query에 scope를 강제할 서비스 계층은 있는가? |
| Dust | data source별 Collection을 shared Collection으로 통합, embedder별 구분 | 수천 data source의 RAM·검색 성능 | 메모리와 문서 RAG의 vector contract·수명주기가 같은가? embedding model별 Collection이 필요한가? |
| Fieldy AI | Qdrant hybrid retrieval + Firestore metadata | 누락 없는 개인 기억 수집과 recall | Qdrant 밖에 둬야 할 원문, 감사, 상태는 무엇인가? 정확 용어 검색이 실제 요구인가? |
| Deutsche Telekom LMOS | platform 계층이 lifecycle·tenancy·context sharing 관리 | 대규모 multi-agent 운영 | Qdrant 호출을 감싸는 MemoryService 또는 control plane이 필요한가? |

---

## 7. 이 단계에서 아직 내리지 않는 결론

공개 사례는 방향을 보여 주지만 아래 선택을 대신해 주지는 않는다.

- user별·agent별·project별 중 무엇을 tenant로 볼지
- 하나의 Point가 fact, decision, episode, transcript 중 무엇인지
- 어떤 필드에 payload index를 만들지
- dense 단독 검색과 hybrid 검색 중 무엇이 필요한지
- shared memory를 누가 쓰고, 누가 승격·수정·삭제할지

이 질문은 다음 단계에서 Qdrant index 구조를 학습한 후, 사례의 전제를 우리 요구사항과 비교해 결정한다.

## 8. 용어를 사례에 대입해 다시 정리

| 용어 | 사례에서 보이는 실제 의미 |
| --- | --- |
| Collection | Dust에서는 embedder/data contract 경계, Qdrant 공식 멀티테넌시에서는 다수 tenant가 공유하는 검색 집합 |
| Point | Fieldy에서는 검색 가능한 transcript/embedding 단위이며, Qdrant에서는 vector와 payload를 가진 검색 레코드 |
| Vector | Fieldy의 dense embedding과 BM25 sparse representation처럼 검색 표현을 담당 |
| Payload / scope | Qdrant의 `group_id`처럼 tenant와 데이터 범위를 검색에서 제한하는 metadata |
| 외부 상태 저장소 | Fieldy의 Firestore처럼 vector 검색 외 metadata/context를 제공하거나, LMOS처럼 lifecycle·routing을 담당하는 계층 |

## 다음 단계

2단계에서는 HNSW, Exact Search, Payload index, WAL, Segment를 학습한다. 단순 개념 설명이 아니라, 위 사례 중 Qdrant의 tenant index와 Dust의 quantization·sharding이 어떤 내부 trade-off를 해결하려 했는지 연결해 정리한다.
