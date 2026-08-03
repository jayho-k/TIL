# MemoryOS: AI 에이전트의 메모리 운영체제

> 원문: Jiazheng Kang, Mingming Ji, Zhe Zhao, Ting Bai, *Memory OS of AI Agent*, arXiv:2506.06326v1 (2025-05-30).
>
> 이 문서는 원문 PDF 9쪽을 문단·수식·표·그림 단위로 대조하여 작성한 학습용 한국어 전체 번역이다. 코드 저장소 URL, 모델명, 데이터셋명, 수식 기호와 인용 표기는 원문 표기를 유지했다. 번역 이외의 해석이나 비평은 넣지 않았다.

## 저자

- Jiazheng Kang — Beijing University of Posts and Telecommunications, `kjz@bupt.edu.cn`
- Mingming Ji — Tencent AI Lab, `matthhewj@tencent.com`
- Zhe Zhao — Tencent AI Lab, `nlpzhezhao@tencent.com`
- Ting Bai<sup>*</sup> — Beijing University of Posts and Telecommunications, `baiting@bupt.edu.cn`

<sup>*</sup> 교신저자.

## 초록

대규모 언어 모델(LLM)은 고정된 컨텍스트 창과 불충분한 메모리 관리라는 중대한 문제에 직면한다. 이는 AI 에이전트와 상호작용할 때 장기 기억 능력을 심각하게 부족하게 만들고 개인화도 제한한다. 이 문제를 해결하기 위해 저자들은 AI 에이전트를 위한 포괄적이고 효율적인 메모리 관리를 달성하는 **메모리 운영체제(Memory Operating System)**, 즉 **MemoryOS**를 새롭게 제안한다.

운영체제의 메모리 관리 원리에서 영감을 받아, MemoryOS는 계층형 저장 아키텍처를 설계하고 Memory Storage, Updating, Retrieval, Generation의 네 핵심 모듈로 구성한다. 구체적으로 이 아키텍처는 단기 메모리, 중기 메모리, 장기 개인 메모리라는 세 단계 저장 단위로 이루어진다. MemoryOS의 핵심 연산에는 저장 단위 사이의 동적 갱신이 포함된다. 단기 메모리에서 중기 메모리로의 갱신은 대화 체인 기반 FIFO 원리를 따르고, 중기 메모리에서 장기 메모리로의 갱신은 세그먼트 페이지 조직 전략을 사용한다.

제안하는 MemoryOS는 계층적 메모리 통합과 동적 갱신을 가능하게 한다. LoCoMo 벤치마크의 광범위한 실험에서 GPT-4o-mini 기반으로 기준선보다 F1은 평균 49.11%, BLEU-1은 평균 46.18% 개선되었으며, 긴 대화에서 맥락 일관성과 개인화된 기억 보존을 보였다. 구현 코드는 <https://github.com/BAI-LAB/MemoryOS>에 공개되어 있다.

## 1. 서론

대규모 언어 모델(LLM)은 텍스트 이해와 생성에서 인상적인 능력을 보이지만, 메모리 관리를 고정 길이 컨텍스트 창에 의존하기 때문에 대화의 일관성을 지속하는 데 본질적 한계가 있다. 이 고정 길이 설계는 시간 간격이 큰 대화에서 연속성을 보존하기 어렵고, 종종 사실 불일치와 개인화 저하로 나타나는 단절된 기억을 초래한다. 지속적인 사용자 적응, 여러 세션에 걸친 지식 보존, 장기 상호작용 전반의 안정적인 페르소나 표현이 필요한 상황에서는 장기 기억의 일관성이 결정적이다. 이러한 상황에서 기본 LLM의 고정 길이 메모리 관리 한계는 특히 심각하며, 해당 분야의 중요한 미해결 과제가 된다.

이 문제를 해결하기 위한 현재 LLM 메모리 메커니즘은 크게 세 방법론으로 나눌 수 있다. (1) A-Mem처럼 메모리를 상호 연결된 의미 네트워크 또는 노트로 구조화하여 적응적 관리와 유연한 검색을 가능하게 하는 **지식 조직 방법**(Xu et al., 2025; Liu et al., 2023), (2) MemoryBank처럼 의미 검색과 기억 망각 곡선 메커니즘을 결합해 장기 기억 갱신을 허용하는 **검색 메커니즘 중심 접근**(Huang et al., 2024; Zhong et al., 2024; Li et al., 2024), (3) MemGPT처럼 명시적 읽기·쓰기 연산을 갖춘 계층 구조로 맥락을 동적으로 관리하는 **아키텍처 중심 방법**(Packer et al., 2023; Chhikara et al., 2025)이다. 그러나 이 다양한 전략은 보통 저장 구조, 검색 메커니즘, 갱신 전략 등 하나의 차원에 각각 초점을 두고 분리되어 동작한다. AI 에이전트의 체계적·포괄적 메모리 관리를 가능하게 하는 통합 운영체제는 아직 제안되지 않았다.

저자들은 운영체제의 메모리 관리 원리에서 영감을 받아, MemoryOS라는 포괄적 메모리 운영체제를 선구적으로 제안한다. 그림 1과 같이 MemoryOS는 Memory Storage, Updating, Retrieval, Generation의 네 핵심 기능 모듈로 이루어진다. 이 모듈들이 협력하여 계층형 저장, 동적 갱신, 적응적 검색, 맥락적 생성을 포괄하는 통합 메모리 관리 프레임워크를 구축한다. 구체적으로 Memory Storage는 정보를 단기·중기·장기 저장 단위로 조직한다. Memory Updating은 대화 체인과 heat 기반 메커니즘에 기초한 세그먼트 페이징 아키텍처를 통해 동적으로 갱신한다. Memory Retrieval은 의미 분할을 이용해 이 계층들을 질의하고, Response Generation은 검색된 메모리 정보를 통합하여 일관되고 개인화된 응답을 생성한다. 이 시너지적 흐름은 장기 대화 메모리를 전체적으로 관리하여, 확장된 대화에서 맥락 일관성과 개인화된 회상을 가능하게 한다.

본 연구의 주요 기여는 다음과 같다.

- 저자들은 메모리 관리를 위한 체계적 운영체제 MemoryOS를 처음으로 도입하여, 장기 대화 상호작용에서 AI 에이전트가 장기 대화 일관성과 사용자 페르소나 지속성을 갖도록 시도한다.
- MemoryOS는 선구적인 3계층 계층형 메모리 저장 아키텍처를 도입하고, 저장·갱신·검색·생성이라는 네 핵심 기능 모듈을 메모리 관리에 통합한다. 이를 통해 확장된 대화 전반에서 사용자 선호도를 동적으로 포착하고 발전시킨다.
- 포괄적 실험으로 다양한 벤치마크 데이터셋에서 응답 정확성과 일관성을 유지하는 MemoryOS의 효과성과 효율성을 검증하고, 긴 대화 상호작용을 처리할 수 있음을 보인다.

## 2. 관련 연구

### 2.1 LLM 에이전트를 위한 메모리

기존 LLM은 장기 일관성이 필요한 복잡한 시나리오를 처리할 때 근본적인 어려움을 겪는다. 이러한 어려움은 시간 간격이 큰 대화에서 연속성을 유지하기 힘든 고정 길이 설계의 내재적 한계에서 비롯된다. 그 결과 기억이 단편화되고, 이는 사실 불일치와 약화된 개인화로 나타난다. 이 문제를 다루는 LLM 메모리 시스템의 발전은 크게 지식 조직, 검색 메커니즘 중심, 아키텍처 중심 프레임워크의 세 범주로 묶을 수 있다(Zhang et al., 2024; Wu et al., 2025; Du et al., 2025).

지식 조직 방법은 대규모 언어 모델의 중간 추론 상태를 포착하고 구조화하는 데 집중한다. 예를 들어 Think-in-Memory(TiM)(Liu et al., 2023)는 발전하는 사고 사슬을 저장하며, 지속적 갱신을 통해 일관성을 가능하게 한다. A-Mem(Xu et al., 2025)은 세션을 아우르는 상호 연결 노트 네트워크로 지식을 조직한다. Grounded Memory(Ocker et al., 2025)는 지각을 위한 vision-language 모델과 구조화된 메모리 표현을 위한 지식 그래프를 통합하여, 스마트 개인 비서에서 맥락 인식 추론을 가능하게 한다.

검색 메커니즘 중심 접근은 외부 메모리 라이브러리로 모델을 보강한다. MemoryBank(Zhong et al., 2024)는 대화, 사건, 사용자 특성을 벡터 데이터베이스에 기록하고 망각 곡선 일정으로 갱신한다. AI-town(Park et al., 2023)은 기억을 자연어로 보관하고 관련성 필터링을 위한 성찰 루프를 더한다. EmotionalRAG(Huang et al., 2024)는 하이브리드 전략으로 의미 유사도와 에이전트의 현재 감정 상태를 결합하여 메모리 항목을 검색한다.

아키텍처 중심 설계는 맥락을 명시적으로 관리하도록 핵심 제어 흐름을 바꾼다. 예를 들어 MemGPT(Packer et al., 2023)는 전용 읽기·쓰기 호출을 갖춘 OS 유사 계층을 채택한다. Self-Controlled Memory(SCM)(Wang et al., 2025)은 이중 버퍼와 선택적 회상을 게이트하는 메모리 컨트롤러를 도입한다.

### 2.2 OS의 메모리 관리

현대 운영체제(OS)는 논리적 구조와 효율적인 물리적 활용의 균형을 맞추기 위해 세그먼트-페이지 결합 메모리 관리를 사용한다. Multics 같은 고전적 접근(Bensoussan et al., 1972)은 메모리를 여러 페이지로 나뉜 세그먼트로 조직하여 효율적 관리, 보호, 공유를 지원한다. 세그먼트 메타데이터(크기, 접근 권한)는 외부 단편화를 방지하고(Bensoussan et al., 1972), 페이징은 내부 단편화를 줄인다(Denning, 1970). 고급 OS는 hot 데이터 유지를 위해 우선순위 기반 퇴출(예: LRU, working-set 모델)을 사용한다(Denning, 1970). Zheng et al.(2020)은 거친 단위의 세그먼테이션과 세밀한 페이지를 결합하면 many-core 프로세서의 오버헤드를 최소화함을 보였다.

> 그림 1. MemoryOS의 전체 아키텍처. 메모리 저장(Store), 갱신(Updating), 검색(Retrieval), 응답(Response)을 포함한다. STM은 `Page`와 `Dialogue Chain`을 FIFO 방식으로 관리하여 MTM으로 삽입한다. MTM은 `Segment`를 `Heat`로 관리하고 상위 `m`개 세그먼트와 상위 `k`개 페이지를 검색하며, 낮은 heat 세그먼트는 삭제한다. 높은 heat 세그먼트는 LPM으로 갱신된다. LPM은 정적·동적 사용자 페르소나(User Profile, User KB, User Traits)와 에이전트 페르소나(Agent Profile, Agent Traits)를 보관하며, 이와 STM·MTM의 검색 결과를 응답 생성에 사용한다.

OS의 관리 방식에서 영감을 받아 MemoryOS는 메모리를 페이지로 세분한 논리 세그먼트(대화 주제)로 구조화해 이 원리를 적용한다. heat 기반 우선순위화로 관련 내용은 유지하고 접근이 적은 정보는 효율적으로 버리거나 보관하여, 맥락 관리와 개인화를 향상한다.

## 3. MemoryOS

MemoryOS는 메모리를 동적으로 갱신하고 의미적으로 관련된 맥락을 검색하여, 긴 대화에서 일관되고 개인화된 상호작용을 보장하는 AI 에이전트용 포괄적 메모리 관리 시스템이다.

### 3.1 전체 아키텍처

MemoryOS의 전체 아키텍처는 그림 1에 보였으며, 메모리 저장, 갱신, 검색, 생성의 네 모듈로 구성된다.

**Memory Storage.** 이 모듈은 메모리 정보의 조직과 저장을 담당한다. 즉시성 있는 대화를 위한 Short-Term Memory(STM), 반복되는 주제의 요약을 위한 Mid-Term Memory(MTM), 사용자 또는 에이전트 선호도를 위한 Long-term Personal Memory(LPM)라는 3계층 구조를 사용해 메모리 무결성과 효율적 활용을 보장한다.

**Memory Updating.** 이 모듈은 동적 메모리 갱신을 관리한다. STM에서 MTM으로는 대화 체인 FIFO로 갱신하고, MTM에서 LPM으로는 heat 기반 교체를 갖춘 세그먼트 페이지 전략으로 갱신한다.

**Memory Retrieval.** 이 모듈은 특정 질의를 통해 관련 메모리를 검색한다. MTM에서는 먼저 의미 관련성으로 세그먼트를 식별한 뒤 관련 대화 페이지를 검색하는 2단계 접근을 쓴다. 마지막으로 LPM의 페르소나 속성과 STM의 맥락 정보를 결합하여 응답을 생성하고, 관련 메모리 전체를 응답 생성에 통합한다.

**Response Generation.** 이 모듈은 데이터를 처리하고 적절한 응답을 생성한다. STM, MTM, LPM의 검색 결과를 하나의 일관된 프롬프트에 통합하여, 맥락적으로 일관되고 개인화된 응답 생성을 가능하게 한다.

### 3.2 메모리 저장 모듈

메모리 저장 모듈은 Short-Term Memory(STM), Mid-Term Memory(MTM), Long-term Personal Memory(LPM)라는 세 종류의 저장 단위로 이루어진 계층형 구조로 구현한다.

**Short-Term Memory(STM).** STM은 대화 페이지(dialogue page)라는 단위로 실시간 대화 데이터를 저장한다. 각 대화 페이지는 사용자 질의 $Q$, 모델 응답 $R$, 타임스탬프 $T$를 포함하며 다음과 같이 구성된다.
$$
page_i = \{Q_i, R_i, T_i\}.
$$

맥락 일관성을 보장하기 위해 각 페이지에는 대화 체인을 구성한다. 이는 단기 연속 대화 교환의 맥락 정보를 유지하고 일관된 맥락 추적을 보장한다. 대화 페이지는 다음과 같이 정의한다.

$$
page_i^{chain} = \{Q_i, R_i, T_i, meta_i^{chain}\}. \tag{1}
$$

메타 정보는 LLM이 두 단계로 생성한다. 먼저 새 페이지가 이전 페이지와 맥락상 관련되는지 평가하여 체인 연결 여부를 정하고, 의미적으로 불연속이면 현재 페이지부터 체인을 다시 시작한다. 다음으로 체인에 속한 모든 페이지를 $meta_i^{chain}$으로 요약한다.

**Mid-Term Memory(MTM).** MTM은 운영체제의 메모리 관리 원리에서 영감을 받은 **세그먼트 페이징(Segmented Paging)** 저장 아키텍처를 채택한다. 같은 주제의 대화 페이지를 세그먼트로 묶고, 각 세그먼트는 하나의 고유 주제에 관한 여러 페이지를 담는다. MTM의 세그먼트는 다음과 같이 정의한다.
$$
segment_i = \{page_i \mid F_{score}(page_i, segment_i) > \theta\}. \tag{2}
$$

세그먼트의 내용은 해당 대화 페이지에 기초해 LLM이 요약한다. $F_{score}$는 의미 유사도와 키워드 유사도를 모두 바탕으로 대화 페이지와 세그먼트 사이의 유사도를 측정하며, 다음과 같이 정의한다.

$$
F_{score} = \cos(e_s, e_p) + F_{Jacard}(K_s, K_p), \tag{3}
$$

여기서 $e_s$, $e_p$는 각각 세그먼트와 대화 페이지의 임베딩 벡터이고, $K_s$, $K_p$는 각각 세그먼트와 페이지에서 LLM이 요약한 키워드 집합이다. $F_{Jacard}$는 Jaccard 유사도이며 다음과 같다.

$$
F_{Jacard} = \frac{|K_s \cap K_p|}{|K_s \cup K_p|}.
$$

세그먼트와의 유사도 점수가 임계값 $\theta$를 넘는 페이지는 같은 세그먼트로 병합한다. 이를 통해 세그먼트 내부의 주제 일관성과 의미 일관성을 보장한다.

**Long-term Persona Memory(LPM).** 이 모듈은 사용자와 보조자 모두 중요한 개인 상세 정보와 특성을 지속적으로 기억하게 해, 장기 상호작용에서도 일관성과 개인화를 보장한다. LPM은 User Persona와 AI Agent Persona의 두 구성 요소로 이루어진다.

- **User Persona.** User Profile은 성별·이름·출생 연도 같은 고정 속성으로 이루어진 정적 구성 요소, 과거 상호작용에서 추출한 사실 정보를 동적으로 저장하고 점진적으로 갱신하는 User Knowledge Base(User KB), 시간에 따라 변화하는 사용자의 관심사·습관·선호를 담는 User Traits로 구성된다.
- **Agent Persona.** Agent Profile을 포함한다. 여기에는 AI 에이전트 보조자가 수행하는 역할이나 성격 특성 같은 고정 설정이 들어가 일관된 자기 설명을 제공한다. Agent Traits는 사용자와의 상호작용을 통해 발전하는 동적 속성으로, 대화 중 사용자가 새로 추가한 설정이나 추천 항목 같은 상호작용 이력이 포함될 수 있다.

### 3.3 메모리 갱신 모듈

핵심 갱신 연산에는 각 저장 단위 내부 갱신과 STM에서 MTM으로, MTM에서 LPM으로의 갱신 메커니즘이 포함된다.

**STM–MTM 갱신.** STM은 고정 길이 큐에 대화 페이지 형태로 정보를 저장한다. 저자들은 정보를 MTM으로 옮길 때 선입선출(First-In-First-Out, FIFO) 갱신 전략을 사용한다. 새 대화 페이지는 큐의 끝에 추가된다. STM 큐가 최대 용량에 도달하면 가장 오래된 대화 페이지를 FIFO 원칙에 따라 STM에서 MTM으로 전송한다.

**MTM–LPM 갱신.** MTM 갱신은 세그먼트 삭제와 세그먼트에서 LPM으로의 갱신이라는 두 연산으로 이루어지며, 둘 다 다음과 같이 정의한 세그먼트의 Heat 점수를 기반으로 한다.
$$
Heat = \alpha \cdot N_{visit} + \beta \cdot L_{interaction} + \gamma \cdot R_{recency}. \tag{4}
$$

계수 $\alpha$, $\beta$, $\gamma$는 각 요인의 상대적 중요도를 정한다. $N_{visit}$은 세그먼트를 검색한 횟수이고, $L_{interaction}$은 세그먼트 안의 총 대화 페이지 수이며, $R_{recency}$는 현재 세그먼트의 마지막 검색 시점 이후 경과 시간을 나타내는 시간 감쇠 계수다. 이는 다음과 같이 정의한다.

$$
R_{recency} = \exp\left(-\frac{\Delta t}{\mu}\right),
$$

여기서 $\Delta t$는 마지막 접근 이후 경과 시간(초)이고, $\mu$는 구성 가능한 시간 상수(즉, $1e+7$)다. 이 세 지표, 즉 검색 횟수($N_{visit}$), 총 대화 페이지 수($L_{interaction}$), 시간 감쇠 계수($R_{recency}$)는 각각 빈번한 접근, 높은 상호작용, 최근 사용을 세그먼트 heat의 핵심 지표로 나타낸다. 세그먼트 길이가 최대 용량을 넘으면 heat가 가장 낮은 세그먼트를 퇴출한다. 이 메커니즘은 긴 사용자 대화에서 상호작용 빈도가 높은 주제를 MTM에 유지하고, 세그먼트 페이징 구조를 통해 해당 주제의 상세 대화 내용을 보존하게 한다.

**LPM 갱신.** heat가 임계값 $\tau$(즉, 5)를 넘는 세그먼트는 LPM으로 전송한다. 세그먼트와 그 대화 페이지는 User Traits, User KB, Agent Traits를 갱신한다. Li et al.(2025)의 사용자 특성을 따라, 기본 욕구 및 성격, AI alignment 차원, 콘텐츠 플랫폼 관심 태그의 세 범주에 걸친 90개 차원으로 개인화된 User Traits를 구성한다. 그런 뒤 LLM으로 세그먼트와 대화 페이지에서 이 차원을 추출·갱신하여 특성이 자율적으로 발전하게 한다.

동시에 사용자와 에이전트 보조자에 각각 관련된 사실 정보를 추출하여 User KB와 Agent Traits에 기록한다. User KB와 Assistant Traits는 모두 고정 크기 큐(즉, 100)를 유지하며 FIFO 전략을 사용한다. 메모리가 전이된 뒤 식 (4)의 페이지 수 $L_{interaction}$은 0으로 재설정되어 세그먼트 heat 점수가 낮아진다. 이는 중복 없이 페르소나가 계속 발전하게 한다.

### 3.4 메모리 검색 모듈

Memory Retrieval Module은 최근 맥락을 위한 STM, 세그먼트와 페이지 수준의 2단계 검색을 사용하는 MTM, 개인화 지식을 위한 LPM의 세 부분에서 정보를 검색한다. 사용자 질의가 주어지면, 이 모듈은 저장된 STM·MTM·LPM에서 응답 생성에 가장 관련된 정보를 검색한다. 이를 다음과 같이 정의한다.

$$
F_{Retrieval}(STM, MTM, LPM \mid Q). \tag{5}
$$

여기서 $F_{Retrieval}$은 세 메모리 저장 단위에 적용하는 검색 전략이다.

**STM 검색.** STM은 현재 대화의 가장 최근 맥락 메모리를 보유하므로 모든 대화 페이지를 검색한다.

**MTM 검색.** 심리학적 기억 회상 메커니즘(Yuan et al., 2024)에서 영감을 받아 2단계 검색을 사용한다. 먼저 식 (3)의 매칭 점수로 세그먼트를 선택하여 상위 $m$개 후보 세그먼트를 고른다. 다음으로 이 세그먼트 안에서 의미 유사도를 기준으로 가장 관련된 상위 $k$개 대화 페이지를 선택한다. 검색 뒤에는 세그먼트의 방문 카운터 $N_{visit}$와 최근성 요인 $R_{recency}$를 갱신한다.

**LPM 검색.** User KB와 Assistant Traits는 질의 벡터와 의미 관련성이 가장 높은 항목을 각각 상위 10개씩 배경 지식으로 검색한다. User Profile, Agent Profile, User Traits의 모든 정보도 사용한다. 이들은 각각 사용자 선호 정보, 에이전트 특성 정보, 사용자별 특성 정보를 저장한다.

### 3.5 응답 생성 모듈

사용자 질의가 주어지면 STM, MTM, LPM에서 위와 같이 검색한 세 종류의 내용과 사용자 질의를 통합해 최종 프롬프트를 구성하고, 이를 LLM의 최종 응답 생성 입력으로 사용한다. 최근 대화(STM), 관련 대화 페이지(MTM), 페르소나 정보(LPM)의 메모리를 함께 포함하면, 응답은 현재 상호작용과 맥락적으로 일관되게 유지되고, 깊이를 위해 과거 대화 상세 정보와 요약을 활용하며, 각각 사용자와 보조자의 정체성에 맞게 정렬된다. 그 결과 AI 에이전트 시스템은 일관되고 정확하며 개인화된 상호작용 경험을 제공할 수 있다.

## 4. 실험

### 4.1 실험 설정

**데이터셋.** 저자들은 GVD(Zhong et al., 2024)와 LoCoMo benchmark(Maharana et al., 2024) 데이터셋에서 실험했다. GVD 데이터셋은 15명의 가상 사용자와 보조자가 10일 동안 상호작용한 것을 시뮬레이션한 다중 턴 대화로 구성되며, 하루에 적어도 두 주제를 포함한다. LoCoMo benchmark는 장기 대화 기억 능력을 평가하도록 특별히 설계되었다. 대화 하나당 평균 300턴, 약 9K 토큰인 초장기 대화로 이루어진다. 질문은 LLM의 기억 능력을 체계적으로 평가하도록 Single-hop, Multi-hop, Temporal, Open-domain의 네 유형으로 분류된다.

**평가 지표.** GVD 데이터셋에는 Memory Retrieval Accuracy(Acc.), Response Correctness(Corr.), Contextual Coherence(Cohe.)의 세 지표를 사용한다. Memory Retrieval Accuracy는 이진 지표(0 또는 1)로 평가하고, Correctness와 Coherence는 3점 척도(0, 0.5 또는 1)로 평가한다. GVD의 모든 평가는 DeepSeek-R1(DeepSeek-AI et al., 2025)이 자동 채점한다. LoCoMo benchmark에서는 모델 성능 평가에 표준 F1과 BLEU-1(Papineni et al., 2002)을 사용한다.

**비교 방법.** MemoryOS는 다음의 대표적 메모리 방법과 비교한다.

**TiM(Think-in-Memory)(Liu et al., 2023).** 이 접근은 원시 대화 대신 추론 결과를 저장하여 인간의 기억을 모방한다. 응답 생성 전 locality-sensitive hashing(LSH)으로 관련 맥락을 검색하고, 사후 성찰로 메모리를 갱신한다. TiM은 삽입, 망각, 병합으로 메모리를 관리하여 중복 추론을 줄이고 일관성을 높인다.

**MemoryBank(Zhong et al., 2024).** 이 프레임워크는 Ebbinghaus 망각 곡선에 따라 메모리 강도를 동적으로 조정하여 시간에 따라 중요한 내용을 우선시한다. 또한 지속적인 상호작용 분석을 통해 사용자 초상을 구축하여 개인화된 응답을 지원한다.

**MemGPT(Packer et al., 2023).** 이 방법은 빠른 접근을 위한 주 컨텍스트와 장기 저장을 위한 외부 컨텍스트로 이루어진 이중 계층 메모리를 도입한다. 이 설계는 LLM의 고정 컨텍스트 창을 넘어 확장 가능한 메모리 확장을 가능하게 하는 것을 목표로 한다.

**A-Mem(Agentic Memory)(Xu et al., 2025).** 구조화된 노트를 동적으로 생성하고 연결해 상호 연결된 지식 네트워크를 형성한다. 이를 통해 LLM의 지속적인 메모리 발전과 적응적 관리를 가능하게 한다.

**MemoryOS.** 네 핵심 기능 모듈인 Memory Storage, Updating, Retrieval, Generation을 협조적으로 작동시키는 포괄적 메모리 관리 프레임워크다. MemoryOS는 장기 상호작용에서 대화 일관성과 사용자 페르소나 지속성을 달성한다.

**구현 세부사항.** 실험은 H20 GPU 8개를 장착한 하드웨어에서 수행했다. STM의 대화 페이지 큐 고정 길이는 7이다. MTM 세그먼트 최대 길이는 200으로 설정했다. User KB와 Agent Traits의 최대 용량은 모두 100개 항목으로 설정했다. MTM에서 LPM으로 보내는 정보를 제어하는 미리 정한 Heat 임계값 $\tau$는 5다. 식 (4)의 $\alpha$, $\beta$, $\gamma$ 값은 모두 1로 설정했다. 메모리 검색에서 검색할 상위 $m$개 세그먼트 수는 5로 설정하고, 검색할 대화 페이지의 하이퍼파라미터 top-$k$는 GVD와 LoCoMo 데이터셋에서 각각 5와 10으로 설정했다. 식 (2)의 유사도 값 $\theta$는 0.6이고 시간 상수 $\mu$는 $1e+7$이다.

> 표 1. GVD 데이터셋 비교 결과. $\uparrow$는 높을수록 좋음을 뜻한다. 원문은 각 모델군의 최고 값을 굵게 표시했다.

| 모델 | 방법 | Acc. $\uparrow$ | Corr. $\uparrow$ | Cohe. $\uparrow$ |
| --- | --- | ---: | ---: | ---: |
| GPT-4o-mini | TiM | 84.5 | 78.8 | 90.8 |
|  | MemoryBank | 78.4 | 73.3 | 91.2 |
|  | MemGPT | 87.9 | 83.2 | 89.6 |
|  | A-Mem | 90.4 | 86.5 | 91.4 |
|  | **Ours** | **93.3** | **91.2** | **92.3** |
|  | Improvement (%) | $3.2\%\uparrow$ | $5.4\%\uparrow$ | $1.0\%\uparrow$ |
| Qwen2.5-7B | TiM | 82.2 | 73.2 | 85.5 |
|  | MemoryBank | 76.3 | 70.3 | 82.7 |
|  | MemGPT | 85.1 | 80.2 | 86.9 |
|  | A-Mem | 87.2 | 79.5 | 87.8 |
|  | **Ours** | **91.8** | **82.3** | **90.5** |
|  | Improvement (%) | $5.3\%\uparrow$ | $3.5\%\uparrow$ | $3.1\%\uparrow$ |

### 4.2 주요 결과

GVD와 LoCoMo benchmark 데이터셋의 실험 결과는 표 1과 표 2에 제시했다. 저자들은 다음을 관찰했다.

1. 모든 메모리 방법 중 MemoryBank의 성능이 가장 나쁘다. 이는 메모리 감쇠 메커니즘만 적용해서는 대화 메모리를 효과적으로 관리하기에 부족함을 보여 준다. TiM은 원시 턴이 아니라 ‘생각(thoughts)’을 저장하여 반복 추론을 완화하므로 MemoryBank보다 좋지만, 단일 단계 해시 검색으로는 주제 간 의존성을 보존할 수 없다.

2. A-Mem과 MemGPT는 장문 대화에서 비교적 강한 성능을 보이지만, 둘 다 체계적 메모리 관리 메커니즘이 부족하여 문제가 생긴다. 예를 들어 MemGPT는 OS 방식 페이징으로 컨텍스트를 확장하지만, 평면 FIFO 큐는 대화가 길어질수록 주제를 섞는다. A-Mem은 기억을 그래프로 조직하여 의미를 풍부하게 하지만, 무거운 다단계 링크 생성은 지연 시간과 오류 누적을 키운다. 반대로 MemoryOS는 heat 기반 퇴출과 페르소나 모듈이 있는 세그먼트 페이징을 통해 계층형 STM/MTM/LPM 아키텍처를 결합한다. 따라서 주제에 맞는 내용에 계속 접근할 수 있으며 사용자별 선호도와의 일관성도 유지한다.

3. 제안한 MemoryOS는 계층형 저장 설계, 의미 검색 능력, 페르소나 기반 동적 갱신 덕분에 모든 벤치마크 데이터셋에서 우수한 성능을 달성한다. 이는 일관되고 정확한 메모리 관리를 보장한다. 특히 더 어려운 메모리 관리 과제에서 이점이 두드러진다. 예를 들어 GPT-4o-mini 기반 LoCoMo benchmark에서 F1 점수는 평균 49.11%, BLEU-1은 평균 46.18% 개선했다. 모든 방법이 더 높은 baseline 정확도를 얻는 더 쉬운 GVD 데이터셋에서도, MemoryOS는 SOTA baseline A-Mem보다 정확도에서 3.2% 높아 의미 일관성이 필요한 복잡한 장문 맥락 과제를 강건하게 처리함을 보였다.

4. 모델 효율성 평가는 소비 토큰 수(메모리 검색에서)와 각 응답의 평균 LLM 호출 수라는 두 지표로 수행했다. 표 3과 같이 제안 방법은 두 측면 모두에서 상위 2개 baseline(MemGPT, A-Mem)을 앞선다. A-Mem*보다 필요한 LLM 호출 수가 유의하게 적고(4.9 대 13), MemGPT보다 토큰 소비량이 훨씬 낮다(3,874 대 16,977).

> 표 2. LoCoMo 데이터셋의 범주별 점수와 평균 순위 비교. A-Mem은 원 논문에 보고된 결과이며, A-Mem*은 제안 모델과 같은 실험 환경에서 저자들이 구현해 얻은 결과다. $\uparrow$는 높을수록 좋고, `—`는 원문에서 보고되지 않은 값이다.

| 모델 | 방법 | Single Hop F1 | BLEU-1 | Multi Hop F1 | BLEU-1 | Temporal F1 | BLEU-1 | Open Domain F1 | BLEU-1 | 평균 순위(F1) | 평균 순위(BLEU-1) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4o-mini | TiM | 16.25 | 13.12 | 18.43 | 17.35 | 8.35 | 7.32 | 23.74 | 22.05 | 3.8 | 4.0 |
|  | MemoryBank | 5.00 | 4.77 | 9.68 | 6.99 | 5.56 | 5.94 | 6.61 | 5.16 | 5.0 | 5.0 |
|  | MemGPT | 26.65 | 17.72 | 25.52 | 19.44 | 9.15 | 7.44 | 41.04 | 34.34 | 2.2 | 2.5 |
|  | A-Mem | 27.02 | 20.09 | 45.85 | 36.67 | 12.14 | 12.00 | 44.65 | 37.06 | — | — |
|  | A-Mem* | 22.61 | 15.25 | 33.23 | 29.11 | 8.04 | 7.81 | 34.13 | 27.73 | 3.0 | 2.5 |
|  | **Ours** | **35.27** | **25.22** | **41.15** | **30.76** | **20.02** | **16.52** | **48.62** | **42.99** | **1.0** | **1.0** |
|  | Improvement (%) | $32.35\%\uparrow$ | $42.33\%\uparrow$ | $23.83\%\uparrow$ | $5.67\%\uparrow$ | $118.80\%\uparrow$ | $111.52\%\uparrow$ | $18.47\%\uparrow$ | $25.19\%\uparrow$ | — | — |
| Qwen2.5-3B | TiM | 4.37 | 5.01 | 2.54 | 3.21 | 6.20 | 5.37 | 6.35 | 7.34 | 4.3 | 3.5 |
|  | MemoryBank | 3.60 | 3.39 | 1.72 | 1.97 | 6.63 | 6.58 | 4.11 | 3.32 | 4.8 | 4.8 |
|  | MemGPT | 5.07 | 4.31 | 2.94 | 2.95 | 7.04 | 7.10 | 7.26 | 5.52 | 2.8 | 3.8 |
|  | A-Mem | 12.57 | 9.01 | 27.59 | 25.07 | 7.12 | 7.28 | 17.23 | 13.12 | — | — |
|  | A-Mem* | 10.31 | 8.76 | 16.31 | 11.07 | 6.94 | 7.31 | 12.34 | 10.62 | 2.3 | 2.0 |
|  | **Ours** | **23.26** | **15.39** | **21.44** | **14.95** | **10.18** | **8.18** | **26.23** | **22.39** | **1.0** | **1.0** |
|  | Improvement (%) | $125.61\%\uparrow$ | $75.68\%\uparrow$ | $31.45\%\uparrow$ | $35.05\%\uparrow$ | $46.69\%\uparrow$ | $11.90\%\uparrow$ | $112.56\%\uparrow$ | $110.83\%\uparrow$ | — | — |

> 그림 2. GVD 및 LoCoMo benchmark 데이터셋에서의 절제 연구. (a)는 GPT-4o-mini 기반 GVD의 Retrieval Accuracy, Correctness, Coherence를, (b)는 GPT-4o-mini 기반 LoCoMo의 Single Hop, Multi Hop, Temporal, Open Domain F1을 보인다. 범례의 구성은 `w/o MemoryOS`, `w/o MTM`, `w/o LPM`, `w/o Chain`, `MemoryOS`다.

그림 안의 막대 수치는 다음과 같다.

| 구성 | GVD Retrieval Acc. | GVD Correctness | GVD Coherence |
| --- | ---: | ---: | ---: |
| w/o MemoryOS | 2.7 | 6.8 | 57.3 |
| w/o MTM | 40.4 | 46.6 | 63.2 |
| w/o LPM | 79.3 | 76.5 | 73.3 |
| w/o Chain | 89.3 | 88.5 | 91.3 |
| MemoryOS | 93.3 | 91.2 | 92.3 |

| 구성 | LoCoMo Single Hop F1 | Multi Hop F1 | Temporal F1 | Open Domain F1 |
| --- | ---: | ---: | ---: | ---: |
| w/o MemoryOS | 1.16 | 1.47 | 1.52 | 4.56 |
| w/o MTM | 15.23 | 12.12 | 6.31 | 17.39 |
| w/o LPM | 25.50 | 30.87 | 17.81 | 30.57 |
| w/o Chain | 31.42 | 38.21 | 20.30 | 45.90 |
| MemoryOS | 35.27 | 41.15 | 20.02 | 48.62 |

> 표 3. LoCoMo benchmark의 효율성 분석(LLM 호출 횟수와 회상한 토큰 수로 정량화). 원문은 각 열의 최고 값을 굵게 표시했다.

| 방법 | Tokens | Avg. Calls | Avg. F1 |
| --- | ---: | ---: | ---: |
| MemoryBank | 432 | 3.0 | 6.84 |
| TiM | 1,274 | 2.6 | 18.01 |
| MemGPT | 16,977 | 4.3 | 29.13 |
| A-Mem* | 2,712 | 13.0 | 26.55 |
| **Ours** | **3,874** | **4.9** | **36.23** |

### 4.3 절제 연구

프레임워크의 각 핵심 모듈 기여를 평가하기 위해, 저자들은 Mid-Term Memory(-MTM), Long-term Persona Module(-LPM), Dialogue page Chain(-Chain), 전체 메모리 시스템(-MemoryOS)의 세 핵심 구성 요소를 각각 제거하는 절제 연구를 수행했다. 결과는 그림 2에 제시했다. 메모리 시스템은 긴 대화 중 응답 품질에 핵심적 역할을 하며, MemoryOS가 없으면 모델 성능이 크게 떨어진다. MemoryOS 안에서는 Mid-Term Memory(MTM)의 영향이 가장 크고, Long-Term Memory(LPM)가 그다음이며, Chain의 영향은 가장 작다.

### 4.4 하이퍼파라미터 분석

저자들은 Mid-Term Memory(MTM)에서 검색할 top-$k$ 대화 페이지가 모델 성능에 미치는 영향을 분석했다. 그림 3과 같이 LoCoMo benchmark에서 하이퍼파라미터 $k$를 $k = \{5, 10, 20, 30, 40\}$으로 달리 설정하면 $k$가 커질수록 모델 성능이 개선되지만, 임계값을 넘으면 개선 폭이 줄어든다. 더 많은 페이지를 검색하면 모델 성능을 높일 수 있지만, 지나친 내용은 노이즈를 도입해 성능에 악영향을 줄 수 있다. 저자들은 계산 오버헤드를 최소화하면서 비교적 좋은 성능을 얻기 위해 $k=10$으로 설정했다.

> 그림 3. LoCoMo benchmark에서 하이퍼파라미터 $k$(MTM에서 검색한 페이지 수)의 영향. (a) Single Hop, (b) Multi Hop, (c) Temporal, (d) Open Domain의 F1과 BLEU-1을 $k=5, 10, 20, 30, 40$에서 비교한다.

그래프의 수치는 다음과 같다.

| $k$ | Single Hop F1 | BLEU-1 | Multi Hop F1 | BLEU-1 |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 25.13 | 16.32 | 25.42 | 14.82 |
| 10 | 35.27 | 25.22 | 41.15 | 30.76 |
| 20 | 37.82 | 27.37 | 42.56 | 32.89 |
| 30 | 38.32 | 28.35 | 44.75 | 35.54 |
| 40 | 37.98 | 26.95 | 43.68 | 34.01 |

| $k$ | Temporal F1 | BLEU-1 | Open Domain F1 | BLEU-1 |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 8.45 | 12.11 | 29.32 | 21.21 |
| 10 | 20.02 | 16.52 | 48.62 | 42.99 |
| 20 | 23.12 | 17.31 | 49.52 | 44.65 |
| 30 | 25.12 | 19.87 | 49.61 | 44.38 |
| 40 | 24.58 | 19.31 | 47.74 | 43.63 |

### 4.5 사례 연구

사용자의 장기 기억 유지가 대화 일관성을 어떻게 높이는지, 특히 메모리 시스템의 역할을 시각적으로 보이기 위해 저자들은 그림 4에 사례 연구를 제시한다. 대화 이력에 기반하여 기본 LLM의 응답과 MemoryOS를 갖춘 LLM의 응답을 비교한다. MemoryOS는 사용자의 장기 대화와 선호를 회상하는 뛰어난 능력을 보인다.

> 그림 4. 메모리 관리 시스템 도입의 긍정적 효과를 보이는 사례 연구. 왼쪽은 기본 LLM, 오른쪽은 MemoryOS를 사용한 경우다.
>
> **대화 이력**
>
> - 사용자: 지난주 습지 공원에 갔는데, 그곳 풍경이 아름다웠어.
> - 사용자: 나무에서 많은 작은 다람쥐가 뛰어다녔어. 정말 귀여웠어.
> - 사용자: 공원에서 두 바퀴 뛰었는데 기분이 아주 좋았어. 더 날씬해지려고 계속 운동할 거야.
> - AI: 편안한 경험이었겠네요!
> - AI: 저는 다람쥐를 좋아해요. 다람쥐는 건강한 환경의 신호니까요.
> - AI: 운동은 건강에 좋아요. 계속 동기를 유지하도록 도와드릴게요!
>
> **몇 주 뒤**
>
> | 사용자 발화 | MemoryOS 없이 | MemoryOS 사용 |
> | --- | --- | --- |
> | 지난주 습지 공원에 갔는데, 그곳 풍경이 아름다웠어. | 미안하지만 공원 이야기를 한 것은 기억나지 않아요. | 아름다운 풍경을 보고, 달리기를 하고, 다람쥐를 봤다고 하셨죠. |
> | 햄버거가 먹고 싶은데, 추천해 줄래? | 데리야키 치킨 버거요. 아주 맛있어요! | 치즈버거는 […]. 다만 운동 중이라는 점은 잊지 마세요! |

그림 4는 처음 몇 주 전에 언급한 “습지 공원에 갔다”는 내용에서, MemoryOS가 “풍경을 보고, 달리고, 습지 공원에서 다람쥐를 발견했다” 같은 세부사항을 회상함을 보인다. 이 세부사항은 중기 메모리의 세그먼트-페이지 저장과 대화 페이지 체인이 서로 작용하고 보완하여 검색된다. 또한 시스템은 개인화 모듈을 통합하므로, 사용자의 “건강해지고 싶다”는 목표를 기억하고 사용자가 햄버거를 먹고 싶다고 말할 때 “날씬해지고 싶다고 했던 것을 잊지 마세요”라고 능동적으로 상기할 수 있다. 이는 대화 일관성과 사용자 경험을 높이는 메모리 모듈의 결정적 역할을 강조한다.

## 5. 결론

저자들은 운영체제의 메모리 관리 메커니즘에서 영감을 받아 AI 에이전트를 위한 새로운 메모리 관리 시스템 MemoryOS를 선구적으로 제안한다. 계층형 메모리 저장 아키텍처로 구현한 MemoryOS는 긴 대화에서 고정 컨텍스트 창의 한계를 다룬다. 대화 이력에 OS 방식 세그먼트-페이징 저장을 적용함으로써, MemoryOS는 heat 기반 퇴출로 메모리 계층 전반의 중요한 정보를 동적으로 우선시하고, 효율적인 메모리 저장·갱신·의미 검색을 가능하게 한다.

통합 페르소나 모듈은 개인화된 특성 추출로 변화하는 사용자 선호를 포착하여, 응답이 장기 대화 맥락에 맞게 정렬되도록 한다. OS 원리와 AI 메모리 관리를 연결함으로써 MemoryOS는 LLM이 확장된 상호작용에 걸쳐 일관되고 개인화된 대화를 지속하게 하고, 실제 응용에서 사람 같은 대화 능력을 향상한다.

## 참고문헌

- André Bensoussan, C. T. Clingen, and R. C. Daley. 1972. *The multics virtual memory: Concepts and design.* Communications of the ACM, 15(5):308–318.
- Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, and Deshraj Yadav. 2025. *Mem0: Building production-ready AI agents with scalable long-term memory.* arXiv preprint arXiv:2504.19413.
- DeepSeek-AI, Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, Xiaokang Zhang, Xingkai Yu, Yu Wu, Z. F. Wu, Zhibin Gou, Zhihong Shao, Zhuoshu Li, Ziyi Gao, and 5 others. 2025. *DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning.* Preprint, arXiv:2501.12948.
- Peter J. Denning. 1970. *Virtual memory.* ACM Computing Surveys, 2(3):153–189.
- Yiming Du, Wenyu Huang, Danna Zheng, Zhaowei Wang, Sebastien Montella, Mirella Lapata, Kam-Fai Wong, and Jeff Z Pan. 2025. *Rethinking memory in AI: Taxonomy, operations, topics, and future directions.* arXiv preprint arXiv:2505.00675.
- Le Huang, Hengzhi Lan, Zijun Sun, Chuan Shi, and Ting Bai. 2024. *Emotional RAG: Enhancing role-playing agents through emotional retrieval.* In 2024 IEEE International Conference on Knowledge Graph (ICKG), pages 120–127.
- Hao Li, Chenghao Yang, An Zhang, Yang Deng, Xiang Wang, and Tat-Seng Chua. 2024. *Hello again! LLM-powered personalized agent for long-term dialogue.* arXiv preprint arXiv:2406.05925.
- Jia-Nan Li, Jian Guan, Songhao Wu, Wei Wu, and Rui Yan. 2025. *From 1,000,000 users to every user: Scaling up personalized preference for user-level alignment.* Preprint, arXiv:2503.15463.
- Lei Liu, Xiaoyan Yang, Yue Shen, Binbin Hu, Zhiqiang Zhang, Jinjie Gu, and Guannan Zhang. 2023. *Think-in-memory: Recalling and post-thinking enable LLMs with long-term memory.* arXiv preprint arXiv:2311.08719.
- Adyasha Maharana, Dong-Ho Lee, Sergey Tulyakov, Mohit Bansal, Francesco Barbieri, and Yuwei Fang. 2024. *Evaluating very long-term conversational memory of LLM agents.* In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 13851–13870, Bangkok, Thailand. Association for Computational Linguistics.
- Felix Ocker, Jörg Deigmöller, Pavel Smirnov, and Julian Eggert. 2025. *A grounded memory system for smart personal assistants.* Preprint, arXiv:2505.06328.
- Charles Packer, Vivian Fang, Shishir G. Patil, Kevin Lin, Sarah Wooders, and Joseph E. Gonzalez. 2023. *MemGPT: Towards LLMs as operating systems.*
- Kishore Papineni, Salim Roukos, Todd Ward, and Wei Jing Zhu. 2002. *BLEU: A method for automatic evaluation of machine translation.* In Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics, pages 311–318.
- Joon Sung Park, Joseph O'Brien, Carrie Jun Cai, Meredith Ringel Morris, Percy Liang, and Michael S. Bernstein. 2023. *Generative agents: Interactive simulacra of human behavior.* In Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology, pages 1–2.
- Bing Wang, Xinnian Liang, Jian Yang, Hui Huang, Shuangzhi Wu, Peihao Wu, Lu Lu, Zejun Ma, and Zhoujun Li. 2025. *SCM: Enhancing large language model with self-controlled memory framework.* Preprint, arXiv:2304.13343.
- Yaxiong Wu, Sheng Liang, Chen Zhang, Yichao Wang, Yongyue Zhang, Huifeng Guo, Ruiming Tang, and Yong Liu. 2025. *From human memory to AI memory: A survey on memory mechanisms in the era of LLMs.* arXiv preprint arXiv:2504.15965.
- Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, and Yongfeng Zhang. 2025. *A-Mem: Agentic memory for LLM agents.* arXiv preprint arXiv:2502.12110.
- Peiwen Yuan, Xinglin Wang, Shaoxiong Feng, Boyuan Pan, Yiwei Li, Heda Wang, Xupeng Miao, and Kan Li. 2024. *Generative dense retrieval: Memory can be a burden.* In Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers), St. Julian's, Malta. Association for Computational Linguistics.
- Zeyu Zhang, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Quanyu Dai, Jieming Zhu, Zhenhua Dong, and Ji-Rong Wen. 2024. *A survey on the memory mechanism of large language model-based agents.* arXiv preprint arXiv:2404.13501.
- Yan Zheng, Tong Zou, and Xingyan Wang. 2020. *Segment-page-combined memory management technology based on a homegrown many-core processor.* CCF Transactions on High Performance Computing, 2(4):376–381.
- Wanjun Zhong, Lianghong Guo, Qiqi Gao, He Ye, and Yanlin Wang. 2024. *MemoryBank: Enhancing large language models with long-term memory.* In Proceedings of the AAAI Conference on Artificial Intelligence, volume 38, pages 19724–19731.
