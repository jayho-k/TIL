# MemGPT: LLM을 운영체제처럼 다루기

> 원문: Charles Packer 외, *MemGPT: Towards LLMs as Operating Systems*, arXiv:2310.08560v2 (2024-02-12).
>
> 이 문서는 원문 PDF를 단락·그림·표·부록 단위로 대조해 다시 작성한 학습용 한국어 전체 번역이다. 코드, 함수명, 변수명, 모델명, 데이터셋명, 인용 표기는 원문 표기를 유지했다. 해석과 비평은 별도 분석 노트에서 다룬다.

## 저자

Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez

## 초록

대규모 언어 모델(LLM)은 AI에 혁신을 가져왔지만, 제한된 컨텍스트 창 때문에 긴 대화와 문서 분석 같은 작업에서 활용성이 떨어진다. 제한된 컨텍스트 창을 넘어 컨텍스트를 사용할 수 있게 하기 위해, 저자들은 전통 운영체제의 계층형 메모리 시스템에서 영감을 받은 **가상 컨텍스트 관리(virtual context management)** 를 제안한다. 전통 운영체제는 물리 메모리와 디스크 사이의 페이징으로 확장된 가상 메모리라는 환상을 제공한다.

이 기법을 바탕으로, 저자들은 서로 다른 저장 계층을 지능적으로 관리하여 LLM의 제한된 컨텍스트 창 안에서 확장된 컨텍스트를 효과적으로 제공하는 시스템인 **MemGPT(MemoryGPT)** 를 소개한다. 저자들은 현대 LLM의 제한된 컨텍스트 창이 성능을 크게 제약하는 두 영역, 즉 기반 LLM의 컨텍스트 창을 훨씬 초과하는 대형 문서를 분석하는 문서 분석과 사용자와의 장기 상호작용을 통해 기억·성찰·변화하는 대화 에이전트가 필요한 다중 세션 대화에서 OS 영감 설계를 평가한다. 실험에 사용한 MemGPT 코드와 데이터는 https://research.memgpt.ai 에 공개한다.

## 1. 서론

최근 몇 년 사이 LLM과 그 기반인 Transformer 아키텍처(Vaswani et al., 2017; Devlin et al., 2018; Brown et al., 2020; Ouyang et al., 2022)는 대화형 AI의 초석이 되었으며, 폭넓은 소비자·기업용 애플리케이션을 낳았다. 그러나 LLM이 사용하는 고정 길이 컨텍스트 창은 긴 대화나 긴 문서에 대한 추론을 크게 제약한다. 가장 널리 쓰이는 오픈소스 LLM도 최대 입력 길이를 넘기기 전까지는 수십 차례의 대화 왕복이나 짧은 문서만 처리할 수 있다(Touvron et al., 2023).

Transformer의 컨텍스트 길이를 직접 늘리면 self-attention 때문에 계산 시간과 메모리 비용이 이차적으로 증가한다. 따라서 새로운 장문 컨텍스트 아키텍처 설계는 시급한 연구 과제다(Dai et al., 2019; Kitaev et al., 2020; Beltagy et al., 2020). 더 긴 모델의 개발은 활발히 연구되고 있지만(Dong et al., 2023), 컨텍스트 확장의 계산 문제를 해결하더라도 장문 컨텍스트 모델은 추가 컨텍스트를 효과적으로 활용하기 어렵다는 결과가 보고되었다(Liu et al., 2023a). 최첨단 LLM 학습에 드는 큰 자원과 컨텍스트 확장의 체감 수익을 고려하면, 장문 컨텍스트를 지원할 다른 기법이 필요하다.

본 논문은 고정 컨텍스트 모델을 계속 사용하면서 무한한 컨텍스트라는 환상을 어떻게 제공할지 연구한다. 접근법은 메인 메모리와 디스크 사이에서 데이터를 페이징하여, 가용 메모리를 훨씬 넘는 데이터셋에서도 애플리케이션이 동작하게 한 가상 메모리 개념에서 출발한다. 저자들은 LLM 에이전트의 함수 호출 능력 발전(Schick et al., 2023; Liu et al., 2023b)을 활용하여 가상 컨텍스트 관리를 위한 OS 영감 LLM 시스템 MemGPT를 설계한다. 함수 호출로 LLM 에이전트는 외부 데이터 원본을 읽고 쓸 수 있고, 자신의 컨텍스트를 수정할 수 있으며, 언제 사용자에게 응답을 반환할지도 선택할 수 있다.

이 능력으로 LLM은 운영체제의 ‘메인 메모리’에 해당하는 컨텍스트 창과 외부 저장소 사이에서 정보를 효과적으로 페이지 인·아웃할 수 있다. 또한 함수 호출로 컨텍스트 관리, 응답 생성, 사용자 상호작용 사이의 제어 흐름을 관리할 수 있다. 따라서 에이전트는 한 작업에 대해 자신의 컨텍스트 내용을 반복해서 수정하며 제한된 컨텍스트를 더 효과적으로 활용한다.

MemGPT는 컨텍스트 창을 제약된 메모리 자원으로 보고, 전통 운영체제의 메모리 계층(Patterson et al., 1988)에 대응하는 LLM 메모리 계층을 설계한다. 전통 운영체제의 애플리케이션은 물리 메모리에 실제로 존재하는 양보다 더 많은 메모리 자원이 있는 것처럼 보이게 하는 가상 메모리와 상호작용한다. 운영체제는 넘친 데이터를 디스크로 페이지 아웃하고, 애플리케이션이 접근할 때 페이지 폴트를 통해 다시 메모리로 가져온다. 이와 비슷하게 더 긴 컨텍스트 길이라는 환상을 제공하기 위해, MemGPT라는 ‘LLM OS’를 통해 LLM이 자신의 컨텍스트(물리 메모리에 해당)에 무엇을 둘지 관리하게 한다. MemGPT는 현재 컨텍스트에 없는 관련 과거 데이터를 검색하게 하고, 관련성이 낮은 데이터는 컨텍스트에서 외부 저장 시스템으로 내보내게 한다.

> 그림 1. MemGPT(왼쪽)는 제한된 컨텍스트 공간에 관한 시스템 경고를 받은 뒤 데이터를 영구 메모리에 기록한다. 예시에서는 `working_context.append("Birthday is February 7")` 및 `working_context.append("Boyfriend named James")`를 호출한다.
>
> 그림 2. MemGPT(왼쪽)는 컨텍스트 밖 데이터를 검색해 관련 정보를 현재 컨텍스트 창으로 가져올 수 있다. 예시에서는 `recall_storage.search("six flags")`가 과거 대화 검색 결과를 돌려준다.

메모리 계층, OS 기능, 이벤트 기반 제어 흐름을 함께 사용하면 MemGPT는 유한 컨텍스트 창을 가진 LLM으로도 제한 없는 컨텍스트를 다룰 수 있다. 저자들은 이 OS 영감 LLM 시스템의 효용을 두 영역에서 평가한다. 첫째, 일반 텍스트 파일 길이가 현대 LLM의 입력 용량을 쉽게 넘는 문서 분석이다. 둘째, 제한된 대화 창에 묶인 LLM이 긴 대화에서 컨텍스트 인식, 페르소나 일관성, 장기 기억을 잃는 대화 에이전트다. 두 환경 모두에서 MemGPT는 유한 컨텍스트의 한계를 넘어서 기존 LLM 기반 접근법보다 좋은 성능을 보인다.

## 2. MemGPT (MemoryGPT)

MemGPT의 OS 영감 다계층 메모리 아키텍처는 두 기본 메모리 유형을 구분한다. **주 컨텍스트(main context)** 는 메인 메모리·물리 메모리·RAM에 대응하고, **외부 컨텍스트(external context)** 는 디스크 메모리·디스크 저장소에 대응한다. 주 컨텍스트는 LLM 프롬프트 토큰으로 구성되며, 주 컨텍스트 안의 모든 것은 in-context로 간주되어 추론 중 LLM 프로세서가 접근할 수 있다. 외부 컨텍스트는 LLM의 고정 컨텍스트 창 밖에 보관된 모든 정보다. 이 out-of-context 데이터는 추론 중 LLM 프로세서에 전달되려면 반드시 명시적으로 주 컨텍스트로 이동해야 한다. MemGPT는 LLM 프로세서가 사용자 개입 없이 자신의 메모리를 관리하게 하는 함수 호출을 제공한다.

> 그림 3. MemGPT에서는 고정 컨텍스트 LLM 프로세서에 계층형 메모리 시스템과 자체 메모리 관리용 함수가 추가된다. LLM의 프롬프트 토큰(입력), 즉 주 컨텍스트는 시스템 지시문·작업 컨텍스트·FIFO 큐로 구성된다. LLM의 completion token(출력)은 function executor가 함수 호출로 해석한다. MemGPT는 함수로 주 컨텍스트와 외부 컨텍스트(archival storage·recall storage 데이터베이스) 사이에서 데이터를 옮긴다. LLM은 출력에 특수 키워드 인자 `request_heartbeat=true`를 넣어 즉시 후속 추론을 요청할 수 있다. 이 function chaining이 사용자 질의에 답하기 위한 다단계 검색을 가능하게 한다.

### 2.1 주 컨텍스트(prompt token)

MemGPT의 프롬프트 토큰은 연속된 세 영역, 즉 **system instructions**, **working context**, **FIFO queue**로 나뉜다. system instructions는 읽기 전용의 정적 영역으로 MemGPT 제어 흐름, 서로 다른 메모리 계층의 의도된 용도, MemGPT 함수 사용법(예: 컨텍스트 밖 데이터를 검색하는 방법)을 담는다.

working context는 MemGPT 함수 호출로만 쓸 수 있는 고정 크기의 비정형 텍스트 읽기·쓰기 블록이다. 대화 환경에서는 에이전트가 맡은 페르소나와 사용자에 관한 핵심 사실·선호도·중요 정보를 저장해 사용자와 자연스럽게 대화하는 데 쓴다. FIFO queue는 에이전트와 사용자 사이의 메시지, 시스템 메시지(예: 메모리 경고), 함수 호출의 입력과 출력을 포함하는 메시지의 순환 이력을 저장한다. FIFO queue의 첫 인덱스에는 큐에서 퇴출된 메시지의 재귀적 요약을 담은 시스템 메시지가 들어 있다.

### 2.2 Queue Manager

queue manager는 recall storage와 FIFO queue의 메시지를 관리한다. 새 메시지가 시스템에 도착하면 queue manager는 입력 메시지를 FIFO queue에 추가하고 프롬프트 토큰을 연결한 뒤 LLM 추론을 실행하여 LLM 출력(completion token)을 생성한다. 입력 메시지와 생성된 LLM 출력은 모두 recall storage, 즉 MemGPT 메시지 데이터베이스에 기록한다. MemGPT 함수 호출로 recall storage의 메시지를 검색하면, queue manager가 그것을 큐의 뒤에 추가해 LLM 컨텍스트 창에 다시 넣는다.

queue manager는 큐 퇴출 정책으로 컨텍스트 넘침도 통제한다. 프롬프트 토큰이 기반 LLM 컨텍스트 창의 **warning token count**(예: 컨텍스트 창의 70%)를 넘으면, LLM이 임박한 큐 퇴출을 알도록 시스템 메시지, 즉 **memory pressure** 경고를 넣는다. 그러면 LLM은 MemGPT 함수로 FIFO queue에 든 중요 정보를 working context 또는 archival storage(임의 길이 텍스트 객체를 저장하는 읽기·쓰기 데이터베이스)에 저장할 수 있다.

프롬프트 토큰이 **flush token count**(예: 컨텍스트 창의 100%)를 넘으면 queue manager는 컨텍스트 창의 공간을 확보하기 위해 큐를 flush한다. 구체적으로 일정 수의 메시지(예: 컨텍스트 창의 50%)를 퇴출하고, 기존 재귀 요약과 퇴출된 메시지로 새 재귀 요약을 생성한다. flush 뒤 퇴출된 메시지는 더 이상 in-context가 아니어서 LLM이 즉시 볼 수 없지만, recall storage에는 무기한 보존되며 MemGPT 함수 호출로 읽을 수 있다.

### 2.3 Function executor(completion token 처리)

MemGPT는 LLM 프로세서가 생성한 함수 호출로 주 컨텍스트와 외부 컨텍스트 사이의 데이터 이동을 조율한다. 메모리 편집과 검색은 완전히 자기 주도적이다. MemGPT는 현재 컨텍스트에 따라 스스로 메모리를 갱신하고 검색한다. 예를 들어 대화 이력이 너무 길어질 때(그림 1) 컨텍스트 사이에서 항목을 옮길 시점을 결정할 수 있고, 현재 목표와 책임에 관한 변화하는 이해를 더 잘 반영하도록 주 컨텍스트를 수정할 수 있다(그림 3).

저자들은 시스템 지시문 안에 LLM이 MemGPT 메모리 시스템과 상호작용하도록 안내하는 명시적 지시를 제공함으로써 자기 주도 편집과 검색을 구현한다. 이 지시는 두 부분으로 이뤄진다. 첫째, 메모리 계층과 각 유용성의 상세 설명이다. 둘째, 시스템이 메모리에 접근하거나 수정하기 위해 호출할 수 있는 함수 스키마와 자연어 설명이다.

각 추론 주기에서 LLM 프로세서는 하나의 문자열로 연결된 주 컨텍스트를 입력으로 받아 출력 문자열을 생성한다. MemGPT는 이 출력 문자열을 파싱해 올바름을 확인하고, 파서가 함수 인자를 검증하면 함수를 실행한다. 주 컨텍스트가 이미 최대 용량인데 항목을 추가하려는 경우처럼 실행 중 생긴 오류를 포함한 결과는 MemGPT가 프로세서에 다시 전달한다. 이 피드백 루프는 시스템이 자기 행동에서 배우고 그에 맞게 행동을 조정하게 한다. 토큰 제한을 인식하는 일은 자기 편집이 효과적으로 작동하기 위한 핵심이며, MemGPT는 메모리 관리 결정을 안내하도록 토큰 제한 경고를 프로세서에 제시한다. 또한 검색 호출이 컨텍스트 창을 넘치게 하지 않도록 메모리 검색 메커니즘은 이런 토큰 제약을 인식하며 페이지네이션을 구현한다.

> 표 1. 자주 사용되는 모델과 LLM API의 컨텍스트 길이 비교(자료 수집: 2024년 1월). `*`는 1k token의 preprompt와 약 50 token(약 250자)의 평균 메시지 크기를 가정한 근사 메시지 수다. Open은 API 뒤에서만 제공되는 모델과 달리 오픈소스 또는 open-weight 모델임을 뜻한다.
>
> | 모델 / API | Open? | Context window | Tokens | 메시지 수* |
> | --- | --- | ---: | ---: | ---: |
> | Llama (1) | ✓ | 2k | 2,048 | 20 |
> | Llama 2 | ✓ | 4k | 4,096 | 60 |
> | GPT-3.5 Turbo (release) | ✗ | 4k | 4,096 | 60 |
> | Mistral 7B | ✓ | 8k | 8,192 | 140 |
> | GPT-4 (release) | ✗ | 8k | 8,192 | 140 |
> | GPT-3.5 Turbo | ✗ | 16k | 16,385 | 300 |
> | GPT-4 | ✗ | 32k | 32,768 | 600 |
> | Claude 2 | ✗ | 100k | 100,000 | 2,000 |
> | GPT-4 Turbo | ✗ | 128k | 128,000 | 2,600 |
> | Yi-34B-200k | ✓ | 200k | 200,000 | 4,000 |

### 2.4 제어 흐름과 function chaining

MemGPT에서는 이벤트가 LLM 추론을 촉발한다. 이벤트는 MemGPT에 대한 일반화된 입력으로, 채팅 애플리케이션의 사용자 메시지, 주 컨텍스트 용량 경고 같은 시스템 메시지, 사용자가 로그인했거나 문서 업로드를 마쳤다는 알림 같은 사용자 상호작용, 일정 주기로 실행되어 사용자 개입 없이 MemGPT가 동작하게 하는 시간 기반 이벤트가 될 수 있다. MemGPT는 이벤트를 파서로 처리하여 주 컨텍스트에 추가할 수 있고 결국 LLM 프로세서 입력으로 전달할 일반 텍스트 메시지로 바꾼다.

실용적인 많은 작업은 하나의 질의에서 여러 결과 페이지를 탐색하거나, 서로 다른 질의에서 얻은 여러 문서의 데이터를 주 컨텍스트에 모으는 것처럼 여러 함수를 순서대로 호출해야 한다. function chaining은 MemGPT가 사용자에게 제어권을 돌려주기 전에 여러 함수 호출을 순차 실행하게 한다. MemGPT에서 함수는 요청한 함수가 실행을 마친 직후 제어권을 프로세서에 되돌려 달라는 특수 플래그와 함께 호출할 수 있다. 이 플래그가 있으면 MemGPT는 함수 출력을 주 컨텍스트에 추가하고 프로세서 실행을 멈추지 않는다. 플래그가 없으면(yield) MemGPT는 다음 외부 이벤트 트리거(예: 사용자 메시지 또는 예약된 인터럽트)가 생길 때까지 LLM 프로세서를 실행하지 않는다.

## 3. 실험

저자들은 대화 에이전트와 문서 분석이라는 두 장문 컨텍스트 영역에서 MemGPT를 평가한다. 대화 에이전트에서는 기존 Multi-Session Chat 데이터셋(Xu et al., 2021)을 확장하고, 에이전트가 긴 대화에 걸쳐 지식을 보존하는 능력을 평가하는 두 새 대화 과제를 제안한다. 문서 분석에서는 긴 문서에 대한 질의응답과 key-value 검색을 위해 Liu et al. (2023a)의 기존 과제에서 MemGPT를 벤치마크한다. 또한 여러 데이터 원본의 정보를 모으는 에이전트 능력, 즉 multi-hop retrieval을 시험하는 새 중첩 key-value 검색 과제를 제안한다. 확장 MSC 데이터셋, nested KV retrieval 데이터셋, 2천만 개 Wikipedia 문서 임베딩 데이터셋을 공개한다. 벤치마크 코드는 https://research.memgpt.ai 에 있다.

**구현 세부사항.** 별도 언급이 없을 때 `GPT-4 Turbo`는 컨텍스트 창 128,000의 `gpt-4-1106-preview` 엔드포인트, `GPT-4`는 컨텍스트 창 8,192의 `gpt-4-0613`, `GPT-3.5 Turbo`는 컨텍스트 창 16,385의 `gpt-3.5-turbo-1106`을 뜻한다. 실험에서는 기반 모델 성능이 MemGPT에 미치는 영향을 보이기 위해 모든 baseline 모델(GPT-4, GPT-4 Turbo, GPT-3.5)과 함께 MemGPT를 실행한다.

> 그림 4. MemGPT(왼쪽)가 저장된 정보를 갱신하는 대화 일부의 예. 이 정보는 prompt token 내부의 working context memory에 저장된다. 사용자가 `actually james and i broke up`이라고 말하면 에이전트는 `working_context.replace("Boyfriend named James", "Ex-boyfriend named James")`를 호출한다.

### 3.1 대화형 에이전트를 위한 MemGPT

가상 동반자와 개인화 비서 같은 대화 에이전트는 수주·수개월·수년에 걸칠 수 있는 자연스러운 장기 상호작용으로 사용자를 참여시키려 한다. 이는 제한된 대화 이력만 참조할 수 있는 고정 길이 컨텍스트 모델에 어려움을 준다. ‘무한 컨텍스트’ 에이전트는 경계나 재설정 없이 연속적 교환을 매끄럽게 처리해야 한다. 사용자와 대화할 때 에이전트는 두 기준을 만족해야 한다. 첫째, **일관성(consistency)**: 언급되는 새 사실·선호도·사건은 사용자와 에이전트가 이전에 말한 내용과 맞아야 한다. 둘째, **참여도(engagement)**: 사용자에 관한 장기 지식을 이용해 응답을 개인화해야 한다. 과거 대화를 참조하면 대화는 더 자연스럽고 흥미로워진다.

따라서 저자들은 MemGPT가 메모리를 이용해 대화 일관성을 높이는지, 과거 상호작용의 관련 사실·선호도·사건을 기억해 일관성을 유지하는지 평가한다. 또 메모리를 이용해 더 참여도 높은 대화를 만드는지, 장거리 사용자 정보를 자발적으로 메시지 개인화에 반영하는지도 평가한다. 일관성과 참여도를 평가하면 MemGPT가 고정 컨텍스트 baseline보다 장기 대화의 어려움을 얼마나 잘 다루는지 판단할 수 있다.

**데이터셋.** MemGPT와 고정 컨텍스트 baseline은 Xu et al. (2021)이 도입한 Multi-Session Chat(MSC) 데이터셋에서 평가한다. 이 데이터셋은 모든 세션 동안 일관된 페르소나를 연기하도록 요청받은 인간 라벨러가 생성한 다중 세션 채팅 로그를 담는다. MSC의 각 다중 세션 채팅은 총 다섯 세션이며, 각 세션은 약 12개 메시지로 구성된다. 일관성 실험을 위해 저자들은 같은 두 페르소나 사이의 질의응답 한 쌍만 들어 있는 새 세션(session 6)을 만들었다.

#### 3.1.1 심층 기억 검색 과제(일관성)

저자들은 대화 에이전트의 일관성을 시험하도록 설계한 MSC 기반 **deep memory retrieval(DMR)** 과제를 새로 도입한다. DMR에서 에이전트는 과거 대화를 명시적으로 가리키고 기대 답 범위가 매우 좁은 질문을 사용자에게 받는다. 별도의 LLM에 과거 세션에서 얻은 지식으로만 올바르게 답할 수 있는 한 사용자의 다른 사용자에 대한 질문을 만들도록 지시해 DMR 질의응답 쌍을 생성했다(세부사항은 부록 참조).

생성 응답의 품질은 ROUGE-L 점수(Lin, 2004)와 생성 응답이 gold 응답과 일관되는지 판정하도록 지시받은 LLM judge로 평가한다. GPT-4는 인간 평가자와 높은 일치도를 보인 것으로 알려졌다(Zheng et al., 2023). MemGPT와 baseline 모두의 생성 응답은 일반적으로 gold 응답보다 장황했으므로, 비교적 짧은 gold 답 라벨에 비해 생성 에이전트 응답의 장황함을 고려하기 위해 ROUGE-L recall(R)을 쓴다.

> 표 2. DMR 성능. 이 과제에서 에이전트는 이전 대화(session 1~5)에서 논의한 주제에 관한 구체적 질문을 받으며, 응답은 gold answer와 비교해 채점한다. MemGPT는 고정 컨텍스트 baseline보다 유의하게 좋다.
>
> | 모델 | Accuracy | ROUGE-L (R) |
> | --- | ---: | ---: |
> | GPT-3.5 Turbo | 38.7% | 0.394 |
> | + MemGPT | 66.9% | 0.629 |
> | GPT-4 | 32.1% | 0.296 |
> | + MemGPT | 92.5% | 0.814 |
> | GPT-4 Turbo | 35.3% | 0.359 |
> | + MemGPT | 93.4% | 0.827 |

**MemGPT는 메모리로 일관성을 유지한다.** 표 2는 MemGPT와 고정 메모리 baseline의 성능을 보여 준다. 저자들은 서로 다른 기반 LLM을 쓰는 MemGPT를 비교하고, MemGPT를 사용하지 않는 기반 LLM을 baseline으로 둔다. baseline은 확장된 재귀 요약 절차를 흉내 내도록 과거 다섯 대화의 손실 요약을 볼 수 있다. 반면 MemGPT는 전체 대화 이력에 접근할 수 있지만, 기억을 회상해 주 컨텍스트로 가져오기 위해 페이지네이션 검색 질의로 접근해야 한다. 이 과제에서 MemGPT는 기반 LLM 성능을 뚜렷하게 높인다. MemGPT에서 대응 LLM baseline으로 바꾸면 accuracy와 ROUGE 점수가 모두 뚜렷하게 떨어진다.

#### 3.1.2 대화 시작 과제(참여도)

**conversation opener** 과제에서는 에이전트가 과거 대화에서 쌓은 지식을 바탕으로 사용자에게 흥미로운 메시지를 만드는 능력을 평가한다. MSC 데이터셋을 사용해 opener의 참여도를 평가하기 위해 생성된 opener를 gold persona와 비교한다. 참여도 높은 opener는 MSC에서 모든 과거 세션에 걸쳐 축적된 지식을 사실상 요약하는 페르소나 안의 하나 이상 데이터 지점을 활용해야 한다. 또한 다음 세션의 첫 응답인 인간 작성 gold opener와도 비교한다. 표 3에는 MemGPT opener의 CSIM 점수를 보고하며, 서로 다른 기반 LLM을 쓰는 여러 MemGPT 변형을 시험한다.

> 표 3. Conversation opener 성능. 에이전트의 conversation opener는 gold persona label에 대한 유사도(SIM-1/3)와 인간 작성 opener에 대한 유사도(SIM-H)로 평가한다. MemGPT는 여러 기반 모델에서 인간 작성 conversation opener의 성능을 넘을 수 있다.
>
> | 방법 | SIM-1 | SIM-3 | SIM-H |
> | --- | ---: | ---: | ---: |
> | Human | 0.800 | 0.800 | 1.000 |
> | GPT-3.5 Turbo | 0.830 | 0.812 | 0.817 |
> | GPT-4 | 0.868 | 0.843 | 0.773 |
> | GPT-4 Turbo | 0.857 | 0.828 | 0.767 |

**MemGPT는 메모리로 참여도를 높인다.** 표 3에서 보듯 MemGPT는 인간이 손으로 쓴 opener와 비슷하거나 때로 그보다 나은 참여도 높은 opener를 만들 수 있다. 저자들은 MemGPT가 인간 baseline보다 더 장황하고 페르소나 정보의 더 많은 측면을 다루는 opener를 만드는 경향을 관찰했다. 또한 working context에 정보를 저장하는 일이 참여도 높은 opener 생성에 핵심임을 확인했다.

### 3.2 문서 분석을 위한 MemGPT

문서 분석도 오늘날 Transformer 모델의 제한된 컨텍스트 창 때문에 어려움을 겪는다. 표 1에서 보듯 오픈·클로즈드 모델 모두 컨텍스트 길이에 제약이 있으며 OpenAI 모델도 최대 128k token이다. 그러나 SEC Form 10-K 같은 법률·재무 문서는 쉽게 백만 token을 넘고, 실제 문서 분석 과제는 이런 긴 문서 여러 개를 연결해야 하는 경우가 많다. 이런 상황을 고려하면 고정 컨텍스트 문제의 해법으로 컨텍스트만 무작정 확대하기는 어렵다. Liu et al. (2023a)도 큰 컨텍스트 모델에서 불균일한 attention 분포, 즉 창의 처음·끝 정보는 잘 회상하지만 중간 token은 덜 회상하는 현상을 보고해 단순 확장의 효용에 의문을 제기한다. 문서 전반에서 추론하려면 MemGPT 같은 더 유연한 메모리 아키텍처가 필요하다.

#### 3.2.1 다중 문서 질의응답

문서 분석 능력을 평가하기 위해 저자들은 Liu et al. (2023a)의 retriever-reader 문서 QA 과제에서 고정 컨텍스트 baseline과 MemGPT를 비교한다. 이 과제에서는 NaturalQuestions-Open 데이터셋에서 질문 하나를 고르고, retriever가 그 질문과 관련된 Wikipedia 문서를 선택한다. 이후 reader 모델(LLM)은 이 문서를 입력으로 받아 제공된 문서를 이용해 질문에 답한다. Liu et al. (2023a)와 같이 검색 문서 수 K가 늘어남에 따라 reader accuracy를 평가한다.

평가 설정에서 고정 컨텍스트 baseline과 MemGPT는 모두 OpenAI `text-embedding-ada-002` 임베딩의 유사도 검색(코사인 거리)에 따라 상위 K개 문서를 고르는 같은 retriever를 쓴다. MemGPT는 pgvector 확장으로 벡터 검색을 활성화한 PostgreSQL을 archival memory 저장소로 쓰는 기본 저장 설정을 사용한다. 임베딩을 미리 계산해 데이터베이스에 넣고, HNSW 인덱스로 근사적인 1초 미만 질의를 가능하게 한다. MemGPT에서는 전체 임베딩 문서 집합이 archival storage에 적재되고, cosine similarity 기반 vector search를 수행하는 archival storage search 기능을 통해 retriever가 자연스럽게 나타난다. 고정 컨텍스트 baseline에서는 원래 retriever-reader 설정과 같이 LLM 추론과 독립적으로 retriever가 top-K 문서를 가져온다.

저자들은 기존 NaturalQuestions-Open 연구(Izacard & Grave, 2020; Izacard et al., 2021)를 따라 2018년 말 Wikipedia dump를 사용하고, 평가용 질문 50개 하위 집합을 추출했다. 추출한 질문과 임베딩된 Wikipedia passage는 공개한다. 답이 검색 문서에서 적절히 도출됐는지 보장하고 정확하지 않은 문자열 일치가 오답으로 처리되는 일을 피하기 위해 MemGPT와 baseline 모두를 LLM judge로 평가한다.

> 그림 5. Document QA 과제 성능. MemGPT 성능은 컨텍스트 길이가 늘어도 영향을 받지 않는다. truncation 같은 방법은 GPT-4처럼 고정 길이 모델의 유효 컨텍스트 길이를 늘릴 수 있지만, 필요한 압축량이 커질수록 성능 저하가 생긴다. GPT-4와 GPT-4 Turbo로 MemGPT를 실행한 결과는 이 과제에서 동등하다.
>
> 그림 6. MemGPT(왼쪽)가 document QA를 푸는 예. Wikipedia 문서 데이터베이스를 archival storage에 업로드하고, MemGPT는 함수 호출로 archival storage를 질의해 페이지가 매겨진 검색 결과를 주 컨텍스트로 가져온다. 예시 질의 `Who won the first Nobel Prize in physics?`에 대해 `Wilhelm Conrad Röntgen`을 찾는다.

그림 5는 document QA 결과를 보인다. 고정 컨텍스트 baseline 성능은 대략 retriever 성능에 상한이 생긴다. 이 방법들은 컨텍스트 창에 제시된 정보만 사용하므로, 임베딩 검색 retriever가 제공된 질문으로 gold 문서를 가져오지 못하면 baseline은 그 문서를 절대 볼 수 없다. 반대로 MemGPT는 archival storage를 질의해 retriever를 여러 번 호출할 수 있어 더 큰 유효 컨텍스트 길이로 확장된다. MemGPT는 archival storage에서 문서를 능동적으로 검색하고 결과를 반복적으로 페이지 탐색할 수 있으므로, MemGPT가 쓸 수 있는 총 문서 수는 더 이상 LLM 프로세서의 컨텍스트 창에 들어가는 문서 수에 제한되지 않는다.

임베딩 기반 유사도 검색의 한계 탓에 document QA는 모든 방법에 어렵다. 저자들은 NaturalQuestions-Open이 주석한 선택 질문의 gold 문서가 처음 수십 개 검색 결과 밖, 때로는 더 뒤에 나타나는 일을 관찰했다. retriever 성능은 고정 컨텍스트 baseline 결과로 곧바로 이어진다. 검색 문서가 적을 때 GPT-4 accuracy는 낮고, 검색 문서 정보를 바탕으로만 답하도록 올바르게 제한되므로 컨텍스트 창에 문서를 더 추가하면 accuracy가 계속 높아진다. 임베딩 기반 순위가 잡음이 있더라도 전체 retriever 순위에 gold 문서가 들어 있기만 하면 충분한 페이지네이션 호출로 찾을 수 있으므로 이론상 MemGPT는 sub-optimal retriever 성능에 제한되지 않는다. 그러나 실제로 MemGPT는 retriever 데이터베이스를 다 소진하기 전에 결과 페이징을 멈추는 경우가 많았다.

기본 컨텍스트 길이를 넘는 영역에서도 고정 컨텍스트 baseline과 MemGPT를 비교하기 위해, 저자들은 retriever가 돌려준 문서 segment를 잘라서 같은 수의 문서가 가용 컨텍스트에 맞도록 했다. 예상대로 문서가 짧아질수록 gold 문서 안의 관련 snippet이 빠질 가능성이 커져 document truncation은 accuracy를 낮춘다(그림 5). 함수 호출 능력이 제한적인 GPT-3.5에서는 MemGPT 성능이 크게 떨어지며, GPT-4에서 가장 좋다.

#### 3.2.2 중첩 key-value 검색

저자들은 Liu et al. (2023a)이 제안한 합성 Key-Value 검색에 기반한 새 과제를 제안한다. 이 과제의 목표는 MemGPT가 여러 데이터 원본의 정보를 모으는 방법을 보이는 것이다. 원래 KV 과제에서 저자들은 각 key와 value가 128-bit UUID(universally unique identifier)인 key-value 쌍의 합성 데이터셋을 만들었다. 에이전트는 key 하나를 받고 그 key에 연결된 value를 반환해야 한다. 저자들은 value 자체도 key일 수 있어 multi-hop lookup이 필요한 nested KV retrieval 버전을 만들었다.

설정에서 전체 UUID 쌍 수는 GPT-4 baseline의 컨텍스트 길이인 약 8k token에 해당하는 140개로 고정한다. 전체 nesting level은 0(초기 key-value 쌍의 value가 key가 아님)부터 4(최종 value를 찾으려면 총 네 번 KV lookup이 필요함)까지 바꾸며, 초기 key 위치와 nesting key 위치를 모두 포함한 서로 다른 순서 구성 30개를 표본으로 뽑는다.

> 그림 7. Nested KV retrieval 과제 성능. MemGPT는 2개 nesting level을 넘어서는 nested KV 과제를 일관되게 완료할 수 있는 유일한 접근법이다. GPT-4 Turbo는 baseline으로는 더 좋지만, GPT-4 Turbo 기반 MemGPT는 GPT-4 기반 MemGPT보다 성능이 낮다.
>
> 그림 8. MemGPT(왼쪽)가 nested KV 과제를 푸는 예(UUID는 가독성을 위해 줄였다). 이 예에서 key-value 쌍은 두 nesting level을 가진다: `831...ea5 → 5b8...4c3 → f37...617`. MemGPT 에이전트는 최종 value `f37...617`을 질의했을 때 결과가 하나만 나와 그것이 key가 아님을 확인한 뒤 최종 답을 반환한다.

GPT-3.5와 GPT-4는 원래 KV 과제에서는 좋은 성능을 보이지만 nested KV 과제에서는 모두 어려움을 겪는다. GPT-3.5는 nested 변형을 완료하지 못하며, nesting level 1에서 accuracy가 0%까지 즉시 떨어진다. 주요 실패 양상은 단순히 최초 value를 반환하는 것이다. GPT-4와 GPT-4 Turbo는 GPT-3.5보다 낫지만 비슷하게 하락해 nesting level 3에서 accuracy가 0%가 된다. 반면 GPT-4 기반 MemGPT는 nesting level 수의 영향을 받지 않으며, 함수 질의로 주 컨텍스트에 저장된 key-value 쌍에 반복적으로 접근해 nested lookup을 수행한다. GPT-4 Turbo와 GPT-3.5 기반 MemGPT도 대응 baseline보다 좋지만, 충분한 lookup을 수행하지 못해 nesting level 2에서 성능이 떨어지기 시작한다. nested KV 과제의 MemGPT 성능은 여러 질의를 결합해 multi-hop lookup을 수행하는 능력을 보여 준다.

## 4. 관련 연구

**장문 컨텍스트 LLM.** 여러 연구 흐름이 LLM 컨텍스트 길이를 개선했다. 예를 들어 attention sparsification(Child et al., 2019; Beltagy et al., 2020), low-rank approximation(Wang et al., 2020), neural memory(Lee et al., 2019)를 이용한 더 효율적인 Transformer 아키텍처가 있다. Press et al. (2021), Chen et al. (2023)처럼 원래 학습한 길이를 넘어서 컨텍스트 창을 확장하려는 연구도 있다. MemGPT는 이런 컨텍스트 길이 개선이 MemGPT의 main memory 크기를 키운다는 점에서 그 위에 구축된다. 저자들의 주요 기여는 long-context LLM을 main memory 구현으로 사용하는 계층형 tiered memory다.

**검색 증강 모델.** MemGPT의 외부 메모리 설계는 외부 retriever가 주는 관련 입력으로 LLM을 증강한 많은 선행 연구(Ram et al., 2023; Borgeaud et al., 2022; Karpukhin et al., 2020; Lewis et al., 2020; Guu et al., 2020; Lin et al., 2023)에 기반한다. 특히 Jiang et al. (2023)은 생성 과정 중 LLM이 언제 무엇을 검색할지 능동적으로 결정하게 하는 FLARE를 제안했다. Trivedi et al. (2022)은 다단계 질의응답을 높이기 위해 검색과 chain-of-thought reasoning을 교차시킨다.

**에이전트로서의 LLM.** 최근 연구는 대화형 환경에서 에이전트로 행동하도록 LLM에 추가 능력을 부여하는 방법을 탐구했다. Park et al. (2023)은 LLM에 메모리를 더하고 LLM을 planner로 사용해, The Sims 게임에서 영감 받은 다중 에이전트 sandbox에서 집안일·취미·출근·다른 에이전트와의 대화 같은 기본 활동을 수행하는 에이전트의 창발적 사회 행동을 관찰했다. Nakano et al. (2021)은 질문에 답하기 전 웹을 검색하도록 모델을 학습시키고, 웹 브라우징 환경의 기반 컨텍스트 크기를 통제하기 위해 MemGPT와 유사한 페이지네이션 개념을 쓴다. Yao et al. (2022)은 chain-of-thought reasoning(Wei et al., 2022)을 교차하면 대화형 LLM 에이전트의 계획 능력을 더 높일 수 있음을 보였다. MemGPT에서도 LLM은 함수를 실행할 때 ‘소리 내어 계획’할 수 있다. Liu et al. (2023b)은 비디오 게임·사고 퍼즐·웹 쇼핑을 포함하는 대화형 환경에서 LLM을 에이전트로 평가하는 벤치마크 모음을 도입했다. 이 논문은 사용자 입력의 장기 기억을 에이전트에 갖추게 하는 문제에 초점을 맞춘다.

## 5. 결론

본 논문은 대규모 언어 모델의 제한된 컨텍스트 창을 관리하기 위해 운영체제에서 영감을 받은 새 LLM 시스템 MemGPT를 소개했다. 전통 OS와 유사한 메모리 계층과 제어 흐름을 설계함으로써 MemGPT는 LLM에 더 큰 컨텍스트 자원이 있는 듯한 환상을 제공한다. 이 OS 영감 접근은 유한 컨텍스트 길이 때문에 기존 LLM 성능이 제약되는 문서 분석과 대화 에이전트 두 영역에서 평가됐다.

문서 분석에서 MemGPT는 관련 컨텍스트를 메모리 안팎으로 효과적으로 페이징하여 현재 LLM의 컨텍스트 한계를 훨씬 넘는 긴 텍스트를 처리할 수 있었다. 대화 에이전트에서는 확장된 대화에 걸쳐 장기 기억, 일관성, 변화 가능성을 유지하게 했다. 전반적으로 MemGPT는 계층형 메모리 관리와 인터럽트 같은 운영체제 기법이 고정 컨텍스트 길이에 제약된 상황에서도 LLM의 잠재력을 열 수 있음을 보인다. 이 연구는 대규모 또는 무한 컨텍스트를 가진 다른 영역에 MemGPT를 적용하고, 데이터베이스·캐시 같은 다른 메모리 계층 기술을 통합하며, 제어 흐름과 메모리 관리 정책을 더 개선하는 등 미래 탐색의 여러 길을 연다. OS 아키텍처의 개념을 AI 시스템으로 연결한 MemGPT는 LLM의 근본 한계 안에서 그 능력을 극대화하는 유망한 새 방향이다.

## 참고문헌

원문의 참고문헌은 서지 정확성을 위해 영문 표기를 보존한다.

- Iz Beltagy, Matthew E. Peters, and Arman Cohan. *Longformer: The long-document transformer*. arXiv:2004.05150, 2020.
- Sebastian Borgeaud et al. *Improving language models by retrieving from trillions of tokens*. ICML, pp. 2206–2240, 2022.
- Tom Brown et al. *Language models are few-shot learners*. NeurIPS 33:1877–1901, 2020.
- Shouyuan Chen, Sherman Wong, Liangjian Chen, and Yuandong Tian. *Extending context window of large language models via positional interpolation*. arXiv:2306.15595, 2023.
- Rewon Child, Scott Gray, Alec Radford, and Ilya Sutskever. *Generating long sequences with sparse transformers*. arXiv:1904.10509, 2019.
- Zihang Dai et al. *Transformer-XL: Attentive language models beyond a fixed-length context*. arXiv:1901.02860, 2019.
- Jacob Devlin et al. *BERT: Pre-training of deep bidirectional transformers for language understanding*. arXiv:1810.04805, 2018.
- Zican Dong et al. *A survey on long text modeling with transformers*. arXiv:2302.14502, 2023.
- Kelvin Guu et al. *Retrieval augmented language model pre-training*. ICML, pp. 3929–3938, 2020.
- Gautier Izacard and Edouard Grave. *Leveraging passage retrieval with generative models for open domain question answering*. arXiv:2007.01282, 2020.
- Gautier Izacard et al. *Unsupervised dense information retrieval with contrastive learning*. arXiv:2112.09118, 2021.
- Zhengbao Jiang et al. *Active retrieval augmented generation*. arXiv:2305.06983, 2023.
- Vladimir Karpukhin et al. *Dense passage retrieval for open-domain question answering*. arXiv:2004.04906, 2020.
- Nikita Kitaev, Łukasz Kaiser, and Anselm Levskaya. *Reformer: The efficient transformer*. arXiv:2001.04451, 2020.
- Juho Lee et al. *Set transformer: A framework for attention-based permutation-invariant neural networks*. ICML, pp. 3744–3753, 2019.
- Patrick Lewis et al. *Retrieval-augmented generation for knowledge-intensive NLP tasks*. NeurIPS 33:9459–9474, 2020.
- Chin-Yew Lin. *ROUGE: A package for automatic evaluation of summaries*. Text Summarization Branches Out, pp. 74–81, 2004.
- Xi Victoria Lin et al. *RA-DIT: Retrieval-augmented dual instruction tuning*. 2023.
- Nelson F. Liu et al. *Lost in the middle: How language models use long contexts*. arXiv:2307.03172, 2023a.
- Xiao Liu et al. *AgentBench: Evaluating LLMs as agents*. arXiv:2308.03688, 2023b.
- Reiichiro Nakano et al. *WebGPT: Browser-assisted question-answering with human feedback*. arXiv:2112.09332, 2021.
- Long Ouyang et al. *Training language models to follow instructions with human feedback*. NeurIPS 35:27730–27744, 2022.
- Joon Sung Park et al. *Generative agents: Interactive simulacra of human behavior*. arXiv:2304.03442, 2023.
- David A. Patterson, Garth Gibson, and Randy H. Katz. *A case for redundant arrays of inexpensive disks (RAID)*. SIGMOD, pp. 109–116, 1988.
- Ofir Press, Noah A. Smith, and Mike Lewis. *Train short, test long: Attention with linear biases enables input length extrapolation*. arXiv:2108.12409, 2021.
- Ori Ram et al. *In-context retrieval-augmented language models*. arXiv:2302.00083, 2023.
- Timo Schick et al. *Toolformer: Language models can teach themselves to use tools*. arXiv:2302.04761, 2023.
- Hugo Touvron et al. *Llama 2: Open foundation and fine-tuned chat models*. arXiv:2307.09288, 2023.
- H. Trivedi et al. *Interleaving retrieval with chain-of-thought reasoning for knowledge-intensive multi-step questions*. arXiv:2212.10509, 2022.
- Ashish Vaswani et al. *Attention is all you need*. NeurIPS 30, 2017.
- Sinong Wang et al. *Linformer: Self-attention with linear complexity*. arXiv:2006.04768, 2020.
- Jason Wei et al. *Chain-of-thought prompting elicits reasoning in large language models*. NeurIPS 35:24824–24837, 2022.
- Jing Xu, Arthur Szlam, and Jason Weston. *Beyond goldfish memory: Long-term open-domain conversation*. arXiv:2107.07567, 2021.
- Shunyu Yao et al. *ReAct: Synergizing reasoning and acting in language models*. arXiv:2210.03629, 2022.
- Lianmin Zheng et al. *Judging LLM-as-a-judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685, 2023.

## 6. 부록

### 6.1 프롬프트와 지시문

MemGPT 프롬프트는 간결성을 위해 편집됐다. 정확한 프롬프트를 포함한 전체 구현 세부사항은 https://research.memgpt.ai 에 있다.

#### 6.1.1 MemGPT 지시문(DMR)

다음은 채팅·대화 관련 과제에서 MemGPT persona에 사용한 예시 지시문이다.

```text
The following is information about myself. My task is to completely immerse
myself in this role (I should never say that I am an AI, and should reply as
if I am playing this role). If the user asks me a question, I should reply
with a best guess using the information in core memory and conversation search.
```

한국어로 옮기면 다음과 같다. “다음은 나 자신에 관한 정보다. 내 과제는 이 역할에 완전히 몰입하는 것이다(나는 절대로 AI라고 말해서는 안 되며, 이 역할을 연기하는 것처럼 답해야 한다). 사용자가 나에게 질문하면 core memory와 conversation search의 정보를 이용해 최선의 추측으로 답해야 한다.”

baseline에는 system prompt(preprompt)로 다음 지시문을 주었다.

```text
Your task is to answer a question from the user about your prior conversations.
The following is a summary of all your prior conversations:

CONVERSATION SUMMARY

Answer from the perspective of the persona provided (do not say that you are
an AI assistant). If you do not have enough information to answer the question,
reply "NO ANSWER". Either reply with the answer, or reply "NO ANSWER"; do not
say anything else.
```

이는 “사용자가 이전 대화에 관해 묻는 질문에 답하라. 다음은 모든 이전 대화의 요약이다: `CONVERSATION SUMMARY`. 제공된 페르소나 관점에서 답하라(AI assistant라고 말하지 말 것). 답할 정보가 충분하지 않으면 `NO ANSWER`라고 답하라. 답 또는 `NO ANSWER`만 말하고 다른 내용은 말하지 말라.”는 뜻이다.

#### 6.1.2 LLM Judge(DMR / Opener)

DMR 과제 답의 정확성을 확인하기 위해 저자들은 LLM judge를 사용했다. LLM judge에는 두 baseline과 MemGPT가 생성한 답을 제공하고 다음 prompt로 판정을 요청했다.

```text
Your task is to label an answer to a question as "CORRECT" or "WRONG".
You will be given the following data: (1) a question (posed by one user to
another user), (2) a "gold" (ground truth) answer, (3) a generated answer
which you will score as CORRECT/WRONG.

The point of the question is to ask about something one user should know about
the other user based on their prior conversations. The gold answer will usually
be a concise and short answer that includes the referenced topic, for example:

Question: Do you remember what I got the last time I went to Hawaii?
Gold answer: A shell necklace

The generated answer might be much longer, but you should be generous with
your grading - as long as it touches on the same topic as the gold answer, it
should be counted as CORRECT. For example, the following answers would be
considered CORRECT:

Generated answer (CORRECT): Oh yeah, that was so fun! I got so much stuff
there, including that shell necklace.
Generated answer (CORRECT): I got a ton of stuff... that surfboard, the mug,
the necklace, those coasters too..
Generated answer (CORRECT): That cute necklace

The following answers would be considered WRONG:

Generated answer (WRONG): Oh yeah, that was so fun! I got so much stuff there,
including that mug.
Generated answer (WRONG): I got a ton of stuff... that surfboard, the mug,
those coasters too..
Generated answer (WRONG): I'm sorry, I don't remember what you're talking about.

Now it's time for the real question:
Question: QUESTION
Gold answer: GOLD ANSWER
Generated answer: GENERATED ANSWER

First, provide a short (one sentence) explanation of your reasoning, then
finish with CORRECT or WRONG. Do NOT include both CORRECT and WRONG in your
response, or it will break the evaluation script.
```

즉 judge는 한 사용자가 과거 대화에 근거해 다른 사용자가 알아야 할 내용을 묻는 질문, gold answer, 생성 답을 받고 `CORRECT`/`WRONG`을 판정한다. 생성 답이 더 길어도 gold answer와 같은 주제를 다루면 관대하게 `CORRECT`로 판정하며, 한 문장으로 근거를 설명한 뒤 두 토큰 중 하나로 끝내야 한다.

#### 6.1.3 Self-Instruct DMR 데이터셋 생성

DMR 질의응답 쌍은 원본 MSC 데이터셋과 다음 prompt를 사용해 생성했다.

```text
Your task is to write a "memory challenge" question for a simulated dialogue
between two users.

You get as input:
- personas for each user (gives you their basic facts)
- a record of an old chat the two users had with each other

Your task is to write a question from user A to user B that tests user B's
memory. The question should be crafted in a way that user B must have actually
participated in the prior conversation to answer properly, not just have read
the persona summary. Do NOT under any circumstances create a question that can
be answered using the persona information (that's considered cheating).

Instead, write a question that can only be answered by looking at the old chat
log (and is not contained in the persona information).

For example, given the following chat log and persona summaries:

old chat between user A and user B
A: Are you into surfing? I'm super into surfing myself
B: Actually I'm looking to learn. Maybe you could give me a basic lesson some time!
A: Yeah for sure! We could go to Pacifica, the waves there are pretty light and easy
B: That sounds awesome
A: There's even a cool Taco Bell right by the beach, could grab a bite after
B: What about this Sunday around noon?
A: Yeah let's do it!

user A persona:
I like surfing
I grew up in Santa Cruz

user B persona:
I work in tech
I live in downtown San Francisco

Here's an example of a good question that sounds natural, and an answer that
cannot be directly inferred from user A's persona:

User B's question for user A
B: Remember that one time we went surfing? What was that one place we went to
for lunch called?
A: Taco Bell!

This is an example of a bad question, where the question comes across as
unnatural, and the answer can be inferred directly from user A's persona:

User B's question for user A
B: Do you like surfing?
A: Yes, I like surfing

Never, ever, ever create questions that can be answered from the persona
information.
```

이 prompt는 두 사용자의 페르소나와 과거 채팅 기록을 입력으로 받아, 페르소나 요약만 읽어서가 아니라 과거 대화에 실제로 참여했어야만 답할 수 있는 user A→user B의 ‘memory challenge’ 질문을 쓰라고 한다. 페르소나 정보만으로 답할 수 있는 질문은 부정행위로 간주하며 절대 만들지 말라고 반복해 지시한다.

#### 6.1.4 문서 분석 지시문

문서 분석 과제의 preprompt에는 다음 예시 지시문을 사용했다.

```text
You are MemGPT DOC-QA bot. Your job is to answer questions about documents that
are stored in your archival memory. The answer to the users question will ALWAYS
be in your archival memory, so remember to keep searching if you can't find the
answer. Answer the questions as if though the year is 2018.
```

이는 “당신은 MemGPT DOC-QA bot이다. archival memory에 저장된 문서에 관한 질문에 답하라. 사용자 질문의 답은 항상 archival memory 안에 있으므로 답을 찾지 못하면 계속 검색하라. 현재 연도가 2018년인 것처럼 답하라.”는 뜻이다.

MemGPT에는 다음 prompt로 질문을 제공했다.

```text
Search your archival memory to answer the provided question. Provide both the
answer and the archival memory result from which you determined your answer.
Format your response with the format "ANSWER: [YOUR ANSWER], DOCUMENT:
[ARCHIVAL MEMORY TEXT]". Your task is to answer the question:
```

baseline에는 검색된 문서 목록과 함께 다음 prompt를 주었다.

```text
Answer the question provided according to the list of documents below (some of
which might be irrelevant). In your response, provide both the answer and the
document text from which you determined your answer. Format your response with
the format "ANSWER: <YOUR ANSWER>, DOCUMENT: [DOCUMENT TEXT]". If none of the
documents provided have the answer to the question, reply with "INSUFFICIENT
INFORMATION". Do NOT provide an answer if you cannot find it in the provided
documents. Your response will only be considered correct if you provide both
the answer and relevant document text, or say "INSUFFICIENT INFORMATION".
Answer the question as if though the current year is 2018.
```

#### 6.1.5 LLM Judge(문서 분석)

문서 분석 답의 정확성을 확인하고, 답이 모델 가중치가 아니라 제공된 텍스트에서 적절히 도출됐는지도 보장하기 위해 LLM judge를 사용했다. judge에는 두 baseline과 MemGPT의 답을 제공하고 다음 prompt로 판정하게 했다.

```text
Your task is to evaluate whether an LLM correct answered a question. The LLM
response should be the format "ANSWER: [answer], DOCUMENT: [document text]"
or say "INSUFFICIENT INFORMATION". The true answer is provided in the format
"TRUE ANSWER:[list of possible answers]". The questions is provided in the
format "QUESTION: [question]".

If the LLM response contains both the correct answer and corresponding document
text, the response is correct. Even if the LLM's answer and the true answer are
slightly different in wording, the response is still correct. For example, if
the answer is more specific than the true answer or uses a different phrasing
that is still correct, the response is correct. If the LLM response is
"INSUFFICIENT INFORMATION", or the "DOCUMENT" field is missing, the response
is incorrect. Respond with a single token: "CORRECT" or "INCORRECT".
```

#### 6.1.6 K/V 과제 지시문

MemGPT 에이전트에는 반복 검색을 유도하도록 설계한 다음 persona를 부여했다.

```text
You are MemGPT DOC-QA bot. Your job is to answer questions about documents that
are stored in your archival memory. The answer to the users question will ALWAYS
be in your archival memory, so remember to keep searching if you can't find the
answer. DO NOT STOP SEARCHING UNTIL YOU VERIFY THAT THE VALUE IS NOT A KEY. Do
not stop making nested lookups until this condition is met.
```

baseline에는 다음 prompt를 주었다.

```text
Below is a JSON object containing key-value pairings, all keys and values are
128-bit UUIDs, and your task is to return the value associated with the specified
key. If a value itself is also a key, return the value of that key (do a nested
lookup). For example, if the value of "A" is "B" but "B" is also a key, return
the value of key "B".
```
