# 사용자와 Subagent 멀티테넌시·Collection 설계 — 범위가 검색 결과를 결정하는 방식

> 학습 단계: 3 / 9  
> 조사 기준일: 2026-07-24  
> 목표: 여러 사용자와 여러 subagent가 하나의 Qdrant 배포 환경을 공유할 때, **어떤 기억을 어느 검색에 포함할 수 있는지**를 Collection·Payload·Shard·서비스 계층의 책임으로 나누어 이해한다.

## 이 노트에서 먼저 구분할 것

**멀티테넌시(multitenancy)**는 하나의 시스템을 여러 고객·조직·사용자가 함께 쓰되, 서로의 데이터가 섞여 보이지 않게 만드는 방식이다. 여기서 tenant는 “누구의 데이터인가”를 가르는 가장 바깥 경계다. Qdrant가 tenant를 하나의 고정된 타입으로 정의하지는 않는다. 제품에 따라 tenant는 회사, 조직, 사용자, 또는 계약 단위가 될 수 있다.

subagent memory에서는 “누구의 데이터인가”와 “현재 agent가 읽어도 되는가”가 별개의 질문이다.

```text
누구 소유인가?                     지금 이 작업이 읽어도 되는가?
tenant / organization              memory_scope / agent / project / run
        │                                       │
        └────────────── 둘 다 만족해야 반환 가능 ─┘
```

예를 들어 같은 사용자에게 속한 기억이라도, 한 subagent의 실험 중간 기록을 다른 subagent가 바로 읽어도 되는지는 별도의 공유 정책 문제다. 반대로 특정 subagent가 읽을 수 있다고 해도 다른 tenant의 데이터라면 절대 후보가 되면 안 된다.

이 노트는 다음 두 가지를 분리한다.

- **데이터 격리 경계:** tenant 간에 절대 넘으면 안 되는 경계. 모든 read/write에서 강제해야 한다.
- **업무상 회상 범위:** 같은 tenant 안에서 user, project, agent, run에 따라 달라지는 허용 범위. 어떤 memory를 공유·승격할지의 제품 정책이다.

Qdrant의 payload filter는 두 경계를 검색 후보에서 제외하는 데 사용한다. 하지만 filter에 어떤 값을 넣을지는 호출자가 아니라 서버의 인증·인가 및 memory service가 결정해야 한다. filter는 “이 조건의 Point만 찾기” 기능이지, 클라이언트가 임의의 `tenant_id`를 요청하지 못하게 하는 사용자 인증 기능 그 자체는 아니다.

---

## 1. 용어부터: tenant, user, project, agent, run은 왜 한 필드로 합치면 안 되는가?

아래 이름들은 Qdrant의 예약 필드가 아니라, 이 학습 목표의 subagent memory에 필요한 **후보 scope**다. 실제 이름과 계층은 제품의 인증 모델에 맞춰 확정해야 한다.

| 범위 | 답하는 질문 | 보통 언제 바뀌는가 | memory와의 관계 |
| --- | --- | --- | --- |
| `tenant_id` | 어느 조직/고객의 데이터인가? | 가입 조직 또는 계약 경계 변경 시 | 다른 tenant와의 절대 격리 기준 |
| `user_id` | tenant 안에서 누구의 개인 기억인가? | 사용자 계정 단위 | 개인 preference·개인 대화의 소유자 |
| `project_id` | 어떤 업무/프로젝트 맥락인가? | 프로젝트 생성·종료 시 | 프로젝트에서만 재사용할 decision·자료 범위 |
| `agent_id` | 어느 subagent가 만들고 관리하는가? | agent 역할 정의 시 | private memory의 작성자·소유 역할 |
| `run_id` | 어느 실행 한 번에서 나온 임시 결과인가? | 요청 또는 작업 실행마다 | 실패·재시도·검토 전 중간 산출물 추적 |
| `memory_scope` | 현재 누가 읽어도 되는가? | 승인·승격·만료 시 | `agent_private`, `project_shared`, `user_shared` 같은 회상 허용 규칙 |

여기서 특히 `agent_id`와 `memory_scope`를 같은 의미로 두면 문제가 생긴다.

```text
agent_id = "research-agent"
  → 누가 만들었는지 또는 기본 관리 주체

memory_scope = "project_shared"
  → 지금은 같은 프로젝트의 다른 agent도 읽어도 되는지
```

즉 하나의 memory는 research-agent가 만들었지만, 검토 후 project_shared로 승격될 수 있다. 작성자 정보는 바뀌지 않아도 회상 허용 범위는 바뀐다. 이 차이가 필요한 이유는 subagent가 만든 모든 중간 결과를 자동으로 전역 공유하면, 검증되지 않은 추론·오류·민감한 작업 맥락이 다른 agent의 검색 결과에 섞일 수 있기 때문이다.

### 보조 흐름 예시 — 검색할 수 있는 범위는 한 조건이 아니다

아래는 개념을 위한 가상 예시다. 실제 field와 권한 규칙은 08단계에서 결정한다.

```text
인증된 요청
  → 서버가 tenant_id, user_id, 현재 project_id, 현재 agent_id를 신뢰 가능한 인증 정보에서 결정
  → memory service가 허용된 memory_scope를 계산
  → Qdrant query에 모든 필수 filter를 넣음
  → “의미상 가까운 Point” 중에서도 허용 범위만 반환
```

예를 들어 현재 agent가 `agent-A`이고 project `P1`에서 실행 중이라면, memory service는 대략 다음 세 부류만 허용할 수 있다.

```text
tenant_id = 현재 tenant
AND user_id = 현재 user
AND status = active
AND (
  memory_scope = user_shared
  OR memory_scope = project_shared AND project_id = P1
  OR memory_scope = agent_private AND agent_id = agent-A
)
```

이 식은 채택 설계가 아니라, “vector의 유사도 점수만으로는 회상 허용 여부를 결정할 수 없다”는 것을 보여 주는 보조 예시다. Qdrant filter의 구체적 조합과 점수 정책은 05단계에서 다룬다.

---

## 2. Collection, payload filter, shard: 각각 무엇을 분리하는 도구인가?

이 세 기능은 모두 “나누기”처럼 보이지만, 나누는 대상과 비용이 다르다.

| 도구 | 무엇을 나누는가 | query 때 필요한 동작 | 강점 | 주의점 |
| --- | --- | --- | --- | --- |
| 별도 Collection | vector schema·운영·물리 관리 단위 | 대상 Collection만 query | 모델·보존 정책·강한 운영 격리를 분리하기 쉬움 | user/agent마다 만들면 Collection 수가 폭증할 수 있음 |
| Payload filter | 한 Collection 안의 논리적 검색 범위 | vector query에 `must` 조건을 붙임 | 대량의 tenant/user를 한 schema에서 다루기 좋음 | 조건 누락을 호출 코드가 막아야 함 |
| `is_tenant` payload index | tenant filter가 항상 있는 한 Collection의 내부 배치·index | tenant filter를 항상 사용 | 같은 tenant의 Point를 함께 배치해 filtered search 최적화 | Collection당 한 field만 사용 가능하며, filter 없는 전역 검색에는 맞지 않을 수 있음 |
| Custom shard | 한 Collection 안의 물리적 shard 경계 | shard key selector와 tenant filter를 함께 지정 | 매우 큰 tenant를 전용 shard로 분리해 **noisy neighbor**(한 tenant의 부하가 다른 tenant의 속도를 떨어뜨리는 현상) 완화 | routing·승격 운영이 추가되고, Qdrant FAQ는 낮은 수의 tenant 값에서만 권장 |

### Collection은 “소유자 폴더”가 아니라 vector·운영 계약의 경계다

Qdrant 공식 FAQ는 user마다 Collection을 하나씩 만들지 말고, 일반적으로 하나의 Collection에 `user_id` 또는 `tenant_id` payload를 넣어 분리하는 방식을 권장한다. 이유는 Collection마다 index와 운영 자원이 필요하기 때문이다.

따라서 아래처럼 “사용자 한 명 = Collection 한 개”는 직관적이지만, 사용자가 많아질수록 관리 대상도 같은 비율로 증가한다.

```text
피해야 할 가능성이 큰 형태
user-001 → collection_user_001
user-002 → collection_user_002
user-003 → collection_user_003
...
```

같은 embedding model, 같은 vector schema, 비슷한 보존 정책을 쓰는 memory라면 다음 형태가 보통의 출발점이다.

```text
shared_memory_<embedding_contract>
├─ Point: payload.tenant_id = tenant-A
├─ Point: payload.tenant_id = tenant-A
└─ Point: payload.tenant_id = tenant-B

각 query에는 현재 tenant_id filter를 반드시 포함
```

여기서 `<embedding_contract>`는 “같은 embedding model·차원·distance metric·vector type을 쓸 수 있는가”라는 **vector 저장·비교의 공통 계약**이다. tenant가 같아도 이 계약 또는 보존·컴플라이언스 요구가 본질적으로 다르면 별도 Collection이 필요할 수 있다.

### Payload filter는 “검색 허용 목록”을 먼저 만든다

vector search만 수행하면 Qdrant는 Collection 전체에서 query와 가까운 Point를 찾는다. filter를 붙이면 먼저 “후보가 되어도 되는 Point”를 payload 조건으로 제한하고, 그 안에서 vector 유사도를 계산한다.

```text
filter 없음
  모든 tenant의 Point 중 의미상 가까운 결과

tenant_id filter 있음
  현재 tenant의 Point만 후보
    → 그 안에서 의미상 가까운 결과
```

Qdrant 공식 multitenancy 문서의 예시는 각 Point payload에 `group_id`를 저장하고, query에도 같은 `group_id` 조건을 넣는다. `group_id`는 user를 뜻하는 예시 이름일 뿐이므로, 우리 시스템에서 tenant의 실제 의미를 그대로 결정하지는 않는다.

### Shard는 언제 필요한가?

shared Collection + payload filter가 논리적 분리라면, custom shard는 큰 tenant를 물리적으로 분리할 수 있는 선택지다. Qdrant의 tiered multitenancy는 작은 tenant를 fallback shard에 함께 두고, 성장한 tenant만 dedicated shard로 승격하는 구조를 제공한다.

```text
처음
작은 tenant A, B, C → fallback shard `default`

성장 후
tenant A → dedicated shard `tenant-A`
tenant B, C → fallback shard `default`
```

이때도 query에서 `tenant_id`/`group_id` filter가 사라지지 않는다. shard routing은 어느 물리 저장 구역을 볼지 정하고, payload filter는 그 안에서 어느 tenant의 Point가 허용되는지 정한다. Qdrant 공식 문서는 custom sharding을 해당 field로 항상 filter하고 고유값 수가 낮은 경우에만 권장한다. 즉 user 수가 매우 많은 서비스에서 처음부터 user마다 dedicated shard를 만들라는 권고가 아니다.

---

## 3. 공개 사례 A — Qdrant 공식 `group_id` partition: 한 Collection에서 tenant를 제한하는 실제 query

### 무엇을 저장하고 어떻게 조회하는가?

Qdrant의 공식 multitenancy 문서는 하나의 Collection 안에 서로 다른 `group_id`를 payload로 가진 Point를 저장한다. query 시에도 `group_id = user_1` 같은 `must` filter를 함께 보낸다.

```text
Point 1 → payload.group_id = user_1
Point 2 → payload.group_id = user_1
Point 3 → payload.group_id = user_2

user_1의 query
  → vector query + group_id = user_1 filter
  → Point 1, 2만 검색 후보
```

이는 “vector가 가장 가깝다”보다 “먼저 같은 group에 속한다”가 우선이라는 구조다. 해당 문서는 `group_id`에 keyword payload index를 만들고 `is_tenant=true`를 설정하는 예도 제시한다. 이 설정은 tenant-filtered query를 전제로 같은 tenant의 Point를 함께 배치하고 per-tenant sub-index를 구성하도록 돕는다.

### 왜 이 구조가 필요한가?

동일한 embedding model을 쓰는 수많은 작은 tenant가 있을 때 tenant별 Collection을 만들면 index·관리 단위가 늘어난다. 반대로 모든 Point를 한 Collection에 두되 group filter를 항상 붙이면, 하나의 schema와 index 운영 단위를 공유하면서도 query 후보는 tenant별로 제한할 수 있다.

### 공개 자료만으로 알 수 없는 점

- `group_id`가 조직, 사용자, 프로젝트 중 무엇이어야 하는지는 Qdrant가 정하지 않는다.
- filter를 누락하지 않도록 API를 어떻게 감싸는지는 애플리케이션 책임이다.
- `is_tenant=true`가 tenant 간 authorization을 구현하는 기능은 아니다. 이는 filter 패턴을 위한 index/배치 최적화다.

**출처 유형:** Qdrant 공식 문서, 접근일 2026-07-24.  
**출처:** [Multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/), [Qdrant Fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/)

---

## 4. 공개 사례 B — Dust: 데이터 소스마다 Collection을 만들던 구조를 shared multi-tenant Collection으로 바꾼 이유

### 무엇을 저장하고 어떻게 조회하는가?

Dust는 회사 지식과 agent를 제공하는 제품이다. 공개 사례에 따르면 처음에는 **data source마다 별도의 vector Collection**을 만들었다. data source가 5,000개를 넘으면서 Collection 수가 거의 1,000개에 이르자 RAM 사용량과 검색 성능 문제가 커졌다. 이후 수천 개의 Collection을 몇 개의 shared multi-tenant Collection으로 통합하고, sharding과 payload filtering을 사용했다고 밝혔다.

```text
초기
data source A → collection A
data source B → collection B

변경
shared collection
  ├─ source A의 Point + source/tenant payload
  ├─ source B의 Point + source/tenant payload
  └─ query 시 필요한 source/tenant filter
```

Dust는 `DustQdrantClient`라는 자체 client를 두어 cluster version, embedding model, shard routing의 차이를 감쌌다고도 밝혔다. 즉 agent나 각 connector가 Qdrant query를 제각각 만들게 하지 않고, 중앙 client/service가 routing과 vector 관련 결정을 모으는 형태다.

### 왜 이 구조가 필요한가?

Dust가 해결하려 한 직접 문제는 tenant 자체라기보다, **data source를 Collection 하나와 1:1로 매핑했을 때의 Collection 폭증**이었다. shared Collection으로 통합하면 vector schema·index·운영 설정을 공유할 수 있다. source/tenant 단위의 결과 제한은 payload filter와 sharding으로 처리한다.

이 사례는 subagent memory에서도 “agent 한 개 = Collection 한 개”가 자동으로 좋은 설계가 아님을 보여 준다. agent가 많아지는 구조라면 agent ID는 보통 payload scope가 되고, Collection 분리는 embedding contract·데이터 수명·컴플라이언스처럼 더 큰 운영 차이에 근거해야 한다.

### 공개 자료만으로 알 수 없는 점

- Dust의 실제 payload field 이름, tenant authorization 정책, source filter 조합은 공개되지 않았다.
- Dust가 user/subagent memory를 어떻게 모델링하는지 공개 사례에는 없다.
- 성능·비용 수치는 Qdrant가 발행한 고객 사례이므로 독립 벤치마크가 아니다.

**출처 유형:** Qdrant 고객 사례(벤더 발행), 접근일 2026-07-24.  
**출처:** [How Dust Scaled to 5,000+ Data Sources with Qdrant](https://qdrant.tech/blog/case-study-dust-v2/)

---

## 5. 공개 사례 C — LlamaIndex + Qdrant: metadata filter가 실제 검색 결과를 바꾸는 방식

Qdrant의 LlamaIndex multitenancy 예제는 서로 다른 Python library 문서를 같은 Collection에 넣고, `metadata.library` payload field로 검색 대상을 제한한다. 문서는 node로 나뉘어 embedding과 함께 저장되며, `metadata.library`에는 해당 문서가 어느 library에 속하는지가 들어간다.

```text
같은 Collection
├─ Node: metadata.library = llama-index
└─ Node: metadata.library = qdrant

“large language models” 질의
  + library = qdrant filter
  → qdrant 문서 Node만 반환
```

이 예제에서 중요한 점은 vector가 의미상 가장 가까운 결과만 고르는 것이 아니라는 점이다. `library=qdrant` filter가 있으면, 다른 library 문서가 의미상 더 가깝더라도 후보가 될 수 없다. 또한 예제는 모든 query가 이 metadata로 제한될 때 `metadata.library` payload index를 만들고, global search를 하지 않는 전제에서 HNSW 설정을 조정한다.

subagent memory에 대입하면 `library`는 tenant 자체가 아니라, `project_id`, `agent_id`, `memory_scope` 같은 회상 범위 field의 작동 원리를 보여 주는 사례다. 어떤 필드를 filter할지는 우리 정책이 결정하지만, filter가 실제 검색 결과를 바꾼다는 점은 이 공개 예제로 확인할 수 있다.

**출처 유형:** Qdrant 공식 통합 예제, 접근일 2026-07-24.  
**출처:** [Multitenancy with LlamaIndex](https://qdrant.tech/documentation/examples/llama-index-multitenancy/)

---

## 6. 사용자별 subagent memory에 적용하기 전의 후보 구조

아래는 앞선 공개 설계에서 얻은 원칙을 subagent memory 문제에 맞춰 정리한 **후보 구조**다. 아직 08단계의 확정 설계가 아니다.

```text
Memory API / service
  1. 인증 정보에서 tenant·user·현재 작업 context를 확인
  2. 저장 시 payload scope를 검증해 부여
  3. 조회 시 허용 범위를 filter로 강제
  4. Qdrant에 vector query + filter를 보냄

Qdrant shared memory Collection
  ├─ vector: 의미/키워드 검색 표현
  └─ payload: tenant_id, user_id, project_id, agent_id,
              memory_scope, status, 시간 등

별도 상태·원장 저장소
  └─ 승인, 감사, 원문 증거, 권한 변경처럼 vector search보다
     transaction·감사가 중요한 상태
```

이 구조에서 Qdrant가 맡는 일은 “필터 범위 안에서 관련 memory 후보를 빠르게 찾기”다. 누가 어떤 scope를 읽을 수 있는지의 최종 정책, Point 생성 승인, 삭제 요청의 원장 기록은 memory service와 별도 상태 저장소의 책임으로 남긴다.

### 지금 단계에서의 결정 질문

| 결정할 질문 | 이 단계에서 확인한 사실 | 아직 필요한 검증 |
| --- | --- | --- |
| Collection을 user/agent마다 나눌 것인가? | Qdrant와 Dust 사례 모두 많은 작은 단위의 Collection 증가는 비용·성능 문제가 될 수 있음을 보여 줌 | 예상 tenant·agent 수, 모델 수, retention/규제 차이 |
| tenant field는 무엇인가? | payload filter와 tenant index는 한 field를 기준으로 작동 | 조직·사용자 중 실제 인증·청구·삭제 경계가 무엇인지 |
| agent private와 shared memory를 어떻게 구분할 것인가? | Qdrant가 정책을 결정하지 않으며 payload/filter로 표현 가능 | 승격 주체, 승인 조건, 오류 기억의 전파 방지 정책 |
| 큰 tenant를 별도 shard로 승격할 것인가? | Qdrant은 fallback + dedicated shard 구조를 지원 | tenant 크기 분포, noisy-neighbor 기준, routing 운영 능력 |
| Qdrant filter만으로 격리할 것인가? | filter는 query 범위 조건이며, service가 누락을 막아야 함 | 인증 context를 filter 생성과 묶는 API 설계 및 보안 검토 |

---

## 7. 이 단계에서 확정하지 않는 것

다음 항목은 중요한 설계이지만, 이번 단계의 공개 사례만으로 답할 수 없다.

- `tenant_id`를 organization으로 할지 user로 할지
- `user_shared`, `project_shared`, `agent_private`의 정확한 읽기·쓰기 권한
- `status=active` 같은 lifecycle 상태와 scope 변경의 원장 위치
- 각 scope field에 실제 payload index가 필요한지와 그 순서
- 대형 tenant 승격 기준과 custom shard 도입 시점
- collection-scoped JWT, network/TLS, application authorization을 어떻게 조합할지

이 질문은 다음 단계에서 Point/Payload schema를 구체화하고, 05단계에서 검색 filter를 설계한 뒤 08단계에서 함께 결정한다.

## 핵심 정리

```text
Collection
  = 같은 vector·운영 계약을 공유하는 검색 집합

tenant payload filter
  = 다른 tenant의 Point를 검색 후보에서 제외하는 필수 범위

user/project/agent/run + memory_scope payload
  = 같은 tenant 안에서 현재 agent가 읽을 수 있는 기억을 결정하는 정책 입력

custom shard
  = 일부 큰 tenant의 물리적 격리·성능 문제를 다루는 확장 선택지

Memory service
  = 인증 context에서 filter를 만들고, scope·승격·삭제 정책을 강제하는 계층
```

## 출처와 신뢰도

| 자료 | 유형 | 확인한 내용 | 한계 |
| --- | --- | --- | --- |
| [Qdrant Multitenancy](https://qdrant.tech/documentation/manage-data/multitenancy/) | Qdrant 공식 문서 | `group_id` payload filter, `is_tenant`, custom/fallback shard, tenant promotion | 우리 제품의 tenant 정의·권한 정책은 제공하지 않음 |
| [Qdrant Fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/) | Qdrant 공식 FAQ | user별 Collection 대신 payload separation, filtering·sharding 선택 기준 | 제품별 workload 측정값은 아님 |
| [Dust 고객 사례](https://qdrant.tech/blog/case-study-dust-v2/) | 벤더 발행 고객 사례 | data source별 Collection을 shared multi-tenant Collection으로 통합, custom client·sharding·payload filtering | 내부 schema·수치가 독립적으로 검증되지는 않음 |
| [LlamaIndex multitenancy 예제](https://qdrant.tech/documentation/examples/llama-index-multitenancy/) | Qdrant 공식 통합 예제 | metadata field와 filter가 후보 문서를 제한하는 흐름 | 작은 교육용 예제로 실제 agent memory 권한 모델은 아님 |

## 다음 단계

05번 파일에서는 memory 하나를 Point 하나로 표현할 때 `id`, vector, payload에 무엇을 넣고 무엇을 별도 상태 저장소에 둘지 다룬다. 특히 `status`, `source_evidence_id`, `expires_at`, `schema_version`이 왜 단순 metadata가 아닌 lifecycle·감사·재처리의 입력이 되는지 공개 구현과 함께 확인한다.
