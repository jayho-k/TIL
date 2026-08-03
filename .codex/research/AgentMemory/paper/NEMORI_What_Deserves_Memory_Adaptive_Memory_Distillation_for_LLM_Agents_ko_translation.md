# NEMORI: 무엇이 기억될 가치가 있는가 — LLM 에이전트를 위한 적응형 메모리 증류

> Wenquan Ma, Jiayan Nan, Wenlong Wu, Yize Chen, *What Deserves Memory: Adaptive Memory Distillation for LLM Agents*, arXiv:2508.03341v4 (2026-04-16).
>
> 원문 PDF 24쪽을 기반으로 한 한국어 번역 노트다. 모델명·수식·API·데이터셋·인용 표기는 원문을 유지한다.

## 초록

LLM 에이전트의 메모리 시스템은 무엇을 보존해야 하는지 판단하기 어렵다. 기존 방법은 중요도 점수, 감정 태그, 사실 템플릿처럼 미리 정한 휴리스틱에 의존하며, 데이터에서 배우기보다 설계자 직관을 부호화한다. 저자들은 인지과학 아이디어에서 영감을 받은 적응형 메모리 증류 프레임워크 **NEMORI**를 제안한다. 이 방법은 경험의 미래 효용을 예측 가능성 문제로 본다. Episodic Memory Integration은 원시 상호작용을 일관된 서사로 바꾸고, Semantic Knowledge Distillation은 예측 오차로 통찰을 추출한다. 프레임워크는 증류에 집중하므로 이후 관리 방식에는 독립적이다. 실험에서 NEMORI는 강한 성능·효율·저장 공간 절감을 보였고, 상호작용 순서의 내재적 성질을 관찰하는 방식이 휴리스틱 메모리 설계의 데이터 기반 대안임을 제시한다. 코드: <https://github.com/nemori-ai/nemori>.

## 1. 서론

고정 상태가 없는 LLM은 선형으로 늘어나는 상호작용 궤적에 의존하지만 컨텍스트 창은 유한하고 Lost in the Middle 현상도 있어, 장기 행동 일관성 유지가 어렵다. 개인 비서·자율 에이전트·개인화 추천처럼 지속적 상호작용을 요구하는 실제 응용은 늘고 있으며, 실시간 컨텍스트 조절을 위한 메모리 시스템이 중요한 접근으로 자리 잡았다.

메모리 시스템은 미래 응답 생성에 쓸 경험을 식별한다. 이 과정은 경험의 저장 형태를 정하는 **증류(distillation)** 와, 지속적 유지 관리를 보장하는 **관리(management)** 로 나뉜다. 관리 중심 방법은 항목을 불투명 컨테이너로 보고 접근 빈도, 시간 감쇠, 명시적 관계 같은 구조 메타데이터로 효용을 추론한다. 반대로 증류 중심 방법은 항목이 들어올 때 형태를 선택적으로 만든다. 이는 유연하지만 미래 효용의 불확실성에 맞서야 한다. 기존 증류 방법은 중요도 점수·감정 태그·사실 템플릿으로 설계자 직관을 넣는다. 이런 휴리스틱은 비가역적 정보 왜곡이나 과도한 저장, 검색 노이즈를 유발할 수 있다.

Predictive Coding Theory에 영감을 받아, NEMORI는 기존 지식으로 예측하지 못한 새 관측을 적응형 메모리 증류 대상으로 삼는다. 그림 1처럼 메모리 구조·표현·증류에 관한 세 간결한 prior가 프레임워크를 이끌며, Complementary Learning Systems를 반영한 두 cascade 모듈로 구성된다. Episodic Memory Integration은 원시 상호작용 순서를 일관된 일화 서사로 바꾸고, Semantic Knowledge Distillation은 기존 지식이 예상하지 못한 새 경험을 뽑는다. NEMORI는 management-agnostic이며, 기본 관리 시스템도 제공한다.

기여는 다음과 같다.

1. 메모리 구성에서 증류와 관리를 구분해 정식화하고, 일반 데이터 성질·인지 아이디어에서 증류 설계를 위한 prior를 이끈다.
2. 관리 방식에 독립적인 적응형 메모리 증류 프레임워크 NEMORI와 기본 관리 시스템을 구현한다.
3. 긴 컨텍스트에서 특히 두드러지는 성능을 실험으로 보인다. 타사 관리 시스템과 결합하면 성능을 유지하며 A-MEM·MemoryOS의 저장량을 45~54% 줄인다.

> 표 1. 메모리 효용을 평가하는 시점에 따른 에이전트 메모리 시스템 분류. Retrieval-time은 평가를 질의 시점으로 미루고, management-time은 접근 패턴으로 사후 필터링하며, distillation-time은 입력 시점에 평가한다. NEMORI는 사전 휴리스틱 대신 prediction error로 증류 시점에 평가한다.

| 범주 | 방법 | 증류 | 관리 | 검색 |
| --- | --- | --- | --- | --- |
| Retrieval-time | Lewis et al. (2020) | — | — | Similarity search |
| Management-time | Packer et al. (2023) | — | Tiered storage | Function calls |
|  | Zhong et al. (2024) | — | Summary + forgetting | — |
|  | Kang et al. (2025) | — | Heat scoring | Two-step search |
|  | Li et al. (2025b) | — | Hierarchical summary | Multi-step search |
|  | Anokhin et al. (2025) | — | Graph update | Graph spreading |
|  | Xu et al. (2025) | — | Adaptive note linking | — |
|  | Rasmussen et al. (2025) | — | Validity management | Reranking |
| Distillation-time | Park et al. (2023) | Importance scoring | Reflection trees | Weighted scoring |
|  | Huang et al. (2024) | Emotion tagging | — | Emotion matching |
|  | Chhikara et al. (2025) | Facts extraction | — | — |
|  | Li et al. (2025a) | Summary + persona | — | Noun overlap |
|  | Pan et al. (2025) | Topic | Token compression | — |
|  | 본 논문 | Prediction error | Agnostic | — |

## 2. 관련 연구

### 2.1 LLM 에이전트 메모리

에이전트 메모리 시스템은 무엇을 보존할지의 증류, 어떻게 조직할지의 관리, 어떻게 내용을 꺼낼지의 검색으로 나뉜다. 순수 RAG는 질의 시점까지 판단을 미루지만, 메모리 시스템은 증류 때 메타데이터로 데이터를 풍부하게 만들고 이후 관리·검색에 쓴다. management-time 방법은 decay weight, 계층 저장, 접근 빈도, 관계 연결로 사후 내용을 보강한다. distillation-time 방법은 중요도 점수, 감정 태그, 사실 추출로 입력 단계에서 보강한다.

### 2.2 인지적 메모리 원리

시각 신경과학에서 출발한 Predictive Coding Theory는 상위 피질 영역이 아래로 예측을 보내고, 하위 영역은 주로 잔차인 prediction error를 위로 전달한다고 본다. Friston은 이를 지각·행동·학습을 아우르는 Free Energy Principle로 일반화했고, Clark은 뇌가 근본적으로 예측 기계라고 주장했다. NEMORI는 이 통찰을 에이전트 메모리 설계에 적용한다. prediction error는 보존할 가치가 있는 정보를 나타내며, 예측 가능한 내용은 중복이다.

## 3. 방법론

NEMORI는 인지 아이디어에서 영감 받은 adaptive memory distillation 프레임워크다. A-MEM·MemoryOS 같은 **native 또는 타사 메모리 시스템을 보완하는 증류 층으로 쓸 수 있다.**

> 그림 1. NEMORI 개요. 세 prior가 두 cascade 모듈을 이끈다. 위쪽 Episodic Memory Integration은 원시 상호작용을 일관된 narrative episode로 바꾸고, 아래쪽 Semantic Knowledge Distillation은 prediction error로 통찰을 뽑는다. 이 프레임워크는 native·타사 management system을 보완하는 distillation layer로 동작한다.

### 3.1 개요와 동기

**구조 prior: 일화의 완결성.** 상호작용 순서는 자연스러운 묶음을 보인다. 한 episodic group 안의 상호작용은 서로 맥락을 제공하며, 더 세밀하거나 임의의 분할은 해석 가능하게 하는 맥락을 끊는다. 따라서 잠재적 완결성을 존중하는 episode를 정의해야 하며 휴리스틱 chunking을 강제해서는 안 된다.

**표현 prior: 관점의 비대칭성.** 메모리는 회상을 위해 존재한다. 회상은 사건의 allocentric 재구성이자 추론의 한 형태인 반면, 원시 episode는 egocentric하고 본질적으로 noisy하다. 따라서 원시 episode를 중요한 세부를 보존하면서 논리 구조를 부각하는 narrative 표현으로 바꿔야 한다.

**증류 prior: 예측 가능성은 중복을 뜻한다.** 상호작용 순서의 정보는 매우 중복된다. predictive coding 관점에서 예상 밖 정보는 메모리 consolidation의 자연스러운 후보이다. 따라서 실제 상호작용과 기존 지식에서 만든 anticipatory schema의 의미 차이를 검사해 메모리를 증류한다.

### 3.2 Episodic Memory Integration

이 모듈은 구조·표현 prior에 따라 원시 상호작용을 episodic memory로 통합하고 이후 증류를 준비한다. Local Message Partitioning, Narrative Episode Generation, Associative Memory Integration의 세 하위 모듈로 나뉜다.

#### 3.2.1 Local Message Partitioning

에이전트와 환경 상호작용을 message exchange 순서로 모델링하고 전용 buffer $B$를 유지한다. 시간 $t$의 $B_t=\{m_1,\dots,m_z\}$에서 $m_i=(r_i,c_i,t_i)$는 발신자·내용·타임스탬프다. 새 상호작용은 buffer 뒤에 추가한다. $|B_t|$가 observation window $w\in\mathbb{Z}^{+}$에 이르면 다음 partitioning을 수행한다.

$$
O\leftarrow f_{LLM}(P_{par}\oplus B_t).
$$

$P_{par}$는 window 안의 잠재적 완결성과 국소 뉘앙스를 구별해 메시지를 분할하도록 LLM에 지시한다. 출력 $O=\{O_1,\dots,O_n\}$는 $\{1,\dots,w\}$의 partition이며, index를 다시 buffer에 대응시켜 raw episode 집합 $P=\{P_1,\dots,P_n\}$을 만든다. $P$를 다음 모듈로 넘기고 buffer는 비운다.

#### 3.2.2 Narrative Episode Generation

각 raw episode $P_j$에서 semantic distillation용 narrative episode $N_j$와 episodic cue $c_j$를 생성한다.

$$
(N_j,c_j)\leftarrow f_{LLM}(P_{nar}\oplus P_j),\qquad v_j\leftarrow f_{emb}(c_j\oplus N_j).
$$

$P_{nar}$는 상호작용의 논리 구조와 구성 요소를 강조하도록 지시하고, $f_{emb}$는 embedding model이다. episodic memory는 $M_j=(c_j,N_j,P_j,v_j)$로 나타낸다. 이 설계는 효율을 위해 narrative $N$을 직접 반환하거나, 정밀도가 중요한 도메인에서는 raw $P$를 반환하는 이중 검색을 가능하게 한다. 이후 전체 파이프라인의 기본 처리 단위가 message가 아니라 episode가 되어 비용을 줄인다.

#### 3.2.3 Associative Memory Integration

observation window 제약으로 갈라졌을 episode를 동적으로 통합한다. 새 $M_j$마다 cosine similarity로 episodic database $D_e$의 상위 $K_e$ 후보를 검색한다.

$$
C=\{U_1,\dots,U_{K_e}\}\leftarrow Search(D_e,v_j,K_e).
$$

LLM은 $(c_j,N_j)$와 후보 $(c_k,N_k)$ 사이의 episodic continuity를 판단해 통합 대상 $idx$를 고른다. 대상이 있으면 두 memory를 하나의 새 cue·narrative·raw sequence·embedding으로 합쳐 기존 항목을 대체한다. 없으면 $M_j$를 독립 항목으로 넣는다. 결과 episodic memory를 semantic knowledge distillation으로 보낸다.

### 3.3 Semantic Knowledge Distillation

이 모듈은 distillation prior에 따라 episodic experience에서 semantic knowledge를 뽑는다. management-agnostic context evocation·knowledge consolidation interface를 정의하며 Anticipatory Schema Synthesis, Prediction Error Distillation, Agnostic Knowledge Consolidation으로 구성된다.

#### 3.3.1 Anticipatory Schema Synthesis

새 또는 통합된 입력 episodic memory $M_{in}$에 대해 관리 시스템 $M$을 abstract context provider로 보고, generic interface로 관련 context를 불러온다.
$$
S_{in}\leftarrow Evoke(M_{in},M).
$$
native 구현에서는 threshold-filtered similarity search를 사용한다. 이어 짧은 episode 요약 $c_{in}$과 이미 아는 context $S_{in}$만으로 실제 episode에서 무슨 일이 일어났을지 예측한다.

$$
\hat P_{in}\leftarrow f_{LLM}(P_{ant}\oplus c_{in}\oplus S_{in}).
$$

#### 3.3.2 Prediction Error Distillation

원시 episode $P_{in}$과 anticipatory schema $\hat P_{in}$의 차이에서 semantic insight를 뽑는다.

$$
K_{in}=\{k_1,\dots,k_d\}\leftarrow f_{LLM}(P_{dis}\oplus P_{in}\oplus\hat P_{in}).
$$

$P_{dis}$는 anticipatory schema에서 벗어나거나 이를 확장하는 정보를 insight로 추출하도록 지시한다.

#### 3.3.3 Agnostic Knowledge Consolidation

distilled $K_{in}$은 $Consolidate(K_{in},M)$ interface로 관리 시스템에 통합한다. native 구현에서 insight $k_q$마다 semantic database $D_s$에서 embedding $u_q=f_{emb}(k_q)$로 관련 지식을 검색한다. LLM은 관계를 판단해 `new`, `merge`, `conflict` directive를 만든다. `new`는 독립 항목 삽입, `merge`는 보완적인 기존 항목을 통합 내용으로 대체, `conflict`는 낡은 항목을 제거하고 새 insight로 대체한다.

### 3.4 응답 생성

메모리의 추론 시점 사용은 구성 절차와 대체로 직교하므로 다양한 retrieval strategy를 허용한다. 실험의 직접 설정에서는 질의 $Q$와 embedding $v_Q$로 episodic database에서 top-$k$ entry, semantic database에서 top-$m$ entry를 병렬 검색한다. 유사도 내림차순의 narrative episode $R_e$, 상위 $r$개 raw episode $R_p$, semantic knowledge $R_s$를 이어 붙여 다음을 생성한다.

$$
a\leftarrow f_{LLM}(P_{ans}\oplus Q\oplus R_e\oplus R_p\oplus R_s).
$$

## 4. 실험

실험은 성능(RQ1), 효율(RQ2), 구성 요소 민감도(RQ3), retrieval 구성(RQ4), 타사 management 통합(RQ5), 장문 확장성(RQ6)을 다룬다.

### 4.1 설정

LoCoMo는 평균 24K token의 대화 10개와 네 reasoning 범주 1,540개 질문으로 구성된다. LongMemEvalS는 평균 105K token 대화 500개로, 더 길고 현실적인 컨텍스트에서 확장성을 시험한다. baseline은 Full Context, RAG-4096, LangMem, Zep, Mem0, A-MEM, MemoryOS다. LoCoMo에서는 `gpt-4o-mini` judge의 LLM score와 F1·BLEU-1을, LongMemEvalS에서는 과업 특화 QA format에 맞춘 LLM-judge score를 쓴다. 지표는 0~100이고 높을수록 좋다.

Mem0·Zep은 commercial API로 memory context를 검색하고 `gpt-4o-mini`·`gpt-4.1-mini`가 답을 만든다. 나머지 방법과 NEMORI는 이 모델을 internal backbone과 answer generator로 모두 사용한다. NEMORI embedding은 `text-embedding-3-small`, similarity threshold $\tau=0.70$, $K_e=K_m=5$, $K_s=10$이다. retrieval은 $m=2k$, 본문 $k=10$, 실험 범위 $k=2$~30이며 상위 2 episodic memory만 원래 대화 text도 포함한다($r=2$).

### 4.2 주요 결과

> 표 2. LoCoMo 성능 비교. NEMORI는 평균 LLM score에서 `gpt-4.1-mini` 80.8, `gpt-4o-mini` 73.0을 얻었고, 각 모델 Full Context의 80.6·72.3도 앞섰다.

NEMORI는 `gpt-4.1-mini`에서 LangMem 73.4보다 10.1%, `gpt-4o-mini`에서 Mem0 61.3보다 19.1% 높은 평균 LLM score를 보인다. Temporal Reasoning에서도 77.3(`gpt-4.1-mini`, A-MEM 대비 +15.9%)과 67.6(`gpt-4o-mini`, Zep 대비 +14.8%)로 강하다. episode 중심 설계가 추론 부담 일부를 메모리 형성으로 앞당기고 경험의 논리 구조에 맞추기 때문이다. Open Domain은 가장 강한 방법보다 약간 낮은데, 이 유형은 memory와 backbone의 prior knowledge를 함께 요구한다.

**표 2. LoCoMo 성능 비교.** 각 칸은 `LLM / F1 / BLEU-1` 순서다. 밑줄은 NEMORI를 제외한 가장 강한 메모리 시스템, `Improv.`는 그 시스템에 대한 NEMORI의 상대 향상률(%)을 뜻한다.

| 모델 | 방법 | Temporal reasoning | Open domain | Multi-hop | Single-hop | 평균 |
| ---- | ---- | ------------------ | ----------- | --------- | ---------- | ---- |
| gpt-4.1-mini | Full Context | 74.2 / 47.5 / 40.0 | 56.6 / 28.4 / 22.2 | 77.2 / 44.2 / 33.7 | 86.9 / 61.4 / 53.4 | 80.6 / 53.3 / 45.0 |
|      | RAG-4096 | 27.4 / 22.3 / 19.1 | 28.8 / 17.9 / 13.9 | 31.7 / 20.1 / 12.8 | 35.9 / 25.8 / 22.0 | 32.9 / 23.5 / 19.2 |
|      | LangMem | 50.8 / 48.5 / 40.9 | 59.0 / 32.8 / 26.4 | 71.0 / 41.5 / 32.5 | 84.5 / 51.0 / 43.6 | 73.4 / 47.6 / 40.0 |
|      | Zep  | 60.2 / 23.9 / 20.0 | 43.8 / 24.2 / 19.3 | 53.7 / 30.5 / 20.4 | 66.9 / 45.5 / 40.0 | 61.6 / 36.9 / 30.9 |
|      | Mem0 | 56.9 / 39.2 / 33.2 | 47.9 / 23.7 / 17.7 | 68.2 / 40.1 / 30.3 | 71.4 / 48.6 / 42.0 | 66.3 / 43.5 / 36.5 |
|      | A-MEM | 66.7 / 40.3 / 33.7 | 37.5 / 13.4 / 12.7 | 55.7 / 30.4 / 20.0 | 64.0 / 45.0 / 39.8 | 61.4 / 39.4 / 33.2 |
|      | MemoryOS | 37.7 / 36.5 / 27.4 | 60.4 / 30.2 / 25.6 | 62.4 / 34.0 / 25.8 | 68.9 / 44.2 / 37.5 | 60.6 / 39.9 / 32.5 |
|      | **NEMORI** | **77.3 / 58.7 / 50.7** | **56.3 / 31.7 / 25.1** | **74.8 / 40.8 / 31.7** | **87.0 / 55.7 / 49.5** | **80.8 / 52.1 / 45.0** |
|      | Improv. | +15.9 / +1.0 / +4.0 | -4.8 / -3.3 / -4.9 | +3.5 / -1.0 / -2.5 | +2.5 / -9.3 / -7.3 | +10.1 / +9.5 / +12.5 |
| gpt-4o-mini | Full Context | 56.2 / 44.1 / 36.1 | 48.6 / 24.5 / 17.2 | 66.8 / 35.4 / 26.1 | 83.0 / 53.1 / 44.7 | 72.3 / 46.2 / 37.8 |
|      | RAG-4096 | 23.7 / 19.5 / 15.7 | 32.6 / 19.0 / 13.5 | 31.3 / 18.6 / 11.7 | 32.0 / 22.2 / 18.6 | 30.2 / 20.8 / 16.4 |
|      | LangMem | 24.9 / 31.9 / 26.2 | 47.6 / 29.4 / 23.5 | 52.4 / 33.5 / 23.9 | 61.4 / 38.8 / 33.1 | 51.3 / 35.8 / 29.4 |
|      | Zep  | 58.9 / 44.8 / 38.1 | 39.6 / 22.9 / 15.7 | 50.5 / 27.5 / 19.3 | 63.2 / 39.7 / 33.7 | 58.5 / 37.5 / 30.9 |
|      | Mem0 | 50.4 / 44.4 / 37.6 | 40.6 / 27.1 / 19.4 | 60.3 / 34.3 / 25.2 | 68.1 / 44.4 / 37.7 | 61.3 / 41.5 / 34.2 |
|      | A-MEM | 54.2 / 38.1 / 33.8 | 22.9 / 9.0 / 8.6 | 43.6 / 24.0 / 18.8 | 58.2 / 35.6 / 29.2 | 52.5 / 32.4 / 27.0 |
|      | MemoryOS | 38.0 / 38.5 / 27.5 | 45.8 / 26.0 / 19.2 | 52.5 / 35.2 / 24.1 | 62.5 / 43.7 / 37.7 | 54.5 / 39.9 / 31.9 |
|      | **NEMORI** | **67.6 / 57.3 / 47.6** | **45.8 / 23.9 / 18.5** | **61.7 / 38.1 / 26.0** | **81.9 / 54.8 / 43.8** | **73.0 / 50.3 / 39.7** |
|      | Improv. | +14.8 / +27.9 / +24.9 | -3.8 / -18.7 / -21.3 | +2.3 / +8.2 / +3.2 | -1.3 / +3.2 / -2.0 | +19.1 / +21.2 / +16.1 |



### 4.3 효율 분석

> 표 3. LoCoMo의 memory construction cost(`gpt-4o-mini`). NEMORI는 LLM 373.2회, input 277.2K, output 45.7K, 총 322.9K token을 사용하며 baseline보다 LLM call 59.5%, token 38.7%를 줄인다.

> 표 4. 응답 생성 비용. NEMORI는 평균 2,745 token, search 787ms, total 3,053ms로 Full Context(23,653 token, 5,806ms)보다 token 88%, 전체 지연 47%를 줄이면서 LLM score 73.0 대 72.3을 보인다.

전문 prompt가 여러 개인 복잡한 pipeline처럼 보이지만, 많은 baseline의 message-wise 처리 대신 episode를 기본 단위로 쓰기 때문에 구성 비용이 낮다.

**표 3. LoCoMo 메모리 구성 비용(`gpt-4o-mini`).** 마지막 세 열은 token 소비량이다.

| 방법 | LLM | 호출 횟수 | 입력(k) | 출력(k) | 총합(k) |
| --- | ---: | ---: | ---: | ---: | ---: |
| LangMem | 51.3 | 920.6 | 898.3 | 112.0 | 1,010.2 |
| Mem0 | 61.3 | 1,602.2 | 1,483.4 | 210.0 | 1,693.4 |
| A-MEM | 52.5 | 1,175.5 | 912.6 | 236.8 | 1,149.4 |
| MemoryOS | 54.5 | 1,016.1 | 404.5 | 122.0 | 526.5 |
| **NEMORI** | **73.0** | **373.2** | **277.2** | **45.7** | **322.9** |
| 향상률 | +19.1% | -59.5% | -31.5% | -62.5% | -38.7% |

**표 4. LoCoMo 응답 생성 비용(`gpt-4o-mini`).** Search는 메모리 검색 시간, Total은 질문 수신부터 답변 완료까지의 종단 간 지연이다.

| 방법 | LLM | Tokens | Search(ms) | Total(ms) |
| --- | ---: | ---: | ---: | ---: |
| Full Context | 72.3 | 23,653 | — | 5,806 |
| RAG-4096 | 30.2 | 3,430 | 544 | 2,884 |
| LangMem | 51.3 | 125 | 19,829 | 22,082 |
| Zep | 58.5 | 2,247 | 522 | 3,255 |
| Mem0 | 61.3 | 1,027 | 784 | 3,539 |
| A-MEM | 52.5 | 2,614 | 947 | 2,867 |
| MemoryOS | 54.5 | 1,560 | 9,910 | 15,220 |
| **NEMORI** | **73.0** | **2,745** | **787** | **3,053** |

### 4.4 절제 연구

prediction error 기반 증류의 `w/o e`는 direct distillation인 Nemori-s보다 높다. `gpt-4o-mini`에서 65.0 대 52.0(+25.0%), `gpt-4.1-mini`에서 74.9 대 65.5(+14.4%)다. native management 유무는 LoCoMo에서 변화가 작지만, 실제 배포에서 knowledge update가 많을 수 있어 유지한다. episodic·semantic retrieval은 상보적이다. episodic을 빼면 73.0→65.0, 80.8→74.9로, semantic을 빼면 73.0→54.7, 80.8→76.9로 낮아진다. adaptive partitioning을 fixed 20-message chunk로 바꾼 `w/o p`도 성능이 떨어진다.

> 그림 2. $w=5$~40 observation window에서 gpt-4.1-mini LoCoMo 성능은 80.4, 80.7, 80.8(default $w=20$), 81.2, 80.7로 안정적이다.

**표 5. LoCoMo 절제 연구.** `w/o NEMORI`는 NEMORI를 쓰지 않음, `Nemori-s`는 semantic-only 직접 증류, `w/o e`는 episodic retrieval 제외, `w/o s`는 semantic retrieval 제외, `w/o p`는 adaptive partitioning을 제외하고 20-message chunk를 고정 사용한다. Native/Naive RAG의 의미는 부록 A.2와 같다.

| 모델 | 구성 / 관리 | LLM | F1 | BLEU |
| --- | --- | ---: | ---: | ---: |
| gpt-4o-mini | w/o NEMORI | 0.6 | 0.5 | 0.9 |
|  | Nemori-s / Native | 51.7 | 36.4 | 28.9 |
|  | Nemori-s / Naive RAG | 52.0 | 36.6 | 29.1 |
|  | w/o e / Native | 64.6 | 46.2 | 37.1 |
|  | w/o e / Naive RAG | 65.0 | 46.2 | 36.9 |
|  | w/o s | 54.7 | 39.6 | 31.7 |
|  | w/o p | 68.0 | 47.4 | 36.8 |
|  | NEMORI | 73.0 | 50.3 | 39.7 |
| gpt-4.1-mini | w/o NEMORI | 1.2 | 1.6 | 1.5 |
|  | Nemori-s / Native | 66.0 | 41.4 | 34.9 |
|  | Nemori-s / Naive RAG | 65.5 | 41.1 | 34.1 |
|  | w/o e / Native | 74.7 | 48.2 | 40.9 |
|  | w/o e / Naive RAG | 74.9 | 48.1 | 40.7 |
|  | w/o s | 76.9 | 50.0 | 42.9 |
|  | w/o p | 75.7 | 48.1 | 40.9 |
|  | NEMORI | 80.8 | 52.1 | 45.0 |

### 4.5 Retrieval 하이퍼파라미터

그림 3에서 top-$k$는 2에서 10까지 빠르게 좋아진 뒤 Full Context를 넘는 안정 구간에 도달한다. 단순 Top-K와 작은 retrieval count만으로 포화하므로, NEMORI의 증류가 memory noise를 완화함을 뜻한다. narrative episode embedding은 반환 내용을 고정해도 raw episode embedding보다 높다(76.9 대 76.4: narrative 반환, 77.0 대 75.3: raw 반환).

> 그림 3. `gpt-4o-mini`(왼쪽)와 `gpt-4.1-mini`(오른쪽)의 LLM score에 대한 retrieval count $k$의 효과. 점선은 Full Context baseline이며, 주석 점은 본문 기본값 $k=10$이다.

**표 6. LoCoMo retrieval strategy 절제 연구(`gpt-4.1-mini`).** N=narrative episode, P=raw(partitioned) episode. Index는 embedding source, Retrieve는 LLM에 반환한 내용을 뜻한다. Retrieve=N이면 상위 2 narrative에 raw도 추가한다.

| Index | Retrieve | LLM | F1 | BLEU |
| --- | --- | ---: | ---: | ---: |
| N | N | 76.9 | 50.0 | 42.9 |
| P | N | 76.4 | 50.7 | 43.7 |
| N | P | 77.0 | 50.2 | 42.6 |
| P | P | 75.3 | 50.1 | 42.7 |

### 4.6 타사 통합

semantic knowledge $K$를 raw message $P$ 대신 A-MEM·MemoryOS에 넣으면 저장을 45~54% 줄이면서 평균 성능은 약 4% 범위로 유지되고, Temporal을 뺀 weighted core score는 1.9~6.1% 좋아진다. 이는 NEMORI가 타사 메모리 시스템의 adaptive distillation kernel로 동작함을 보인다.

**표 7. 타사 management 비교.** P=raw message, K=NEMORI distilled semantic knowledge, Core=Temporal을 제외한 가중 평균이다.

| 모델 / 시스템 | 입력 | LLM score | Average | Core | MemTokens |
| --- | --- | ---: | ---: | ---: | ---: |
| gpt-4o-mini / A-MEM | P | 52.5 | 52.5 | 52.6 | 397K |
|  | K | 50.9 | 50.9 | 55.8 | 142K |
| gpt-4o-mini / MemoryOS | P | 54.6 | 54.6 | 59.2 | 405K |
|  | K | 54.0 | 54.0 | 60.3 | 190K |
| gpt-4.1-mini / A-MEM | P | 61.4 | 61.4 | 60.4 | 498K |
|  | K | 59.0 | 59.0 | 64.1 | 243K |
| gpt-4.1-mini / MemoryOS | P | 60.7 | 60.7 | 66.9 | 354K |
|  | K | 61.4 | 61.4 | 69.2 | 194K |

### 4.7 확장성

평균 105K token의 LongMemEvalS에서 NEMORI는 `gpt-4o-mini` 64.2, `gpt-4.1-mini` 74.6으로 Full Context 55.0·65.6보다 각각 16.7%, 13.7% 높다. LoCoMo에서의 작은 이득(1.0%, 0.2%)보다 커진다. Full Context는 긴 입력에서 attention dilution을 겪지만 NEMORI는 3.7~5.8K token의 focused retrieval로 95~96% 적은 token을 쓴다.

**표 8. LongMemEvalS 성능 비교.** NEMORI는 95–96% 적은 context로 더 높은 accuracy를 달성한다.

| 모델 / 질문 유형 | Full Context(101K tokens) | NEMORI(3.7–5.8K tokens) |
| --- | ---: | ---: |
| gpt-4o-mini / Single-session Preference | 6.7 | 46.7 |
| / Single-session Assistant | 89.3 | 83.9 |
| / Temporal Reasoning | 42.1 | 61.7 |
| / Multi-session | 38.3 | 51.1 |
| / Knowledge Update | 78.2 | 61.5 |
| / Single-session User | 78.6 | 88.6 |
| / Average | 55.0 | 64.2 |
| gpt-4.1-mini / Single-session Preference | 16.7 | 86.7 |
| / Single-session Assistant | 98.2 | 92.9 |
| / Temporal Reasoning | 60.2 | 72.2 |
| / Multi-session | 51.1 | 55.6 |
| / Knowledge Update | 76.9 | 79.5 |
| / Single-session User | 85.7 | 90.0 |
| / Average | 65.6 | 74.6 |

## 5. 결론과 한계

NEMORI는 agent experience의 미래 효용을 증류 단계에서 적응적으로 평가하는 training-free 프레임워크다. prediction error가 메모리로 보존할 가치를 가진다는 관점과 structure·representation·distillation의 세 prior에 따라 cascade 모듈이 협력한다. episode 중심 설계는 token 효율을 높이고 management-agnostic 설계는 하류 memory system의 distillation layer 역할을 가능하게 한다.

한계는 두 가지다. 첫째, NEMORI는 증류에 초점을 맞추며 management·retrieval은 단순 전략을 채택하므로 더 정교한 memory reasoning이 필요한 과업에서 병목이 될 수 있다. 둘째, interface는 현재 개념적이며 표준 protocol이 없어 구체 통합은 case-by-case 구현을 요구한다.

## 부록 A. 관리 구현

**A.1 Flat Summarization.** 개념 설명용으로 $M$이 구조 DB 대신 단일 summary $S_{sum}$을 유지한다. $Evoke(M_{in},M):S_{in}\leftarrow S_{sum}$이고, 새 insight는 $S_{sum}\leftarrow f_{LLM}(P_{sum}\oplus K_{in}\oplus S_{sum})$으로 병합한다.

**A.2 Naive RAG.** 4.4절 절제용 variant다. $S_{in}\leftarrow Top\text{-}K_s(S_r\in D_s\mid sim(v_{in},u_r)>\tau)$로 비슷한 항목만 검색하며, 각 $k_q$를 $(k_q,f_{emb}(k_q))$로 append한다. conflict detection·merge는 없다.

**A.3 타사 시스템.** A-MEM·MemoryOS 같은 host system의 query $M_{in}$용 context buffer $B^*$를 intercept하여 $S_{in}\leftarrow B^*$로 쓴다. 각 distilled insight $k_q$는 host input sequence에 독립 message로 넣어 외부 system이 native하게 관리하게 한다.

### 알고리즘 1. NEMORI 메모리 증류

**요구:** 메시지 버퍼 $B_t=\{m_1,\ldots,m_z\}$  
**보장:** 갱신된 episodic database $D_e$, semantic database $D_s$

1. `P ← f_LLM(P_par ⊕ B_t)`로 $B_t$를 raw episode $P=\{P_1,\ldots,P_n\}$로 분할한다.
2. 각 raw episode $P_j\in P$에 대해 다음을 수행한다.
3. `(N_j, c_j) ← f_LLM(P_nar ⊕ P_j)`로 narrative와 cue를 만든다.
4. `v_j ← f_emb(c_j ⊕ N_j)`를 계산한다.
5. $D_e$에서 후보를 검색하고 merge 또는 insert를 결정한다.
6. 통합된 $\bar M$ 또는 새 $M_j$인 episodic memory $M_{in}$을 얻는다.
7. `S_in ← Evoke(M_in, M)`로 context를 불러온다.
8. `P̂_in ← f_LLM(P_ant ⊕ c_in ⊕ S_in)`으로 anticipatory schema를 합성한다.
9. `K_in ← f_LLM(P_dis ⊕ P_in ⊕ P̂_in)`으로 semantic insight를 증류한다.
10. `Consolidate(K_in, M)`으로 관리 시스템에 통합한다.

### 알고리즘 2. NEMORI 응답 생성

**요구:** 질의 $Q$, episodic database $D_e$, semantic database $D_s$  
**보장:** 응답 $a$

1. $v_Q\leftarrow f_{emb}(Q)$를 계산한다.
2. $R'_e\leftarrow Search(D_e,v_Q,k)$를 검색하고 $R_e=\{N_i\}_{i=1}^k$, $R_p=\{P_d\}_{d=1}^r$를 추출한다.
3. $R'_s\leftarrow Search(D_s,v_Q,m)$를 검색하고 $R_s=\{s_j\}_{j=1}^m$를 추출한다.
4. $a\leftarrow f_{LLM}(P_{ans}\oplus Q\oplus R_e\oplus R_p\oplus R_s)$를 생성한다.
5. $a$를 반환한다.

## 부록 B. 사례 연구

이 절은 본문의 두 대표 사례를 통해, NEMORI가 시간 추론과 open-domain 질문 응답을 어떻게 지원하는지 보인다.

### B.1 시간 추론

LoCoMo의 대표 사례로 NEMORI가 답변 품질을 높이는 방식을 보인다.

- **질문:** “Jon은 언제 멘토링을 받았는가?”
- **난점:** 원래 대화에는 명시적 날짜가 아닌 “어제(yesterday)” 같은 상대 시간 표현이 있어 시간 추론이 필요하다.
- **Full Context baseline:** 원시 대화의 “어제”를 혼동하여 대화 날짜인 6월 16일을 잘못 답했다.
- **NEMORI:** 대화 맥락을 보존한 관련 episodic memory와, 시간 정보를 이미 명시적 사실로 증류한 semantic memory(“Jon은 2023년 6월 15일에 멘토링을 받았다.”)를 모두 검색했다. episodic context와 사전 추론된 semantic knowledge를 결합함으로써, 복잡한 추론을 단순한 사실 검색으로 바꾼다.

**통찰:** 이는 “메모리 형성 중 추론(reasoning during memory formation)”의 능력을 보여준다. prediction error는 기존 지식에 비추어 특정 날짜가 예상 밖임을 드러내며, 따라서 그 정보를 semantic memory로 증류하도록 유도한다.

### B.2 Open Domain

Open Domain 하위 집합에서 NEMORI의 LLM score는 가장 강한 메모리 시스템 baseline보다 약간 낮다. `gpt-4.1-mini`에서는 56.3 대 60.4(6.8% 차이), `gpt-4o-mini`에서는 45.8 대 47.6(3.8% 차이)다. 저자들은 이 하위 집합이 메모리 절차의 효율만을 순수하게 측정하지는 않는다고 지적한다.

LoCoMo의 많은 질문은 원래 대화 기록만으로 직접 답할 수 없다. 대신 backbone model이 대화의 서술을 인식하고 이를 일반 세계 지식의 항목에 연결해야 한다. 따라서 이 범주의 성능은 메모리 품질뿐 아니라 model의 사전 지식에도 의존한다.

대표 질문은 “John이 James와 이야기하던 서로 다른 색 카드가 있는 게임은 무엇인가?”이다. 정답은 `UNO`지만, 대화 자체에는 UNO라는 이름이 명시되어 있지 않다. transcript에는 여러 색 카드와 색·숫자를 맞추는 게임을 논의했고 화자가 이름을 잊었다는 내용만 있다. NEMORI의 episodic memory는 이 대화 근거를 보존하고 semantic memory도 같은 게임 설명을 증류하지만, 상호작용 기록에 없는 어휘 표지 `UNO`를 주입할 수는 없다. 그러므로 최종 답이 UNO가 되는지는 메모리 증류·검색의 실패보다 backbone model이 사전 지식으로 설명을 알아보는 능력에 크게 좌우된다.

## 부록 C. 추가 실험 결과

이 절의 모든 실험은 4.1절 설정을 사용한다.

### 표 9. NEMORI 메모리 구성 비용 구성 요소별 분석

LoCoMo에서 `gpt-4o-mini`를 사용했다. 핵심 비용은 narrative episode 생성(38.3%)과 semantic knowledge distillation(30.3%)이다.

| 구성 요소 | 입력(k) | 출력(k) | 총합(k) | 비율 |
| --- | ---: | ---: | ---: | ---: |
| Partition(§3.2.1) | 44.7 | 4.6 | 49.3 | 15.3% |
| Narration(§3.2.2) | 99.8 | 23.9 | 123.6 | 38.3% |
| Integration(§3.2.3) | 43.8 | 8.4 | 52.2 | 16.2% |
| Distillation(§3.3) | 88.9 | 8.8 | 97.7 | 30.3% |

### 표 10. 범주별 절제 연구(LoCoMo)

`Nemori-s`=semantic-only(직접 증류), `w/o e`=episodic retrieval 제외, `w/o s`=semantic retrieval 제외, `w/o p`=adaptive partitioning 제외(고정 20-message chunk), `Mgmt`의 **Native**=native management 사용, **Naive RAG**=부록 A.2의 naive RAG 사용이다. 각 값은 `LLM / F1 / BLEU`다.

| 모델 | 구성 / 관리 | Temporal | Open | Multi-hop | Single-hop | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-4o-mini | Nemori-s / Native | 33.3 / 36.8 / 31.1 | 49.0 / 24.4 / 18.6 | 47.9 / 30.5 / 20.2 | 60.3 / 39.7 / 32.1 | 51.7 / 36.4 / 28.9 |
|  | Nemori-s / Naive RAG | 32.7 / 35.9 / 30.4 | 40.6 / 21.8 / 17.0 | 47.5 / 31.3 / 20.7 | 62.1 / 40.3 / 32.7 | 52.0 / 36.6 / 29.1 |
|  | w/o e / Native | 57.9 / 53.0 / 44.6 | 53.1 / 26.5 / 19.6 | 57.8 / 35.5 / 24.4 | 70.8 / 49.4 / 40.4 | 64.6 / 46.2 / 37.1 |
|  | w/o e / Naive RAG | 56.7 / 52.8 / 44.8 | 54.2 / 27.8 / 20.6 | 59.9 / 36.5 / 24.8 | 71.1 / 48.9 / 39.8 | 65.0 / 46.2 / 36.9 |
|  | w/o s | 32.7 / 38.9 / 33.0 | 42.7 / 22.2 / 17.0 | 53.9 / 33.0 / 22.2 | 64.7 / 44.1 / 36.1 | 54.7 / 39.6 / 31.7 |
|  | w/o p | 56.7 / 52.7 / 43.4 | 45.8 / 25.0 / 19.3 | 59.9 / 36.3 / 23.5 | 77.5 / 51.7 / 40.7 | 68.0 / 47.4 / 36.8 |
|  | NEMORI | 67.6 / 57.3 / 47.6 | 45.8 / 23.9 / 18.5 | 61.7 / 38.1 / 26.0 | 81.9 / 54.8 / 43.8 | 73.0 / 50.3 / 39.7 |
| gpt-4.1-mini | Nemori-s / Native | 46.4 / 42.2 / 33.7 | 49.0 / 26.5 / 20.7 | 67.4 / 36.2 / 28.8 | 74.9 / 44.5 / 39.0 | 66.0 / 41.4 / 34.9 |
|  | Nemori-s / Naive RAG | 47.0 / 42.5 / 32.5 | 50.0 / 28.5 / 22.7 | 70.6 / 38.9 / 29.9 | 72.7 / 42.8 / 37.4 | 65.5 / 41.1 / 34.1 |
|  | w/o e / Native | 63.2 / 49.6 / 41.1 | 52.1 / 27.2 / 21.2 | 72.7 / 38.9 / 29.1 | 82.4 / 53.2 / 47.0 | 74.7 / 48.2 / 40.9 |
|  | w/o e / Naive RAG | 65.4 / 51.0 / 42.5 | 56.3 / 29.1 / 23.0 | 70.2 / 39.0 / 29.5 | 82.2 / 52.2 / 45.8 | 74.9 / 48.1 / 40.7 |
|  | w/o s | 73.5 / 54.3 / 46.9 | 55.2 / 26.9 / 21.3 | 73.1 / 41.9 / 32.5 | 81.9 / 53.7 / 47.3 | 76.9 / 50.0 / 42.9 |
|  | w/o p | 67.3 / 53.4 / 45.0 | 52.1 / 24.7 / 19.5 | 71.3 / 40.1 / 30.7 | 83.1 / 51.4 / 45.2 | 75.7 / 48.1 / 40.9 |
|  | NEMORI | 77.3 / 58.7 / 50.7 | 56.3 / 31.7 / 25.1 | 74.8 / 40.8 / 31.7 | 87.0 / 55.7 / 49.5 | 80.8 / 52.1 / 45.0 |

예측오차 기반 증류는 모든 범주에서 직접 지식 증류보다 일관되게 우수하다. 특히 Temporal Reasoning은 `gpt-4o-mini`에서 33.3→57.9(+73.9%), `gpt-4.1-mini`에서 46.4→63.2(+36.2%)로, 시간 민감 정보를 식별·변환하는 효과가 가장 크다.

### 표 11. 관찰 창 길이별 성능

LoCoMo와 `gpt-4.1-mini`에서의 결과다. $w=20$(기본 설정)은 굵게 표시했다. $w=5$부터 40까지 overall score는 약 1% 이내에서 안정적이며, message partitioning+integration 설계가 이 hyperparameter에 견고함을 보인다. 각 값은 `LLM / F1 / BLEU`다.

| w | Temporal | Open domain | Multi-hop | Single-hop | Overall |
| ---: | --- | --- | --- | --- | --- |
| 5 | 77.0 / 57.6 / 49.6 | 59.4 / 30.0 / 24.9 | 73.8 / 43.0 / 34.0 | 86.3 / 55.0 / 48.5 | 80.4 / 51.8 / 44.6 |
| 10 | 77.6 / 59.0 / 50.4 | 57.3 / 29.5 / 24.7 | 77.0 / 44.0 / 34.3 | 85.7 / 54.5 / 48.1 | 80.7 / 52.0 / 44.6 |
| **20** | **77.3 / 58.7 / 50.7** | **56.3 / 31.7 / 25.1** | **74.8 / 40.8 / 31.7** | **87.0 / 55.7 / 49.5** | **80.8 / 52.1 / 45.0** |
| 30 | 76.6 / 57.7 / 49.6 | 60.4 / 32.2 / 26.1 | 79.4 / 45.0 / 34.8 | 86.0 / 55.4 / 48.8 | 81.2 / 52.5 / 45.0 |
| 40 | 76.3 / 58.6 / 50.4 | 54.2 / 27.1 / 21.4 | 77.3 / 42.8 / 34.0 | 86.4 / 55.0 / 48.4 | 80.7 / 51.8 / 44.5 |

### 표 12. retrieval count $k$의 범주별 결과

LoCoMo의 결과이며 semantic memory 수는 $m=2k$로 고정했다. 굵은 행은 본문 기본값 $k=10$이다. $k$가 2→10으로 늘며 성능이 크게 상승한 뒤 평탄해진다. 각 값은 `LLM / F1 / BLEU`다.

| 모델 / k | Temporal | Open | Multi-hop | Single-hop | Overall |
| --- | --- | --- | --- | --- | --- |
| gpt-4o-mini / 2 | 62.3 / 55.3 / 46.5 | 41.7 / 20.9 / 15.4 | 55.0 / 33.7 / 21.8 | 75.0 / 51.1 / 40.9 | 66.6 / 46.9 / 37.0 |
| / 5 | 64.5 / 56.7 / 47.4 | 47.9 / 24.9 / 19.2 | 62.4 / 36.7 / 25.0 | 79.1 / 53.3 / 42.4 | 71.0 / 49.2 / 38.8 |
| / **10** | **67.6 / 57.3 / 47.6** | **45.8 / 23.9 / 18.5** | **61.7 / 38.1 / 26.0** | **81.9 / 54.8 / 43.8** | **73.0 / 50.3 / 39.7** |
| / 15 | 68.9 / 58.6 / 48.4 | 44.8 / 24.5 / 19.0 | 61.4 / 37.0 / 25.4 | 83.1 / 54.9 / 43.6 | 73.8 / 50.5 / 39.8 |
| / 20 | 67.9 / 57.4 / 47.7 | 45.8 / 24.3 / 18.9 | 63.5 / 38.2 / 25.9 | 82.8 / 54.7 / 43.1 | 73.8 / 50.4 / 39.4 |
| / 30 | 68.2 / 58.9 / 48.4 | 45.8 / 23.9 / 18.8 | 64.5 / 37.7 / 25.6 | 83.2 / 55.0 / 43.3 | 74.4 / 50.7 / 39.6 |
| gpt-4.1-mini / 2 | 68.5 / 52.8 / 45.5 | 52.1 / 25.7 / 20.5 | 64.5 / 38.2 / 28.3 | 80.6 / 51.7 / 45.6 | 73.4 / 47.8 / 40.9 |
| / 5 | 74.1 / 56.7 / 48.9 | 55.2 / 28.8 / 22.6 | 73.1 / 41.9 / 32.3 | 86.1 / 54.4 / 48.1 | 79.3 / 51.0 / 43.8 |
| / **10** | **77.3 / 58.7 / 50.7** | **56.3 / 31.7 / 25.1** | **74.8 / 40.8 / 31.7** | **87.0 / 55.7 / 49.5** | **80.8 / 52.1 / 45.0** |
| / 15 | 80.1 / 59.6 / 51.7 | 57.3 / 31.1 / 24.3 | 77.7 / 42.6 / 33.2 | 88.2 / 55.9 / 49.5 | 82.7 / 52.7 / 45.4 |
| / 20 | 79.8 / 59.4 / 51.1 | 58.3 / 30.3 / 24.4 | 81.2 / 45.3 / 35.5 | 88.5 / 55.6 / 49.1 | 83.4 / 52.9 / 45.5 |
| / 30 | 80.4 / 60.0 / 52.0 | 60.4 / 29.9 / 23.0 | 79.4 / 44.3 / 35.0 | 88.4 / 56.1 / 49.5 | 83.3 / 53.1 / 45.7 |

### 표 13. 검색 전략 절제 연구

`N`=narrative episode, `P`=raw(partitioned) episode. Index는 embedding 원천, Retrieve는 LLM에 반환한 내용이다. Retrieve=N일 때는 4.1절처럼 상위 2 narrative에 raw도 추가한다. 기본 행은 굵게 표시했다.

| Index | Retrieve | Temporal | Open | Multi-hop | Single-hop | Overall |
| --- | --- | --- | --- | --- | --- | --- |
| **N** | **N** | 72.9 / 55.7 / 48.3 | 55.2 / 26.0 / 20.4 | 72.3 / 41.8 / 32.8 | 82.3 / 53.3 / 47.1 | 76.9 / 50.0 / 42.9 |
| P | N | 71.7 / 56.5 / 49.0 | 47.9 / 24.0 / 19.6 | 72.3 / 40.5 / 30.8 | 82.8 / 55.0 / 48.7 | 76.4 / 50.7 / 43.7 |
| N | P | 73.8 / 43.4 / 35.8 | 55.2 / 27.3 / 21.5 | 72.0 / 43.2 / 32.4 | 82.4 / 57.8 / 51.0 | 77.0 / 50.2 / 42.6 |
| P | P | 69.5 / 42.5 / 35.2 | 51.0 / 22.6 / 18.2 | 67.0 / 40.2 / 30.5 | 83.0 / 59.4 / 52.4 | 75.3 / 50.1 / 42.7 |

### 표 14. 타사 management의 입력별 LLM Score 비교

`N`은 raw conversation, `K`는 NEMORI가 증류한 semantic memory다. Core는 Temporal을 제외한 가중 평균이다. K를 입력으로 쓰면 Core score는 1.9–6.1% 개선되고 저장량은 45–54% 줄어든다.

| 모델 / 시스템 | 입력 | Temporal | Open | Multi | Single | Average | Core |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-4o-mini / A-MEM | N | 54.2 | 22.9 | 43.6 | 58.2 | 52.5 | 52.6 |
|  | K | 33.6 | 38.5 | 50.4 | 59.1 | 50.9 | 55.8 |
| gpt-4o-mini / MemoryOS | N | 38.0 | 45.8 | 52.5 | 62.5 | 54.6 | 59.2 |
|  | K | 30.8 | 44.8 | 58.5 | 62.4 | 54.0 | 60.3 |
| gpt-4.1-mini / A-MEM | N | 66.7 | 37.5 | 55.7 | 64.0 | 61.4 | 60.4 |
|  | K | 41.1 | 41.7 | 58.2 | 68.0 | 59.0 | 64.1 |
| gpt-4.1-mini / MemoryOS | N | 37.7 | 60.4 | 62.4 | 68.9 | 60.7 | 66.9 |
|  | K | 32.7 | 58.3 | 62.4 | 72.3 | 61.4 | 69.2 |

### 표 15. 타사 management의 입력별 메모리 저장량 비교

| 모델 / 시스템 | 입력 | Tokens | Chars | Entries |
| --- | --- | ---: | ---: | ---: |
| gpt-4o-mini / A-MEM | N | 396,812 | 2,475,511 | 5,882 |
|  | K | 141,682 | 820,025 | 2,725 |
| gpt-4o-mini / MemoryOS | N | 404,611 | 1,956,432 | 3,014 |
|  | K | 189,662 | 927,678 | 2,613 |
| gpt-4.1-mini / A-MEM | N | 498,234 | 3,811,770 | 5,882 |
|  | K | 242,801 | 1,459,777 | 2,676 |
| gpt-4.1-mini / MemoryOS | N | 354,463 | 1,712,305 | 3,017 |
|  | K | 193,744 | 1,023,709 | 2,383 |

Entries는 각 시스템 자체 저장 형식으로 정의한 memory entry 수이므로 시스템 간이 아니라 같은 시스템 안에서만 비교할 수 있다. Tokens와 Chars는 모든 entry를 이어 붙여 측정했다.

## 부록 D. 프롬프트 템플릿

이 절은 NEMORI pipeline에서 사용한 완전한 prompt template을 제시한다. 중괄호 변수와 JSON key는 실행 호환성을 위해 원문 그대로 유지한다.

### D.1 핵심 증류 프롬프트

#### D.1.1 Local Message Partitioning Prompt (`P_par`)

```text
당신은 지능형 대화 분할 전문가다. 여러 메시지를 분석하여 일관된 episode로 묶어라.

번호가 1부터 {count}까지 매겨진 {count}개 메시지를 받는다: {messages}

## 과업
주제 변화에 높은 민감도로 메시지를 분석하여 일관된 episode로 묶어라. 다음을 탐지하면 엄격하게 새 episode를 만든다.

1. 주제 변경(최우선): 완전히 다른 주제를 도입하는가? 특정 사건에서 다른 사건으로 전환하는가? 하나의 질문에서 무관한 새 질문으로 이동했는가?
2. 의도 전환: 대화 목적이 바뀌었는가(예: 잡담→도움 요청, 업무→개인 생활)? 현재 핵심 질문·사안이 답변되었거나 충분히 논의되었는가?
3. 시간 표지: “earlier”, “before”, “by the way”, “oh right”, “also” 등의 전환 표지가 있는가? 메시지 사이 시간 간격이 30분 이상인가?
4. 구조 신호: “changing topics”, “speaking of which”, “quick question” 같은 명시적 주제 전환 구절이 있는가? 현재 주제가 끝났음을 나타내는 결론 문장이 있는가?
5. 내용 관련성: 새 메시지는 앞선 논의와 얼마나 관련 있는가(관련성 30% 미만이면 분할 고려)? 완전히 다른 사람·장소·사건을 다루는가?

판단 원칙: 각 episode는 하나의 핵심 주제 또는 사건을 중심으로 해야 한다. 확신이 없으면 분할한다. 단일 episode는 보통 10–15개 메시지를 넘지 않아야 한다.

## 출력 형식
아래처럼 JSON object만 반환한다. 각 episode는 이 episode에 속하는 1부터 시작하는 메시지 번호 `indices`와 구체적인 주제를 나타내는 짧은 `topic`을 가진다.
{"episodes":[{"indices":[1,2,3,4],"topic":"주말 하이킹 계획 논의"},{"indices":[5,6,7],"topic":"Python 프로그래밍 질문"},{"indices":[8,9],"topic":"업무 일정 논의"}]}

## 중요 지침
- 메시지가 서로 끼어 있으면 episode의 indices는 연속되지 않아도 된다.
- episode는 보통 2–15개 메시지를 포함한다.
- 엄격한 시간 순서보다 주제적 일관성을 우선한다.
- 망설이면 더 작고 집중된 episode를 택한다.
JSON object만 반환하고 다른 텍스트는 쓰지 마라.
```

#### D.1.2 Narrative Episode Generation Prompt (`P_nar`)

```text
당신은 episodic memory 생성 전문가다. 다음 대화를 episodic memory로 변환하라.
대화 내용: {conversation}
경계 탐지 이유: {boundary_reason}

대화를 분석해 시간 정보를 추출하고 구조화한 episodic memory를 만들어라. 다음 세 field만 가진 JSON object를 반환한다.
{"episodic_cue":"주제를 정확히 요약하는 10–20단어의 간결하고 서술적인 제목","narrative_episode":"누가 언제 대화에 참여했고, 무엇을 논의했으며, 어떤 결정·감정·계획·결과가 있었는지를 모두 담은 자세한 3인칭 서사. 연·월·일·시까지 정확한 시간을 포함한다.","timestamp":"episode가 발생한 YYYY-MM-DDTHH:MM:SS 형식 timestamp"}

시간 분석: (1) message metadata나 내용의 명시적 timestamp를 먼저 찾는다. (2) “yesterday”, “last week”, “this morning” 등의 시간 표현을 분석한다. (3) 시간 정보가 없으면 맥락에 근거한 합리적 추정치를 쓴다. (4) timestamp는 항상 `2024-01-15T14:30:00` 같은 ISO 형식으로 쓴다.

요구사항: 제목은 핵심 주제·활동을 담아 구체적이고 검색하기 쉬워야 한다. 내용에는 대화의 모든 중요 정보를 포함하고, 대화체를 narrative로 바꾸며, 시간 순서와 인과 관계를 지킨다. 명시적으로 1인칭이어야 하는 경우를 제외하고 3인칭을 쓴다. keyword 검색을 돕는 구체적 세부와 시간 정보를 내용에 넣는다. “지난주”, “다음 달” 같은 상대 시간은 절대 날짜(연·월·일)로 바꾸고 원래 표현 뒤 괄호에 쓴다. 현재 시각이 아니라 메시지 timestamp 또는 내용으로 실제 대화 시각을 분석한다.

예: 2024-03-14 15:00의 하이킹 대화라면 title은 “2024년 3월 16일 주말 하이킹 계획: 레이니어산 일출 여행”, content는 사용자가 3월 16일 일출을 보기 위해 새벽 4시에 떠나기로 했고 장비 추천을 받고 친구를 초대하기로 했다는 3인칭 서사, timestamp는 `2024-03-14T15:00:00`으로 한다.
JSON object만 반환하고 다른 텍스트는 쓰지 마라.
```

#### D.1.3 Optimal Candidate Identification Prompt (`P_sel`)

```text
당신은 episodic memory 병합 판단 전문가다. 새 episode를 유사한 기존 episode와 병합해야 하는지 결정하라.
## New Episode
Time Range: {new_time_range}
Content: {new_content}
Candidate Episodes to Merge With: {candidates}

새 episode가 (1) 후보 하나와 병합되어야 하는지(동일 사건/주제를 서술함), 또는 (2) 별도 새 episode인지(서로 다른 사건)를 판단한다.
두 episode가 같은 사건 또는 같은 대화 session이고, 시간상 크게 겹치거나 아주 가깝고, 한 주제의 연속/다른 관점이며, 병합이 다른 사건을 섞지 않고 더 완전한 그림을 만들 때만 병합한다. 주제만 유사한 다른 사건·대화, 1시간 초과의 큰 시간 간격, 다른 맥락·참여자는 병합하지 않는다.
{"decision":"merge 또는 new","merge_target_id":"merge일 때만 episode_id, 아니면 null","reason":"짧은 판단 이유"}
JSON만 반환한다.
```

#### D.1.4 Episodic Integration Prompt (`P_int`)

```text
당신은 episodic memory 병합 내용 생성기다. 관련된 두 episode를 하나의 일관된 episode로 결합하라.
## Original Episode: Time Range {original_time_range}; Title {original_title}; Content {original_content}
## New Episode to Merge: Time Range {new_time_range}; Title {new_title}; Content {new_content}
Combined Event Details: {combined_events}

두 episode의 정보를 중복 없이 결합하고 시간 흐름을 유지하며, 양쪽의 모든 중요한 세부를 보존하고 일관된 narrative를 만들어라.
{"title":"완전한 주제를 포착하는 병합 제목","content":"참여자·핵심 결정·감정·결과를 포함하여 시간순으로 결합한 자세한 3인칭 서사","timestamp":"병합 episode의 가장 이른 시각 ISO timestamp"}
세부를 자연스럽게 통합하고 단순 연결하지 마라. 중복은 제거하되 고유 정보는 보존하고, 시간적 일관성·검색성·3인칭 narrative를 유지한다. JSON만 반환한다.
```

#### D.1.5 Anticipatory Schema Synthesis Prompt (`P_ant`)

```text
당신은 지식 기반 episode 예측 시스템이다. 제한된 단서와 지식 베이스로 완전한 대화 episode를 재구성하라.
중요: 문체·형식이 아니라 실제로 무슨 내용과 지식이 있었는지를 예측한다.
Episodic Cue (Title/Summary): {episode_title}
Evoked Context (Prior Knowledge): {evoked_context}

단서를 바탕으로 이 episode에서 무슨 일이 있었는지 재구성한다. 구체적 사실, 핵심 결정, 공유·학습한 지식, 대화의 논리적 진행에 집중한다. 문체·세부 수준·정확한 표현·형식·timestamp 포함 여부·격식성은 무시한다. 다른 사람에게 episode를 설명하듯 실질에 집중한 자연스러운 narrative를 출력한다.
Your prediction:
```

#### D.1.6 Prediction Error Distillation Prompt (`P_dis`)

```text
당신은 원래 대화와 예측 내용을 비교해 가치 있는 지식을 추출한다.
Actual Episode (P_in - Ground Truth): {original_messages}
Anticipatory Schema (P̂_in - Expectation): {predicted_episode}

원문에 있지만 예측에는 없거나 잘못 표현된 가치 있는 지식만 뽑아라. 시간에 걸쳐 참인 사실, 이름·직함·선호·이유처럼 구체적인 내용, 미래 상호작용에 유용한 내용, 예측에 정확히 포착되지 않은 내용을 추출한다. 일시적 상태·감정, 대화 흐름·문체, 예측에 이미 충분히 있는 정보, 사교적 인사·반응은 무시한다.

예: “Alice는 Google의 senior engineer이고 ML 프로젝트를 하려고 작년에 Java에서 Python으로 바꿨다.”가 “Alice가 프로그래밍 경험을 논의했다.”로 예측되었다면, “Alice는 Google의 senior engineer다”, “Alice는 ML 프로젝트를 위해 Java에서 Python으로 바꿨다”를 뽑는다. “Alice가 Microsoft에 2019년 입사해 2022년에 team lead가 되었고 2024년 12월 온라인 CS 석사를 마칠 계획”이라면 재직 기간, 승진, 석사 계획을 각각 뽑는다.
{"statements":["gap에서 추출한 첫 번째 사실","두 번째 사실","..."]}
각 문장은 자족적이어야 하고, 지속 사실은 현재형으로 쓰며, 구체적 이름·직함·세부를 포함한다. 양보다 질을 우선한다.
```

#### D.1.7 Semantic Consolidation Prompt (`P_con`)

```text
당신은 보수적인 knowledge base 관리자다. 병합이나 충돌에 대해 절대적으로 확신하지 않으면 기본 행동은 NEW다.
## New Item Type: {new_type}
Content: {new_content}
Existing Similar Items: {candidates}

정확히 하나를 고른다.
1. NEW(기본): 새 항목을 더한다. 서로 다른 사실·사건·entity, 다른 시간·장소·맥락, 또는 정말 동일·모순인지 어떤 의심이라도 있는 경우다.
2. MERGE(드묾): 새 항목과 기존 항목이 다른 표현일 뿐 정확히 같은 사실일 때만 한다. 예: “사용자는 커피를 좋아한다”와 “사용자는 커피를 즐긴다”.
3. CONFLICT_DELETE(매우 드묾): 같은 구체 사실을 직접 모순할 때만 한다. 예: “사용자는 베이징에 산다”와 “사용자는 상하이에 산다”.

NEW: {"decision":"NEW","reason":"..."}
MERGE: {"decision":"MERGE","target_ids":["id1"],"new_content":"100단어 이하의 표준 표현","reason":"..."}
CONFLICT_DELETE: {"decision":"CONFLICT_DELETE","target_ids":["id1"],"reason":"..."}

의심되면 항상 NEW를 택한다. 유사한 주제는 같은 사실이 아니다(“사용자에게 고양이가 있다”와 “사용자에게 개가 있다”는 모두 유효하므로 NEW). 의미적으로 동일할 때만 MERGE하고, 같은 속성의 직접 모순일 때만 CONFLICT_DELETE한다. 중복보다 고유 세부를 잃는 일이 나쁘므로 정보 풍부함을 보존한다.
```

### D.2 직접 증류 프롬프트(NEMORI-s)

이는 4.4절의 NEMORI-s 설정에서 prediction-error 기반 증류 없이 직접 지식 증류를 수행하는 prompt다.

```text
당신은 AI memory system이다. 다음 episode에서 고가치·지속적인 semantic memory를 추출하라.
중요: 일시적 대화 세부가 아니라 장기적으로 가치 있는 지식에 집중하라.
Episodes to analyze: {episodes}

다음 네 시험을 모두 통과하는 지식만 추출한다.
- 지속성: 6개월 뒤에도 참인가?
- 구체성: 구체적이고 검색 가능한 정보인가?
- 효용성: 미래 사용자 요구를 예측하는 데 도움이 되는가?
- 독립성: 대화 맥락 없이 이해 가능한가?

우선 범주: (1) 이름·직함·회사·역할, 교육·자격·기술의 정체성/직업 정보, (2) 좋아하는 책·영화·음악·도구, 이유가 있는 기술 선호 등 지속 선호, (3) 사용 기술·버전·architecture·methodology·기술 결정과 근거, (4) 가족·동료·친구·팀 구조·보고선·전문 네트워크, (5) 경력·학습·프로젝트 목표와 계획, (6) 정기 활동·workflow·일정·반복 과제의 패턴/습관.

고가치 예: “Caroline이 가장 좋아하는 책은 Amy Ellis Nutt의 Becoming Nicole이다”, “사용자는 ByteDance의 senior ML engineer다”, “사용자는 debugging을 위해 TensorFlow보다 PyTorch를 선호한다”, “사용자의 team lead 이름은 Sarah다”, “사용자는 systems programming을 위해 Rust를 학습 중이다”, “사용자는 2021년 3월부터 yoga를 해 왔다”, “사용자는 2020년 8월 Amazon에 data scientist로 입사했다”, “사용자는 2025년 1월 Seattle로 이주할 계획이다.”

저가치로 건너뛸 것: assistant에게 감사함, X를 혼동함, 도움에 감사함, 생산적인 대화였음, 모든 일시 감정·반응.
{"statements":["첫 번째 고가치 지속 사실...","두 번째 고가치 지속 사실...","세 번째 고가치 지속 사실..."]}
JSON으로 고가치 지식만 반환한다. 양보다 장기적으로 사용자를 이해하는 데 실제 도움이 되는 지식의 질을 우선한다.
```

### D.3 응답 생성 프롬프트(`P_ans`)

```text
당신은 대화 memory에서 정확한 정보를 검색하는 지능형 memory assistant다.
# CONTEXT
대화의 두 화자가 남긴 memory에 접근할 수 있다. 여기에는 질문과 관련될 수 있는 timestamp가 붙은 정보가 있다.
# INSTRUCTIONS
1. 두 화자의 제공 memory를 모두 신중히 분석한다.
2. 답을 정할 때 timestamp를 특히 주의한다.
3. 특정 사건·사실 질문이면 memory에서 직접 근거를 찾는다.
4. 모순 정보가 있으면 가장 최근 memory를 우선한다.
5. “last year”, “two months ago” 같은 시간 표현이면 memory timestamp로 실제 날짜를 계산한다. 예를 들어 2022년 5월 4일 memory가 “작년에 India에 갔다”고 하면 여행은 2021년이다.
6. 상대 시간 표현은 항상 구체 날짜·월·년으로 변환한다. 예컨대 timestamp를 기준으로 “last year”는 “2022”, “two months ago”는 “March 2023”으로 바꾸고, 답할 때는 상대 표현을 무시한다.
7. 두 화자의 memory 내용에만 집중하며, memory에 언급된 등장인물 이름을 실제 memory 작성자와 혼동하지 않는다.
8. 답은 5–6단어 이하여야 한다.
# APPROACH(단계적으로 사고)
1) 질문 관련 정보를 담은 memory를 찾는다. 2) 해당 memory의 timestamp와 내용을 면밀히 본다. 3) 답이 되는 날짜·시간·장소·사건의 명시적 언급을 찾는다. 4) 상대 시간 변환 등 계산이 필요하면 계산을 보인다. 5) memory 근거만으로 정확하고 간결한 답을 만든다. 6) 질문에 직접 답하는지 재확인한다. 7) 구체적이고 모호한 상대 시간 표현이 없는 최종 답을 낸다.
Episodic Memories: {episodic}
Semantic Memories: {semantic}
Question: {question}
Answer:
```

### D.4 LLM-as-Judge 프롬프트

#### D.4.1 LoCoMo

```text
질문에 대한 답을 CORRECT 또는 WRONG으로 표시하라. (1) 한 사용자가 다른 사용자에게 한 질문, (2) gold(ground truth) 답, (3) 생성 답을 받는다. 이 질문은 한 사용자가 이전 대화에 근거하여 다른 사용자에 대해 알아야 하는 것을 묻는다.

gold 답은 보통 간결하고 짧다. 예: 질문 “마지막으로 Hawaii에 갔을 때 무엇을 샀는지 기억해?”; Gold answer “A shell necklace”. 생성 답은 더 길 수 있으나 gold와 같은 주제를 언급하면 관대하게 CORRECT로 한다. 시간 질문에서 gold는 특정 날짜·월·년이다. 생성 답이 길거나 “last Tuesday”, “next month” 같은 상대 시간이어도 같은 날짜·기간을 가리키면 CORRECT다. “May 7th”와 “7 May”처럼 형식이 달라도 같은 날짜면 CORRECT다.

Question: {question}
Gold answer: {gold_answer}
Generated answer: {generated_answer}
먼저 한 문장으로 판단 근거를 쓰고 CORRECT 또는 WRONG으로 끝낸다. 두 label을 모두 넣지 말아야 평가 script가 깨지지 않는다. key가 "label"인 JSON 형식으로 CORRECT 또는 WRONG label만 반환한다.
```

#### D.4.2 LongMemEvalS

LoCoMo의 통합 prompt와 달리 LongMemEvalS는 과업별 네 variant를 쓴다.

```text
[Temporal Reasoning]
질문, 정답, model 응답을 주겠다. 응답에 정답이 있으면 yes, 아니면 no라 답하라. 정답과 동등하거나 정답에 이르는 모든 중간 단계를 담아도 yes다. 필요한 정보의 일부만 있으면 no다. 일수/주수/월수 질문은 하루 차이(off-by-one)를 벌점 주지 않는다(예: 정답 18일, 예측 19일도 정답). 
Question: {question}
Correct Answer: {gold_answer}
Response: {response}

[Knowledge Update]
질문, 정답, model 응답을 주겠다. 응답에 정답이 있으면 yes, 아니면 no다. 이전 정보와 갱신 답을 함께 포함해도, 갱신 답이 요구 답이면 yes다.
Question: {question}
Correct Answer: {gold_answer}
Response: {response}

[Single Session Preference]
질문, 원하는 개인화 답변의 rubric, model 응답을 주겠다. 응답이 원하는 답을 만족하면 yes, 아니면 no다. model이 rubric의 모든 항목을 반영할 필요는 없으며, 사용자 개인 정보를 정확히 기억하고 활용하면 정답이다.
Question: {question}
Rubric: {gold_answer}
Response: {response}

[Default]
질문, 정답, model 응답을 주겠다. 응답에 정답이 있으면 yes, 아니면 no다. 정답과 동등하거나 정답에 이르는 모든 중간 단계를 담아도 yes다. 필요한 정보의 일부만 있으면 no다.
Question: {question}
Correct Answer: {gold_answer}
Response: {response}
```

## 참고문헌

원문의 서지 정보는 제목·저자·출판 정보를 보존하고, 설명이 필요한 부분만 한국어로 옮겼다.

1. Petr Anokhin, Nikita Semenov, Artyom Y. Sorokin, Dmitry Evseev, Andrey Kravchenko, Mikhail Burtsev, and Evgeny Burnaev. 2025. *Arigraph: Learning knowledge graph world models with episodic memory for LLM agents.* IJCAI 2025, Montreal, Canada, pp. 12–20. ijcai.org.
2. Harrison Chase. 2022. *LangChain.* https://github.com/langchain-ai/langchain. Accessed: 2025-12-31.
3. Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, and Deshraj Yadav. 2025. *Mem0: Building production-ready AI agents with scalable long-term memory.* CoRR, abs/2504.19413.
4. Andy Clark. 2013. *Whatever next? Predictive brains, situated agents, and the future of cognitive science.* Behavioral and Brain Sciences, 36(3):181–204.
5. Jizhan Fang et al. 2025. *LightMem: Lightweight and efficient memory-augmented generation.* CoRR, abs/2510.18866.
6. Karl Friston. 2010. *The free-energy principle: A unified brain theory?* Nature Reviews Neuroscience, 11(2):127–138.
7. Le Huang, Hengzhi Lan, Zijun Sun, Chuan Shi, and Ting Bai. 2024. *Emotional RAG: Enhancing role-playing agents through emotional retrieval.* IEEE ICKG 2023, Shanghai, pp. 120–127.
8. Jiazheng Kang, Mingming Ji, Zhe Zhao, and Ting Bai. 2025. *Memory OS of AI agent.* EMNLP 2025, Suzhou, pp. 25972–25981.
9. Patrick Lewis et al. 2020. *Retrieval-augmented generation for knowledge-intensive NLP tasks.* NeurIPS 2020.
10. Hao Li, Chenghao Yang, An Zhang, Yang Deng, Xiang Wang, and Tat-Seng Chua. 2025a. *Hello again! LLM-powered personalized agent for long-term dialogue.* NAACL 2025, pp. 5259–5276.
11. Rui Li et al. 2025b. *CAM: A constructivist view of agentic memory for LLM-based reading comprehension.* NeurIPS 2025.
12. Nelson F. Liu et al. 2024. *Lost in the middle: How language models use long contexts.* TACL, 12:157–173.
13. Adyasha Maharana et al. 2024. *Evaluating very long-term conversational memory of LLM agents.* ACL 2024, pp. 13851–13870.
14. James L. McClelland, Bruce L. McNaughton, and Randall C. O'Reilly. 1995. *Why there are complementary learning systems in the hippocampus and neocortex: Insights from the successes and failures of connectionist models of learning and memory.* Psychological Review, 102(3):419.
15. Charles Packer et al. 2023. *MemGPT: Towards LLMs as operating systems.* CoRR, abs/2310.08560.
16. Zhuoshi Pan et al. 2025. *SeCom: On memory construction and retrieval for personalized conversational agents.* ICLR 2025, Singapore. OpenReview.net.
17. Joon Sung Park et al. 2023. *Generative agents: Interactive simulacra of human behavior.* UIST 2023, San Francisco, pp. 2:1–2:22.
18. Rajesh P. N. Rao and Dana H. Ballard. 1999. *Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects.* Nature Neuroscience, 2(1):79–87.
19. Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, and Daniel Chalef. 2025. *Zep: A temporal knowledge graph architecture for agent memory.* CoRR, abs/2501.13956.
20. Di Wu et al. 2025. *LongMemEval: Benchmarking chat assistants on long-term interactive memory.* ICLR 2025, Singapore. OpenReview.net.
21. Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, and Yongfeng Zhang. 2025. *A-MEM: Agentic memory for LLM agents.* NeurIPS 2025.
22. Wanjun Zhong, Lianghong Guo, Qiqi Gao, He Ye, and Yanlin Wang. 2024. *MemoryBank: Enhancing large language models with long-term memory.* AAAI 2024, Vancouver, pp. 19724–19731.
