# Agentic Context Engineering: 자기 개선 언어 모델을 위한 진화하는 컨텍스트

> 원문: Qizheng Zhang 외, *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models*, ICLR 2026, arXiv:2510.04618v3 (2026-03-29).
>
> 이 문서는 원문 PDF 32쪽을 섹션·표·그림·부록 단위로 대조하여 작성한 한국어 전체 번역 노트다. 모델·데이터셋·API·프롬프트 변수·코드·JSON 스키마·인용 표기는 원문 표기를 유지했다. 그림 안의 수치는 표로도 옮겨 검색 가능하게 했으며, 해석·비평은 추가하지 않았다.

## 저자

Qizheng Zhang<sup>1*</sup>, Changran Hu<sup>2*</sup>, Shubhangi Upasani<sup>2</sup>, Boyuan Ma<sup>2</sup>, Fenglu Hong<sup>2</sup>, Vamsidhar Kamanuru<sup>2</sup>, Jay Rainton<sup>2</sup>, Chen Wu<sup>2</sup>, Mengmeng Ji<sup>2</sup>, Hanchen Li<sup>3</sup>, Urmish Thakker<sup>2</sup>, James Zou<sup>1</sup>, Kunle Olukotun<sup>1</sup>

<sup>1</sup> Stanford University · <sup>2</sup> SambaNova Systems, Inc. · <sup>3</sup> UC Berkeley · <sup>*</sup> 공동 제1저자.  
코드: <https://github.com/ace-agent/ace> · 웹사이트: <https://ace-agent.github.io>

## 초록

에이전트와 도메인 특화 추론 같은 대규모 언어 모델(LLM) 애플리케이션은 점점 더 컨텍스트 적응(context adaptation)에 의존한다. 이는 가중치를 갱신하는 대신 지시문·전략·근거를 입력에 넣어 수정하는 방식이다. 기존 접근은 사용성을 높이지만, 간결한 요약을 위해 도메인 통찰을 버리는 **간결성 편향(brevity bias)**, 반복 재작성에서 시간이 갈수록 세부사항이 침식되는 **컨텍스트 붕괴(context collapse)** 문제가 있다.

저자들은 컨텍스트를 전략을 축적·정제·조직하는 진화하는 플레이북으로 다루는 프레임워크 **ACE(Agentic Context Engineering)** 를 제안한다. ACE는 생성·성찰·큐레이션의 모듈식 과정과 구조화된 점진적 갱신으로 붕괴를 막고, 상세 지식을 보존하며 장문 컨텍스트 모델과 함께 확장한다. 에이전트 및 도메인 특화 벤치마크에서 ACE는 오프라인(예: 시스템 프롬프트)과 온라인(예: 에이전트 메모리) 컨텍스트를 모두 최적화한다. 강력한 기준선보다 에이전트에서 10.6%, 금융에서 8.6% 향상했고, 적응 지연 시간과 rollout 비용도 크게 줄였다.

특히 ACE는 라벨 감독 없이 자연스러운 실행 피드백만으로 효과적으로 적응할 수 있다. AppWorld 리더보드에서는 **더 작은 오픈소스 모델을 사용하면서도 전체 평균에서 1위 production-level 에이전트와 동률**이며, 더 어려운 test-challenge 분할에서는 이를 앞선다. 이 결과는 포괄적이고 진화하는 컨텍스트가 적은 오버헤드로 확장 가능하고 효율적이며 자기 개선하는 LLM 시스템을 가능하게 함을 보인다.

## 1. 서론

LLM 에이전트(Yao et al., 2023; Yang et al., 2024)와 compound AI system(Zaharia et al., 2024) 같은 현대 LLM 애플리케이션은 컨텍스트 적응에 크게 의존한다. 컨텍스트 적응은 모델 가중치를 바꾸지 않고, 명확해진 지시·구조화된 추론 단계·도메인 특화 입력 형식을 모델 입력에 직접 넣어 학습 후 성능을 높인다. 컨텍스트는 하위 과업을 안내하는 시스템 프롬프트, 과거 사실과 경험을 전달하는 메모리, 환각을 줄이고 지식을 보완하는 사실 근거 등 AI 시스템의 여러 구성 요소를 뒷받침한다.

가중치가 아니라 컨텍스트로 적응하면 사용자와 개발자가 해석·설명할 수 있고, 런타임에 새 지식을 빠르게 통합하며, compound system의 여러 모델 또는 모듈이 공유할 수 있다. 장문 컨텍스트 LLM과 KV cache 재사용 같은 컨텍스트 효율적 추론의 발전은 이런 접근을 배포에 더 실용적으로 만든다. 따라서 컨텍스트 적응은 유능하고 확장 가능하며 자기 개선하는 AI 시스템을 만드는 핵심 패러다임으로 떠오르고 있다.

그러나 기존 컨텍스트 적응에는 두 한계가 있다. **첫째, 많은 프롬프트 최적화기는 포괄적 축적보다 짧고 바로 적용 가능한 지시를 우선시하는 간결성 편향**을 보인다. GEPA(Agrawal et al., 2025)는 간결성을 장점으로 보지만, 이 추상화는 실제로 중요한 도메인별 휴리스틱, 도구 사용 지침, 흔한 실패 양상을 빼버릴 수 있다. 일부 환경에서의 검증 지표에는 부합하지만, 에이전트와 지식 집약적 응용에 필요한 상세 전략을 포착하지 못하는 경우가 많다. **둘째, LLM이 축적된 컨텍스트 전체를 반복해 다시 쓰는 방식은 시간이 지나며 더 짧고 정보량이 적은 요약으로 퇴화해 급격한 성능 저하를 낳는다**(그림 2). 상호작용 에이전트, **도메인 특화 프로그래밍, 금융·법률 분석에서는 압축해 없애기보다 상세한 과업 특화 지식을 보존해야 높은 성능을 낸다.**

에이전트와 지식 집약적 추론의 신뢰성 요구가 커지면서, 최근 연구는 장문 컨텍스트 LLM의 발전에 기대어 잠재적으로 유용한 풍부한 정보로 컨텍스트를 채우는 쪽으로 이동했다. 저자들은 컨텍스트가 짧은 요약이 아니라 상세하고 포괄적이며 도메인 통찰이 풍부한 구조화된 **플레이북(playbook)** 으로 기능해야 한다고 주장한다. 간결한 일반화에서 이득을 보는 인간과 달리 LLM은 길고 상세한 컨텍스트를 받을 때 더 효과적이며, 추론 시 관련성을 자율적으로 증류할 수 있다. 그러므로 도메인별 휴리스틱과 전술을 압축해 버리는 대신 보존하고, 무엇이 중요한지는 모델이 추론 시점에 결정하게 해야 한다.

이를 위해 저자들은 오프라인(예: 시스템 프롬프트 최적화)과 온라인(예: 테스트 시점 메모리 적응) 환경에서 포괄적 컨텍스트 적응을 수행하는 ACE를 도입한다. ACE는 컨텍스트를 압축 요약이 아닌, 시간이 지나며 전략을 축적하고 조직하는 진화하는 플레이북으로 취급한다. 생성·성찰·큐레이션의 모듈식 흐름과 **grow-and-refine** 원리에 따른 구조화된 증분 갱신을 결합해, 상세한 도메인 지식을 보존하고 컨텍스트 붕괴를 방지하며 적응 내내 포괄성과 확장성을 유지한다.

저자들은 진화 컨텍스트의 이점을 특히 크게 받는 두 부류를 평가한다. (1) 다중 턴 추론·도구 사용·환경 상호작용이 필요하며 축적 전략을 에피소드 간 재사용할 수 있는 에이전트(AppWorld), (2) 금융 분석처럼 특수 전술과 지식이 필요한 도메인 특화 벤치마크다. 주요 결과는 다음과 같다.

- ACE는 오프라인·온라인 적응 모두에서 강한 기준선을 일관되게 앞서며, 에이전트에서 평균 10.6%, 도메인 특화 벤치마크에서 평균 8.6% 개선한다.
- ACE는 라벨 감독 없이 실행 피드백과 환경 신호만 활용해 효과적 컨텍스트를 구성한다. 이는 자기 개선 LLM과 에이전트의 핵심 구성 요소다.
- AppWorld에서 ACE는 오픈소스 `DeepSeek-V3.1`을 사용하면서 GPT-4.1 기반 1위 production-level 에이전트 IBM-CUGA(Marreed et al., 2025)를 능가한다.
- 기존 적응 방법보다 rollout이 훨씬 적고 적응 지연 시간도 낮아, 정확도와 비용 모두에서 확장 가능한 자기 개선을 보인다.

> 그림 1. 전체 성능 결과. 제안 프레임워크 ACE는 에이전트 및 도메인 특화 과업 전반에서 강한 기준선을 일관되게 앞선다.

| 과업 | Base LLM | ICL | GEPA | DC | ACE |
| --- | ---: | ---: | ---: | ---: | ---: |
| Agent: AppWorld | 42.4% | 46.0% | 46.4% | 51.9% | **59.5%** |
| Domain Knowledge: FiNER | 70.7% | 72.3% | 73.5% | 74.2% | **78.3%** |
| Numerical Reasoning: Formula | 67.5% | 67.0% | 71.5% | 69.5% | **76.5%** |

## 2. 배경과 동기

### 2.1 컨텍스트 적응

컨텍스트 적응(또는 context engineering)은 LLM 가중치를 바꾸지 않고 LLM 입력을 구성하거나 수정해 모델 행동을 개선하는 방법을 말한다. 현재 최고 수준 방법은 자연어 피드백(Shinn et al., 2023; Yuksekgonul et al., 2025; Agrawal et al., 2025)을 활용한다. 이 패러다임에서는 언어 모델이 현재 컨텍스트와 실행 궤적, 추론 단계, 검증 결과 같은 신호를 살피고 컨텍스트를 어떻게 고칠지 자연어 피드백을 생성한다. 그 피드백을 컨텍스트에 반영하여 반복적으로 적응한다.

대표적으로 Reflexion은 실패를 성찰해 에이전트 계획을 개선하고, TextGrad는 gradient 같은 텍스트 피드백으로 프롬프트를 최적화한다. GEPA는 실행 궤적에 기반해 프롬프트를 반복 정제하며 일부 환경에서는 강화학습 접근까지 능가한다. Dynamic Cheatsheet는 추론 중 과거 성공과 실패에서 전략과 교훈을 축적하는 외부 메모리를 구성한다. 이 자연어 피드백 방법들은 가중치 갱신을 넘어 LLM 시스템을 개선할 유연하고 해석 가능한 신호를 제공한다는 중요한 진전이다.

### 2.2 기존 컨텍스트 적응 방법의 한계

**간결성 편향.** 컨텍스트 적응 방법의 반복되는 한계는 최적화가 짧고 일반적인 프롬프트로 수렴하는 경향이다. Gao et al.(2025)은 테스트 생성 프롬프트 최적화에서 반복 방법이 “메서드가 기대대로 동작하도록 단위 테스트를 작성하라”와 같은 거의 동일한 지시를 계속 만들며, 다양성을 희생하고 도메인 세부사항을 빠뜨리는 현상을 기록했다. 이 수렴은 탐색 공간을 좁히고 최적화 프롬프트가 seed의 같은 결함을 물려받기 때문에 반복되는 오류도 전파한다. 다단계 에이전트, 프로그램 합성, 지식 집약적 추론처럼 과업 특화 통찰을 압축하는 대신 축적해야 하는 영역에서는 특히 성능을 해친다.

> 그림 2. 컨텍스트 붕괴. LLM이 컨텍스트 전체를 단일 덩어리로 다시 쓰면 더 짧고 정보량이 적은 요약으로 붕괴해 성능이 급락할 수 있다. 사례에서 18,282토큰·정확도 66.7이던 컨텍스트는 다음 단계에 122토큰·정확도 57.1로 붕괴했으며, 컨텍스트가 없는 정확도 63.7보다도 낮았다.

**컨텍스트 붕괴.** AppWorld 사례 연구(Trivedi et al., 2024)에서 저자들은 매 적응 단계마다 축적 컨텍스트 전체를 다시 쓰도록 LLM에 요구할 때 발생하는 컨텍스트 붕괴를 관찰했다. 컨텍스트가 커질수록 모델은 이를 매우 짧고 정보량이 적은 요약으로 압축하는 경향이 있고, 정보가 극적으로 손실된다. 예를 들어 60단계에서 컨텍스트는 18,282토큰이고 정확도는 66.7이었으나, 바로 다음 단계에서 122토큰으로 붕괴하며 정확도가 57.1로 떨어졌다. 이는 적응이 없는 baseline 63.7보다 낮다. 이 현상은 Dynamic Cheatsheet로 보였지만 그 방법만의 문제는 아니다. 축적 지식을 보존하지 않고 갑자기 지울 수 있는 LLM의 end-to-end 컨텍스트 재작성 자체가 지닌 근본 위험이다.

> 그림 3. AppWorld에서 ACE가 생성한 컨텍스트의 예시(일부만 표시). ACE 컨텍스트는 바로 사용할 수 있는 도구·코드와 상세한 도메인 특화 통찰을 담아, LLM 애플리케이션을 위한 포괄적 플레이북 역할을 한다.

## 3. Agentic Context Engineering(ACE)

ACE는 오프라인과 온라인 컨텍스트 적응을 모두 확장 가능하고 효율적으로 수행하는 프레임워크다. 지식을 짧은 요약이나 정적 지시로 응축하지 않고, 시간이 지나며 전략을 계속 축적·정제·조직하는 진화 플레이북으로 컨텍스트를 취급한다. Dynamic Cheatsheet의 agentic 설계에서 영감을 받아 세 역할로 일을 분리한다(그림 4). **Generator**는 추론 궤적을 만들고, **Reflector**는 성공과 오류에서 구체적 통찰을 증류하며, **Curator**는 그 통찰을 구조화된 컨텍스트 갱신으로 통합한다. 이는 실험·성찰·통합으로 학습하는 인간의 방식을 본뜨되, 한 모델에 모든 책임을 과적재하는 병목을 피한다.

2.2절의 간결성 편향·컨텍스트 붕괴를 해결하기 위해 ACE는 세 혁신을 도입한다. (1) 평가·통찰 추출을 큐레이션과 분리해 컨텍스트 품질과 하류 성능을 높이는 전용 Reflector, (2) 비용 큰 단일 전체 재작성 대신 국소 편집을 수행해 지연 시간과 계산 비용을 줄이는 점진적 delta 갱신(3.1절), (3) 안정적 컨텍스트 확장과 중복 제어의 균형을 잡는 grow-and-refine 메커니즘(3.2절)이다.

흐름은 새 질의에 대해 Generator가 추론 궤적을 만드는 것으로 시작한다. 이 궤적은 효과적 전략과 반복되는 함정을 드러낸다. Reflector는 이를 비평하여 교훈을 뽑고 필요하면 여러 번 정제한다. Curator는 교훈을 압축된 delta 항목으로 합성하고, 경량 비LLM 로직이 기존 컨텍스트에 결정적으로 병합한다. 갱신이 항목화되어 국소적이므로 여러 delta를 병렬 병합하여 배치 적응을 확장할 수 있다. ACE는 같은 질의를 다시 방문해 컨텍스트를 점진적으로 강화하는 다중 epoch 적응도 지원한다.

> 그림 4. ACE 프레임워크. Dynamic Cheatsheet에서 영감을 받은 ACE는 Generator, Reflector, Curator라는 세 전문 구성 요소의 agentic 아키텍처를 채택한다. `Query → Generator → Trajectory → Reflector → Insights → Curator → Delta Context Items → Update → Context Playbook` 흐름이며, Reflector에는 iterative refinement가 가능하다.

### 3.1 점진적 delta 갱신

ACE의 핵심 설계 원칙은 컨텍스트를 하나의 단일 프롬프트가 아니라 구조화되고 항목화된 bullet들의 모음으로 나타내는 것이다. bullet은 Dynamic Cheatsheet와 A-MEM의 memory entry와 비슷하지만, (1) 고유 식별자와 helpful/harmful 표시 횟수 같은 메타데이터, (2) 재사용 전략·도메인 개념·흔한 실패 양상 같은 작은 내용 단위를 함께 가진다. 새 문제를 풀 때 Generator는 어느 bullet이 유용했거나 오도했는지 표시하고, 이 피드백이 Reflector가 교정 갱신을 제안하도록 안내한다.

이 항목화 설계는 세 성질을 제공한다. (1) **국소성**: 관련 bullet만 갱신한다. (2) **세밀한 검색**: Generator가 가장 관련된 지식에 집중한다. (3) **점진 적응**: 추론 중 효율적 병합·pruning·중복 제거를 가능하게 한다. ACE는 컨텍스트 전체를 재생성하지 않고, Reflector가 증류하고 Curator가 통합하는 작은 후보 bullet 집합인 압축된 delta context를 점진적으로 생성한다. 이는 전체 재작성의 계산 비용과 지연 시간을 피하면서 기존 지식 보존과 새 통찰의 안정적 추가를 보장한다. 컨텍스트가 커져도 장기 지평·도메인 집약 응용에 필요한 확장성을 제공한다.

### 3.2 Grow-and-refine

ACE는 점진 성장에 더해 주기적 또는 지연된 refinement로 컨텍스트를 압축적이고 관련성 있게 유지한다. grow-and-refine에서 새 식별자를 가진 bullet은 추가하고 기존 bullet은 제자리에서 갱신한다(예: counter 증가). 이어 semantic embedding으로 bullet을 비교하는 deduplication 단계가 중복을 제거한다. 이 refinement는 각 delta 뒤 선제적으로 수행할 수도 있고, 컨텍스트 창을 넘을 때만 지연 수행할 수도 있으며 이는 응용의 지연 시간·정확도 요구에 따른다.

결국 점진 갱신과 grow-and-refine은 적응적으로 확장하면서 해석 가능하고, 단일 컨텍스트 재작성이 일으키는 잠재적 분산을 피하는 컨텍스트를 유지한다.

## 4. 결과

ACE의 평가는 다음을 보인다.

- **고성능 자기 개선 에이전트**: 실행 피드백만으로 더 나은 컨텍스트를 학습해 AppWorld 정확도를 최대 17.1% 높이며, 오프라인·온라인 모두에서 입력 컨텍스트를 동적으로 정제한다.
- **도메인 특화 벤치마크의 큰 향상**: 복잡한 금융 추론에서 도메인 특화 개념·통찰을 담은 포괄적 플레이북을 구성하여 강한 baseline보다 평균 8.6% 개선한다.
- **설계 자체의 효과**: Reflector, 다중 epoch refinement, 점진 delta 갱신이 각각 상당한 성능 향상에 기여함을 절제 연구가 확인한다.
- **낮은 비용과 적응 지연**: 평균 적응 지연 시간을 86.9% 줄이면서 rollout과 토큰 달러 비용도 낮춘다.

### 4.1 과업과 데이터셋

저자들은 진화하는 컨텍스트의 이점을 가장 많이 받는 두 종류의 LLM 애플리케이션을 평가한다. 첫째, 다중 턴 추론·도구 사용·환경 상호작용이 필요하고 ACE로 에피소드·환경 간 전략을 축적·재사용할 수 있는 **LLM agent**다. 둘째, 특수 개념·전술의 숙달이 필요한 **도메인 특화 추론**이며, 주요 사례로 금융 분석을 다루고 의료 추론과 text-to-SQL 결과도 보인다.

- **LLM Agent: AppWorld**(Trivedi et al., 2024)는 API 이해, 코드 생성, 환경 상호작용을 포함한 자율 에이전트 과업 모음이다. 이메일·파일 시스템 등 일반 애플리케이션 및 API로 현실적 실행 환경을 제공하고 normal/challenge 두 난도를 가진다. 제출 당시 공개 리더보드 최고 시스템의 평균 정확도도 60.3%뿐이어서 난도와 현실성을 보인다.
- **도메인 특화 추론: 금융·의료·Text-to-SQL**. 금융에서는 XBRL에 의존하는 금융 추론을 시험하는 FiNER(Loukas et al., 2022)와 Formula(Wang et al., 2025a)를 쓴다. FiNER는 XBRL 재무 문서 토큰에 139개 세분화 entity type 중 하나를 라벨링하는 과업으로, 규제 도메인의 금융 정보 추출 핵심 단계다. Formula는 금융 개념을 적용하고 계산해 질의에 답하는 수치 추론에 초점을 둔다. 금융 밖에서는 StreamBench(Wu et al., 2024)의 DDXPlus(Fansi Tchango et al., 2022; 의료 추론)와 BIRD-SQL(Li et al., 2023; text-to-SQL)을 평가한다.

**평가 지표.** AppWorld에서는 공식 프로토콜을 따라 test-normal·test-challenge의 Task Goal Completion(TGC), Scenario Goal Completion(SGC)을 보고한다. FiNER·Formula·DDXPlus는 정답과 정확히 일치한 예측 비율인 정확도를 보고한다. BIRD-SQL은 LLM-as-a-judge(Zheng et al., 2023)에서 `GPT-4o-mini`를 쓴다. 모든 데이터셋은 원래 train/validation/test 분할을 따른다. 오프라인 적응은 train에서 최적화하고 test에서 pass@1 정확도를 평가한다. 온라인 적응은 섞은 동일 test split을 모든 방법에 사용하며, 각 표본에서 현재 컨텍스트로 먼저 예측한 뒤 해당 표본에 기반해 컨텍스트를 갱신하는 순차 방식이다.

### 4.2 기준선과 방법

**Base LLM**은 컨텍스트 엔지니어링 없이 데이터셋 저자의 기본 프롬프트로 직접 평가한다. AppWorld는 저자들이 공개한 공식 ReAct(Yao et al., 2023) 구현을 따르고, 나머지 baseline과 방법을 이 프레임워크 위에 구축한다.

**In-Context Learning(ICL)**(Agarwal et al., 2024)은 few-shot 또는 many-shot 과업 시연을 입력 프롬프트에 제공해 가중치 갱신 없이 과업 형식과 원하는 출력을 추론하게 한다. 학습 표본 전체가 컨텍스트 창에 들어가면 모두 제공하고, 아니면 가능한 많은 시연으로 창을 채운다.

**MIPROv2**(Opsahl-Ong et al., 2024)는 Bayesian optimization으로 시스템 지시와 in-context 시연을 함께 최적화하는 널리 쓰이는 프롬프트 최적화기다. 공식 DSPy 구현을 쓰고 최적화 성능 극대화를 위해 `auto="heavy"`로 설정한다.

**GEPA**(Agrawal et al., 2025)는 reflective prompt evolution 기반의 sample-efficient 프롬프트 최적화기다. 실행 궤적(추론, 도구 호출, 중간 출력)을 수집하고 자연어 성찰로 오류를 진단·credit assignment하며 프롬프트 갱신을 제안한다. genetic Pareto search가 높은 성능 프롬프트 frontier를 유지하여 local optimum을 완화한다. 실증적으로 GRPO 같은 강화학습과 MIPROv2 같은 프롬프트 최적화기를 앞서며, 최대 10% 높은 정확도와 최대 35배 적은 rollout을 달성했다고 보고된다. 공식 DSPy 구현을 `auto="heavy"`로 사용한다.

**Dynamic Cheatsheet(DC)**(Suzgun et al., 2025)는 재사용 가능한 전략·코드 조각의 적응적 외부 메모리를 도입한 테스트 시점 학습 접근이다. 새 입력과 출력을 계속 이 메모리에 갱신하여 과업 간 지식을 축적·재사용한다. 정답 라벨을 요구하지 않고 모델 생성물에서 메모리를 스스로 큐레이션할 수 있다는 장점이 있다. 저자들은 공식 구현을 누적 모드(DC-CU)로 사용한다.

**ACE(제안 방법)** 는 agentic context engineering으로 오프라인·온라인 모두의 LLM 컨텍스트를 최적화한다. 공정성을 위해 Generator·Reflector·Curator에 동일 LLM(DeepSeek-V3.1의 non-thinking mode)을 사용해, 더 강한 Reflector/Curator 지식이 약한 Generator로 이전되는 일을 막고 컨텍스트 구성 자체의 이득을 분리한다. 부록에서는 다른 backbone LLM도 평가하여 일관된 향상을 보인다. 배치 크기는 1(표본마다 delta context 하나 구성), Reflector refinement 최대 라운드와 오프라인 적응 최대 epoch는 각각 5로 설정한다.

### 4.3 에이전트 벤치마크 결과

> 표 1. AppWorld 에이전트 벤치마크 결과(`DeepSeek-V3.1-671B`가 base LLM). `GT Labels`는 적응 중 Reflector가 정답 라벨을 볼 수 있는지 뜻한다. 괄호 안은 ReAct 대비 변화량이다.

| 설정 / 방법 | GT Labels | Normal TGC | Normal SGC | Challenge TGC | Challenge SGC | 평균 |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| ReAct | — | 63.7 | 42.9 | 41.5 | 21.6 | 42.4 |
| **오프라인** ReAct + ICL | ✓ | 64.3 (+0.6) | 46.4 (+3.5) | 46.0 (+4.5) | 27.3 (+5.7) | 46.0 (+3.6) |
| ReAct + GEPA | ✓ | 64.9 (+1.2) | 44.6 (+1.7) | 46.0 (+4.5) | 30.2 (+8.6) | 46.4 (+4.0) |
| ReAct + ACE | ✓ | **76.2 (+12.5)** | **64.3 (+21.4)** | 57.3 (+15.8) | 39.6 (+18.0) | 59.4 (+17.0) |
| ReAct + ACE | ✗ | 75.0 (+11.3) | **64.3 (+21.4)** | 54.4 (+12.9) | 35.2 (+13.6) | 57.2 (+14.8) |
| **온라인** ReAct + DC(CU) | ✗ | 65.5 (+1.8) | 58.9 (+16.0) | 52.3 (+10.8) | 30.8 (+9.2) | 51.9 (+9.5) |
| ReAct + ACE | ✗ | 69.6 (+5.9) | 53.6 (+10.7) | **66.0 (+24.5)** | **48.9 (+27.3)** | **59.5 (+17.1)** |

공식 ReAct 구현 위에서 ACE를 여러 baseline과 오프라인·온라인으로 비교했다. ReAct + ACE는 선택 baseline보다 평균 10.6% 앞서며, GT label 없이도 좋은 성능을 얻는다. 오프라인에서 ACE는 ReAct + ICL 및 ReAct + GEPA보다 각각 12.3%, 11.9% 크게 앞서, 구조화·진화·상세 컨텍스트가 고정 시연이나 단일 최적화 지시보다 효과적 에이전트 학습을 제공함을 보인다. 온라인에서도 DC보다 평균 7.6% 높다.

라벨 없이도 ReAct + ACE는 ReAct baseline보다 평균 14.8% 향상한다. 이는 코드 실행 성공·실패처럼 실행 중 자연스럽게 얻는 신호를 이용해 Reflector와 Curator가 성공·실패의 구조화된 교훈을 만들기 때문이다. 2025년 9월 20일 기준 AppWorld 리더보드에서 ReAct + ACE의 59.4% 평균은 더 작은 오픈소스 DeepSeek-V3.1로 GPT-4.1 기반 production-level IBM CUGA의 60.3%와 같은 수준이다. 온라인 적응 ACE는 test-challenge에서 IBM CUGA보다 TGC 8.4%, SGC 0.7% 높다. IBM CUGA는 방법론 baseline이 아니라 성능 범위를 보일 맥락적 참조이며, 내부 설계가 ACE의 컨텍스트 적응 초점과 다르고 모든 baseline은 방법 효과를 분리하도록 동일 설정에서 평가했다.

### 4.4 도메인 특화 벤치마크 결과

> 표 2. 금융 분석 벤치마크 결과(`DeepSeek-V3.1-671B` base LLM). 괄호 안은 base LLM 대비 변화량이다.

| 설정 / 방법 | GT Labels | FiNER Acc. | Formula Acc. | 평균 |
| --- | :---: | ---: | ---: | ---: |
| Base LLM | — | 70.7 | 67.5 | 69.1 |
| **오프라인** ICL | ✓ | 72.3 (+1.6) | 67.0 (-0.5) | 69.6 (+0.5) |
| MIPROv2 | ✓ | 72.4 (+1.7) | 69.5 (+2.0) | 70.9 (+1.8) |
| GEPA | ✓ | 73.5 (+2.8) | 71.5 (+4.0) | 72.5 (+3.4) |
| ACE | ✓ | **78.3 (+7.6)** | **85.5 (+18.0)** | **81.9 (+12.8)** |
| ACE | ✗ | 71.1 (+0.4) | 83.0 (+15.5) | 77.1 (+8.0) |
| **온라인** DC(CU) | ✓ | 74.2 (+3.5) | 69.5 (+2.0) | 71.8 (+2.7) |
| DC(CU) | ✗ | 68.3 (-2.4) | 62.5 (-5.0) | 65.4 (-3.7) |
| ACE | ✓ | 76.7 (+6.0) | 76.5 (+9.0) | 76.6 (+7.5) |
| ACE | ✗ | 67.3 (-3.4) | 78.5 (+11.0) | 72.9 (+3.8) |

GT label이 있을 때 ACE는 오프라인과 온라인에서 모두 일관된 향상을 보이며, 구조화되고 진화하는 컨텍스트가 도메인 특화 추론에 유리함을 보여 준다. 그러나 신뢰할 실행 결과나 정답 같은 피드백 신호가 없으면 ACE와 DC 모두 성능이 떨어질 수 있다. 컨텍스트가 허위 또는 오도 신호로 오염될 수 있으므로, 컨텍스트 적응은 피드백 품질에 결정적으로 의존한다.

오프라인에서 GT 정답을 제공한 ACE는 ICL·MIPROv2·GEPA보다 평균 10.9% 높다. 금융 개념, XBRL 규칙처럼 고정 시연이나 단일 최적화 프롬프트를 넘어서는 정확한 도메인 지식이 필요할 때 특히 효과적임을 보인다. 온라인에서도 DC보다 평균 6.2% 높아, 특수 도메인 전반에서 재사용 가능한 통찰 축적의 이점을 확인한다. 신뢰 가능한 감독 또는 실행 신호가 전혀 없으면 두 방법은 저하될 수 있다. ACE는 코드 실행 결과나 formula 정답처럼 풍부한 피드백에는 강건하지만, Reflector와 Curator가 타당한 판단을 내릴 신호가 있어야 한다. 금융 외 의료 추론과 text-to-SQL에서도 일관된 향상을 보며, 전체 결과는 부록 A.2에 있다.

### 4.5 LLM 전반의 일반화

표 1·2는 기본 backbone인 DeepSeek-V3.1을 사용하지만 ACE가 이 모델에 특화된 것은 아니다. 알고리즘이나 프롬프트를 바꾸지 않고 다른 LLM으로 교체해도 AppWorld·금융에서 일관된 향상을 본다. 부록 A.1은 GPT-OSS-120B, GPT-5.1, Llama-3.3-70B-Instruct의 전체 결과를 보고하며, ACE가 대응 base agent/model보다 향상한다. 따라서 ACE는 LLM 계열 전반의 테스트 시점 컨텍스트 진화를 위한 일반화 가능한 방법이다.

### 4.6 절제 연구와 민감도 분석

절제 연구(표 3)는 ACE의 효과적 컨텍스트 적응에 개별 설계 선택이 기여하는 방식을 분석한다. 분석 요인은 (1) Dynamic Cheatsheet의 agentic 프레임워크에 추가한 iterative refinement를 갖는 Reflector, (2) 학습 표본을 여러 번 통과해 컨텍스트를 정제하는 multi-epoch adaptation, (3) 온라인 적응 전 오프라인 적응으로 컨텍스트를 초기화하는 offline warmup이다. 점진적 컨텍스트 갱신의 효과와 그 중요성은 부록 A.5에서 별도 분석한다.

> 표 3. AppWorld 절제 연구(`DeepSeek-V3.1`). iterative refinement, multi-epoch adaptation, offline warmup의 도움을 검토한다. 괄호 안은 ReAct 대비 변화량이다.

| 설정 / 방법 | GT Labels | Normal TGC | Normal SGC | Challenge TGC | Challenge SGC | 평균 |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| ReAct | — | 63.7 | 42.9 | 41.5 | 21.6 | 42.4 |
| **오프라인** ACE (Reflector·multi-epoch 없음) | ✓ | 70.8 (+7.1) | 55.4 (+12.5) | 55.9 (+14.4) | 38.1 (+17.5) | 55.1 (+12.7) |
| ACE (multi-epoch 없음) | ✓ | 72.0 (+8.3) | 60.7 (+17.8) | 54.9 (+13.4) | 39.6 (+18.0) | 56.8 (+14.4) |
| ACE | ✓ | **76.2 (+12.5)** | **64.3 (+21.4)** | 57.3 (+15.8) | 39.6 (+18.0) | 59.4 (+17.0) |
| **온라인** ACE | ✗ | 67.9 (+4.2) | 51.8 (+8.9) | 61.4 (+19.9) | 43.2 (+21.6) | 56.1 (+13.7) |
| ACE + offline warmup | ✗ | 69.6 (+5.9) | 53.6 (+10.7) | **66.0 (+24.5)** | **48.9 (+27.3)** | **59.5 (+17.1)** |

ACE는 약한 Reflector에서도 효과적이고 더 강한 Reflector에서만 완만한 추가 이득을 보이며, noisy/harmful reflection 아래에서는 완만히 저하한다. 완전히 적대적인 갱신이 매 반복 일어나는 경우를 제외하면 base model보다 높은 성능을 유지한다(부록 A.4). 또한 Reflector refinement 라운드, adaptation epoch 수, grow-and-refine 임계값 같은 합리적 하이퍼파라미터 넓은 범위에서 이득이 안정적이며, 대응 baseline보다 계속 높다(부록 A.6).

### 4.7 비용과 속도 분석

ACE는 점진적 delta 컨텍스트 갱신, 비LLM 기반 컨텍스트 병합·중복 제거 때문에 rollout 수 또는 토큰 입출력 달러 비용과 적응 지연 시간을 줄이는 데 특히 유리하다. AppWorld 오프라인 적응에서 ACE는 GEPA보다 적응 지연을 82.3%, rollout 수를 75.1% 줄인다. FiNER 온라인 적응에서는 DC보다 적응 지연을 91.5%, 토큰 입출력 달러 비용을 83.6% 줄인다.

> 표 4. 비용 및 속도 분석. ACE를 GEPA(오프라인)와 DC(온라인)에 대해 컨텍스트 적응 지연, rollout 수, 달러 비용으로 측정한다.

| 환경 | 방법 | Latency (s) | # Rollouts | Token Cost ($) |
| --- | --- | ---: | ---: | ---: |
| 오프라인(AppWorld) | ReAct + GEPA | 53,898 | 1,434 | — |
|  | ReAct + ACE | 9,517 (-82.3%) | 357 (-75.1%) | — |
| 온라인(FiNER) | DC(CU) | 65,104 | — | 17.7 |
|  | ACE | 5,503 (-91.5%) | — | 2.9 (-83.6%) |

세밀한 비용 분석에서도 ACE는 AppWorld 오프라인 적응에서 GEPA보다 입력/출력 토큰을 80.8%/83.6% 줄인다. GEPA의 프롬프트 검증 루프를 피하고 반복 전체 재작성을 국소 delta 갱신으로 바꾸기 때문이다. 평가 시에는 더 풍부하고 실행 가능한 플레이북 때문에 raw 입력 토큰이 더 많을 수 있지만, 이것이 반드시 더 높은 청구 비용을 뜻하지는 않는다. 현대 serving infrastructure는 KV cache 재사용(Prompt Cache, CacheBlend), 압축, offload로 장문 컨텍스트를 최적화한다. 자주 재사용되는 컨텍스트 구간을 cache하여 비싼 prefill을 피하므로 장문 컨텍스트 비용의 상각 비용은 낮아질 수 있다. GPT-5.1 OpenAI API의 prompt caching 연구에서 ACE는 평가 단계 입력 토큰 91.8%를 cache에서 제공받아 raw 컨텍스트 토큰 기준보다 청구 입력 토큰 비용을 82.6% 줄였다.

## 5. 논의

**온라인·연속 학습의 함의.** 온라인·연속 학습은 분포 변화와 제한된 학습 데이터 문제를 다루는 핵심 기계학습 연구 방향이다. ACE는 컨텍스트 적응이 보통 가중치 갱신보다 저렴하므로 전통 fine-tuning의 유연하고 효율적인 대안을 제공한다. 컨텍스트는 사람이 해석할 수 있어 privacy·법률 제약(GDPR, CCPA), 또는 도메인 전문가가 낡거나 잘못된 정보를 찾았을 때 선택적 unlearning도 가능하게 한다. ACE가 지속적이고 책임 있는 학습을 진전시킬 핵심 역할을 할 수 있는 유망한 미래 방향이다.

**제한과 과제.** ACE는 합리적으로 강한 Reflector에 의존한다. Reflector가 생성 궤적·결과에서 의미 있는 통찰을 뽑지 못하면 구성된 컨텍스트는 noisy하거나 해로울 수 있다. 어떤 모델도 유용한 통찰을 뽑지 못하는 도메인 특화 과업에서는 결과 컨텍스트도 자연히 부족하다. 이는 적응 품질이 기반 모델의 메모리 큐레이션 능력에 달린 Dynamic Cheatsheet와 유사하다. 또한 모든 응용에 풍부하고 상세한 컨텍스트가 필요한 것은 아니다. HotPotQA처럼 근거 검색·종합 방법의 간결한 상위 수준 지시가 더 유리한 과업도 있으며, Game of 24처럼 고정 전략 게임은 재사용 규칙 하나면 충분해 추가 컨텍스트가 중복될 수 있다. ACE는 모델 가중치나 단순 시스템 지시에 이미 담긴 것을 넘어 상세 도메인 지식, 복잡한 도구 사용, 환경 특화 전략이 필요한 환경에서 가장 유익하다.

## 감사의 글·윤리·재현성

저자들은 논문 개선에 도움을 준 익명 리뷰어와 area chair에게 감사한다. Qizheng Zhang은 NSF award CNS-2211384와 DARPA award TFAWI-HR00112520038의 지원을 받았다. Lakshya A Agrawal, Xuekai Zhu, Yuhan Liu, Junchen Jiang, Azalia Mirhoseini에게 유익한 논의에 대해 감사한다.

본 연구는 특정 윤리 우려를 제기하지 않는다. 기여는 LLM의 효과적 컨텍스트 적응을 위한 알고리즘·시스템 프레임워크 개발에 집중한다. 모든 실험은 공개 벤치마크와 오픈소스 모델로 수행했으며, 인간 대상·민감 데이터·privacy 관련 정보는 포함하지 않았고 이해 상충도 없다.

코드는 `github.com/ace-agent/ace`에 공개했다. 데이터셋·벤치마크·평가 지표·baseline·하이퍼파라미터를 포함한 실험 설정을 상세히 기술하고, LLM 프롬프트와 확장 실험 설정은 부록에 넣었다. 합리적 계산 자원을 가진 독자는 결과를 재현할 수 있다.

## 부록 A. 확장 결과

### A.1 서로 다른 LLM 전반의 일반화

ACE는 실행 궤적과 컨텍스트 delta에서 동작하는 model-agnostic 프레임워크로, 본문 기본 backbone인 DeepSeek-V3.1의 아키텍처나 학습 특성에 의존하지 않는다. 크기·비용·성능이 다른 GPT-OSS-120B(표 5·7), GPT-5.1(표 6·8), Llama-3.3-70B-Instruct(표 9)도 평가했다. 매 경우 알고리즘을 바꾸지 않고 Generator·Reflector·Curator를 새 모델로 모두 교체했다.

테스트한 네 LLM 계열(DeepSeek-V3.1, GPT-OSS-120B, GPT-5.1, Llama-3.3-70B-Instruct) 전체에서 ACE는 base LLM/agent·GEPA·다른 baseline보다 계속 향상했으며, 과업과 감독 설정에 따라 흔히 5~12점 높았다. 크기·비용·학습 recipe가 크게 다른 모델로 바꾸어도 상대 향상은 안정적이고, GT label 유무와 무관하게 이득을 제공한다. 온라인 variant가 모든 모델에서 가장 강한 성능을 안정적으로 달성한다. 다만 더 작은·약한 모델은 intermediate reflection과 calibration이 noisy하므로 GPT-5.1·GPT-OSS-120B보다 Llama-3.3-70B-Instruct의 향상 폭이 작을 수 있다.

> 표 5. AppWorld, `GPT-OSS-120B` base LLM. 괄호는 ReAct 대비 변화량이다.

| 방법 | GT | Normal TGC/SGC | Challenge TGC/SGC | 평균 |
| --- | :---: | ---: | ---: | ---: |
| ReAct | — | 54.8 / 33.9 | 34.5 / 15.1 | 34.6 |
| 오프라인 GEPA | ✓ | 56.0 (+1.2) / 33.9 (+0.0) | 40.1 (+5.6) / 20.9 (+5.8) | 37.7 (+3.1) |
| 오프라인 ACE | ✓ | 61.3 (+6.5) / 39.3 (+5.4) | 40.3 (+5.8) / 20.9 (+5.8) | 40.5 (+5.9) |
| 오프라인 ACE | ✗ | 58.3 (+3.5) / 41.1 (+7.2) | 39.6 (+5.1) / 18.7 (+3.6) | 39.4 (+4.8) |
| 온라인 DC(CU) | ✗ | 49.4 (-5.4) / 33.9 (+0.0) | 30.8 (-3.7) / 18.2 (+3.1) | 33.1 (-1.5) |
| 온라인 ACE | ✗ | 60.7 (+5.9) / 44.6 (+10.7) | 43.2 (+8.7) / 20.1 (+5.0) | 42.2 (+7.6) |

> 표 6. AppWorld, `GPT-5.1` base LLM.

| 방법 | GT | Normal TGC | Normal SGC | 평균 |
| --- | :---: | ---: | ---: | ---: |
| ReAct | — | 61.9 | 46.4 | 54.2 |
| 오프라인 GEPA | ✓ | 64.3 (+2.4) | 48.2 (+1.8) | 56.2 (+2.0) |
| 오프라인 ACE | ✓ | 66.7 (+4.8) | 53.6 (+7.2) | 60.2 (+6.0) |
| 오프라인 ACE | ✗ | 67.3 (+5.4) | 55.4 (+9.0) | 61.3 (+7.1) |
| 온라인 DC(CU) | ✗ | 62.5 (+0.6) | 55.4 (+9.0) | 58.9 (+4.7) |
| 온라인 ACE | ✗ | 72.6 (+10.7) | 58.9 (+12.5) | 65.8 (+11.6) |

> 표 7. 금융 분석, `GPT-OSS-120B` base LLM.

| 방법 | GT | FiNER | Formula | 평균 |
| --- | :---: | ---: | ---: | ---: |
| Base LLM | — | 66.6 | 71.5 | 69.1 |
| 오프라인 GEPA | ✓ | 67.9 (+1.3) | 71.5 (+0.0) | 69.7 (+0.6) |
| 오프라인 ACE | ✓ | 73.8 (+7.2) | 88.5 (+17.0) | 81.2 (+12.1) |
| 오프라인 ACE | ✗ | 69.7 (+3.1) | 84.0 (+12.5) | 76.9 (+7.8) |
| 온라인 DC | ✗ | 55.8 (-10.8) | 66.0 (-5.5) | 60.9 (-8.2) |
| 온라인 ACE | ✗ | 70.5 (+3.9) | 85.0 (+13.5) | 77.8 (+8.7) |

> 표 8. 금융 분석, `GPT-5.1` base LLM.

| 방법 | GT | FiNER | Formula | 평균 |
| --- | :---: | ---: | ---: | ---: |
| Base LLM | — | 73.5 | 73.0 | 73.3 |
| 오프라인 GEPA | ✓ | 74.5 (+1.0) | 73.0 (+0.0) | 73.8 (+0.5) |
| 오프라인 ACE | ✓ | 81.0 (+7.5) | 84.5 (+11.5) | 82.8 (+9.5) |
| 오프라인 ACE | ✗ | 78.2 (+4.7) | 76.5 (+3.5) | 77.4 (+4.1) |
| 온라인 DC | ✗ | 70.0 (-3.5) | 69.0 (-4.0) | 69.5 (-3.8) |
| 온라인 ACE | ✗ | 75.2 (+1.7) | 79.0 (+6.0) | 77.1 (+3.8) |

> 표 9. 금융 분석, `Llama-3.3-70B-Instruct` base LLM.

| 방법 | GT | FiNER Acc. |
| --- | :---: | ---: |
| Base LLM | — | 62.5 |
| 오프라인 GEPA | ✓ | 59.4 (-3.1) |
| 오프라인 ACE | ✓ | 64.9 (+2.4) |
| 오프라인 ACE | ✗ | 64.2 (+1.7) |
| 온라인 DC | ✗ | 59.0 (-3.5) |
| 온라인 ACE | ✗ | 63.6 (+1.1) |

### A.2 금융 밖의 추가 도메인 과업

저자들은 StreamBench의 non-streaming(오프라인 적응) 설정에서 DDXPlus 의료 추론과 BIRD-SQL text-to-SQL 생성도 평가한다. ACE는 임의 추출한 학습 예시 1,000개로 오프라인 적응한다. GEPA도 같은 1,000개로 학습하고, BIRD-SQL에는 별도 검증 500개, DDXPlus에는 372개를 남긴다(StreamBench는 DDXPlus train/validation 예시 1,372개 제공). 달리 언급하지 않은 설정은 본문과 같다.

DDXPlus에서 ACE는 base LLM 정확도 75.2를 90.2(+15.0)로 크게 높였지만 GEPA는 76.4(+1.2)로 작은 향상에 그쳤다. 이는 ACE의 테스트 시점 진화 컨텍스트가 다단계·도메인 집약 진단 추론으로 잘 이전됨을 시사한다. BIRD-SQL에서도 ACE는 모든 split에서 base model보다 향상하여 전체 평균 52.9(+5.1)를 얻었고, 주로 Simple subset 53.5(+7.1)가 이득을 이끈다. Moderate·Challenging에서는 GEPA 향상이 더 크지만 ACE도 둘 모두에서 base보다 높다. 따라서 ACE는 금융을 넘어 지식 집약 추론과 구조화 코드 생성에 일반화한다.

> 표 10. 의료 추론(DDXPlus from StreamBench), `DeepSeek-V3.1-671B`.

| 방법 | Accuracy |
| --- | ---: |
| Base LLM | 75.2 |
| GEPA | 76.4 (+1.2) |
| ACE | **90.2 (+15.0)** |

> 표 11. Text-to-SQL(BIRD-SQL from StreamBench), `DeepSeek-V3.1-671B`.

| 방법 | Simple | Moderate | Challenging | 평균 |
| --- | ---: | ---: | ---: | ---: |
| Base LLM | 46.4 | 48.2 | 55.1 | 47.8 |
| GEPA | 51.6 (+5.2) | **51.9 (+3.7)** | **57.2 (+2.1)** | 52.2 (+4.4) |
| ACE | **53.5 (+7.1)** | 50.7 (+2.5) | 56.6 (+1.5) | **52.9 (+5.1)** |

### A.3 세밀한 비용 분석

AppWorld를 대표 응용으로 삼아 ACE와 GEPA의 적응·평가 단계 비용을 세밀히 분석한다(오프라인 적응). ACE는 1 epoch와 Reflector refinement 1회로 실행했다. epoch 또는 refinement round를 늘리면 비용도 커지지만, ACE는 비용 큰 validation-time 재평가를 피하고 반복 전체 재작성 대신 국소 갱신을 수행한다는 질적 경향은 유지된다. GEPA는 최적화 강도를 극대화하도록 공식 DSPy 구현의 `auto="heavy"`를 사용했다.

적응 단계에서 ACE는 GEPA 대비 입력 토큰을 80.8%(204.1M → 39.3M), 출력 토큰을 83.6%(1.87M → 0.31M) 줄인다. 차이의 주된 원인은 held-out validation set 57개 질의에 후보 프롬프트를 반복 평가하는 GEPA의 prompt-validation loop와, 전체 프롬프트 재작성 대신 국소 Generator–Reflector–Curator 갱신을 하는 ACE다. 평가 단계에서는 풍부한 실행 가능 플레이북 탓에 ACE가 질의당 raw 입력 토큰을 더 쓰지만 출력 토큰은 115.0 대 101.8로 비슷하고 rollout 수도 유사하다. OpenAI의 기본 prompt caching으로 ACE 입력 토큰 91.8%를 cache에서 제공하여 billed input-token cost를 82.6% 줄일 수 있다.

> 표 12. AppWorld 적응 단계 총 비용. 백분율은 ACE 총계와 GEPA 총계의 비교다.

| 방법 | 총 입력 토큰 | 총 출력 토큰 | 총 rollouts | 총 질의 |
| --- | ---: | ---: | ---: | ---: |
| GEPA (prompt generation) | 65,005,192 | 1,266,090 | 429 | 90 |
| GEPA (prompt validation) | 139,070,904 | 604,098 | 1,026 | 57 |
| GEPA (total) | 204,076,096 | 1,870,188 | 1,455 | 147 |
| ACE (Generator) | 31,012,122 | 198,847 | 1,790 | 90 |
| ACE (Reflector) | 4,685,840 | 70,487 | 161 | 90 |
| ACE (Curator) | 3,552,963 | 37,794 | 124 | 90 |
| ACE (total) | 39,250,925 (-80.8%) | 307,128 (-83.6%) | 2,075 (+42.6%) | 90 (-38.8%) |

> 표 13. AppWorld 적응 단계 평균 비용.

| 방법 | 입력/rollout | 출력/rollout | 입력/질의 | 출력/질의 | rollouts | 질의 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GEPA (generation) | 151,600.4 | 2,951.4 | 722,279.9 | 14,067.7 | 429 | 90 |
| GEPA (validation) | 135,550.8 | 589.2 | 2,439,840.4 | 10,600.0 | 1,026 | 57 |
| GEPA (total) | 140,291.8 | 1,285.4 | 1,387,538.4 | 12,721.7 | 1,455 | 147 |
| ACE (Generator) | 17,326.6 | 111.1 | 344,579.1 | 2,209.4 | 1,790 | 90 |
| ACE (Reflector) | 29,112.4 | 437.3 | 52,064.9 | 783.2 | 161 | 90 |
| ACE (Curator) | 28,667.4 | 304.8 | 39,477.4 | 420.0 | 124 | 90 |
| ACE (total) | 18,914.9 (-86.5%) | 148.0 (-88.5%) | 436,121.4 (-68.6%) | 3,412.5 (-73.2%) | 2,075 (+42.6%) | 90 (-38.8%) |

> 표 14. AppWorld 평가 단계 총 비용(ACE와 GEPA 비교).

| 방법 | 총 입력 토큰 | 총 출력 토큰 | 총 rollouts | 총 평가 질의 |
| --- | ---: | ---: | ---: | ---: |
| Base ReAct | 27,460,411 | 289,802 | 2,430 | 160 |
| GEPA | 26,960,675 | 251,442 | 2,470 | 160 |
| ACE | 58,623,267 (+117.4%) | 270,652 (+7.6%) | 2,354 (-4.7%) | 160 (+0.0%) |

> 표 15. AppWorld 평가 단계 평균 비용.

| 방법 | 입력/rollout | 출력/rollout | 입력/질의 | 출력/질의 | rollouts | 평가 질의 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base ReAct | 11,298.5 | 119.3 | 171,627.6 | 1,811.3 | 2,430 | 160 |
| GEPA | 10,918.5 | 101.8 | 168,504.2 | 1,571.5 | 2,470 | 160 |
| ACE | 24,912.4 (+128.2%) | 115.0 (+13.0%) | 366,395.4 (+117.4%) | 1,691.6 (+7.6%) | 2,354 (-4.7%) | 160 (+0.0%) |

### A.4 성찰 품질에 대한 강건성

저자들은 ACE가 성찰 품질에 얼마나 민감한지 두 분석을 수행하며, 달리 언급하지 않으면 FiNER의 ACE 오프라인 적응을 사용한다. 강한 Reflector가 필요한지 시험하기 위해 GPT-OSS-120B, DeepSeek-V3.1-671B, GPT-5.1의 크게 다른 능력 모델로 Reflector만 바꾸고 Generator/Curator는 고정했다. 모든 선택에서 ACE는 훨씬 약한 Reflector를 써도 base LLM보다 좋아졌고, 강한 Reflector일수록 이득은 커지지만 넓은 강도 범위에서 방법은 유효했다.

> 표 16. FiNER의 약한 Reflector 모델. 괄호는 base LLM 대비 변화량이다.

| 방법 | Generator | Reflector | Curator | Accuracy |
| --- | --- | --- | --- | ---: |
| Base LLM | DeepSeek-V3.1 | — | — | 70.7 |
| ACE | DeepSeek-V3.1 | GPT-OSS-120B | DeepSeek-V3.1 | 76.6 (+5.9) |
| ACE | DeepSeek-V3.1 | DeepSeek-V3.1 | DeepSeek-V3.1 | 78.3 (+7.6) |
| ACE | DeepSeek-V3.1 | GPT-5.1 | DeepSeek-V3.1 | 78.5 (+7.8) |

또한 adversarial 또는 상충 bullet을 주입하는 명시적으로 harmful한 Reflector를 매 $X$ 적응 단계마다 한 번 호출해 stress test했다. $X$가 클수록 오염 빈도는 낮다. 중간 수준 noise에는 강건하며, 매 반복 harmful update를 주입하는 극단을 제외하면 성능은 base LLM 위에 유지된다. 이는 update 메커니즘이 reflection stream의 상당한 noise를 견디며, 의도적으로 적대적인 조건에서만 실패가 나타남을 뜻한다.

> 표 17. FiNER에서 noisy/harmful Reflector 피드백 강건성.

| Harmful Reflector 빈도(매 X회) | Accuracy |
| --- | ---: |
| base LLM | 70.7 |
| 1 | 66.7 (-4.0) |
| 5 | 76.1 (+5.4) |
| 10 | 77.0 (+6.3) |
| 25 | 77.8 (+7.1) |
| 50 | 78.2 (+7.5) |
| 100 | 78.2 (+7.5) |
| harmful reflector 없음 | 78.3 (+7.6) |

요점과 완화책은 다음과 같다. (1) 약한 Reflector도 상당한 이득을 제공하고, (2) 중간 noise·상충 갱신은 대체로 견디며, (3) 지속적 적대 오염 아래에서만 base보다 낮아진다. 실제로 grow-and-refine(3.2절)의 bullet analyzer는 의미적으로 비슷한 bullet을 병합·중복 제거하고 메타데이터로 잠재적 harmful 항목을 필터링할 수 있어 컨텍스트 noise의 첫 방어선이다. contradiction detection, Curator에게 high-confidence update 우선 지시, 오래된 항목 주기 pruning은 플레이북의 압축성과 일관성을 더 개선할 호환 가능한 확장이다.

### A.5 점진적 컨텍스트 갱신 절제

AppWorld에서 incremental context update를 쓰는 ACE와 쓰지 않는 ACE로 오프라인 적응을 실행하고, DeepSeek-V3.1의 test-normal을 평가했다. 점진 갱신은 중요하다. 컨텍스트 붕괴로 잃을 유용한 정보를 보존하므로 ACE 이득의 큰 비중을 설명한다.

> 표 18. 점진 컨텍스트 갱신 절제(AppWorld, DeepSeek-V3.1). 개선은 ReAct 대비다.

| 방법 | Normal TGC | Normal SGC | 평균 |
| --- | ---: | ---: | ---: |
| ReAct | 63.7 | 42.9 | 53.3 |
| ACE(점진 갱신 없음) | 67.3 (+3.6) | 46.4 (+3.5) | 56.9 (+3.6) |
| ACE(점진 갱신 사용) | **76.2 (+12.5)** | **64.3 (+21.4)** | **70.3 (+17.0)** |

### A.6 하이퍼파라미터 선택 민감도

**Reflection iteration.** 이 파라미터는 추론 궤적에서 충분히 좋은 통찰을 뽑는 것과 noisy하거나 불필요한 갱신을 넣는 overthinking을 피하는 것 사이의 trade-off다. 실증적으로 5라운드가 좋은 균형을 제공한다. AppWorld에서 1라운드는 유용한 전략 조각을 충분히 추출하지 못하고, 10라운드처럼 너무 많으면 성능이 떨어질 수 있다.

> 표 19. Reflection iteration 효과(AppWorld, DeepSeek-V3.1; 오프라인, test-normal).

| # Reflection iterations | Normal TGC | Normal SGC | 평균 |
| --- | ---: | ---: | ---: |
| N/A(ACE 없음) | 63.7 | 42.9 | 53.3 |
| 1 | 69.0 (+5.3) | 53.6 (+10.7) | 61.3 (+8.0) |
| 3 | **74.4 (+10.7)** | 57.1 (+14.2) | 65.8 (+12.5) |
| 5 | 72.6 (+8.9) | **62.5 (+19.6)** | **67.6 (+14.3)** |
| 10 | 71.4 (+7.7) | 58.9 (+16.0) | 65.2 (+11.9) |

**Deduplication threshold.** 새로 뽑은 통찰을 기존 항목과 얼마나 공격적으로 병합할지 제어한다. FiNER에서 시험 범위의 성능 변화는 작아, 중복 제거 강도의 중간 변화에 ACE가 강건함을 보인다.

> 표 20. Deduplication threshold 효과(FiNER, DeepSeek-V3.1).

| Threshold | FiNER Acc. |
| --- | ---: |
| N/A(ACE 없음) | 70.7 |
| 50% | 77.0 (+6.3) |
| 70% | 73.9 (+3.2) |
| 90% | 78.6 (+7.9) |

**Pruning trigger(최대 컨텍스트 길이).** 이 임계값은 무한 성장을 막기 위해 오래되었거나 효용이 낮은 항목을 병합·제거할 시점을 정한다. 경험에서 학습할 충분한 컨텍스트 보존과 비용·noise를 줄일 압축성의 균형을 맞춘다. FiNER에서 10K~100K 토큰까지 성능이 안정적이므로, ACE는 정밀 튜닝한 길이 임계값을 요구하지 않는다. pruning은 핵심 재사용 전략을 보존하며 낡거나 harmful한 조각을 주로 제거한다.

> 표 21. Pruning trigger 효과(FiNER, DeepSeek-V3.1).

| 최대 컨텍스트 길이 | FiNER Acc. |
| --- | ---: |
| N/A(ACE 없음) | 70.7 |
| 10K | 78.6 (+7.9) |
| 50K | 78.4 (+7.7) |
| 100K | 78.3 (+7.6) |

전체적으로 ACE는 하이퍼파라미터에 매우 민감하지 않다. 3~5 reflection round, 50~90% dedup threshold, 10K~100K pruning trigger 같은 합리적 선택은 모두 강한 성능을 일관되게 낸다.

## 부록 B. 확장 관련 연구: 에이전트 메모리

점점 많은 연구가 에이전트가 과거 trajectory의 경험을 축적하고 외부(흔히 non-parametric) 메모리를 이용해 미래 행동을 안내하는 방법을 탐색한다. AgentFly(Zhou et al., 2025)는 에이전트가 과업을 풀면서 메모리를 계속 진화시켜 다양한 환경에서 확장 가능한 강화학습과 장기 지평 추론을 가능하게 하는 확장 프레임워크를 제시한다. AWM(Agent Workflow Memory)(Wang et al., 2025b)은 과거 trajectory에서 증류한 구조화된 routine인 재사용 workflow를 유도하고, 이를 선택적으로 메모리에 주입해 웹 탐색 벤치마크의 효율성과 일반화를 높인다. A-MEM(Xu et al., 2025)은 Zettelkasten 방식에서 영감 받은 동적 조직 메모리 시스템을 도입한다. 저장 메모리마다 tag·keyword·맥락 설명 같은 구조화 속성을 붙이고 관련 과거 항목과 자동 연결하며, 기존 항목도 새 지식으로 갱신한다. Agentic Plan Caching(Zhang et al., 2025c)은 비용 효율에 초점을 두고 에이전트 trajectory에서 재사용 계획 template를 뽑아 테스트 시점 빠른 실행을 위해 cache한다.

이 연구들은 LLM 에이전트의 적응성·효율성·일반화를 높이는 외부 메모리 가치를 보인다. ACE는 에이전트 메모리뿐 아니라 시스템 프롬프트·사실 근거·AI 시스템을 떠받치는 다른 입력까지 포괄하는 더 넓은 컨텍스트 적응 과제를 다룬다는 점에서 다르다. 또한 간결성 편향과 컨텍스트 붕괴라는 기존 적응법의 두 근본 한계를 강조하고, raw task 성능을 넘어 강건성·신뢰성·확장성에 중요함을 보인다. 따라서 정확도뿐 아니라 비용·지연·확장성도 평가한다.

## 부록 C. 확장 논의

### C.1 ACE와 GEPA

**범위와 목표.** GEPA와 ACE 모두 가중치를 갱신하지 않고 테스트 시점 컨텍스트 적응으로 모델 또는 에이전트 행동을 개선하지만, 서로 다른 형태의 적응을 위해 설계되었다. GEPA는 rollout trajectory와 reflection feedback으로 개선 instruction prompt를 반복 제안·선택하는 prompt evolution으로 적응을 본다. 목표는 rollout budget 안에서 과업 evaluator를 최대화하는 것이다. ACE는 장기 지평에서 세밀하고 재사용 가능한 많은 통찰을 축적·보존해야 성능이 나오는 환경을 겨냥한다. AppWorld 같은 다중 턴 에이전트는 상호작용 내내 단계별 절차·도구 사용 규칙을 보존해야 하고, FiNER·Formula 같은 도메인 특화·지식 집약 벤치마크는 상세를 잃지 않고 단일 instruction prompt에 압축하기 어려운 특수 규칙·edge case·도메인 개념을 많이 유지해야 정확하다.

**갱신 메커니즘과 표현.** GEPA는 후보마다 end-to-end로 최적화한 완전 프롬프트를 evolutionary loop에서 생성·선택하여 컨텍스트를 갱신한다. ACE는 구조화·항목화된 Playbook으로 컨텍스트를 표현하고 incremential delta update를 적용한다. Curator는 새 통찰만 작성하고 단순 결정 로직으로 Playbook에 병합한다. 이는 반복 전체 프롬프트 재작성을 피하고 장기 실행에서 이전 규칙을 안정적으로 유지하며, 중복 제거·표적 refinement·정확도를 돕거나 해친 항목의 추적 같은 세밀한 bookkeeping을 가능하게 한다.

### C.2 ACE와 Dynamic Cheatsheet(DC)

**범위와 목표.** DC와 ACE 모두 테스트 시점 재사용 통찰을 모으지만, 서로 다른 환경을 겨냥한다. DC는 각 질의가 독립인 AIME, Game of 24, GPQA 같은 단일 턴 추론 벤치마크에서 주로 평가된다. 이 환경에서는 나중 문제에 도움이 되는 짧은 재사용 휴리스틱·실행 artifact(예: 코드 조각)를 저장해서 향상하는 경우가 많다. ACE는 상세한 high-fidelity guidance가 계속 남아야 하는 환경을 다룬다. 다중 턴 에이전트는 상호작용 전반의 단계별 절차·도구 사용 규칙을 기억해야 하며, 도메인 특화·지식 집약 벤치마크는 압축 시 정보를 잃기 쉬운 특수 규칙·edge case·도메인 개념을 많이 보존해야 한다.

**갱신 메커니즘.** DC는 cheatsheet 전체를 다시 써서 메모리를 갱신한다. DC-CU는 매 단계 전체 cheatsheet를 재생성하고, DC-RS는 검색한 예시에서 새 요약을 작성한다. 반복 전체 재작성은 기존 내용을 줄이고 압축하는 경향이 있어 유용한 도메인 세부사항이 시간이 지나며 빠지거나 갑자기 사라지는 컨텍스트 붕괴를 일으킬 수 있다. ACE는 incremental delta update로 전체 재작성을 피한다. Curator는 새 통찰만 작성하고 단순 결정 로직으로 구조화·항목화된 Playbook에 병합한다. 이전 규칙이 장기 실행에도 안정적이고, 도움이 된 항목 추적·중복 제거·항목 refinement도 쉬워진다. 절제 연구에서 delta update를 없애면 AppWorld test-normal의 TGC는 11.7%, SGC는 27.8% 크게 떨어져 delta update가 핵심임을 보인다.

## 부록 D. AppWorld 리더보드 스냅샷(2025-09)

> 그림 5. 2025년 9월에 접근한 AppWorld 리더보드. 본문 비교에서 IBM CUGA는 방법론 baseline이 아닌 리더보드 성능 범위를 보여 주는 참조다.

## 부록 E. LLM 사용

이 연구는 LLM의 효과적 컨텍스트 적응을 위한 알고리즘과 시스템 프레임워크 개발에 초점을 둔다. 따라서 제안 방법의 실증 평가에 LLM을 사용했다. 논문 작성에는 문법 오류 교정 같은 문장 다듬기 용도로만 LLM을 썼으며, 새 텍스트를 처음부터 생성하는 데 사용하지 않았다.

## 부록 F. 프롬프트

이 부록의 코드·변수·API 이름과 `{{...}}` placeholder는 원문 그대로 사용한다. 아래는 각 그림에 실린 자연어 지시의 전체 구조를 한국어로 옮긴 것이다.

### F.1 그림 6 — AppWorld ICL baseline Generator

> 그림 6. AppWorld의 ICL-baseline Generator 프롬프트.

프롬프트는 에이전트에게 “감독자이며 일상 과업을 완전히 자율적으로 달성해야 하는 매우 지능적인 AI Assistant”라고 역할을 준다. Spotify·Venmo 등의 앱 API를 사용해 사용자를 대신하고, Python REPL에서 코드를 쓰면 환경이 실행 결과를 보여 주고 그 결과에 따라 다음 작은 코드 조각을 써서 목표를 달성하는 다단계 대화를 수행한다고 설명한다. 제공되는 세 핵심 API와 각 실행 출력은 이후 호출에 사용할 수 있으며, 실제 과업 해결 코드를 생성하게 한다. `[3 shot example]` 뒤에 다음 지시를 둔다.

1. 코드 블록은 반드시 newline 뒤의 ```` ``` ````로 끝낸다.
2. 이전 코드 블록의 변수를 이후 코드 블록에서 사용할 수 있다.
3. 예시에 나온 이메일·access token·변수(예: `spotify_password`)는 더 이상 유효하지 않다.
4. 계정 정보는 `supervisor` 앱, 친구·가족 정보는 `phone` 앱에서 얻을 수 있다.
5. API 호출 전에는 항상 `apis.api_docs.show_api_doc`으로 명세를 본다.
6. 매 단계 작은 코드 조각 하나만 작성하고, 되돌릴 수 없는 변경 전에 모든 것이 올바로 작동하는지 확인한다.
7. 많은 API가 `pages`로 항목을 반환하므로 `page_index`를 순회해 모든 페이지를 처리한다.
8. 과업 완료 뒤 반드시 `apis.supervisor.complete_task()`를 호출한다. 정보 답이 필요한 과업이면 `apis.supervisor.complete_task(answer=<answer>)`를 호출하고, 답이 필요 없으면 인자 없이 호출한다.

실제 과업 입력은 `{{ main_user.first_name }}`, `{{ main_user.last_name }}`, `{{ main_user.email }}`, `{{ main_user.phone_number }}`, `{{ input_str }}`로 구성한다. 앱 목록·앱별 API 목록·개별 API 명세 조회 예시는 각각 다음 코드다.

```python
print(apis.api_docs.show_app_descriptions())
print(apis.api_docs.show_api_descriptions(app_name='spotify'))
print(apis.api_docs.show_api_doc(app_name='spotify', api_name='login'))
```

### F.2 그림 7 — AppWorld Dynamic Cheatsheet Generator

> 그림 7. AppWorld의 Dynamic Cheatsheet Generator 프롬프트.

그림 6의 역할·REPL·API·8개 핵심 지시를 유지하되, 현재 과업에 적용할 관련 전략·패턴·예시를 담은 cheatsheet가 주어진다고 명시하고 `CHEATSHEET: {{ cheat_sheet }}`를 넣는다. 추가 지시는 다음 세 묶음이다.

- **분석과 전략**: 시작 전 질문과 cheatsheet를 주의 깊게 분석하고, 적용 가능한 패턴·전략·예시를 찾으며, 구조적 접근을 만들고 제공된 참고 자료의 제한도 검토·기록한다.
- **해결 개발**: 다른 사람이 따르고 검토할 수 있는 명확하고 논리적 단계로 해결책을 제시하며, 최종 결론 전 추론·방법론을 설명하고, 각 단계를 상세히 설명하며, 가정·중간 계산을 확인한다.
- **프로그래밍 과업**: 깨끗하고 효율적인 Python을 쓰고, Python 코드 블록 뒤에 명시적으로 `EXECUTE CODE!`를 요청하는 엄격한 실행 프로토콜을 따른다. import·의존성을 상단에 선언하고, 복잡한 로직에는 inline comment를 넣으며, 실행 뒤 결과를 검증한다. 적용 가능하면 cheatsheet 최적화 기법을 쓴다. 코드는 외부 파일 의존성 없이 자체 완결적이어야 하며 placeholder·system-specific/local hard-coded path는 넣지 않는다. 표준적인 pip package는 사용할 수 있고, 오류가 지속되면 대안을 택하며 `chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")` 같은 local path·engine-specific 설정은 피한다.

### F.3 그림 8 — AppWorld GEPA Generator

> 그림 8. AppWorld의 GEPA 프롬프트.

그림 8은 그림 6과 동일한 자율 AppWorld agent 기본 프롬프트와 8개 핵심 지시를 사용한다. 코드 블록 종료, 변수 재사용, 예시 credential 무효, `supervisor`/`phone` 정보원, API 명세 선조회, 한 단계 한 코드 조각, pagination, `complete_task` 호출을 명시한다. GEPA는 실행 trajectory에서 프롬프트 전체를 반성적으로 발전시키며, 이 Generator 프롬프트에는 별도 cheatsheet/playbook 주입이 없다.

### F.4 그림 9 — AppWorld ACE Generator

> 그림 9. AppWorld의 ACE Generator 프롬프트.

그림 6의 기본 역할·REPL·API·8개 핵심 지시를 유지한다. 추가로 ACE가 축적한 구체 전략·흔한 실수·검증된 해결책을 담은 포괄적 Playbook을 제공한다고 하고, 실행 전 Playbook을 읽은 뒤 관련 section을 명시적으로 활용하라고 지시한다.

```text
ACE Playbook:
PLAYBOOK_BEGIN
{{ playbook }}
PLAYBOOK_END
```

추가 9번째 지시는 cheatsheet를 도구로 취급하고, 특정 상황·과업 맥락에 관련되고 적용 가능한 부분만 사용하며 나머지는 자기 판단을 쓰라는 것이다. 실제 과업 입력과 API 조회 코드 형식은 그림 6과 동일하다.

### F.5 그림 10 — AppWorld ACE Reflector

> 그림 10. AppWorld의 ACE Reflector 프롬프트.

역할은 현재 trajectory를 진단하는 AppWorld coding agent·교육자다. 실행 피드백, API 사용, unit test report, 해당할 때 ground truth에 근거해 무엇이 잘못됐는지 또는 더 나아질 점을 찾는다. 모델 reasoning trace를 면밀히 분석하고, 예측과 ground truth를 비교해 간극을 이해하며, 구체적 개념 오류·계산 오류·잘못 적용한 전략을 식별하고 미래 오류를 막을 실행 가능한 통찰을 제시해야 한다. 잘못된 source of truth, filter(기간/방향/정체성), formatting, 인증 누락 같은 root cause와 과업의 단계별 교정을 구체화한다. Generator가 사용한 playbook bullet마다 정답 생성에 `helpful`, `harmful`, `neutral` 중 어떤 tag인지 지정하고, API 출력 형식이 불명확하거나 기대와 다르면 예를 들어 `apis.blah.show_contents()`가 content object가 아니라 `content_id` 문자열 list를 반환한다는 식으로 schema를 명시적으로 큐레이션한다.

입력은 다음 구획이다: `GROUND_TRUTH_CODE_START ... END`, `TEST_REPORT_START ... END`, `PLAYBOOK_START ... END`, 그리고 전체 agent-environment trajectory. 출력은 순수 JSON이며 `reasoning`, `error_identification`, `root_cause_analysis`, `correct_approach`, `key_insight` 필드를 가진다. 원문은 (a) Venmo transaction description의 keyword가 아니라 Phone app contact로 roommate를 식별해야 총액 오류를 피한다는 예, (b) playlist pagination에 `range(10)` 대신 빈 결과까지 `while True`와 `page_index` 증가를 써야 한다는 예를 제공한다.

### F.6 그림 11 — AppWorld ACE Curator

> 그림 11. AppWorld의 ACE Curator 프롬프트.

역할은 이전 시도의 reflection에 기반해 기존 playbook에 더할 새 통찰을 찾는 master curator다. playbook은 유사 질문 답변을 돕고, reflection은 나중 playbook 사용 시 보이지 않는 ground truth answer로 생성되므로, ground truth와 맞을 가능성을 높일 일반화 가능한 내용을 만들어야 한다. 기존 playbook·reflection을 검토하고 현재 playbook에 **없는** 새 통찰·전략·실수만 식별하며, 유사 조언이 이미 있으면 완벽히 보완하는 내용만 더한다. 전체 playbook을 재생성하지 말고 필요한 추가만 제공하며, 양보다 질·간결성·실행 가능성을 중시한다. API schema가 불명확하면 그 형식도 추가한다.

입력은 `{question_context}`, `{current_playbook}`, `{final_generated_code}`, `{guidebook}`이고, 출력은 markdown 없이 순수 JSON `reasoning`, `operations`다. operation은 `type`, `section`, `content`를 가지며 가능한 operation은 fresh ID를 시스템이 부여하는 `ADD`다. 새 내용이 없으면 `operations`는 빈 list다. 예시는 roommate 정체성을 Phone contact라는 권위 있는 source에서 해결하라는 `strategies_and_hard_rules` 추가와, 모든 page를 `while True`로 순회하라는 `apis_to_use_for_specific_information` 추가를 보인다.

### F.7 그림 12 — FiNER ACE Generator

> 그림 12. FiNER의 ACE Generator 프롬프트.

역할은 지식, 큐레이션된 전략·통찰 Playbook, 이전 실수의 진단 reflection을 이용해 질문에 답하는 분석 전문가다. Playbook을 주의 깊게 읽어 관련 전략·formula·insight를 적용하고, 거기 적힌 흔한 실수를 피하며, 단계별 추론을 보이고, 간결하지만 철저히 분석한다. 관련 code snippet 또는 formula를 적절히 사용하고 최종 답 전 계산·논리를 재검사한다. 출력 JSON은 `reasoning`, `bullet_ids`, `final_answer`다. `bullet_ids`에는 답변에 관련되고 도움이 된 모든 Playbook bullet의 ID(예: `calc-00001`, `fin-00002`)를 넣는다. 입력은 Playbook, Reflection, Question, Context다.

### F.8 그림 13 — FiNER ACE Reflector

> 그림 13. FiNER의 ACE Reflector 프롬프트.

역할은 모델 reasoning이 틀린 이유를 예측 답과 ground truth 사이의 간극으로 진단하는 분석가·교육자다. reasoning trace에서 오류 지점을 찾고, 환경 피드백 및 예측/정답 비교를 고려하며, 구체 개념 오류·계산 실수·오적용 전략을 식별한다. surface error가 아니라 root cause에 초점을 맞추고, 미래에 피할 실행 가능한 통찰과 모델이 달리 했어야 할 구체 행동을 제시한다. Generator가 쓴 각 playbook bullet에는 `helpful`·`harmful`·`neutral` tag를 준다.

입력은 Question, Model's Reasoning Trace, Model's Predicted Answer, Ground Truth Answer, Environment Feedback, Generator가 사용한 Playbook 부분이다. JSON 출력은 `reasoning`, `error_identification`, `root_cause_analysis`, `correct_approach`, `key_insight`, 그리고 각 `id`와 `tag`를 담은 `bullet_tags`다.

### F.9 그림 14 — FiNER ACE Curator

> 그림 14. FiNER의 ACE Curator 프롬프트.

역할과 원칙은 그림 11의 Curator와 같다. 반드시 valid JSON만 응답하고 markdown/code block을 쓰지 말아야 한다. 기존 Playbook과 최근 reflection을 검토하여 누락된 새 통찰·전략·실수만 찾고, 중복을 피하며, 전체 playbook을 다시 만들지 말고 필요한 추가만 작성한다. 각 추가는 실행 가능해야 하고, 새 내용이 없으면 빈 operation list를 돌려준다.

추가 입력에는 `token_budget`, `current_step`, `total_samples`, `playbook_stats`, `recent_reflection`, `current_playbook`, `question_context`가 들어간다. 출력은 `reasoning`과 `operations`를 가진 순수 JSON이며, 현재 원문에 정의된 operation은 새 bullet을 추가하는 `ADD` 하나다. `section` 예시는 `formulas_and_calculations`이고 `content`에는 새 계산 방법 등을 넣는다.

## 참고문헌

원문은 GDPR·CCPA와 2010~2025년의 컨텍스트 적응, 에이전트 메모리, 장문 컨텍스트, KV cache, 프롬프트 최적화, 평가 벤치마크 연구를 포함한 참고문헌을 수록한다. 본문 인용 표기는 원문 저자·연도 표기를 유지했다. 주요 서지 항목은 다음과 같다.

- Agarwal et al. (2024), *Many-Shot In-Context Learning*.
- Agrawal et al. (2025), *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*.
- Asai et al. (2024), *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*.
- Borgeaud et al. (2022), *Improving Language Models by Retrieving from Trillions of Tokens*.
- Fansi Tchango et al. (2022), *DDXPlus: A New Dataset For Automatic Medical Diagnosis*.
- Gao et al. (2025), *The Prompt Alchemist: Automated LLM-Tailored Prompt Optimization for Test Case Generation*.
- Gim et al. (2024), *Prompt Cache: Modular Attention Reuse for Low-Latency Inference*.
- Krause et al. (2019), *Dynamic Evaluation of Transformer Language Models*.
- Li et al. (2023), *Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs*.
- Liu et al. (2024a), *DeepSeek-V3 Technical Report*.
- Loukas et al. (2022), *FiNER: Financial Numeric Entity Recognition for XBRL Tagging*.
- Marreed et al. (2025), *Towards Enterprise-Ready Computer Using Generalist Agent*.
- Opsahl-Ong et al. (2024), *Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs*.
- Shinn et al. (2023), *Reflexion: Language Agents with Verbal Reinforcement Learning*.
- Suzgun et al. (2025), *Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory*.
- Trivedi et al. (2024), *AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents*.
- Wang et al. (2025a), *FinLoRA: Benchmarking LoRA Methods for Fine-Tuning LLMs on Financial Datasets*.
- Wang et al. (2025b), *Agent Workflow Memory*.
- Wu et al. (2024), *StreamBench: Towards Benchmarking Continuous Improvement of Language Agents*.
- Xu et al. (2025), *A-Mem: Agentic Memory for LLM Agents*.
- Yao et al. (2023), *ReAct: Synergizing Reasoning and Acting in Language Models*.
- Yuksekgonul et al. (2025), *Optimizing Generative AI by Backpropagating Language Model Feedback*.
- Zhang et al. (2025c), *Agentic Plan Caching: Test-Time Memory for Fast and Cost-Efficient LLM Agents*.
- Zheng et al. (2023), *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*.
- Zhou et al. (2025), *AgentFly: Fine-tuning LLM Agents without Fine-tuning LLMs*.
