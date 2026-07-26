# 사용자별 Subagent 메모리 설계안 — 조건부 채택안과 검증 항목

> 학습 단계: 8 / 9  
> 작성일: 2026-07-24  
> 상태: **조건부 설계안**. 마지막 실습과 실제 workload 평가 전에는 production 확정안이 아니다.

## 1. 이 설계안의 전제

현재 목표는 “각 사용자의 여러 subagent가 장기 memory를 안전하게 저장하고, 필요한 범위에서만 다시 읽는 시스템”이다. 따라서 다음을 전제로 한다.

- 한 요청은 인증된 사용자/tenant context를 가진다.
- 한 사용자 안에는 여러 subagent와 여러 project가 있을 수 있다.
- 모든 agent의 중간 결과를 즉시 공유 memory로 만들지 않는다.
- Qdrant는 retrieval index이고, 원문 evidence·감사·상태 전이의 유일한 원장은 아니다.

`tenant_id`는 가장 바깥 authorization 경계다. 현재 개인 사용자 제품이라면 `tenant_id = user_id`로 시작할 수 있다. 조직 단위 제품으로 확장되면 `tenant_id = organization_id`로 바꾸고 내부에 `user_id`를 둔다. 이 두 경우에 Collection 구조와 query 흐름은 유지된다.

---

## 2. 한눈에 보는 채택 구조

```text
인증된 요청
  → Memory Service
     ├─ tenant/user/project/agent context를 서버에서 확정
     ├─ memory lifecycle·scope 정책 적용
     ├─ Qdrant query filter를 강제
     └─ 원장 DB의 evidence·audit와 연결

Qdrant: shared `agent_memory_v1` Collection
  ├─ Point: 재사용 가능한 memory 하나
  ├─ dense vector: 의미 검색 baseline
  └─ payload: scope, status, 시간, kind, evidence reference

원장 DB + 원문 저장소
  ├─ evidence/original event
  ├─ memory 상태 전이와 승인·삭제 audit
  └─ Qdrant projection을 위한 outbox event
```

이 구조의 핵심은 다음 한 문장이다.

> Qdrant는 **허용된 범위 안에서 관련 memory 후보를 찾는 곳**이고, Memory Service는 **누가 어떤 memory를 읽고 바꿀 수 있는지 결정하는 곳**이다.

---

## 3. 설계 항목별 채택안

| 설계 항목 | 조건부 채택안 | 이유 | 기각/보류한 대안 |
| --- | --- | --- | --- |
| Collection topology | embedding contract당 shared Collection | user/agent마다 Collection을 늘리지 않고 index·운영을 공유 | user별·agent별 Collection: 대량 생성 시 자원 부담 |
| tenant 격리 | 모든 read/write에서 server-derived `tenant_id`를 payload filter로 강제 | vector score보다 앞서는 절대 경계 | caller가 tenant_id를 직접 전달해 선택 |
| subagent 격리 | `agent_id` + `memory_scope`로 private/shared를 표현 | 작성 agent와 현재 읽기 권한을 분리 | agent마다 별도 Collection |
| Point 단위 | 재사용 가능한 fact, decision, procedure, 짧은 episode | query에 넣을 context를 작고 검증 가능하게 유지 | 전체 transcript를 무조건 Point 하나로 저장 |
| vector schema | dense vector 하나로 baseline | 먼저 의미 recall·latency·비용을 측정 | 처음부터 sparse·MultiVector 강제 |
| hybrid | 고유명사/ID/코드 recall 필요성이 확인되면 named dense+sparse + RRF 평가 | dense/sparse의 신호가 실제로 보완되는지 검증 | 점수 scale을 직접 더하기 |
| status | `candidate → active → superseded/expired/deleted` | 검증 전 memory와 과거 memory가 기본 recall에 섞이지 않음 | 저장 즉시 전역 공유 |
| source of truth | 원장 DB, Qdrant는 검색 projection | audit·권한·부분 실패 복구에 적합 | Qdrant payload만으로 모든 상태 관리 |
| backup/failure | Qdrant snapshot + 원장/원문 backup + reconcile 절차 | snapshot은 vector/payload만 복구 | Qdrant snapshot만으로 전체 memory 복구 |

---

## 4. Collection과 vector schema

### 시작 Collection

```text
agent_memory_v1
```

같은 Collection에 둘 수 있는 조건은 다음이다.

- 같은 embedding model·차원·distance metric을 사용한다.
- 같은 lifecycle 상태와 payload schema를 사용한다.
- tenant filter가 모든 query에 적용된다.

embedding model이 달라 차원/metric이 달라지거나, 보존 정책·컴플라이언스·지역 분리가 달라지면 별도 Collection을 만든다. 대형 tenant의 noisy-neighbor 문제가 실제로 측정될 때만 custom shard 승격을 검토한다.

### vector의 단계적 도입

```text
1단계: dense vector만
  → 의미 memory recall baseline과 golden query 측정

2단계: 필요가 확인되면 Named Vector 추가
  → `semantic` dense + `lexical` sparse
  → RRF hybrid와 dense-only 비교

3단계: late-interaction 모델을 실제 채택할 때만 MultiVector 검토
```

MultiVector는 “vector를 여러 개 저장하고 싶다”는 이유가 아니라, ColBERT 같은 late-interaction model output을 정교하게 검색해야 할 때만 사용한다.

---

## 5. Point와 Payload schema

```json
{
  "id": "stable memory UUID",
  "vector": "dense baseline; hybrid 도입 뒤 named vectors",
  "payload": {
    "tenant_id": "authorization boundary",
    "user_id": "personal-memory owner",
    "project_id": "project context or null",
    "agent_id": "creating/private agent",
    "memory_scope": "agent_private | project_shared | user_shared",
    "memory_kind": "preference | fact | decision | procedure | episode",
    "status": "candidate | active | superseded | expired | deleted",
    "content": "LLM/retrieval agent에 반환할 정규화된 memory text",
    "importance": "optional policy score",
    "confidence": "optional evidence/extractor score",
    "created_at": "RFC 3339 datetime",
    "updated_at": "RFC 3339 datetime",
    "expires_at": "RFC 3339 datetime or null",
    "source_evidence_id": "원장/원문 evidence reference",
    "embedding_model": "model identifier",
    "schema_version": 1
  }
}
```

처음부터 index를 검토할 field는 `tenant_id`, `status`, 그리고 실제 모든 query에 사용되는 scope field다. `project_id`, `agent_id`, `memory_scope`, `expires_at`은 query 로그와 filter 패턴을 확인한 뒤 index한다. 반환만 하는 `content`는 기본적으로 payload index 대상이 아니다.

---

## 6. write와 read의 실제 흐름

### Write: memory를 바로 전역 지식으로 만들지 않는다

```text
원문 event/tool 결과/사람 수정
  → 원장에 evidence와 상태 기록
  → memory candidate 추출
  → stable memory_id 부여
  → vector + payload를 Qdrant에 upsert
  → 검증/정책 통과 시 status=active, 필요한 scope로 승격
```

원장 transaction에 outbox event를 남기고 worker가 Qdrant projection을 갱신한다. 실패하면 같은 memory ID로 재시도한다. Qdrant의 idempotent upsert는 재시도를 돕지만 원장과 Qdrant를 하나의 transaction으로 묶어 주지는 않는다.

### Read: score가 아니라 허용 범위부터 확정한다

```text
인증된 request
  → Memory Service가 tenant/user/project/agent context 확인
  → 허용 memory_scope 계산
  → Qdrant query에 필수 filter 강제
       tenant_id = current
       status = active
       expires_at 조건
       user/project/agent/scope 조건
  → dense search Top-K + threshold
  → 필요하면 hybrid/RRF·rerank
  → content + evidence reference를 retrieval context로 반환
```

빈 결과의 fallback은 같은 tenant 안에서만 scope를 넓힐 수 있다. 예를 들어 current agent의 private memory가 없을 때 user_shared를 추가할 수는 있어도, tenant filter를 제거해서는 안 된다.

---

## 7. lifecycle과 삭제

| 상태 | 일반 recall | 원장/audit | 전환 예 |
| --- | --- | --- | --- |
| candidate | 제외 | 추출 근거·검토 대기 기록 | 자동 추출 직후 |
| active | 포함 | 현재 사용 가능한 이유 기록 | 검증 또는 정책 통과 |
| superseded | 제외 | 새 memory와 대체 이유 연결 | 담당자·규칙 변경 |
| expired | 제외 | 만료 시각·보존 정책 기록 | 임시 작업/권한 종료 |
| deleted | 제외 | 삭제 요청·처리 상태 기록 | 사용자 삭제 또는 정책 삭제 |

Qdrant delete는 API 차원에서 Point 접근을 막지만 내부 physical cleanup은 비동기다. 따라서 개인정보/보존 요구는 Qdrant·원장·원문·backup 각각에 대한 삭제·보존 정책을 따로 가져야 한다.

## 8. 마지막 실습에서 검증할 가설

1. 다른 `tenant_id`의 Point는 어떤 query에서도 반환되지 않는다.
2. 같은 tenant에서도 active + 허용 scope가 아닌 Point는 반환되지 않는다.
3. 동일 memory write 재시도는 duplicate Point를 만들지 않는다.
4. superseded/expired/deleted 뒤에는 기본 recall에서 사라진다.
5. dense-only와 hybrid의 recall/latency가 실제 query에서 어떤 차이를 보이는지 측정한다.
6. snapshot 복구 후 원장과 Qdrant projection의 불일치를 탐지할 수 있다.

## 9. 근거와 한계

이 설계는 Qdrant 공식 multitenancy·payload/index·hybrid query·snapshot 문서와 Dust, Fieldy, LlamaIndex 공개 사례에서 확인한 원칙을 결합한 것이다. 그러나 tenant 정의, 실제 data volume, embedding model, 보존 법규, latency SLA는 아직 주어지지 않았다. 따라서 Collection 수, index 목록, shard/replica 수, hybrid parameter는 실습과 workload 평가 후 조정해야 한다.

## 다음 단계

10번 파일에서 이 설계의 격리·검색·lifecycle 가설만 검증하는 최소 실습을 작성한다. 실습은 설계안을 새로 정하는 자리가 아니라, 위 가설이 코드와 Qdrant 동작에서 실제로 성립하는지 확인하는 단계다.
