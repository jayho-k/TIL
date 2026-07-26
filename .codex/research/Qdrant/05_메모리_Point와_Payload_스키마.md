# 메모리 Point와 Payload 스키마 — 무엇을 검색 레코드에 넣고, 무엇을 원장에 남길 것인가

> 학습 단계: 4 / 9  
> 조사 기준일: 2026-07-24  
> 목표: subagent memory 하나를 Qdrant Point로 만들 때, vector·payload·별도 상태 저장소가 각각 어떤 역할을 맡아야 하는지 이해한다.

## 먼저 결론: Point는 “기억 전체의 원장”이 아니라 검색용 투영본이다

Qdrant Point는 `id`, vector, 선택적 payload로 이루어진 검색 레코드다. memory system에서 Point는 보통 원문 이벤트 전체가 아니라, **현재 query와 관련 있는지 판단하고, 허용된 범위인지 제한하고, 원문 근거로 다시 연결하기 위한 검색용 표현**이다.

```text
원문 이벤트·감사 기록·권한 변경
  └─ 별도 원장/상태 저장소가 책임질 가능성이 큼

추출된 memory Point
  ├─ vector: 이 memory가 질문과 의미상 가까운가?
  ├─ payload: 이 memory를 지금 검색해도 되는가? 어떤 종류·상태·시간인가?
  └─ id: 원문 근거와 현재 상태를 연결하는 안정적인 키
```

이 분리가 필요한 이유는 검색 DB와 원장이 해결하는 문제가 다르기 때문이다.

- Qdrant는 “관련 후보를 빠르게 찾기”에 강하다.
- 원장 DB는 승인·삭제 요청·감사·관계 무결성·동시 상태 변경처럼 정확한 상태 관리에 더 적합하다.

Qdrant payload는 JSON을 저장할 수 있으므로 많은 정보를 넣을 수 있다. 하지만 **넣을 수 있음**과 **원본을 Qdrant 하나에만 둬도 됨**은 다르다. 검색에 필요한 작은 metadata와 반환할 text는 payload에 둘 수 있지만, 변경 이력·대용량 원문·민감한 증거·관계형 권한 모델까지 전부 payload에 복제하면 동기화와 삭제·감사 책임이 불명확해진다.

---

## 1. Point의 세 부분은 각각 어떤 질문에 답하는가?

| 구성요소 | 답하는 질문 | memory에서의 역할 | 혼동하기 쉬운 점 |
| --- | --- | --- | --- |
| `id` | “이것은 어느 레코드인가?” | Qdrant Point와 memory 원장·증거를 연결 | `id` 자체가 권한·scope를 대신하지 않음 |
| vector | “질문과 얼마나 관련 있는가?” | semantic/sparse 등 유사도 후보 탐색 | vector 안에는 tenant·상태 같은 권한 정책을 넣지 않음 |
| payload | “검색 후보가 되어도 되는가? 반환 후 어떻게 해석할까?” | scope filter, 상태 filter, 시간 조건, content/근거 참조 | 모든 field를 index하면 비용 없이 빨라지는 것이 아님 |

### 1.1 `id` — 재시도와 연결을 위한 안정적인 식별자

Qdrant Point ID는 64-bit unsigned integer 또는 UUID다. 같은 ID로 다시 upsert하면 기존 Point를 덮어쓴다. Qdrant는 동일 요청을 여러 번 실행해도 결과가 한 번 실행한 것과 같도록 point loading을 idempotent하게 제공한다.

**idempotent(멱등)**란 재시도 때문에 같은 요청이 두 번 도착해도 최종 상태가 중복 생성되지 않는 성질이다. 예를 들어 ingestion worker가 네트워크 오류 뒤 같은 memory를 다시 전송했을 때, 새 Point가 두 개 생기는 대신 같은 Point ID의 레코드가 갱신되는 방식이다.

```text
원장 memory_id = 018f... (UUID)
    │
    ├─ Qdrant point id = 018f...   # 같은 식별자를 쓰거나 안정적으로 매핑
    └─ evidence/source record와도 연결

재시도
    └─ 같은 id로 upsert → 중복 Point를 추가하지 않음
```

다만 Qdrant의 upsert는 기본적으로 Point 전체를 삽입 또는 갱신한다. Named Vector를 쓰는 경우 일부 vector만 담아 재-upsert하면 지정하지 않은 vector가 사라질 수 있으므로, 부분 vector 변경에는 전용 update API를 써야 한다. 또한 Qdrant가 반환하는 Point version과 애플리케이션의 `schema_version`, memory의 업무 상태 버전은 같은 개념이 아니다. 우리 시스템의 optimistic concurrency나 상태 전이는 별도 version field/원장 규칙으로 설계해야 한다.

### 1.2 Vector — “무엇을 기억하는가”가 아니라 “무엇과 비슷한가”

vector는 memory의 원문 또는 추출된 사실 문장을 embedding 모델에 넣어 만든 검색 표현이다. 예를 들어 “승인 금액이 5만 달러를 넘으면 재무 검토가 필요하다”라는 memory를 vector로 바꾸면, 나중에 “큰 지출의 승인 절차” 같은 표현으로도 후보를 찾을 수 있다.

이때 vector가 담당하는 일은 관련성 후보 탐색이다. `tenant_id`, `status`, `expires_at` 같은 field를 vector의 의미에 기대어 처리하면 안 된다. “현재 active인 동일 tenant memory만 허용”은 payload filter와 서비스 정책의 일이다.

### 1.3 Payload — filter·반환 context·추적을 위한 JSON

Qdrant payload는 JSON object다. string, number, bool, datetime, UUID, array, 중첩 object 등을 저장할 수 있다. filter에서 실제로 비교할 field에는 해당 타입의 payload index를 만들 수 있다. 예를 들어 UUID 형식 ID는 `uuid` index, 범위 조건을 줄 시간은 `datetime` index, 정확 일치를 볼 scope 값은 `keyword` index가 대응한다.

```text
payload에는 서로 목적이 다른 field가 섞일 수 있다.

검색 범위용: tenant_id, user_id, project_id, agent_id, memory_scope, status
시간 조건용: created_at, expires_at
결과 해석용: memory_kind, importance, confidence, content
근거 추적용: source_evidence_id, source_type, schema_version
```

하지만 payload index는 모든 JSON field에 자동으로 생기지 않는다. index를 만들면 filtering은 빨라질 수 있지만 indexed field 값은 storage 방식과 관계없이 RAM에 보존된다. 그러므로 “항상 filter하는 작은 field”와 “가끔 화면에 보여 주기만 하는 큰 text”를 구분해야 한다.

---

## 2. memory 하나가 Point가 되는 흐름

아래는 개념을 설명하는 후보 흐름이다. 실제 extractor, 승인 규칙, DB 종류는 아직 확정하지 않는다.

```text
1. 원문 이벤트 발생
   - 대화 turn, tool 실행 결과, 사람의 수정, 문서 변경 등

2. 원문/증거를 원장에 기록
   - evidence_id, 작성 시각, 작성 주체, 원문 위치 등

3. memory 후보 추출
   - “재사용할 가치가 있는 fact/decision/procedure인가?”

4. memory Point 생성
   - stable memory_id 부여
   - 검색용 text를 embedding하여 vector 생성
   - scope·status·근거 reference를 payload에 설정

5. Qdrant upsert
   - vector + payload를 검색용 Point로 저장

6. 이후 query
   - payload filter로 허용 범위를 제한
   - vector로 관련 후보를 찾음
   - source_evidence_id로 원문/감사 정보가 필요한 경우 연결
```

핵심은 4단계의 `content`와 2단계의 원문이 반드시 같지 않을 수 있다는 점이다. 원문 대화가 길더라도 Point에는 검색에 적합한 짧은 사실·결정·chunk를 둘 수 있다. 반대로 “이 Point가 왜 만들어졌는가?”를 검증하려면 `source_evidence_id`로 원문 기록을 다시 찾아야 한다.

---

## 3. 후보 Payload schema를 필드별로 읽기

아래 schema는 01에서 제시한 초안 필드를 설명하기 위한 **후보**다. Qdrant 공식 schema나 공개 기업의 실제 memory schema가 아니다.

```json
{
  "tenant_id": "...",
  "user_id": "...",
  "project_id": "...",
  "agent_id": "...",
  "memory_scope": "agent_private | project_shared | user_shared",
  "memory_kind": "preference | fact | decision | procedure | episode",
  "status": "candidate | active | superseded | expired | deleted",
  "content": "검색 결과에 반환할 정규화된 memory text",
  "importance": 0.0,
  "confidence": 0.0,
  "created_at": "RFC 3339 datetime",
  "updated_at": "RFC 3339 datetime",
  "expires_at": "RFC 3339 datetime 또는 null",
  "source_evidence_id": "원문/증거 원장의 UUID",
  "embedding_model": "생성에 사용한 모델 식별자",
  "schema_version": 1
}
```

### 3.1 범위 field: 누가 읽을 수 있는지 제한한다

`tenant_id`, `user_id`, `project_id`, `agent_id`, `memory_scope`는 검색 결과를 보기 좋게 분류하려고만 존재하지 않는다. 04에서 본 것처럼 payload filter의 입력이 되어, 현재 요청에서 허용되지 않은 Point가 vector 후보가 되지 않게 한다.

| field | 왜 필요한가 | 보통 filter에 쓰는가? | 주의점 |
| --- | --- | --- | --- |
| `tenant_id` | 다른 고객/조직 data의 절대 분리 | 예. 모든 read/write 경로에서 | 실제 tenant가 조직인지 개인인지 인증 모델로 결정 |
| `user_id` | tenant 안 개인 기억 분리 | 제품 정책에 따라 예 | 조직 공유 memory가 있는 경우 무조건 must로 고정하면 안 될 수 있음 |
| `project_id` | 특정 업무 맥락에만 유효한 memory 제한 | project 작업 query에서 예 | project 밖에도 재사용 가능한지 `memory_scope`와 함께 판단 |
| `agent_id` | private memory의 작성/소유 agent 식별 | private scope query에서 예 | 작성 agent와 현재 읽기 권한을 같은 뜻으로 만들지 않음 |
| `memory_scope` | user/project/agent 중 허용된 회상 범위 표현 | 예 | scope 값만 보고 tenant filter를 생략하면 안 됨 |

### 3.2 종류와 상태: “무엇인가”와 “지금 써도 되는가”는 다르다

`memory_kind`는 memory가 어떤 역할을 하는지 나타낸다. 예를 들어 preference는 사용자의 지속적 선호, decision은 특정 업무에서 내린 선택, procedure는 반복 작업 방법, episode는 한 번의 사건 요약이다.

`status`는 지금 검색 결과로 사용해도 되는지를 나타낸다. candidate는 아직 검토되지 않은 추출물, active는 사용할 수 있는 현재 memory, superseded는 더 새 memory로 대체된 과거 내용, expired는 시간 제한이 끝난 내용, deleted는 더 이상 반환하지 않아야 하는 상태를 뜻하는 후보 상태다.

```text
“A 팀장이 담당자다”
  ├─ memory_kind: fact
  └─ status: active

담당자가 바뀌면
  ├─ 기존 Point: status = superseded
  └─ 새 Point:  status = active
```

이렇게 두 field를 나누는 이유는 같은 `fact`도 현재 참인지, 검토 중인지, 과거 기록으로만 남겨야 하는지가 다르기 때문이다. 단, Qdrant payload update만으로 상태 전이의 감사 기록이 자동으로 남는 것은 아니다. 승인자·변경 이유·이전 값이 중요하다면 원장에 immutable event를 남기고 Qdrant에는 현재 검색 가능한 projection을 동기화하는 방식을 검토해야 한다.

### 3.3 시간·신뢰도·중요도: 점수의 재료이지 자동 진실 판정기는 아니다

`created_at`, `updated_at`, `expires_at`은 시간 범위 filter와 최신성 판단에 사용한다. Qdrant는 RFC 3339 datetime payload와 range filtering을 지원한다. `expires_at`이 지난 Point를 제외하려면 query에 시간 조건을 넣거나, lifecycle worker가 status를 갱신해야 한다. 값만 저장하고 filter를 넣지 않으면 만료 memory도 검색될 수 있다.

`confidence`와 `importance`는 서로 다른 값이다.

- `confidence`: 이 memory가 원문 근거로 뒷받침된 정도 또는 extractor의 확신
- `importance`: 맞더라도 앞으로 자주 재사용할 가능성·영향도

예를 들어 “이번 회의는 오후 3시”는 원문이 명확해 confidence는 높아도 장기 기억으로서 importance는 낮고, “고액 승인에는 재무 검토가 필요하다”는 중요도는 높을 수 있다. 이 값들은 LLM이 숫자를 만들었다는 이유만으로 사실이 되지 않는다. 산출 방법, 검토, 점수 사용 방식은 07단계 lifecycle에서 결정한다.

### 3.4 `content`와 `source_evidence_id`: 검색용 문장과 검증 근거를 분리한다

`content`는 Qdrant가 검색으로 반환했을 때 retrieval agent 또는 LLM에 전달할 수 있는 정규화된 memory text다. vector를 만들 때 사용한 text와 같거나, 검색 품질을 위해 정리된 짧은 문장일 수 있다.

`source_evidence_id`는 그 memory의 근거가 되는 원문 이벤트·문서·사람의 수정 기록을 가리키는 reference다. 원문 전체를 Point마다 복사하지 않고 reference를 두는 이유는 다음과 같다.

```text
원문 대화 하나에서 memory 여러 개가 추출될 수 있음
  → 원문을 각 Point에 반복 저장하면 수정·삭제·권한 변경 때 모두 갱신해야 함

source_evidence_id 하나를 참조
  → 검색 결과는 작은 content로 빠르게 사용
  → 필요할 때만 원문·앞뒤 문맥·감사 정보를 원장에서 조회
```

Fieldy 공개 사례는 이 분리의 실제 제품 예시다. Fieldy는 transcript와 embedding을 Qdrant에 저장하고, 검색 후 conversation metadata를 Firestore에서 가져와 context를 조립한다고 공개했다. Firestore metadata의 정확한 field는 공개되지 않았으므로, 이를 특정 schema의 근거로 사용하면 안 된다. 다만 vector 검색 결과만으로는 대화의 전체 맥락·관계를 모두 처리하지 않고, 별도 metadata 계층을 결합했다는 사실은 확인된다.

### 3.5 `embedding_model`과 `schema_version`: 나중에 재처리할 수 있게 남긴다

embedding model이 바뀌면 같은 문장을 서로 비교해도 품질이 달라지거나 차원·metric이 달라질 수 있다. `embedding_model`을 Point에 기록하면 어떤 Point가 어떤 model output인지 추적하고 재-embedding 대상을 선택할 수 있다.

`schema_version`은 payload field의 의미나 content 생성 규칙이 바뀌었을 때 어느 규칙으로 만들어진 Point인지 알려 주는 애플리케이션 field다. Qdrant 내부 Point version과는 다르다. 예를 들어 `memory_scope` 값의 규칙을 변경했다면, `schema_version`으로 이전 Point를 찾아 migration/review 대상으로 만들 수 있다.

---

## 4. 어떤 field에 payload index를 만들 것인가?

payload index는 “payload에 있는 모든 field를 빠르게 만드는 스위치”가 아니다. query에서 자주 filter·range 조건으로 사용하는 field를 위한 별도 자료구조다. index를 늘리면 write와 RAM 비용도 늘어난다.

| field 후보 | query에서의 역할 | index 검토 이유 | 지금 확정하지 않는 이유 |
| --- | --- | --- | --- |
| `tenant_id` | 모든 query의 격리 조건 | 항상 비교하는 핵심 scope | tenant 정의·`is_tenant` 적용 여부는 08단계 결정 |
| `user_id`, `project_id`, `agent_id`, `memory_scope`, `status` | 허용 scope와 active 상태 제한 | 반복적으로 exact match할 가능성 | 실제 query 빈도와 조합을 먼저 측정해야 함 |
| `expires_at`, `created_at` | 만료 제외·기간 제한 | datetime range 조건 가능 | 만료를 filter로 처리할지 worker로 상태 갱신할지 미결정 |
| `memory_kind` | 특정 종류만 회상 | 화면/agent policy에서 category filter가 필요할 수 있음 | 모든 query에 필요한지 알 수 없음 |
| `content` | 결과 반환·LLM context | 일반적으로 vector가 주 검색 수단 | full-text filter까지 필요한지는 hybrid 검색 단계에서 판단 |
| `source_evidence_id` | 원문 추적 | point에서 evidence로 직접 조회할 수 있음 | 대량 역조회·감사가 실제로 필요한지 확인 필요 |
| `importance`, `confidence` | 후처리·보정 | range/formula에 쓸 수 있음 | 숫자 산출의 신뢰성과 score policy가 먼저 필요 |

Qdrant 공식 문서는 UUID 값이 많은 payload-heavy Collection에서 `uuid` index가 RAM 사용과 검색 성능에 유리할 수 있다고 설명한다. 그러나 어떤 ID든 일단 index해야 한다는 뜻은 아니다. field가 filter·lookup에 쓰이지 않는다면 payload에만 저장하고 index하지 않는 선택도 필요하다.

---

## 5. 공개 구현과 사례에서 확인되는 구조

### 사례 A — Qdrant Point API: 안정적 ID와 재시도를 전제로 한 upsert

Qdrant 공식 Points 문서는 Point ID로 integer 또는 UUID를 지원하며, 동일 ID의 재-upsert가 Point를 덮어쓰는 idempotent API임을 명시한다. 메시지 큐가 exactly-once 전달을 보장하지 않아도 같은 ID로 재시도하면 중복 Point를 줄일 수 있다는 것이 공식 설명이다.

이 사례가 보여 주는 것은 “Qdrant Point ID는 단순 자동 번호가 아니라 ingestion retry와 외부 원장 연결에 쓸 수 있는 안정 키”라는 점이다. 다만 Qdrant의 idempotence가 원장 DB와 Qdrant 사이의 분산 transaction을 만들어 주지는 않는다. 한쪽만 성공했을 때의 보상·재처리는 07단계에서 설계해야 한다.

**출처 유형:** Qdrant 공식 문서, 접근일 2026-07-24.  
**출처:** [Points](https://qdrant.tech/documentation/concepts/points/)

### 사례 B — LlamaIndex + Qdrant: 원문 node와 metadata를 payload로 보관하고 filter에 사용

Qdrant의 LlamaIndex 통합 예제는 문서를 node로 나누고 embedding과 함께 Qdrant에 저장한다. 각 node에는 `metadata.library`처럼 출처를 나타내는 metadata가 있으며, retriever는 이 metadata exact-match filter를 붙여 허용된 library의 node만 반환한다.

이 구조에서 payload metadata는 설명용 꼬리표가 아니라 candidate set을 제한하는 입력이다. 반면 예제의 `library` field가 tenant와 동일한 보안 경계라는 뜻은 아니다. 교육용 문서 범위 제어를 보여 주는 공개 예제이며, subagent memory의 tenant/user/agent scope 규칙은 별도 설계가 필요하다.

**출처 유형:** Qdrant 공식 통합 예제, 접근일 2026-07-24.  
**출처:** [Multitenancy with LlamaIndex](https://qdrant.tech/documentation/examples/llama-index-multitenancy/)

### 사례 C — Fieldy: Qdrant 검색 레코드와 Firestore conversation metadata를 결합

Fieldy는 audio를 transcript로 만들고 transcript와 embedding을 Qdrant에 저장한다고 밝혔다. 사용자 query 후 retrieval agent가 Qdrant hybrid search를 수행하고, conversation metadata를 Firestore에서 가져와 context를 조립한 뒤 결과를 반환한다.

이 구조는 “검색 결과를 반환할 수 있는 text”와 “대화 전체 맥락을 복원하는 metadata”를 같은 저장소에 반드시 모두 넣지 않아도 된다는 사례다. Fieldy의 Firestore field, Qdrant payload schema, 원문 보존 정책은 공개되지 않았으므로 이 노트의 후보 schema에 직접 대입하지 않는다.

**출처 유형:** Qdrant 고객 사례(벤더 발행), 접근일 2026-07-24.  
**출처:** [How Fieldy AI Achieved Reliable AI Memory with Qdrant](https://qdrant.tech/blog/case-study-fieldy/)

---

## 6. 이 단계에서 남기는 설계 원칙과 미결정 사항

### 후보 원칙

1. Point 하나는 재검색 가능한 memory 단위이며, 원문 이벤트 전체와 1:1일 필요는 없다.
2. tenant·scope·status는 vector의 의미가 아니라 payload filter와 service policy로 강제한다.
3. Point ID는 재시도와 evidence/original state 연결을 고려해 안정적으로 부여한다.
4. `content`는 검색 후 사용할 짧은 context이고, 원문 증거·감사·변경 이력은 reference와 원장으로 분리하는 방향을 우선 검토한다.
5. index는 “저장하는 모든 field”가 아니라 “실제 query에서 반복적으로 조건에 쓰는 field”에만 검토한다.

### 아직 확정하지 않는 것

- fact·decision·episode·transcript 중 Point의 최소 단위를 어떻게 다르게 둘지
- candidate와 active를 한 Collection에 함께 둘지, 별도 Collection으로 둘지
- `content`에 어느 길이까지 저장하고 원문을 어디에 보존할지
- `confidence`, `importance`를 누가 어떤 기준으로 산출·수정할지
- source evidence의 삭제 요청과 Point deletion을 어떤 순서로 처리할지
- 실제 payload index 목록과 `is_tenant=true` 적용 field

## 다음 단계

06번 파일에서는 vector 검색이 어떤 Point를 후보로 만들고, Top-K·score threshold·HNSW/exact search·payload filter가 최종 회상 범위를 어떻게 바꾸는지 다룬다. 05의 scope/status/시간 field가 실제 query에 어떤 조건으로 들어가는지도 그 단계에서 연결한다.
