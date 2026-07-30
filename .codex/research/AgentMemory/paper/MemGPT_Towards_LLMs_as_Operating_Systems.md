# MemGPT_Towards_LLMs_as_Operating_Systems- 메모



- 목표
  - 컨텍스트 관리를 어떻게 할 것이냐? >> 가상 컨텍스트 관리
    - 제한된 컨텍스트 창 안에서 확장된 컨텍스트를 사용하는 것이 목표다
    - 즉 필요한 것만 ContextWindow에 올리자. 
  - 가상 메모리 paging 기법에서 차용
- 어떻게 효과적으로 페이지 인 아웃을 시킬 것인가?
- 컨텍스트 관리, 응답 생성, 사용자 상호작용 사이의 제어 흐름을 관리
- 넘친 데이터들은 어떻게 page out할 것인가?
- 두 가지 문제
  - 문서
  - 긴 대화에서의 장기 기억



## MemoryGPT 

### main context

- **system instructions**,
  - AGENTS.md, skills? 에 대한 대한 내용
  - 함수 사용 방법, 검색 방법 등 >> 지침
- **working context**, 
  - 함수 호출로만 쓸 수 있는 고정 크기의 비정형 텍스트 읽기·쓰기 블록
  - 대화 환경에서는 에이전트가 맡은 페르소나와 사용자에 관한 핵심 사실·선호도·중요 정보를 저장해 사용자와 자연스럽게 대화하는 데 쓴다
  - AGENTS.md  > 우리 입장  |  핵심 사실, 사용자 선호, 등
    - 매번 참고해야 하지만 대화 전체를 다시 읽을 필요는 없는 정보
- **FIFO queue**
  - 에이전트와 사용자 사이의 메시지, 시스템 메시지(예: 메모리 경고), 함수 호출의 입력과 출력을 포함하는 메시지의 순환 이력을 저장
  - FIFO queue의 첫 인덱스에는 큐에서 퇴출된 메시지의 재귀적 요약을 담은 시스템 메시지가 들어 있다.
  - 단기 기억

### queue manager (Compact를 어떻게 할것인가?)

- 해당 단기기억 몇개 빼와서 같이 넣어준다 (deepagent : checkpoint)
- 입력 메시지와 생성된 LLM 출력은 모두 recall storage 에 저장한다 (history 저장) >> 이부분은 필수 인거 같아보임
- 퇴출 정책 (Context 넘칠 경우)
  1. Context Window > 70% 
  2. memory pressure 경고 
  3. 중요 정보 > working context or  DB 넣음
- Context Window == 100% 
  - 구체적으로 일정 수의 메시지(예: 컨텍스트 창의 50%)를 퇴출
    - DB에 넣음
  - 기존 재귀 요약과 퇴출된 메시지로 새 재귀 요약을 생성



### function executor

- 메모리 계층과 각 유용성의 상세 설명에 대한 프롬프트
- 시스템이 메모리에 접근하거나 수정하기 위해 호출할 수 있는 함수 시키마와 자연어 설명
  - 각 tool 사용 or SubAgent 를 호출할 때 이런 스키마가 있어야 할 듯하다. + 예시?
  - DeepAgent 에선 Description을 읽어서 구현해놓긴 했지만..

### function chaining 

- lang graph 의 workflow와 비슷하다고 보임
- flag 를 통해서 통제권 제어
  - o : 계속 작업
  - x : 통제권 넘기고 event 발생될 때까지 대기
- event
  - 채팅 애플리케이션의 사용자 메시지,
  - 주 컨텍스트 용량 경고 같은 시스템 메시지
  - 사용자가 로그인했거나 문서 업로드를 마쳤다는 알림
  - 일정 주기로 실행되어 사용자 개입 없이 MemGPT가 동작하게 하는 시간



## Exp

 ## 각 구성요소

  - NaturalQuestions-Open: 실제 질문과 정답으로 구성된 오픈 도메인 QA 데이터
    셋입니다.

  - Wikipedia passage: Wikipedia를 작은 문서 조각으로 나눈 것입니다.
  - 임베딩 + cosine similarity: 질문과 문서 조각을 벡터로 바꾼 후 의미적으로
    가까운 문서를 찾습니다.

  - PostgreSQL + pgvector: 문서 임베딩을 저장하고 벡터 유사도 검색을 수행하
    는 데이터베이스 구성입니다.

  - HNSW: 수많은 벡터 중 가까운 후보를 매우 빠르게 찾는 근사 최근접 이웃 인
    덱스입니다.

  - archival storage: MemGPT의 장기 외부 저장소입니다. 여기서는 Wikipedia 문
    서와 임베딩이 들어 있습니다.

  - LLM judge: 답 자체뿐 아니라 답을 뒷받침하는 검색 문서를 제시했는지도 LLM
    으로 판정합니다. “노벨상은 모델이 원래 아는 정보니까” 우연히 맞힌 답을
    줄이려는 장치예요.

왜 고정 컨텍스트 baseline에는 상한이 생기나?

  baseline도 검색을 잘하면 답할 수 있습니다. 하지만 컨텍스트 창이 8k token이
  고 문서 하나가 길다면, 문서를 많이 넣을 수 없습니다.

  ## truncation이 왜 성능을 낮추나?

  문서 수를 늘리면 정답 문서를 포함할 확률은 높아집니다. 하지만 LLM 컨텍스트
  창은 고정입니다.

  예를 들어 8,000 token 창에 문서 8개를 넣을 때와 80개를 넣을 때를 비교하면:

  - 8개: 문서당 약 1,000 token을 줄 수 있다.
  - 80개: 문서당 약 100 token만 줄 수 있다.

  80개를 넣으려면 문서를 심하게 잘라야 하고, 정답이 든 문장이 잘려 나갈 수
  있습니다. 그래서 baseline은 “더 많은 문서를 넣어 정답 문서를 찾을 가능
  성”과 “각 문서의 내용을 충분히 보존할 가능성” 사이에서 트레이드오프가 생깁
  니다.

  MemGPT는 문서 80개를 한 번에 프롬프트에 밀어 넣지 않습니다. 현재 필요해 보
  이는 소수 결과를 보고, 부족하면 다음 검색을 호출합니다. 이것이 논문이 말하
  는 가상 메모리식 접근입니다.

  ## MemGPT도 실패하는 이유

  논문도 MemGPT가 완벽하지 않다고 밝힙니다.

  - LLM이 첫 페이지를 보고 너무 빨리 “답을 찾았다”고 판단할 수 있다.
  - 다음 페이지를 끝까지 넘기지 않고 검색을 멈출 수 있다.
  - 약한 모델은 함수 호출과 반복 검색을 잘 수행하지 못한다.
  - 그래서 GPT-3.5 기반 MemGPT는 성능이 크게 떨어지고, GPT-4 기반 MemGPT가
    가장 좋았습니다.

  한 문장으로 정리하면, MemGPT의 이점은 검색 정확도를 직접 높이는 것이 아니
  라, 작은 컨텍스트 창 안에서도 LLM이 외부 문서를 여러 차례 탐색하도록 만들
  어 검색 결과의 더 넓은 범위를 활용하게 하는 것입니다.



  ## 먼저, 일반 KV 검색

  일반 key-value 검색은 딕셔너리 조회와 같습니다.

  key:   A
  value: B

  질문이 “A의 값은?”이면 답은 B예요. 한 번 찾으면 끝입니다.

  ## nested KV 검색

  nested KV에서는 value가 최종값이 아니라, 다음 key일 수 있습니다.

  A → B
  B → C
  C → "최종 답"

  따라서 A를 받으면 해야 할 일은 다음과 같아요.

  1. A 조회 → B
  2. B도 key인지 확인
  3. B 조회 → C
  4. C도 key인지 확인
  5. C 조회 → "최종 답"
  6. "최종 답"은 key가 아님을 확인하고 반환

  중요한 점은 A의 값 B를 찾았다고 바로 답하면 안 된다는 것입니다. B는 아직
  중간 경유지일 수 있으니까요.

  논문의 예시도 같은 구조입니다.

  831...ea5 → 5b8...4c3 → f37...617

  - 831...ea5를 조회하면 5b8...4c3을 얻음
  - 그런데 5b8...4c3도 key이므로 다시 조회
  - 결과 f37...617을 얻음
  - f37...617은 더 이상 key가 아님을 확인
  - 최종 답: f37...617

  ## nesting level의 의미

   Nesting level    구조                          필요한 행동
  ━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━
               0    A → 최종값                    1회 조회 후 답변
  ───────────────  ────────────────────────────  ──────────────────────────
               1    A → B → 최종값                A, B를 순서대로 조회
  ───────────────  ────────────────────────────  ──────────────────────────
               2    A → B → C → 최종값            세 단계 연결을 따라감
  ───────────────  ────────────────────────────  ──────────────────────────
               4    A → B → C → D → E → 최종값    여러 번의 연속 조회 필요

  이 실험은 UUID를 씁니다. UUID는 의미 있는 단어가 아니라 무작위 문자열이라,
  모델이 상식이나 언어 의미로 추측할 수 없게 합니다. 오직 정확한 조회 결과를
  따라가야 해요.

  ## 왜 일반 GPT도 어려웠나?

  여기서 중요한 설계가 하나 있습니다. key-value 쌍 140개 전체는 약 8k token
  으로, GPT-4 baseline의 컨텍스트 창에 들어가도록 만들었습니다.

  즉 baseline의 실패는 단순히 “문서를 못 담아서”가 아닙니다. 모든 JSON 데이
  터를 이미 봤는데도 다음처럼 행동하기 쉽습니다.

  A를 찾음 → B를 발견함 → “답은 B”라고 성급하게 종료

  또는 중간 key를 따라가다가 몇 단계 뒤 멈추거나, 비슷한 UUID를 혼동합니다.
  GPT-3.5가 nesting level 1에서 바로 0%가 된 주된 이유가 바로 최초 value를
  최종 답으로 반환했기 때문입니다.

  ## MemGPT가 유리한 이유

  MemGPT는 함수 호출과 request_heartbeat=true 같은 chaining을 이용해 작업을
  단계로 쪼갭니다.

  search(A) → B
  search(B) → C
  search(C) → 최종값
  최종값이 key인지 검사
  → 사용자에게 최종값 반환

  각 함수 결과가 다시 현재 컨텍스트에 들어오므로, 에이전트는 “아직 다음 조회
  가 필요한가?”를 매 단계 판단할 수 있습니다. 그래서 이 실험은 MemGPT의 핵심
  인 반복적 검색 + 함수 chaining + 제어 흐름 유지를 잘 보여 줍니다.

  ## 결과를 어떻게 읽으면 되나?

  - GPT-3.5 / GPT-4 baseline: 자료 전체를 봐도 여러 단계의 정확한 lookup을
    끝까지 이어 가는 데 실패

  - GPT-4 기반 MemGPT: 필요한 만큼 함수 호출을 반복해 nesting level이 커져도
    안정적

  - GPT-3.5·GPT-4 Turbo 기반 MemGPT: baseline보다는 좋지만, 어느 시점에 충분
    히 검색하지 않고 멈춰 성능 하락

  즉 이 결과는 “더 강한 LLM이면 항상 더 나은 agent”라는 뜻은 아닙니다. 도구
  를 여러 번 호출하고, 중간 결과를 읽고, 종료 조건을 확인하는 제어 능력이 중
  요하다는 뜻이에요.







### 1. 문제 정의

LLM은 한 번에 볼 수 있는 context가 제한되어 있어, 긴 대화나 긴 문서를 계속 다루기 어렵다. 하지만 단순히 context window 크기를 키우는 게 정답은 아니다.

1. **확장이 비싸다** : Transformer self-attention의 비용이 context 길이에 대해 quadratic.

   quadratic"은 2026년에도 맞고, 다만 "이걸 깨려는 subquadratic 흐름이 본격화"됐다
    ( Mamba/SSM(linear O(n)), linear attention, sparse/subquadratic attention)

2. **늘려도 잘 못 쓴다**  : 긴 context를 줘도 모델이 중간 정보를 활용하지 못함 (Liu et al. 2023, *Lost in the Middle*).

2025~2026 벤치마크(RULER, NoLiMa, ∞Bench)에서 재확인됨: 최신 모델도 긴 context에서 성능이 저하되고, 중간 정보 활용이 약함 (정답을 중간에 두면 정확도가 ~20%p 떨어짐)

### 2. 핵심 아이디어

OS의 계층적 메모리(hierarchical memory)와 paging 아이디어를 빌려 **virtual context**를 관리한다.

<aside>
 💡

프로그램이 쓰는 메모리는 RAM보다 크니까, OS는 **지금 필요한 부분만 RAM에 올려두고** 나머지는 디스크.

</aside>

- LLM = "프로세서"
- context window = "물리 메모리"
- 외부 DB = "디스크"
- function call = 메모리를 직접 page in/out 하는 명령

LLM이 function call로 **자기 메모리를 스스로 관리**(self-editing memory)하는 것이 핵심.





External context

| **Recall Storage**   | 대화 메시지의 *전체 기록*. FIFO queue가 넘칠 때 evict된 메시지를 보관 → 이후 function으로 재검색 |
| -------------------- | ------------------------------------------------------------ |
| **Archival Storage** | 임의 길이 텍스트 지식/메모리 DB. function으로 read/write     |







Retrievel

- MemGPT가 필요하다고 판단하면 function call로 out-of-context 데이터를 검색해 현재 context window로 가져온다. 한번에 안 되면, function chaining으로 여러 번 검색한다. 
- 

### 3. Function chaining (`request_heartbeat=true`)

보통 LLM은 한 번 행동하면 멈추고 다음 사용자 입력을 대기한다.

`request_heartbeat`는 모든 tool에 자동 주입된 인자(default false)로,

**LLM이 function call 출력에 직접** `request_heartbeat=**true`를 넣으면,** 사용자를 기다리지 않고 후속 inference가 이어진다.

**실제 구현 (** MemGPT에서 LLM의 모든 행동은 **tool call!** 사용자에게 말하는 것조차 `send_message`라는 tool call! 그래서 "검색"이라는 tool call은 **아직 사용자에게 답한 게 아니야! )**

- OS interrupt가 아니라 `while True`루프 — heartbeat가 걸리면 heartbeat 메시지를 다음 입력으로 넣고 `continue`해 inner_step을 다시 실행.
- **함수 실패·메모리 경고 시에도** 같은 chaining이 자동 발생하며, `max_chaining_steps`로 폭주를 막는다. (interrupt는 논문의 비유)



## 5. Contribution & Limitation

### Contribution (핵심 기여)

- LLM을 프로세서, context window를 메모리로 보는 **OS-inspired 추상화** 제시.
- LLM이 function call로 **자기 메모리를 스스로 편집**하는 self-editing memory 구조.
- 코드/데이터 공개 → 이후 **Letta** 프로젝트로 발전.

### Limitation (한계)

- **Function-calling 성능에 전적으로 의존.** 모델이 메모리 관리 함수를 잘못/안 호출하면 깨짐.
- 메모리 이동·요약마다 추가 LLM 호출 발생 → **latency · token cost 증가**.
- **Recursive summary는 lossy.** evict 원문이 archival에 남아도 summary 단계에서 손실/왜곡 가능.
- 검색 품질이 retrieval(임베딩/쿼리) 성능에 좌우, 메모리가 있어도 못 찾으면 의미가 없음
