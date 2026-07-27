# MemGPT 논문 분석 — 계층형 Context Runtime과 Agent Memory의 경계

작성일: 2026-07-27  
대상: Charles Packer et al., *MemGPT: Towards LLMs as Operating Systems*, arXiv:2310.08560v2 (2024-02-12)  
번역본: [MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md](MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md)  
관련 조사: [Agent Memory / Context Provider 최종 리포트](../agent_memory_provider_final_report.md)

## 1. 한 줄 결론

MemGPT의 핵심은 기억을 fact로 추출하는 알고리즘이 아니라, 제한된 LLM context window를 RAM처럼 취급하고 **working context, 최근 대화 queue, recall storage, archival storage 사이의 읽기·쓰기·paging을 LLM function call과 event loop로 제어하는 runtime**이다.

따라서 Chat Portal에서는 Mem0의 대체 durable memory DB가 아니라, DeepAgents와 같은 agent runtime이 참고할 설계 패턴으로 보는 것이 맞다. source of truth·ACL·문서 citation·memory lifecycle은 여전히 Portal과 기존 저장소의 책임이다.

## 2. 문제 정의와 연구 범위

LLM의 context window는 제한되어 있고, 단순히 window를 키우면 self-attention 비용이 커지며 긴 context의 중간 정보를 잘 활용하지 못할 수 있다. MemGPT는 model 자체의 context를 늘리지 않고도 “더 긴 context가 있는 것 같은” 효과를 내는 **virtual context management**를 제안한다.

운영체제의 virtual memory에 대응시키면 다음과 같다.

| 운영체제 비유 | MemGPT 대응물 | 의미 |
| --- | --- | --- |
| RAM / physical memory | LLM prompt 안의 main context | 현재 추론에서 직접 접근 가능한 token |
| Disk / external memory | recall·archival storage | prompt 밖의 대화 이력·문서 |
| Paging | function call을 통한 검색·삽입·축출 | 필요한 정보만 context에 이동 |
| Interrupt | 사용자 메시지, context pressure, timer event | 다음 LLM 추론을 촉발하는 사건 |

논문은 이 구조를 장기 대화와 문서 분석에서 평가한다. 이는 “무한 기억”을 실현했다는 뜻이 아니라, 유한 context의 LLM이 외부 storage를 반복적으로 탐색하도록 만든 것이다.

## 3. 아키텍처 해부

```text
event (사용자 메시지 / system alert / timer)
        ↓
Queue manager ──→ main context에 최근 상태를 구성
        ↓                         │
LLM processor ── completion ──→ Function executor
        ↑                         │
        └──── function 결과 / 오류 ┘

main context
  ├─ system instructions (read-only)
  ├─ working context (read/write, function으로만 수정)
  └─ FIFO queue (최근 메시지 + 축출 이력의 재귀 요약)

external context
  ├─ recall storage: 전체 메시지 이력 검색
  └─ archival storage: 문서 등 장기 데이터 검색·저장
```

### 3.1 Main context

prompt token은 세 연속 영역으로 나뉜다.

1. **System instructions**: memory tier의 용도, control flow, function schema를 설명하는 read-only 지시문이다.
2. **Working context**: 사용자 선호, agent persona, 현재 목표 같은 핵심 정보를 적는 고정 크기 read/write 텍스트 블록이다. LLM은 일반 답변이 아니라 허용된 function call로만 수정한다.
3. **FIFO queue**: 사용자·agent·system message와 function 입출력의 최근 이력이다. 앞부분이 밀려나면, 축출된 메시지를 요약한 system message가 첫 항목에 남는다.

working context는 장기 memory DB가 아니다. 모델이 당장 알아야 할 작고 편집 가능한 scratchpad/summary에 가깝다.

### 3.2 External context

- **Recall storage**는 들어온 메시지와 생성된 응답을 queue manager가 기록하는 message database다. LLM은 function으로 과거 메시지를 검색해 결과를 FIFO queue 뒤에 넣을 수 있다.
- **Archival storage**는 문서처럼 더 큰 데이터를 두는 계층이다. 논문 문서 QA에서는 PostgreSQL + pgvector + HNSW에 embedding을 사전 적재했다.

이 분리는 “무엇을 영구 저장할 것인가”보다 “지금 context에 무엇을 올릴 것인가”에 초점을 둔다. storage의 데이터 모델·권한·retention은 논문에서 완결적으로 해결하지 않는다.

### 3.3 Queue manager와 function executor

Queue manager는 새 메시지를 FIFO queue에 넣고, 입·출력 메시지를 recall storage에 기록하며, 검색 결과를 다시 queue에 반영한다. Function executor는 LLM completion을 function call로 파싱·검증·실행한다.

함수 실행 결과와 runtime error(예: working context 최대 크기 초과)는 다시 LLM에 들어간다. context capacity가 부족하면 system warning을 줘 LLM이 덜 중요한 내용을 외부 storage로 옮기거나 요약하도록 유도한다.

이것이 MemGPT의 중요한 설계 선택이다. memory retrieval과 편집을 외부 orchestrator가 고정 규칙으로 결정하지 않고, **LLM이 현재 목표와 context pressure를 보고 tool을 호출해 결정**한다.

### 3.4 Event-driven control flow와 function chaining

사용자 메시지 외에도 context warning, 로그인·문서 업로드 같은 system event, 정기 timer가 LLM inference를 촉발할 수 있다. `function chaining`은 여러 검색 결과 페이지를 넘기거나 여러 문서의 정보를 모아야 할 때, user에게 답을 돌려주기 전 LLM이 연속 function call을 하게 한다.

function call에 즉시 processor로 제어를 되돌리는 flag가 있으면 결과를 context에 넣고 다음 추론을 계속한다. flag가 없으면 yield하여 다음 외부 event까지 멈춘다. 이 모델은 단순 chat completion보다 agent loop에 가깝다.

## 4. 실험 결과를 어떻게 읽어야 하는가

### 4.1 장기 대화: Deep Memory Retrieval(DMR)

저자들은 Multi-Session Chat(MSC)을 확장해, 이전 세션에서만 알 수 있는 좁은 정답 범위의 질문을 묻는 DMR task를 만들었다. LLM judge accuracy와 ROUGE-L recall로 평가했다.

| 기반 모델 | 기본 Accuracy / ROUGE-L | + MemGPT Accuracy / ROUGE-L |
| --- | ---: | ---: |
| GPT-3.5 Turbo | 38.7% / 0.394 | 66.9% / 0.629 |
| GPT-4 | 32.1% / 0.296 | 92.5% / 0.814 |
| GPT-4 Turbo | 35.3% / 0.359 | 93.4% / 0.827 |

이 결과는 과거 대화를 검색해 context에 되가져오는 loop가, 고정 context만으로 답하는 baseline보다 이 벤치마크에서 훨씬 낫다는 근거다. 다만 DMR 질문·정답을 별도 LLM으로 생성했고 judge도 LLM이므로, 실제 업무의 citation 정확성·안전성까지 증명하지는 않는다.

### 4.2 Engagement: Conversation opener

다음 세션을 시작할 때 이전 대화에서 얻은 persona 정보를 활용해 자연스러운 opener를 만드는 과제도 평가했다. GPT-3.5/4/4 Turbo 기반 MemGPT가 persona label similarity(SIM-1/3)에서는 human opener보다 높은 점수를 얻었다.

이는 “기억을 검색하면 개인화 문장을 만들 수 있다”는 신호이지만, similarity가 사용자 만족·정확한 personalization·과도한 친밀감 위험을 직접 측정하는 것은 아니다.

### 4.3 문서 분석

다중 문서 QA에서는 baseline과 MemGPT에 같은 retriever를 주고, 문서 수 `K`가 증가할 때 reader 정확도를 비교했다. MemGPT는 archival storage의 vector search로 필요한 문서를 반복적으로 page-in하므로, context 길이를 초과하는 문서 집합에서도 정확도가 크게 떨어지지 않는다는 결과를 보였다.

중첩 key-value 과제에서는 GPT-3.5가 한 단계 nesting에서 0% 정확도로 떨어지고 GPT-4/GPT-4 Turbo도 세 단계에서 0%가 된 반면, MemGPT + GPT-4는 반복 function query로 lookup을 수행해 nesting level 증가에 영향을 받지 않았다고 보고한다.

이 결과는 “문서가 길면 LLM에 더 많이 넣는다”보다 **검색 → 결과 확인 → 다음 검색**의 tool loop가 multi-hop retrieval에 유리할 수 있음을 보인다. 다만 UUID 기반 synthetic KV는 실제 문서의 모호한 의미·ACL·버전 충돌·인용 문제를 대표하지 않는다.

## 5. 강점과 한계

### 강점

- LLM context를 하나의 prompt가 아니라 OS가 관리하는 제한 자원으로 모델링했다.
- working state, 최근 대화, 전체 대화, 문서를 서로 다른 tier로 분리했다.
- context pressure·tool result·timer를 포함한 event loop를 설계해 단일 turn completion의 한계를 넘어섰다.
- 장기 대화와 긴 문서라는 서로 다른 문제에서 같은 paging abstraction을 시험했다.

### 한계와 위험

1. **LLM이 memory controller**: 잘못된 tool 선택, 반복 검색, 불필요한 context overwrite, premature yield가 곧 품질·비용 오류가 된다. 종료 조건·최대 chain 수·token budget·retry policy가 필요하다.
2. **사실 lifecycle의 부재**: working context와 recall storage는 추론 상태를 다루지만, durable fact의 승인·정정·supersession·retention을 해결하지 않는다.
3. **권한은 별도 문제**: LLM이 archival search를 고른다고 해도 ACL filter가 search 전에 강제되지 않으면 유출 경로가 된다. function schema는 authorization boundary가 아니다.
4. **평가의 제한**: DMR/Opener는 저자가 만든 task이고, document/KV 평가는 특정 데이터·retriever·모델에 의존한다. tail latency, tool call 비용, concurrent session, prompt injection, 실제 기업 문서 citation 평가는 중심 평가 대상이 아니다.
5. **요약의 누적 손실**: FIFO에서 밀려난 이력의 recursive summary는 압축 오류를 누적할 수 있다. 원문으로 되돌아가는 retrieval과 summary provenance가 필요하다.
6. **운영체제 비유의 한계**: RAM/disk paging은 데이터 의미가 변하지 않지만, LLM context는 순서·표현·프롬프트 주입에 따라 의미와 행동이 달라진다. 따라서 전통 OS의 page replacement 정책을 그대로 적용할 수 없다.

## 6. Generative Agents·Mem0와의 역할 분리

| 논문 | 주된 문제 | memory 단위 | 누가 선택/갱신하는가 | Chat Portal에서의 위치 |
| --- | --- | --- | --- | --- |
| Generative Agents | 장기적으로 일관된 persona 행동 | observation, reflection, plan | retrieval 점수 + LLM planning | agent 행동 설계 참고 |
| Mem0 | 대화에서 재사용할 durable fact | 압축된 사실·entity/relation | extraction/update LLM + memory store | personal/project fact memory 후보 |
| MemGPT | 유한 prompt에서의 context paging | working state, message, document | LLM tool call + event runtime | runtime/session context 설계 참고 |

세 논문은 모두 “긴 context를 전부 넣지 말라”는 점에서는 만난다. 그러나 저장 책임을 하나로 합치면 안 된다.

- MemGPT working context는 **thread/task의 단기 실행 상태**다.
- Mem0 fact는 **scope와 lifecycle을 가진 장기 재사용 후보**다.
- 문서 원문과 ACL·버전·citation은 **기존 RAG/MinIO/PostgreSQL의 권위 데이터**다.
- Agent의 장기 계획·reflection은 **명시적 evidence와 policy가 있을 때만** durable layer로 승격할 수 있다.

## 7. Chat Portal 적용 판단

### 7.1 가져올 설계 원칙

1. **Context tier를 분리한다.** System policy, thread working state, 최근 대화, durable fact, document evidence를 같은 vector collection이나 prompt 문자열에 섞지 않는다.
2. **수행 중 검색을 허용한다.** 첫 retrieval top-k만 넣고 답하지 말고, agent가 부족함을 인지하면 ACL-filtered search/read를 한정된 budget 안에서 추가 호출할 수 있게 한다.
3. **Event와 runtime 상태를 모델링한다.** 사용자 정정, 문서 버전 변경, tool 실행 실패, 장시간 작업 완료를 state transition으로 다룬다.
4. **원문으로 돌아갈 수 있게 한다.** summary/working context는 cache이며, 중요한 답은 evidence URI와 document version을 통해 원문을 재검증해야 한다.

### 7.2 가져오면 안 되는 것

- LLM이 임의로 PostgreSQL, Qdrant, MinIO 전체를 검색하거나 수정하는 권한
- working context를 user/project의 권위 사실로 영구 저장하는 것
- recursive summary만 남기고 원문 transcript·document reference를 버리는 것
- function call이 성공했다는 사실을 authorization·audit·idempotency 보장으로 간주하는 것

### 7.3 안전한 runtime 경계

```text
DeepAgents 또는 동등 runtime
  ├─ thread-scoped working context / tool budget / max chain
  ├─ Portal retrieval gateway
  │    └─ ACL + tenant + version filter를 search 전에 강제
  ├─ MemoryService
  │    └─ Mem0 fact recall (read) / approval된 write만 허용
  └─ document evidence gateway
       └─ MinIO/PostgreSQL 원문·citation authority
```

LLM은 “어떤 도구를 요청할지”를 제안할 수 있지만, scope 확인, query rewriting 제한, 반환 가능한 최대 데이터, write 승인, 감사 기록은 runtime과 Portal gateway가 강제해야 한다.

## 8. 검증 가능한 PoC

MemGPT 전체를 도입하지 않고, 다음 질문만 shadow PoC로 검증한다.

> 초기 top-k context가 불충분한 다문서 질의에서, 최대 2회의 ACL-filtered 추가 search/read tool loop가 동일 token·latency 예산 안에서 citation faithfulness와 task success를 실제로 개선하는가?

| 군 | 동작 | 측정 목적 |
| --- | --- | --- |
| Control | 현재 단발 retrieval → answer | baseline |
| T1 | 동일 initial retrieval + 최대 1회 추가 read | paging의 최소 효과 |
| T2 | 최대 2회 tool chain + evidence re-check | multi-hop context loop의 효과 |

필수 지표는 answer quality와 citation precision/recall, input/output token, tool call 수, TTFT 및 end-to-end p95, failed/looping tool rate, stale citation, ACL leakage(0)다. T2가 quality 이득 없이 latency·token만 늘리거나 tool loop 오류가 늘면 이 패턴을 확대하지 않는다.

## 9. 최종 판단

MemGPT는 LLM agent runtime이 context를 능동적으로 관리할 수 있다는 중요한 설계 원형이다. 특히 document retrieval과 session state를 정적 prompt assembly가 아니라 event-driven tool loop로 다뤄야 한다는 점은 현재 Agent 시스템에도 유효하다.

그러나 이를 하나의 “memory DB”로 도입하는 것은 잘못된 적용이다. Chat Portal에서는 DeepAgents/runtime 계층의 working state와 controlled retrieval loop에만 원칙을 적용하고, 장기 사실은 Mem0 후보, 문서 지식은 RAG, 권한·버전·감사는 Portal 권위 계층으로 분리하는 것이 적절하다.
