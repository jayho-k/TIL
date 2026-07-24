# Mem0 vs OpenViking: 기존 Chat Portal 성능 개선 관점 비교
작성일: 2026-07-12

## 0. 이 문서의 판단 전제

Chat Portal에는 이미 다음 기능이 구현되어 있다.

1. 사용자가 업로드한 문서와 대화하는 기능
2. 일반 대화 기능
3. 회의록 생성 기능
4. 사전 parsing/embedding한 사내 지식 기반 RAG 기능

또한 Qdrant, PostgreSQL, MinIO, Redis를 이미 운영한다. 이 문서의 목적은 새 기능을 설계하거나 기존 RAG를 무조건 교체하는 것이 아니다.

> **기존 기능과 저장소를 유지한 채 Mem0 또는 OpenViking을 추가했을 때, Agent의 context 선택 품질, 장기 기억 품질, token 사용량, 응답 지연을 실제로 개선할 수 있는가를 비교한다.**

따라서 이 문서에서 provider는 기본적으로 기존 시스템의 **overlay/sidecar**다. 현재 RAG, PostgreSQL 업무 데이터, MinIO 원문 보관소의 source of truth를 provider에 넘긴다는 뜻이 아니다.

## 1. 조사 스냅샷과 신뢰도

| 항목 | Mem0 | OpenViking |
| --- | --- | --- |
| 공식 저장소 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) |
| 공식 문서 | [Mem0 Docs](https://docs.mem0.ai/) | [OpenViking Docs](https://docs.openviking.ai/en/) |
| 확인한 `main` commit | `17836748d7afe0521516c6a73c6a256680f05527` (2026-07-11) | `5bfa9b617ecff478f825ca435a35bc4222b30582` (2026-07-11) |
| 2026-07-12 GitHub stars | 약 60.6k | 약 26.6k |
| 라이선스 | Apache-2.0 | AGPL-3.0 |
| 기본 역할 | durable fact extraction/retrieval engine | Resource/Session/Memory/Skill Context Database |

별 수는 생태계 크기를 보는 보조 정보일 뿐 성능이나 production 적합성의 증거는 아니다. 이슈는 사용자 보고를 포함하므로, 아래에서는 결함 확정이 아니라 PoC에서 재현해야 할 위험 신호로 취급한다.

## 2. 먼저 정리: 두 제품은 기존 기능을 무엇으로 개선하는가

### 2.1 Mem0

Mem0 최신 OSS V3는 대화/agent 실행 결과에서 재사용 가능한 사실을 추출하고, vector store에서 다시 찾는 **fact memory engine**이다.

```text
현재 Chat Portal 대화/회의 결과
  -> Mem0가 durable fact candidate 추출
  -> Qdrant memory collection에 vector + metadata 저장
  -> 다음 요청에서 관련 fact만 recall
  -> DeepAgent prompt에 작은 context로 주입
```

Mem0가 개선하려는 것은 다음이다.

- 사용자가 반복해서 설명하는 선호, 프로젝트 관례, 정정 사항
- 이전 회의의 장기 결정/업무 관례
- agent가 같은 실수를 반복하는 문제
- 현재 요청과 관련된 작은 사실을 찾기 위해 과거 transcript 전체를 다시 넣는 문제

Mem0가 직접 개선하지 않는 것은 다음이다.

- 현재 document RAG의 chunk retrieval/citation/ACL
- 대규모 사내 문서의 directory/section hierarchy 탐색
- 업로드 원문, 회의 전사문, 첨부파일 보관
- 업무 상태의 authoritative update

### 2.2 OpenViking

OpenViking은 `viking://` URI를 중심으로 Resource, Session, Memory, Skill을 조직하고, L0/L1/L2 요약 계층에서 필요한 원문만 탐색하는 **context retrieval system**이다.

```text
현재 Chat Portal 문서/대화/회의 컨텍스트의 사본 또는 선택된 subset
  -> OpenViking Resource / Session / Memory URI
  -> L0 abstract, L1 summary, L2 source hierarchy 생성
  -> Qdrant index로 후보 탐색
  -> 필요한 문맥만 DeepAgent에 전달
```

OpenViking도 durable fact를 가진다. 기본/커스텀 memory template으로 `profile`, `preferences`, `entities`, `events`, `patterns`, `tools`, `skills` 등의 장기 memory를 URI와 파일 계층에 저장하고 session commit에서 추출/갱신할 수 있다. 즉 "durable fact가 필요하므로 Mem0가 필수"는 아니다.

OpenViking이 추가로 개선할 수 있는 것은 다음이다.

- 긴 문서와 여러 사내 문서에서 상위 요약부터 좁혀 가는 retrieval
- 과거 session, meeting context, document, skill을 연결해 탐색하는 agent context
- 큰 RAG 결과를 그대로 prompt에 넣지 않고 L0/L1/L2로 token budget을 제어하는 문제
- 단일 vector similarity가 놓치는 project/document hierarchy

대신 OpenViking은 기존 Chat Portal에 별도 context service와 asynchronous semantic pipeline을 추가한다. 기존 RAG가 이미 충분히 정확하고 context가 짧다면 오히려 응답 경로와 운영 비용만 늘릴 수 있다.

## 3. 비교 기준: 기능 보유 여부가 아니라 개선 효과

기존 기능이 이미 있는 상황에서는 "무엇을 할 수 있는가"보다 다음 지표가 중요하다.

| 범주 | 측정 질문 | 대표 지표 |
| --- | --- | --- |
| Retrieval quality | 필요한 근거를 실제로 더 잘 찾는가 | Recall@k, MRR, nDCG, citation precision/recall |
| Answer quality | 근거에 충실한 더 나은 답을 만드는가 | faithfulness, task success, human preference win-rate |
| Context efficiency | 같은 답을 더 적은 context로 만드는가 | input tokens, retrieved chars, irrelevant-context ratio |
| Latency | 사용자 체감 응답을 악화시키지 않는가 | retrieval p50/p95, TTFT, end-to-end p95 |
| Memory correctness | 오래된/다른 사용자 정보를 잘못 주입하지 않는가 | stale recall rate, cross-tenant leakage, conflict correctness |
| Freshness | 문서/회의 수정 뒤 결과가 얼마나 빨리 맞춰지는가 | ingest-to-searchable, update/delete propagation lag |
| Operational cost | 성능 이득이 운영 복잡도를 상쇄하는가 | component count, failure recovery, storage/LLM cost |

각 provider는 이 모든 지표를 동시에 높이지 않는다. Mem0는 memory correctness와 작은 context efficiency에, OpenViking은 hierarchy retrieval과 large-context efficiency에 가설상 강점이 있다.

## 4. 기존 Chat Portal 기능별 성능 가설

### 4.1 업로드 문서 대화

#### 현재 흐름에서 먼저 확인할 병목

- 긴 문서에서 필요한 section/page를 못 찾는가
- 여러 업로드 문서를 함께 질문할 때 관련 문서를 누락하는가
- 상위 문맥 없이 chunk만 넣어 답변이 단편적인가
- 검색 결과가 너무 많아 prompt token과 응답 지연이 커지는가
- 문서 수정/삭제 후 stale chunk가 답변에 남는가

#### Mem0가 줄 수 있는 개선

제한적이다. 문서 자체를 Mem0 memory로 대량 넣는 것은 문서 RAG 개선 방식이 아니다.

- 사용자가 자주 적용하는 해석 관례나 프로젝트 기준을 작은 fact로 recall
- 문서 대화에서 승인된 결론을 이후 대화에 재사용
- 이전에 사용자가 정정한 답변 형식/정책을 기억

그러나 문서의 section hierarchy, citation, raw content retrieval 품질은 현재 RAG 또는 OpenViking을 평가해야 한다.

#### OpenViking이 줄 수 있는 개선

OpenViking은 기존 upload pipeline의 대체가 아니라 **shadow retrieval path**로 측정한다.

```text
Control: 현재 parser -> chunk -> Qdrant -> top-k context

Treatment: 같은 문서 subset을 OpenViking Resource로 ingest
           -> L0/L1 overview search
           -> 필요한 URI만 read
           -> 동일 LLM prompt budget에서 답변
```

가설은 다음이다.

- 긴 문서/다문서 질의에서 citation precision과 answer faithfulness가 올라간다.
- 상위 요약을 먼저 활용해 input token과 irrelevant chunk 수가 줄어든다.
- agent가 필요한 원문을 tool로 추가 탐색하므로 initial top-k를 크게 잡지 않아도 된다.

반증 조건도 명확하다.

- 현재 chunk RAG와 quality 차이가 없고 latency만 커진다.
- summary 생성 시간이 길어 문서 업로드 후 searchable 상태가 늦어진다.
- document update/delete의 freshness를 현재 pipeline보다 보장하지 못한다.

**이 기능에서의 우선 후보:** OpenViking. 단, 현재 RAG를 교체하지 않고 비교 대상 corpus에서만 A/B한다.

### 4.2 일반 대화

#### 현재 흐름에서 먼저 확인할 병목

- 사용자가 언어/형식/프로젝트 맥락을 반복 설명하는가
- 이전 정정을 잊고 같은 잘못된 기본값을 반복하는가
- 과거 대화 전체를 넣어서 context가 커지는가
- user/project/tenant memory가 잘못 섞일 위험이 있는가

#### Mem0가 줄 수 있는 개선

이 영역은 Mem0의 가장 직접적인 적용 범위다.

```text
현재 요청
  -> tenant/user/project filter로 Mem0 search
  -> top N durable facts만 prompt에 주입
  -> 응답 후 새 fact는 candidate로 기록
```

평가 포인트는 사실 recall이 아니라 행동 변화다.

- 사용자가 "간결한 한국어로 답하라"고 한 뒤 다음 대화에서도 실제로 지키는가
- 프로젝트별 배포/코딩/문서 관례를 반복 정정하지 않는가
- 관련 없는 memory가 답변을 오염시키지 않는가
- memory lookup의 추가 지연보다 반복 설명 감소가 큰가

#### OpenViking이 줄 수 있는 개선

OpenViking memory template도 profile/preference/project fact를 저장할 수 있으므로 이 기능을 구현할 수 있다. 차이는 fact만 찾는 것이 아니라 session, 관련 resource, skill을 함께 탐색할 수 있다는 점이다.

그러나 일반 대화의 병목이 단순 preference/fact recall이라면 OpenViking의 URI hierarchy와 semantic worker는 과할 수 있다. 반대로 일반 대화가 사용자의 프로젝트 문서, 과거 session, skill을 동시에 참조해야 한다면 OpenViking이 하나의 context plane으로 더 일관될 수 있다.

**이 기능에서의 우선 후보:** 작은 fact recall이면 Mem0, session/resource까지 함께 회수해야 하면 OpenViking. 현재 실패 로그가 없으면 사전에 하나를 단정하지 않는다.

### 4.3 회의록 생성

#### 현재 흐름에서 먼저 확인할 병목

- 회의록 생성 자체의 요약 품질이 문제인가
- 이전 회의의 결정/미해결 action item을 다음 회의에서 못 찾는가
- 담당자/기한 변경 뒤 오래된 결정을 주입하는가
- 전사문 전체를 매번 넣어 token 비용과 응답 시간이 큰가
- 결정의 원문 근거를 다시 열어볼 수 없는가

회의록의 원문, 결정, 할 일의 권위 저장소는 여전히 MinIO/PostgreSQL이어야 한다. provider는 recall/index 계층이지 업무 상태 원장이 아니다.

#### Mem0가 줄 수 있는 개선

- 지속되는 프로젝트 convention, 확정된 장기 결정, 사용자/팀 선호의 recall
- 다음 회의에서 관련 결정 fact를 짧게 주입
- 회의 후 새 fact candidate를 추출해 review queue로 전달

주의할 점은 V3 automatic extraction이 `ADD-only`라는 것이다. "담당자가 A에서 B로 변경"된 사실을 새 memory만 추가하면 A와 B가 함께 회수될 수 있다. action item current state는 PostgreSQL에서 결정하고, 그 결과로 Mem0 explicit update/delete 또는 active status filter를 수행해야 한다.

#### OpenViking이 줄 수 있는 개선

- Session archive -> L1 회의 요약 -> L0 recall이라는 계층을 통해 이전 회의 문맥을 작게 회수
- 회의 session, 관련 문서 Resource, decision/action memory를 URI로 연결해 원문 근거까지 탐색
- DeepAgent가 필요한 경우에만 상세 transcript를 읽도록 하여 token budget 절감

이 기능은 OpenViking의 구조와 매우 잘 맞지만, 요약/overview를 비동기로 생성하는 pipeline의 신뢰성이 결과 품질을 좌우한다. summary 생성 실패가 placeholder를 성공으로 저장하고 retry하지 않는 보고가 있으므로 직접 fault injection해야 한다. [OpenViking #3151](https://github.com/volcengine/OpenViking/issues/3151)

**이 기능에서의 우선 후보:** "회의 결과 fact만 기억"이면 Mem0, "과거 회의의 결정 이유와 원문까지 agent가 탐색"해야 하면 OpenViking.

### 4.4 사내 지식 RAG

#### 현재 흐름에서 먼저 확인할 병목

- exact chunk는 맞지만 상위 업무 맥락을 못 잡는가
- 여러 부서/프로젝트 문서에서 검색 공간을 충분히 좁히지 못하는가
- top-k를 늘릴수록 비용만 증가하고 precision이 떨어지는가
- document hierarchy와 metadata filter가 retrieval에 충분히 반영되지 않는가
- query가 긴 설명을 요구할 때 context window를 과도하게 소비하는가

#### Mem0의 개선 가능성

낮다. Mem0는 사내 문서 corpus를 대체할 RAG engine이 아니다. 사내 지식 검색 결과와 사용자의 업무 맥락을 결합하는 작은 fact layer로만 쓸 수 있다.

#### OpenViking의 개선 가능성

높다. Resource URI, directory overview, L0/L1/L2 navigation은 현재 RAG의 다음 병목을 겨냥한다.

```text
현재 RAG: query -> vector top-k chunks -> prompt

OpenViking treatment:
query -> relevant directory/resource overview -> URI 후보 축소
      -> 필요한 resource only read/grep -> prompt
```

핵심 평가는 "OpenViking이 기능이 많다"가 아니라, 같은 query set과 같은 model/prompt budget에서 아래가 개선되는지다.

- relevant document/page recall
- citation precision
- 답변 faithfulness
- retrieved token 수
- end-to-end latency

**이 기능에서의 우선 후보:** OpenViking. 단, 기존 Qdrant RAG corpus의 source of truth는 유지하고 shadow index에서만 먼저 평가한다.

## 5. 두 제품의 durable fact 기능은 겹친다

두 제품은 durable fact 영역에서 실제로 겹친다.

| 질문 | Mem0 | OpenViking |
| --- | --- | --- |
| 사용자 선호 기억 | 지원 | `profile`/`preferences` memory로 지원 |
| 프로젝트 관례 기억 | metadata-filtered fact로 지원 | custom template/URI memory로 지원 |
| 이전 session에서 memory 추출 | 지원 | session commit + memory extraction으로 지원 |
| 수정/철회된 사실 관리 | explicit update/delete를 application이 잘 써야 함. V3 automatic path는 add-only | template의 merge/write/edit/delete lifecycle을 구성 가능 |
| 사실의 근거/원문 탐색 | evidence URI를 metadata로 별도 설계 | Resource/Session/Memory URI hierarchy 안에서 연결 가능 |
| 작은 fact semantic recall | 핵심 강점 | 가능하지만 context plane의 일부 |

그러므로 durable fact만 목적이라면 Mem0와 OpenViking을 함께 쓸 이유가 없다. 둘 중 하나를 선택하고, 공통으로 PostgreSQL의 상태/권한/audit를 유지하면 된다.

선택 기준은 다음이다.

- **Mem0:** personal/project fact recall만 개선하고 싶고 기존 RAG/session structure를 바꾸지 않을 때
- **OpenViking:** fact도 필요하지만 document/session/skill context를 동일한 retrieval model로 개선하고 싶을 때

hybrid는 두 제품의 확실한 성능 이득이 독립적으로 증명된 뒤에만 검토할 수 있는 예외다. 현재 PoC의 목표가 되어서는 안 된다.

## 6. sidecar 배치 원칙

### 6.1 기존 data plane은 유지한다

```text
Current Chat Portal
  PostgreSQL: account/workspace/ACL, meeting/action state, audit
  MinIO: uploaded documents, transcripts, attachments
  Qdrant: current RAG vectors
  Redis: cache, lock, request/task coordination
  DeepAgents: current thread state, tools, subagent execution
```

Mem0/OpenViking PoC는 위 source of truth를 변경하지 않는다.

### 6.2 Mem0 sidecar

```text
Chat Portal / DeepAgent
  -> internal MemoryService
  -> Mem0 SDK or internal Mem0 server
       -> Qdrant: chat_portal_mem0
       -> Qdrant: chat_portal_mem0_entities
  -> PostgreSQL: memory registry, approval, current-state, audit/outbox
  -> MinIO: evidence URI only
```

`chat_portal_rag` collection에 Mem0 record를 넣지 않는다. RAG chunk와 durable fact의 ranking/lifecycle/schema가 다르기 때문이다.

### 6.3 OpenViking shadow sidecar

```text
Current document / transcript source
  -> copy or controlled export of selected corpus only
  -> OpenViking server
       -> MinIO: openviking-context dedicated bucket/prefix
       -> Qdrant: openviking__context
       -> Qdrant: __openviking_meta
       -> QueueFS: provider persistent queue

Chat Portal request
  -> control: current RAG path
  -> treatment: OpenViking context path
  -> evaluator compares result; production response remains control initially
```

OpenViking은 Qdrant와 MinIO를 native backend로 쓸 수 있지만, 기존 collection/prefix를 재사용하지 않는다. OpenViking이 URI, `.abstract.md`, metadata sidecar, index lifecycle을 소유하기 때문이다.

### 6.4 DeepAgents 경계

DeepAgents는 filesystem-backed memory와 LangGraph Store를 통해 memory file을 읽고 수정할 수 있고, subagent는 context isolation을 제공한다. [DeepAgents memory](https://docs.langchain.com/oss/python/deepagents/memory), [DeepAgents subagents](https://docs.langchain.com/oss/python/deepagents/subagents)

그러나 provider를 agent가 직접 호출하게 두면 scope와 write policy가 흔들린다. DeepAgents에는 `recall_context`, `propose_memory`, `get_evidence` 같은 Portal tool만 노출한다.

```text
DeepAgent / subagent
  -> MemoryService tool
      - tenant/workspace/user/project scope 강제
      - context token budget 강제
      - approved/candidate memory 상태 확인
      - provider failure 시 fallback 결정
```

## 7. PoC 이전에 수집해야 할 baseline

provider를 붙이기 전에 현재 시스템의 실패와 비용을 수치로 잡아야 한다. baseline 없이 "답변이 좋아 보인다"는 판단은 provider 선택 근거가 될 수 없다.

### 7.1 공통 trace 필드

모든 representative request에 최소한 아래를 남긴다.

```text
request_id, tenant_id hash, feature_type, query class
retrieval source, retrieved document/session ids, context chars/tokens
retrieval latency, model TTFT, end-to-end latency
answer, citations, user correction/retry signal
document/session version, permission decision
```

원문/개인정보는 trace에 중복 적재하지 않고 ID, 길이, version, 안전한 excerpt reference만 남긴다.

### 7.2 기능별 golden set

| 기능 | 최소 평가 데이터 | 정답/판정 기준 |
| --- | --- | --- |
| 업로드 문서 대화 | 짧은 문서, 긴 문서, 복수 문서, 수정/삭제 문서 | answer, cited page/section, 허용 문서 범위 |
| 일반 대화 | preference, project convention, correction, unrelated-memory case | 기대 행동, 기억하면 안 되는 정보 |
| 회의 | 과거 결정 recall, 담당자 변경, transcript evidence 필요 질문 | latest action state, 근거 meeting/time range |
| 사내 RAG | 부서/프로젝트 cross-doc query, ACL boundary, version conflict | relevant documents, expected citations, forbidden documents |

각 scenario에는 control과 treatment가 동일한 model, system prompt, token budget을 쓰도록 한다. provider가 더 많은 prompt token을 쓰고 이기는 것은 공정한 개선이 아니다.

## 8. Mem0 단독 성능 PoC

### 8.1 검증 가설

> Mem0가 현재 일반 대화와 회의 후속 대화에서 관련 durable fact를 작은 token 비용으로 회수해, 반복 정정과 context 낭비를 줄인다.

### 8.2 범위

- 일반 대화의 개인/프로젝트 preference와 convention
- 회의 후 승인된 durable decision fact
- 50~100개 일반 대화 scenario, 30~50개 meeting follow-up scenario
- 기존 document RAG retrieval은 control/treatment 모두 동일하게 유지

제외 범위:

- 사내 문서 chunk 대량 저장
- 현재 RAG collection 변경
- 업무 action item의 source of truth 대체
- agent가 shared policy를 자동 write하는 기능

### 8.3 실험

```text
Control
  current conversation state + current RAG only

Treatment
  current conversation state + current RAG
  + Mem0 recall top N (strict tenant/project/status filter)
```

필수 negative scenario:

- tenant A memory가 tenant B request에 0건인지
- project A fact가 project B request에 주입되지 않는지
- 정정/철회된 fact가 다시 active context로 들어오지 않는지
- memory service/Qdrant timeout 시 control 경로로 정상 응답하는지

### 8.4 성공 기준

| 지표 | 기준 |
| --- | --- |
| 반복 정정 | control 대비 동일 preference/convention 재정정 비율 감소 |
| 행동 정확도 | fact를 말로 재현하는 것뿐 아니라 기대 tool/answer default를 실제로 선택 |
| context 효율 | 동일 또는 더 적은 input token에서 control 이상의 task success |
| latency | memory recall의 p95 추가 지연이 제품 SLO 안에 있음 |
| isolation | cross-tenant/project negative test에서 0건 누출 |
| stale recall | superseded/deleted fact의 active prompt 주입 0건 |

### 8.5 Mem0 특유의 gate

1. **로컬 SQLite:** Python OSS core는 remote Qdrant/PostgreSQL 설정에도 history/recent messages에 SQLite를 사용한다. 로컬 persistent data 금지 요구라면 PostgreSQL history adapter/fork 또는 다른 운영 방식을 먼저 설계해야 한다.
2. **한국어 hybrid retrieval:** [#4884](https://github.com/mem0ai/mem0/issues/4884)에 따르면 BM25/entity extraction이 English spaCy에 의존해 한국어에서 semantic-only로 degrade할 수 있다. Korean golden set에서 반드시 비교한다.
3. **V3 add-only:** current fact는 Mem0가 아니라 PostgreSQL state projection으로 판정하고 explicit update/delete/outbox를 적용한다.
4. **권한:** self-hosted auth는 data-plane tenant authorization을 대체하지 않는다. browser가 Mem0 API를 직접 호출하지 않는다.
5. **동시성:** [#6243](https://github.com/mem0ai/mem0/issues/6243)의 entity TOCTOU race 보고가 있으므로 entity linkage를 권위 관계로 쓰지 않고 same-scope write를 serialize한다.

### 8.6 Mem0 선택 규칙

다음이 모두 맞으면 Mem0를 선택한다.

- 현재 주 병목이 반복 설명, preference/convention 누락, 이전 결정 fact 누락이다.
- document RAG hierarchy와 citation 품질은 이미 목표 수준이다.
- Postgres history/authorization adapter를 유지할 비용을 감당할 수 있다.
- 한국어 recall이 baseline 이상이다.

## 9. OpenViking 단독 성능 PoC

### 9.1 검증 가설

> OpenViking의 hierarchy-aware context retrieval이 현재 chunk RAG보다 긴 문서/다문서/과거 session 질의에서 더 정확한 근거를 더 작은 context로 제공한다.

### 9.2 범위

- 사내 지식 corpus 일부와 대표 업로드 문서 100~500개
- 긴 문서, 다문서, hierarchy가 중요한 질문
- 회의 session 일부에서 prior decision evidence retrieval
- single OpenViking server, dedicated MinIO bucket/prefix, dedicated Qdrant collection
- production 답변은 control을 유지하거나 결과 evaluator가 선택한 뒤 feature flag로 제한 노출

제외 범위:

- 현재 RAG collection의 삭제/교체
- 모든 tenant 및 모든 문서의 즉시 migration
- active-active/multi-region HA
- Mem0와 같은 request path에서 함께 recall하는 hybrid

### 9.3 실험

```text
Control: current RAG top-k chunk retrieval

Treatment: OpenViking find/search -> L0/L1 context -> URI-specific read

Shared: same query, model, system prompt, max retrieved tokens,
        authorization fixture, expected citation format
```

agentic retrieval도 별도 측정한다.

```text
Control: top-k chunks를 한 번에 prompt에 주입

Treatment: DeepAgent가 overview를 받고 필요한 URI만 추가 read
```

Treatment가 tool call을 더 쓰더라도 total token/cost/latency와 answer quality가 개선되면 의미가 있다. 반대로 quality가 같고 tool latency만 늘면 채택 근거가 없다.

### 9.4 성공 기준

| 지표 | 기준 |
| --- | --- |
| document retrieval | Recall@k, MRR, citation precision이 control 대비 사전 합의한 개선 또는 최소 동등성 충족 |
| answer quality | faithfulness와 human preference win-rate가 control보다 개선 |
| context efficiency | control 대비 retrieved token/irrelevant context 비율 감소 |
| latency | end-to-end p95와 ingest-to-searchable lag가 서비스 SLO 안에 있음 |
| freshness | create/update/delete 후 stale URI/vector가 정한 시간 안에 정리 |
| ACL | cross-account/user/peer negative query에서 0건 누출 |
| recovery | timeout/restart/Qdrant transient failure 뒤 failed 상태가 관측되고 재처리 가능 |

### 9.5 OpenViking 특유의 gate

1. **QueueFS SQLite:** default persistent queue가 SQLite다. 로컬 persistent data 금지 정책과 multi-instance 운영에서 수용 가능한지 확인한다. Redis를 QueueFS 대체재로 가정하면 안 된다.
2. **요약 실패 복구:** [#3151](https://github.com/volcengine/OpenViking/issues/3151)은 overview failure가 placeholder를 성공처럼 저장하고 retry하지 않는다고 보고한다. document/meeting summary의 quality gate로 넣는다.
3. **재시작/queue:** [#3150](https://github.com/volcengine/OpenViking/issues/3150)은 stale lock 이후 tight requeue loop를 보고한다. restart chaos test가 필요하다.
4. **문서 freshness:** [#3152](https://github.com/volcengine/OpenViking/issues/3152)은 nested resource write 뒤 semantic refresh 누락을 보고한다. update/delete 테스트가 필수다.
5. **tenant mode:** [#3171](https://github.com/volcengine/OpenViking/issues/3171)은 trusted auth에서 peer isolation이 VLM extraction tool을 막는다고 보고한다. Portal gateway auth matrix를 검증한다.
6. **license:** 원본을 수정하지 않은 독립 server로 API 호출하는 형태와, 코드 수정/배포/직접 결합의 의무는 다르다. PoC 전 배포 형태를 확정하고 조직 OSS policy 검토를 받는다.

### 9.6 OpenViking 선택 규칙

다음이 모두 맞으면 OpenViking을 선택한다.

- 현재 주 병목이 긴 문서/다문서 RAG, 높은 token cost, 과거 session/evidence 탐색이다.
- shadow test가 current RAG보다 retrieval quality 또는 context efficiency에서 명확한 이득을 보였다.
- Queue/semantic pipeline의 장애 복구와 freshness가 운영 SLO를 충족한다.
- AGPL과 전용 bucket/collection 운영이 조직 정책상 허용된다.

## 10. 둘을 동시에 가져가지 않는 원칙

현재 조사 단계에서 hybrid는 기본 권장안이 아니다.

두 제품을 한 요청에서 함께 조회하면 다음을 분리하기 어렵다.

- quality가 좋아진 원인이 fact recall인지 hierarchy retrieval인지
- token/latency가 증가한 원인이 어느 provider인지
- 같은 사실을 둘 다 저장해 발생한 stale/duplicate context 문제
- provider 장애 때 fallback과 audit의 책임

따라서 다음 순서를 지킨다.

```text
1. baseline을 측정한다.
2. 가장 큰 병목 하나를 선택한다.
3. 그 병목에 맞는 provider 하나만 shadow PoC한다.
4. control 대비 성능 이득과 운영 gate를 함께 판정한다.
5. 통과하면 그 provider만 제한 rollout한다.
```

Mem0와 OpenViking을 둘 다 사용하는 것은 아래가 모두 증명될 때만 고려할 수 있다.

- Mem0가 fact recall에서 독립적인 개선을 보였다.
- OpenViking이 document/session retrieval에서 독립적인 개선을 보였다.
- 두 retrieval 결과를 합칠 명확한 ranking/token budget policy가 있다.
- 두 provider의 데이터 lifecycle과 장애 대응을 운영할 여력이 있다.

그 전까지는 "두 제품을 모두 쓰면 더 좋다"가 아니라 **관측하기 어려운 복잡도만 늘어난다**고 보는 것이 맞다.

## 11. 현재 정보만으로의 우선순위

현재 기능 구성을 보면 문서 대화, 회의록, 사내 지식 RAG가 일반 대화보다 넓은 context/evidence 문제를 공유한다. 따라서 다음 가설이 가장 높은 정보 가치를 가진다.

> **OpenViking이 현재 RAG보다 긴 문서/다문서/meeting evidence retrieval을 실제로 개선하는가?**

이 질문은 Mem0 PoC로 답할 수 없다. 따라서 현재 RAG의 baseline에서 context bloat, long-document miss, multi-document citation 문제가 확인된다면 **OpenViking 단독 shadow PoC를 먼저** 수행하는 편이 맞다.

반대로 baseline이 다음을 보이면 Mem0가 먼저다.

- RAG citation/quality는 충분하다.
- 사용자는 선호, 프로젝트 규칙, 정정을 자주 반복한다.
- agent가 이전 대화의 durable fact를 잊어 같은 실수를 반복한다.

중요한 점은 현재 정보만으로 어느 병목이 더 큰지 확정할 수 없다는 것이다. provider 선택은 기능 목록이 아니라 7장의 baseline trace와 golden set 결과로 확정한다.

## 12. 최종 의사결정 표

| baseline에서 확인된 사실 | 선택 | 이유 |
| --- | --- | --- |
| RAG가 긴 문서/다문서에서 근거를 자주 놓치고 prompt가 크다 | OpenViking PoC | hierarchy-aware context retrieval의 직접 검증 대상 |
| 과거 회의의 근거와 session 흐름을 찾아야 한다 | OpenViking PoC | Session/Resource/Memory 연결 retrieval을 검증할 수 있음 |
| 사용자의 선호/프로젝트 관례를 자주 잊는다 | Mem0 PoC | fact recall만 작게 추가 가능 |
| action item 최신 상태를 자주 잘못 말한다 | provider 이전에 PostgreSQL state/citation 정비 | memory가 업무 상태 authority가 되어서는 안 됨 |
| document update/delete가 stale result를 만든다 | provider 이전에 현재 ingestion invalidation 분석 | OpenViking은 이 문제를 자동으로 해결한다고 가정할 수 없음 |
| baseline 대비 명확한 개선이 없다 | 아무 provider도 채택하지 않음 | 새 data path/운영 비용을 정당화할 수 없음 |

## 참고 자료

### 기존 심층 조사

- [Mem0 Deep Dive](providers/mem0.md): V3 add-only, Qdrant adapter, SQLite history, self-hosted server, tenant authorization 분석.
- [OpenViking Deep Dive](providers/openviking.md): AGFS/MinIO, Qdrant, URI/L0-L1-L2, QueueFS, multi-tenancy, DeepAgents 결합 분석.

### 공식 문서와 소스

- [DeepAgents Memory](https://docs.langchain.com/oss/python/deepagents/memory): persistent memory files, namespace, shared-memory security.
- [DeepAgents Context Engineering](https://docs.langchain.com/oss/python/deepagents/context-engineering): filesystem-backed context와 token 관리 경계.
- [DeepAgents Subagents](https://docs.langchain.com/oss/python/deepagents/subagents): subagent context isolation.
- [Mem0 OSS V2 to V3 migration](https://docs.mem0.ai/migration/oss-v2-to-v3): V3 add-only extraction과 hybrid/entity migration.
- [Mem0 `Memory` implementation](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/mem0/memory/main.py): V3 pipeline과 SQLite history 생성 경로.
- [Mem0 Qdrant adapter](https://github.com/mem0ai/mem0/blob/17836748d7afe0521516c6a73c6a256680f05527/mem0/vector_stores/qdrant.py): dense/sparse/entity sidecar 구현.
- [OpenViking Qdrant adapter](https://github.com/volcengine/OpenViking/blob/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking/storage/vectordb_adapters/qdrant_adapter.py): 전용 collection과 metadata sidecar.
- [OpenViking memory templates](https://github.com/volcengine/OpenViking/tree/5bfa9b617ecff478f825ca435a35bc4222b30582/openviking/prompts/templates/memory): template 기반 memory 확장.

### PoC 위험 신호로 확인한 GitHub 이슈 (2026-07-12 open 상태 확인)

- Mem0: [#4884 Korean/non-English BM25 and entity extraction](https://github.com/mem0ai/mem0/issues/4884), [#6243 entity TOCTOU race](https://github.com/mem0ai/mem0/issues/6243)
- OpenViking: [#3151 overview failure persisted as success](https://github.com/volcengine/OpenViking/issues/3151), [#3150 restart requeue tight loop](https://github.com/volcengine/OpenViking/issues/3150), [#3152 nested resource refresh](https://github.com/volcengine/OpenViking/issues/3152), [#3171 trusted auth/peer isolation](https://github.com/volcengine/OpenViking/issues/3171)

