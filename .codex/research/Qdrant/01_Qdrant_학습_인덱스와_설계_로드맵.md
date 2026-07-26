Exit code: 0
Wall time: 2.5 seconds
Output:
# Qdrant 학습 인덱스 — 사용자별 Subagent 메모리 설계

> 작성일: 2026-07-24  
> 목표: 사용자별 여러 subagent가 사용하는 장기 메모리를 안전하게 저장·검색하기 위한 Qdrant 데이터 모델과 운영 설계를 이해한다.  
> 학습 원칙: 실습은 설계 결정을 문서로 확정한 뒤, 마지막에 검증 목적으로만 수행한다.

## 최종 산출물

학습이 끝나면 아래 결정을 근거와 함께 설명할 수 있어야 한다.

- Collection을 어떤 책임 경계로 나눌지
- Point 하나가 어떤 메모리 단위를 나타낼지
- `tenant_id`, `user_id`, `agent_id`, `project_id`를 어떻게 분리하고 검색에 강제할지
- 사용자 공통 메모리와 subagent 전용 메모리를 어떻게 저장·승격·회상할지
- Dense·Sparse·Hybrid 검색 중 무엇을 어떤 질의에 사용할지
- Qdrant, PostgreSQL, 원문 저장소의 책임을 어떻게 분리할지
- 삭제·만료·중복·충돌·백업을 어떻게 처리할지

## 모든 학습 노트의 작성 원칙

각 주제 노트는 정의만 나열하거나 가상 사례로 설명하지 않는다. 다음 순서를 기본 구조로 사용한다.

1. 개념의 정확한 정의와 공식 1차 출처
2. 공개된 기업·프레임워크·오픈 소스 구현의 실제 설계 사례
3. 그 사례가 해결하려던 문제와 확인 가능한 기술적 선택
4. 우리 요구에 적용할 때의 조건·한계와 출처 신뢰도
5. 공개 사례만으로는 결정할 수 없어 별도 검증이 필요한 항목

- 사례는 가급적 공식 기술 문서, 공개 소스 코드, 기업의 기술 발표를 우선한다.
- 벤더가 작성한 고객 사례의 성능·비용·안정성 주장은 독립 검증 자료가 아님을 표시한다.
- 가상 사용자·가상 agent 사례는 실제 사례를 대체하지 않는다. 필요하면 개념을 보조하는 최소 예시임을 명시한다.
- 각 외부 사실에는 접근일, URL, 출처 유형을 남긴다.

### 독자 중심 설명 규칙

이 문서는 작성자가 조사 내용을 이해한 방식으로 압축해 두는 메모가 아니라, **학습자가 처음 읽어도 개념의 원인과 동작을 따라갈 수 있는 학습 자료**여야 한다. 이후 모든 단계의 노트는 다음 규칙을 적용한다.

1. 조사 결과를 나열하기 전에, 독자가 먼저 알아야 할 용어·전제·비교 대상을 식별한다.
2. 새 기술 용어는 처음 나올 때 **무엇인지 → 왜 필요한지 → 입력이 어떻게 처리되어 어떤 결과가 되는지** 순서로 설명한다. 정의만 쓰고 다음 용어로 넘어가지 않는다.
3. “A는 B에 유리하다”라는 결론에는 그 특성이 생기는 원인(표현 방식, 계산 방식, 데이터 흐름 또는 제약)을 바로 붙인다. 예: sparse vector의 lexical 특성은 token별 index, 0/non-zero 값, dot product의 공통 index 계산에서 나온다.
4. 개념 설명 뒤에는 작은 보조 예시 또는 흐름도를 둔다. 예시는 원리 이해를 위한 가상 예시임을 표시하고, 실제 설계 근거는 별도의 공개 사례와 출처로 제시한다.
5. 실제 사례는 “무엇을 저장했는가 → 어떻게 조회했는가 → 왜 그 분리가 필요한가 → 최종적으로 무엇이 사용자/시스템에 반환되는가”의 흐름으로 풀어 쓴다. 공개 자료에 없는 필드·내부 동작·성능 원인은 추정하지 않고 **비공개/추론**으로 명확히 구분한다.
6. 기능을 설명할 때는 비슷해 보이는 개념과의 차이, 필요한 경우, 불필요하거나 비용만 늘리는 경우를 함께 적는다.
7. 기존 노트를 보강할 때는 사실 오류를 정정하는 경우가 아니면 기존 설명을 삭제하지 않고, 이해를 돕는 설명을 해당 위치에 추가한다.

#### 작성 전 자체 점검

각 절을 저장하기 전 아래 질문에 독자가 문서만 읽고 답할 수 있는지 확인한다.

- 이 용어·기능은 정확히 무엇인가?
- 왜 존재하며, 어떤 문제를 해결하는가?
- 입력부터 검색 또는 반환 결과까지 내부적으로 어떤 흐름이 일어나는가?
- 비슷한 기능과 무엇이 다른가?
- 언제 사용하고, 언제 사용하지 않는가?
- 실제 공개 사례에서 확인된 사실은 무엇이며, 공개되지 않아 알 수 없는 것은 무엇인가?

### 단계 시작 절차

각 학습 단계를 시작할 때는 새 노트를 작성하거나 조사하기 전에 반드시 이 `01_Qdrant_학습_인덱스와_설계_로드맵.md`를 다시 읽는다. 해당 단계의 학습 목표·설계 질문·작성 원칙을 확인한 뒤에만 외부 조사를 시작하고 다음 번호의 노트를 작성한다.

## 진행 현황

| 순서 | 학습 주제 | 상태 | 학습 후 남길 결정/질문 |
| --- | --- | --- | --- |
| 1 | Vector DB와 Qdrant 데이터 모델 | ✅ | Point와 Collection의 책임은 무엇인가? |
| 2 | 저장·인덱스 구조 | ✅ | 어떤 index와 저장 옵션이 필요한가? |
| 3 | 사용자·subagent 멀티테넌시와 Collection 설계 | ✅ | 공유 Collection, 분리 Collection, Shard 중 무엇을 택할 것인가? |
| 4 | 메모리 Point·Payload 스키마 | ✅ | 필수 필드와 필수 Payload index는 무엇인가? |
| 5 | 검색 원리와 검색 범위 | ✅ | 어떤 scope filter와 recall 정책을 강제할 것인가? |
| 6 | 하이브리드 검색 | ✅ | Dense·Sparse 후보를 어떻게 결합할 것인가? |
| 7 | 메모리 생명주기와 운영 | ✅ | 승격·만료·삭제·감사·백업 정책은 무엇인가? |
| 8 | 최종 설계안 | ✅ | 채택안과 기각안의 근거는 무엇인가? |
| 9 | 간단한 검증 실습 | ✅ | 설계가 격리·검색·삭제 요구를 만족하는가? |

---

## 1. Vector DB와 Qdrant 데이터 모델

### 학습할 내용

- Vector DB가 관계형 DB·키워드 검색 엔진과 다른 점
- Collection
- Point = `id` + vector(s) + payload
- Dense Vector, Sparse Vector, MultiVector, Named Vector
- Cosine, Dot Product, Euclidean 거리와 embedding 모델의 관계
- vector 차원과 distance metric이 Collection 스키마에 미치는 영향

### 설계와 연결할 질문

- 메모리 하나를 Point 하나로 저장할 때, “메모리”의 최소 단위는 사실·대화 turn·문서 chunk 중 무엇인가?
- 텍스트 메모리와 향후 이미지·첨부 메모리가 같은 Point schema를 공유할 수 있는가?
- embedding 모델을 변경할 때 기존 Point를 어떻게 마이그레이션할 것인가?

### 1차 출처

- [Qdrant Overview](https://qdrant.tech/documentation/overview/)
- [Qdrant Points](https://qdrant.tech/documentation/concepts/points/)

---

## 2. Qdrant의 저장·인덱스 구조

### 학습할 내용

- Segment와 optimizer
- HNSW 기반 근사 최근접 이웃 검색과 Exact Search
- Payload filtering과 Payload index
- WAL과 쓰기 내구성
- RAM·disk 저장 옵션, Quantization
- Collection 생성 시 정하는 설정과 이후 변경 가능한 설정

### 설계와 연결할 질문

- `user_id`, `agent_id`, `project_id`, `memory_scope`, `status` 중 어떤 필드에 Payload index가 필요한가?
- 검색 속도·회상 품질·비용의 균형을 어떤 지표로 판단할 것인가?
- Qdrant는 검색 인덱스일 뿐이라는 전제에서, 원장·감사 상태는 어디에 둘 것인가?

### 1차 출처

- [Qdrant Collections](https://qdrant.tech/documentation/manage-data/collections/)
- [Qdrant Payload](https://qdrant.tech/documentation/concepts/payload/)

---

## 3. 사용자·subagent 멀티테넌시와 Collection 설계

### 비교할 대안

| 대안 | 설명 | 검토할 장점 | 검토할 위험 |
| --- | --- | --- | --- |
| 사용자별 Collection | 사용자마다 별도 Collection을 생성 | 논리적으로 직관적인 분리 | Collection 수 증가에 따른 자원·운영 부담 |
| 공유 Collection + Payload 분리 | 하나의 memory Collection에 tenant/user/agent scope를 payload로 저장 | 다수 사용자에 대한 기본 권장 구조 | 서버가 모든 조회에 scope filter를 강제해야 함 |
| 계층형 멀티테넌시 | 작은 tenant는 공유 Shard, 큰 tenant는 전용 Shard로 승격 | 대형 tenant의 성능·격리 확보 | Shard routing·승격 운영 복잡도 |

### 학습할 내용

- `tenant_id`, `user_id`, `agent_id`, `project_id`, `run_id`의 의미와 경계
- Payload 기반 멀티테넌시
- `is_tenant=true` tenant index의 목적과 제약
- Custom Sharding, Shard Key Selector, fallback shard
- user/subagent별 Collection 생성이 필요한 예외 조건
- API 인증·인가와 Qdrant filter의 책임 분리

### 설계와 연결할 질문

- 같은 사용자 안에서 subagent는 어떤 기억을 공유하고, 어떤 기억을 전용으로 유지해야 하는가?
- 공통 메모리로 승격할 주체와 승인 조건은 무엇인가?
- tenant 격리를 Qdrant filter만으로 보장하지 않으려면 서비스 계층에 어떤 검증이 필요한가?

### 1차 출처

- [Qdrant Multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/)
- [Qdrant Fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/)
- [Qdrant Security](https://qdrant.tech/documentation/operations/security/)

---

## 4. 메모리 Point·Payload 스키마

### 초안 필드

```text
id
tenant_id
user_id
agent_id
project_id
memory_scope        # user_shared | agent_private | project_shared
memory_kind         # preference | fact | decision | procedure | episode
content
status              # candidate | active | superseded | expired | deleted
importance
confidence
created_at
updated_at
expires_at
source_evidence_id
embedding_model
schema_version
```

### 학습할 내용

- Payload의 역할과 JSON schema 설계
- 필터 가능한 필드와 검색용 필드의 구분
- source evidence를 payload에 복사하지 않고 참조로 보관하는 이유
- immutable event, current state, superseded 상태의 모델링
- Point ID와 idempotency key의 역할

### 설계와 연결할 질문

- Qdrant Point와 PostgreSQL의 현재 상태를 어떻게 연결할 것인가?
- 메모리 후보와 확정된 메모리를 같은 Collection에 둘 것인가?
- 삭제 요청이 들어오면 원문·vector·감사 기록을 각각 어떻게 처리할 것인가?

---

## 5. 검색 원리와 검색 범위

### 학습할 내용

- 벡터 유사도 검색, Top-K, score threshold
- HNSW 검색 파라미터와 Exact Search의 사용 시점
- Payload filter와 필터 인덱스
- scope별 recall 우선순위: 조직/사용자/프로젝트/subagent/런타임
- 검색 결과 부족·과다·충돌 시 처리

### 검색 정책 초안

```text
1. 인증된 호출자에서 tenant_id를 서버가 결정한다.
2. tenant_id는 모든 Qdrant 조회에 필수 조건으로 넣는다.
3. user_id와 현재 project_id를 기본 범위로 넣는다.
4. memory_scope는 user_shared, project_shared, 현재 agent_private만 허용한다.
5. status=active와 만료되지 않은 memory만 후보로 삼는다.
6. 유사도 검색 결과를 provenance·importance·최신성 기준으로 추가 정리한다.
```

### 설계와 연결할 질문

- scope filter를 누락한 호출을 API 계층에서 어떻게 차단할 것인가?
- 현재 subagent의 private memory와 shared memory를 어떤 점수·우선순위로 결합할 것인가?
- 낮은 score의 메모리를 LLM에 넣지 않는 기준은 무엇인가?

---

## 6. 하이브리드 검색

### 학습할 내용

- Dense 검색과 Sparse 검색의 강점·한계
- Named Vector와 여러 검색 공간
- `prefetch`를 이용한 다단계 질의
- RRF와 DBSF
- Formula Query와 payload 기반 score 보정
- reranker의 위치와 비용

### 설계와 연결할 질문

- 코드 식별자·오류 코드·고유명사처럼 정확한 용어가 중요한 메모리는 Sparse 검색이 필요한가?
- Dense와 Sparse의 후보 수를 어떻게 정할 것인가?
- Qdrant Native fusion 뒤 reranker를 둘 가치가 있는가?

### 1차 출처

- [Qdrant Hybrid Queries](https://qdrant.tech/documentation/search/hybrid-queries/)
- [Qdrant Hybrid Search](https://qdrant.tech/documentation/search/text-search/hybrid-search/)

---

## 7. 메모리 생명주기와 운영 설계

### 학습할 내용

- L0 Runtime, L1 Working, L2 Project, L3 User/Organization 메모리 계층
- candidate → active → superseded/expired/deleted 상태 전이
- subagent private memory의 shared memory 승격
- TTL, retention, 삭제, 중복 제거, 충돌 해소
- Snapshot·backup·복구
- Shard, replica, consistency, 장애 시 fallback

### 설계와 연결할 질문

- subagent의 중간 산출물은 기본적으로 저장해야 하는가, 아니면 평가·승격 후에만 저장해야 하는가?
- 메모리 추출·Qdrant 쓰기·상태 DB 갱신의 부분 성공을 어떻게 복구할 것인가?
- Qdrant 장애 중에도 대화·작업을 계속할 수 있는가?

### 1차 출처

- [Qdrant Snapshots](https://qdrant.tech/documentation/snapshots/)
- [Qdrant Distributed Deployment](https://qdrant.tech/documentation/scaling/distributed_deployment/)

---

## 8. 최종 설계안

이 장에서는 아래 표를 채워 채택안을 확정한다.

| 설계 항목 | 채택안 | 근거 | 기각한 대안 |
| --- | --- | --- | --- |
| Collection topology | ⬜ | ⬜ | ⬜ |
| tenant/user/agent 격리 | ⬜ | ⬜ | ⬜ |
| Payload schema | ⬜ | ⬜ | ⬜ |
| Payload indexes | ⬜ | ⬜ | ⬜ |
| Vector schema | ⬜ | ⬜ | ⬜ |
| Retrieval strategy | ⬜ | ⬜ | ⬜ |
| Hybrid search | ⬜ | ⬜ | ⬜ |
| Lifecycle/retention | ⬜ | ⬜ | ⬜ |
| Source of truth | ⬜ | ⬜ | ⬜ |
| Backup/failure policy | ⬜ | ⬜ | ⬜ |

---

## 9. 마지막 검증 실습

설계 확정 전에는 시작하지 않는다. 실습은 다음을 증명하기 위한 최소 범위로 제한한다.

- 선택한 Collection과 Payload index 생성
- 한 사용자와 여러 subagent의 shared/private memory 저장
- 허용된 scope만 검색되는지 확인
- 다른 사용자의 memory가 반환되지 않는지 확인
- Dense 검색과 Hybrid 검색 결과 비교
- 만료·supersede·삭제 뒤 검색 결과 확인
- Snapshot 또는 복구 경로 확인

---

## 기존 노트와의 연결

- [Mem0 기반 에이전트 메모리 아키텍처](../AI/mem0/text/01_Mem0_기반_에이전트_메모리_아키텍처.md): Qdrant·PostgreSQL·원문 저장소의 책임 분리와 memory tier 참고
- [Qdrant 저장소와 Entity Link 구현](../AI/mem0/text/code_analize/05_Qdrant_저장소와_Entity_Link.md): Mem0 adapter가 Qdrant를 사용하는 방식과 Native Qdrant 기능의 차이 참고

## 출처 기록 규칙

- 최신 기능, API, 제한 사항은 Qdrant 공식 문서를 우선한다.
- 이 문서에서 외부 정보는 문서 접근일(2026-07-24)과 출처를 함께 기록한다.
- 벤치마크·성능 수치는 데이터셋, Qdrant 버전, collection 설정, embedding 모델, filter 조건을 함께 적는다.
