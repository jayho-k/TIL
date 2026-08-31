# Agentic Memory: 대규모 언어 모델 에이전트를 위한 통합 장기·단기 메모리 관리 학습

> 논문: Yi Yu, Liuyi Yao, Yuexiang Xie, Qingquan Tan, Jiaqi Feng, Yaliang Li, Libing Wu, *Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents*, arXiv:2601.01885v3 (2026-07-23).
>
> 이 문서는 원문 PDF를 문단 단위로 옮기도록 재작성 중인 한국어 전문 번역본이다. 완료 전에는 최종본으로 사용하지 않는다. 용어와 모델명, 데이터셋명, 도구 이름, 수식 기호, 참고문헌의 서지 정보는 원문 표기를 보존하며, 번역 외의 요약·비평은 추가하지 않는다.

## 저자

Yi Yu<sup>1,2</sup>, Liuyi Yao<sup>2</sup>, Yuexiang Xie<sup>2</sup>, Qingquan Tan<sup>1</sup>, Jiaqi Feng<sup>1</sup>, Yaliang Li<sup>2</sup>, Libing Wu<sup>1</sup>  
<sup>1</sup> Wuhan University, School of Cyber Science and Engineering · <sup>2</sup> Alibaba Group  
교신저자: Liuyi Yao, Libing Wu

## 초록

대규모 언어 모델(LLM) 에이전트는 유한한 컨텍스트 창 때문에 긴 시간 범위의 추론에서 근본적 한계를 겪으며, 따라서 효과적인 메모리 관리가 중요하다. 기존 방법은 대체로 장기 메모리(LTM)와 단기 메모리(STM)를 별개 구성 요소로 다루고, 휴리스틱이나 보조 제어기에 의존한다. 이는 적응성과 종단 간 최적화를 제한한다. 본 논문은 LTM과 STM 관리를 에이전트 정책에 직접 통합하는 통합 프레임워크 **Agentic Memory(AgeMem)** 를 제안한다. AgeMem은 메모리 연산을 도구 기반 행동으로 노출하여, LLM 에이전트가 무엇을 언제 저장·검색·갱신·요약·삭제할지를 자율적으로 결정하도록 한다.

이 통합 행동을 학습시키기 위해 세 단계 점진적 강화학습 전략을 제안하고, 메모리 연산이 유발하는 희소하고 불연속적인 보상을 다루기 위해 단계별 GRPO를 설계한다. 5개의 장기 시간 범위 벤치마크 실험에서 AgeMem은 여러 LLM 백본에 걸쳐 강력한 메모리 증강 기준선을 일관되게 앞섰다. 또한 과제 성능, 장기 메모리 품질, 컨텍스트 사용 효율을 모두 개선했다.

## 1. 서론

다단계 추론과 복잡한 워크플로를 포함하는 장기 에이전트 과제에서 LLM 에이전트의 효과는 어느 순간 주의를 기울일 수 있는 정보, 즉 에이전트의 메모리에 근본적으로 제약된다. 메모리는 보통 사용자 또는 과제별 지식을 지속적으로 저장하는 장기 메모리(LTM)와, 현재 입력 컨텍스트에 포함된 정보를 뜻하는 단기 메모리(STM)로 나뉜다. 고품질 LTM은 누적 지식의 효율적 검색을 지원하고, 효과적인 STM 관리는 중복을 줄이며 두드러진 컨텍스트를 보존한다. 두 종류를 함께 관리하면 유한한 컨텍스트 창의 한계를 완화할 수 있다.

그럼에도 기존 연구는 LTM과 STM을 주로 독립 구성 요소로 취급해 왔다. STM은 MainRAG(Chang et al., 2025)와 ReSum(Wu et al., 2025a)에서처럼 검색 증강 생성(RAG)(Pan et al., 2025b)을 통해 강화되는 경우가 많다. 이들 방법은 외부 검색 또는 주기적 요약으로 사용 가능한 컨텍스트를 넓힌다. 일부 과제에는 효과적이지만, 미리 정한 일정이나 휴리스틱 규칙에 크게 의존한다. 그 결과 자주 나타나지 않지만 중요한 세부 정보를 간과하거나, 불필요한 잡음을 넣을 수 있다(Ma et al., 2025; Dong et al., 2025).

반면 LTM 관리는 서로 다른 계통으로 발전했으며, 대체로 트리거 기반(Kang et al., 2025; Wang and Chen, 2025; Wang et al., 2025c; Chhikara et al., 2025)과 에이전트 기반(Yan et al., 2025; Hu et al., 2025; Xu et al., 2025)으로 나뉜다. 전자는 정해진 순간에 고정된 메모리 연산을 실행하고, 후자는 특수 메모리 관리자가 무엇을 어떻게 저장할지 판단한다. 후자가 더 유연하지만, 대부분의 접근법은 여전히 수작업 규칙이나 보조 전문가 모델에 의존한다. 이는 적응성을 제한하고 시스템 복잡도를 높인다(Xiong et al., 2025).

그 결과 LTM과 STM은 느슨하게 결합된 별도 모듈로 남았다. 이 통합 관리에는 다음 세 과제가 있다. (C1) **기능 이질성 조정**: LTM은 저장·갱신·폐기 대상을 결정하고 STM은 활성 컨텍스트의 검색·요약·제거를 결정하므로, 상호 보완적 기능을 함께 조율해야 한다. (C2) **학습 패러다임 불일치**: LTM 학습은 상호작용 전 세션 정보를 활용하는 경향이 있고 STM 학습은 긴 컨텍스트를 흉내 내기 위해 방해 요소를 주입한다. 안정적 보상이 이어지는 궤적을 가정하는 표준 RL도 단편적 메모리 경험과 맞지 않는다. (C3) **배포 제약**: 많은 시스템이 메모리 제어를 보조 전문가 LLM에 맡겨 추론 비용과 학습 복잡도를 키운다.

구체적으로 AgeMem은 세 가지 근본 과제를 다룬다. 첫째, **기능 이질성의 조정(C1)** 이다. LTM은 무엇을 저장·갱신·폐기할지를 결정하는 반면, STM은 활성 컨텍스트에서 무엇을 검색·요약·제거할지를 조절한다(Zhang et al., 2025b). 과제는 두 기능의 상호작용을 시너지 있게 조율하는 통합 기제를 설계하는 것이다. 둘째, **학습 패러다임 불일치(C2)** 이다. 기존 RL 프레임워크는 두 메모리 유형에 현저히 다른 학습 전략을 적용한다(Ma et al., 2024). LTM 중심 학습은 상호작용 전에 이용 가능한 세션 수준 정보를 활용하는 일이 많고, STM 학습은 긴 컨텍스트를 흉내 내기 위해 방해 요소를 주입한다(Sun et al., 2024). 또한 표준 RL은 안정적 보상을 가진 연속 궤적을 가정하지만, 메모리 연산이 본질적으로 만드는 단편적·불연속적 경험(Wu et al., 2025a)과 충돌한다. 셋째, **실제 배포 제약(C3)** 이다. 많은 에이전트 시스템은 메모리 제어를 보조 전문가 LLM에 의존하여 추론 비용과 학습 복잡도를 크게 키운다. 외부 전문가 모델 없이 통합 메모리 관리를 에이전트에 직접 넣는 방법은 여전히 열린 문제다.
그 결과 LTM과 STM은 대체로 분리되고 느슨하게 결합된 모듈로 취급된다. 그림 1에서 보듯 기존 구조는 대개 두 형태를 따른다. (a) 정적 STM과 트리거 기반 LTM, 또는 (b) 정적 STM과 에이전트 기반 LTM이다. 두 경우 모두 두 메모리 시스템을 독립적으로 최적화한 뒤 임시방편으로 결합하므로, 메모리 구성이 단절되고 긴 시간 범위 추론 과제에서 성능이 최적에 못 미친다. 따라서 LTM과 STM 관리를 통합하는 일은 필요하지만 거의 탐구되지 않은 과제로 남아 있다.

그럼에도 통합 메모리 관리를 실현하려면 세 가지 근본 과제를 풀어야 한다. 첫째, **기능 이질성 조정(C1)** 이다. LTM과 STM은 서로 다르면서 보완적인 목적을 가진다. LTM은 무엇을 저장·갱신·폐기할지 결정하고, STM은 활성 컨텍스트에서 무엇을 검색·요약·제거할지 관장한다(Zhang et al., 2025b). 과제는 이들의 상호작용을 상승효과가 나도록 조율하는 통합 기제를 설계하는 일이다. 둘째, **학습 패러다임 불일치(C2)** 이다. 기존 RL 프레임워크는 두 메모리 유형에 현저히 다른 학습 전략을 적용한다(Ma et al., 2024). LTM 중심 학습은 상호작용 전에 이용 가능한 세션 수준 정보를 활용하는 일이 많고, STM 학습은 긴 컨텍스트를 흉내 내기 위해 방해 요소를 주입한다(Sun et al., 2024). 또한 표준 RL은 안정적 보상을 가진 연속 궤적을 가정하지만, 메모리 연산이 본질적으로 만드는 단편적·불연속적 경험(Wu et al., 2025a)과 충돌하여 종단 간 최적화를 특히 어렵게 한다. 셋째, **실제 배포 제약(C3)** 이다. 많은 에이전트 시스템은 메모리 제어를 보조 전문가 LLM에 의존하여 추론 비용과 학습 복잡도를 크게 키운다. 외부 전문가 모델 없이 통합 메모리 관리를 에이전트에 직접 넣는 방법은 여전히 열린 문제다.

이 문제를 해결하기 위해 본 논문은 그림 1 오른쪽과 같은 Agentic Memory(AgeMem)를 제안한다. 메모리를 외부 구성 요소로 다루는 선행 설계와 달리 AgeMem은 두 메모리 유형을 모두 에이전트 의사결정 과정에 통합한다. 통합 도구 기반 인터페이스를 통해 LLM은 LTM과 STM의 메모리 연산을 자율적으로 호출·실행한다. 또한 3단계 점진적 RL 전략을 설계한다. 모델은 먼저 LTM 저장 능력을 습득하고, 그다음 STM 컨텍스트 관리를 학습하며, 마지막으로 완전 과제 설정에서 두 형태의 메모리를 조정한다. 단계 간 단편화된 경험 문제를 해결하기 위해 출력 보상을 이전 메모리 결정까지 전파하는 단계별 GRPO(Shao et al., 2024)를 설계한다. 이는 RL의 희소·불연속 보상으로 인한 어려움을 완화한다. 5개 장문맥·추론 집약 벤치마크에서의 평가는 AgeMem이 강력한 기준선을 지속적으로 앞서며 통합 메모리 관리의 효과를 입증함을 보인다.

본 논문의 기여는 다음과 같다.

- LLM 기반 에이전트가 장기·단기 메모리를 언제, 무엇을, 어떻게 관리할지 자율적으로 결정하게 하는 통합 에이전트 메모리 프레임워크 AgeMem을 제안한다.
- 통합 메모리 관리 행동을 효과적으로 종단 간 학습할 수 있도록 단계별 GRPO를 갖춘 3단계 점진적 RL 전략을 개발한다.
- 여러 모델과 장기 시간 범위 벤치마크에서 폭넓게 평가하여 복잡한 에이전트 과제에서의 견고성과 효과를 보인다.

> 그림 1. 독립 메모리 관리와 통합 메모리 관리 프레임워크의 비교. (왼쪽) 정적 STM과 트리거 기반 LTM을 쓰는 전통 프레임워크. (가운데) STM은 정적으로 유지한 채, 메모리 관리자가 에이전트 방식으로 LTM을 제어하는 독립 프레임워크. (오른쪽) 명시적 도구 기반 연산으로 LTM과 STM을 함께 지능적으로 관리하는 제안 AgeMem 프레임워크.

## 2. 배경 및 관련 연구

### 장기 메모리

지속적 LTM은 긴 시간 범위에서 동작하는 LLM 에이전트에 중요하다. LangMem은 여러 메모리 유형을 지원하는 모듈형 프레임워크를 제공하고, A-Mem은 구조화된 지식 단위를 연결하는 Zettelkasten 영감 설계를 사용한다. Mem0은 확장 가능한 추출-갱신 파이프라인과 그래프 기반 변형을 제안하며, Zep은 시간 지식 그래프로 세션 간·시간 인지 추론을 지원한다. 이 방법들은 정보를 정리하고 검색하는 데 효과적이지만, 미리 정의한 구조나 휴리스틱 갱신 규칙에 의존한다. 메모리가 커질수록 복잡도가 증가하며, 우선순위와 망각을 위한 적응적 학습 전략이 부족하다. AgeMem은 과제 요구와 장기 효용에 따라 무엇을 저장·갱신·망각할지 동적으로 결정하는 적응적 메모리 정책을 학습한다.

### 단기 메모리

에이전트형 LLM의 STM은 주로 컨텍스트 선택과 검색을 뜻한다. RAG는 검색된 내용을 프롬프트에 삽입해 사용 가능한 컨텍스트를 확장하는 지배적 패러다임이지만, 장기 시간 범위에서 컨텍스트 폭증을 근본적으로 막지 못하고 무관하거나 산만한 정보를 넣을 수 있다. ReSum은 상호작용 이력을 압축된 추론 상태로 주기적으로 압축하지만, 요약 일정은 대체로 미리 정해져 있고 과도한 압축은 드물지만 핵심인 세부를 버릴 수 있다. AgeMem은 검색·요약·필터링을 언제 어떻게 할지 학습하여 효율성과 정보 보존을 유연하게 균형 잡는다.

### LLM 강화학습과 RL 기반 메모리 에이전트

GRPO는 표본 궤적의 상대적 품질로 정책을 최적화해 명시적 가치 함수 없이 안정성을 높인다. 다만 기존 RL 기반 시스템은 메모리를 정적 또는 외부 구성 요소로 다루어 메모리 연산이 만드는 불연속·단편 궤적에 적합하지 않다. 최근 메모리 연산을 행동으로 두고 RL을 적용한 방법도 대개 메모리의 한 측면만 최적화한다. AgeMem은 지속 LTM 연산과 컨텍스트 STM 연산을 포괄하는 이질적 행동의 통합 정책을 지연된 감독 아래 종단 간 학습하며, 저장·검색·필터링·요약을 동일한 최종 과제 보상에 대해 함께 최적화한다.

## 3. 방법

AgeMem은 LLM 에이전트가 LTM과 STM을 종단 간으로 자율 관리하도록 하는 통합 메모리 프레임워크다. 특수 도구 집합으로 메모리 관리 능력을 에이전트에 직접 통합하고, 3단계 점진 전략으로 통합 관리의 최적 전략을 학습한다.

### 3.1 문제 정식화

**AgeMem의 통합 RL 정식화.** 시점 $t$에서 에이전트는 대화 컨텍스트(단기 메모리) $C_t$, 장기 메모리 저장소 $M_t$, 과제 명세 $T$로 이루어진 상태 $s_t=(C_t,M_t,T)$를 관측한다. 명세 $T$에는 입력 질의 $q$, 문맥 정보 $I_q$, 학습 시에만 제공되는 기대 정답 $A_q$가 포함된다. 이 정식화는 일시적 컨텍스트와 지속 지식 모두에 의사결정을 근거하게 한다.

에이전트는 언어 생성과 메모리 연산을 포함하는 혼합 행동 공간 $\mathcal{A}$에서 $a_t$를 선택한다. 매개변수 정책은 $\pi_\theta(a_t\mid s_t)=P(a_t\mid s_t;\theta)$이며, $\theta$는 LLM 매개변수다. 궤적 $\tau=(s_1,a_1,\ldots,s_T,a_T)$의 누적 보상은 다음과 같다.

$$R(\tau)=\sum_iw_iR_i(\tau)+P_{\mathrm{penalty}}(\tau).\tag{1}$$

$R_i$는 과제 성능과 메모리 품질을, $P_{\mathrm{penalty}}$는 중복 저장·과도한 도구 사용·통제되지 않은 컨텍스트 확장을 억제한다. 최적화 목표는 다음과 같다.

$$\theta^*=\arg\max_\theta\mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)].\tag{2}$$

이는 수작업 휴리스틱을 학습 가능한 메커니즘으로 대체하여 메모리 관리를 에이전트 정책의 필수 구성 요소로 취급한다.

**3단계 궤적 구조.** 각 궤적은 $\tau=(\tau^{(1)},\tau^{(2)},\tau^{(3)})$, $T=T_1+T_2+T_3$인 세 연속 단계로 나뉜다. 1단계에서 에이전트는 일상적 상호작용 중 유용한 정보를 LTM에 저장할 수 있다. 2단계에서는 방해·무관 콘텐츠가 제시되며, 선택적 보존·압축을 통해 STM을 관리해야 한다. 3단계에서는 보존된 컨텍스트와 앞서 쌓인 LTM의 조정된 사용이 필요한 과제가 주어진다. $M_t$는 세 단계 내내 지속되는 반면, $C_t$는 정보 누출 방지를 위해 1·2단계 사이에서 초기화된다. 따라서 에이전트는 잔여 컨텍스트로 최종 문제를 풀 수 없고 LTM 검색을 제대로 배워야 한다.

각 단계에서 경험 튜플 $e_t=(s_t,a_t,r_t,\log\pi_{\theta_{old}}(a_t\mid s_t))$을 수집한다. 중간 단계의 $r_t$는 보통 0이고 궤적 완료 후 부여된다. 이 표현은 GRPO의 단계별 공적 할당을 가능하게 하며, 긴 시간의 보상을 단계 간 특정 메모리 결정에 귀속한다.

> 표 1. AgeMem의 LTM·STM 메모리 관리 도구.

| 도구 | 대상 | 기능 |
| --- | --- | --- |
| `ADD` | LTM | $M_t$에 새 지식 추가 |
| `UPDATE` | LTM | $M_t$의 항목 수정 |
| `DELETE` | LTM | $M_t$의 항목 제거 |
| `RETRIEVE` | STM | $M_t$ 항목을 $C_t$로 검색 |
| `SUMMARY` | STM | $C_t$의 구간 요약 |
| `FILTER` | STM | $C_t$에서 무관 구간 필터링 |

### 3.2 도구 인터페이스를 통한 메모리 관리

AgeMem은 표 1의 명시적 도구 인터페이스로 LLM 에이전트에 메모리 연산을 제공한다. `ADD`, `UPDATE`, `DELETE`는 지속 LTM을 수정하고, `RETRIEVE`, `SUMMARY`, `FILTER`는 STM을 세밀하게 제어한다. 이에 따라 메모리 제어는 외부 휴리스틱 파이프라인이 아니라 의사결정의 내재적 구성 요소가 된다.

`ADD`는 장기 저장소 $M_t$에 새 항목을 넣고, `UPDATE`는 `memory_id`로 식별한 항목을 수정하며, `DELETE`는 오래된 지식의 축적을 막기 위해 항목을 제거한다. `RETRIEVE`는 의미적으로 관련 있는 상위 $k$개 기억을 $M_t$에서 활성 컨텍스트 $C_t$로 가져온다. `SUMMARY`는 지정한 상호작용 이력 범위를 핵심 정보를 보존한 간결한 표현으로 압축한다. `FILTER`는 어떤 기준과의 의미 유사도가 임계값 $\theta_f$를 넘는 컨텍스트 메시지를 제거한다. 여섯 연산은 해석 가능하면서도 표현력 있는 메모리 생명주기 제어를 제공한다.

### 3.3 3단계 점진적 RL 전략

안정적인 통합 메모리 행동을 학습하기 위해 과제 인스턴스 $q\in\mathcal T$마다 $K$개의 독립 rollout을 생성한다.

$$\tau_k^{(q)}=(\tau_k^{(1)},\tau_k^{(2)},\tau_k^{(3)}),\quad k=1,\ldots,K.\tag{3}$$

**1단계(LTM 구성).** 에이전트는 일상 대화에서 문맥 정보 $I_q$를 접하고, 중요한 정보를 식별해 $M_t$에 저장한다. 필요할 때 LTM 도구를 호출한다.

**2단계(방해 요소 아래 STM 제어).** STM은 초기화하지만 구성된 LTM은 유지한다. 목표 질의와 의도적으로 관계없는 자연어 발화인 방해 메시지를 제시한다. 에이전트는 이를 최종 답에 이용하지 말고, 필터링·요약 같은 도구 연산으로 잡음을 억제하고 유용한 정보를 보존해야 한다.

**3단계(통합 추론 및 메모리 조정).** 에이전트는 정확한 추론과 효과적인 메모리 검색이 모두 필요한 정식 질의를 받는다. $M_t$에서 관련 지식을 검색하고, $C_t$를 적절히 관리하며, 최종 답을 생성한다.

세 구간은 하나의 완전 궤적 $\tau_k^{(q)}=(e_1,e_2,\ldots,e_T)$를 이루며, 이후 단계별 GRPO의 정책 최적화에 사용된다. 배치 $B$개 과제의 $K$개 rollout 경험을 합친 집합은 $E=\bigcup_{q=1}^B\bigcup_{k=1}^K\{e_t\mid e_t\in\tau_k^{(q)}\}$이며, 크기는 $|E|=B\times K\times T^*$다.

이 교육과정은 QA 형식 감독에 묶이지 않는다. 정보 노출과 과제 실행을 시간적으로 분리해, 지연된 결과 아래 메모리 결정의 유용성을 평가하면 된다. 1단계의 사전 과제 컨텍스트는 환경 설명·검색 문서·이전 대화 이력일 수 있고, 2단계 간섭은 `DISTRACTOR_GEN`으로 합성되며 데이터셋 주석이 필요 없다. 3단계의 하류 과제 보상이 앞선 저장·필터링 결정의 유용성을 판정한다.

### 3.4 통합 관리를 위한 단계별 GRPO

각 과제 $q$의 병렬 rollout 그룹을 $G_q=\{\tau_1^{(q)},\ldots,\tau_K^{(q)}\}$라 하자. 각 궤적의 종료 보상은 $r_T^{(k,q)}=R(\tau_k^{(q)})$다. 종료 단계의 그룹 정규화 이점은 다음과 같다.

$$A_T^{(k,q)}=\frac{r_T^{(k,q)}-\bar r_{G_q}}{\sigma_{G_q}+\epsilon}.\tag{5}$$

$\bar r_{G_q}$와 $\sigma_{G_q}$는 그룹 보상의 평균과 표준편차이며 $\epsilon$은 0으로 나누는 것을 막는다. 이 이점을 같은 궤적의 모든 선행 단계로 방송해 $A_t^{(k,q)}=A_T^{(k,q)}$로 둔다. 따라서 1·2단계의 모든 메모리·추론 행동도 최종 과제 결과에서 일관된 학습 신호를 받는다.

GRPO에 따라 다음 목적함수를 최대화한다.

$$J(\theta)=\mathbb E_{(e_t,A_t)\sim E}\left[r_tA_t-\beta D_{KL}(\pi_\theta\|\pi_{ref})\right].\tag{6}$$

여기서 중요도 비율 $r_t=\pi_\theta(a_t\mid s_t)/\pi_{\theta_{old}}(a_t\mid s_t)$는 새 정책의 갱신 크기를 제어하고, $D_{KL}$은 현재 정책과 고정 참조 정책 사이의 KL 발산, $\beta$는 탐색과 학습 안정성의 균형 계수다.

### 3.5 보상 함수 설계

전체 궤적 보상은 다음과 같다.

$$R(\tau)=\mathbf w^\top\mathbf R+P_{penalty},\tag{7}$$

여기서 $\mathbf w=[w_{task},w_{context},w_{memory}]^\top$, $\mathbf R=[R_{task},R_{context},R_{memory}]^\top$다. $R_{task}$는 LLM 심사자 $S_{judge}(A_{pred},A_q)\in[0,1]$로 과제를 올바르게 풀었는지 평가하며, 답이 없을 때는 선택적으로 벌점을 준다. $R_{context}$는 토큰 사용의 경제성을 평가하는 압축 효율, 한도 초과 전에 요약·필터를 실행했는지 보는 예방 행동, 질의 관련 핵심 내용 손실을 벌하는 정보 보존을 결합한다. $R_{memory}$는 고품질·재사용 가능 저장 비율, 의미 있는 갱신·삭제에 대한 유지보수, 검색 기억과 질의의 LLM 기반 의미 관련성을 합산한다. 대화 턴 수나 컨텍스트 한도 초과는 $P_{penalty}$로 크게 감점한다.

## 4. 실험

### 4.1 실험 설정

**데이터셋.** ALFWorld, SciWorld, PDDL, BabyAI, HotpotQA를 사용했다. 이들은 체화 행동, 게임 기반 추론, 지식 집약 질의응답을 포괄한다. HotpotQA는 질문과 근거 사실을 함께 제공하므로 1단계 문맥 정보를 자동으로 제공한다. AgeMem은 HotpotQA 학습 집합에서만 RL 미세 조정한 뒤, 모든 데이터셋에서 직접 평가했다.

**평가 지표.** ALFWorld·SciWorld·BabyAI에는 Success Rate(SR), PDDL에는 Progress Rate(PR), HotpotQA에는 LLM-as-a-Judge(J)를 사용했다. 지식 추론 중 저장 LTM의 품질은 LLM 평가기로 Memory Quality(MQ)를 계산했다.

**기준선 및 백본.** LangMem, A-Mem, Mem0, Mem0g와 비교하고, RL 미세 조정을 하지 않은 AgeMem-noRL도 포함했다. STM 절제에서는 RAG와 STM 도구를 비교했다. 기반 에이전트는 Qwen2.5-7B-Instruct 및 Qwen3-4B-Instruct다. 에이전트는 Agentscope, AgeMem 미세 조정에는 Trinity를 사용했다.

### 4.2 주요 결과

**대응 방법과의 비교.** 표 2에서 AgeMem은 Qwen2.5-7B-Instruct와 Qwen3-4B-Instruct에서 각각 평균 41.96%, 54.31%로 가장 높은 성능을 보였다. no-memory 대비 상대 개선은 각각 49.59%, 23.52%다. 최고 기준선인 Mem0·A-Mem보다 평균 4.82, 8.57%p 높았고, RL 학습은 AgeMem-noRL보다 각각 8.53, 8.72%p 향상시켜 3단계 RL 전략의 효과를 보였다.

> 표 2. 5개 벤치마크 성능 비교. 굵게는 최고, 밑줄은 차상위 결과를 뜻한다.

| 백본 / 방법 | ALFWorld | SciWorld | PDDL | BabyAI | HotpotQA | 평균 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B · No-Memory | 27.16 | 13.80 | 10.15 | 50.80 | 38.36 | 28.05 |
| Qwen2.5-7B · LangMem | 38.27 | 28.29 | 15.85 | 51.34 | 37.43 | 34.23 |
| Qwen2.5-7B · A-Mem | 34.68 | 28.06 | 18.39 | 58.82 | 43.95 | 36.78 |
| Qwen2.5-7B · Mem0 | 37.49 | 26.99 | 13.96 | 60.58 | 46.66 | 37.14 |
| Qwen2.5-7B · Mem0g | 35.34 | 30.50 | 14.86 | 58.78 | 42.06 | 36.31 |
| Qwen2.5-7B · AgeMem-noRL | 37.90 | 28.67 | 8.87 | 46.34 | 45.36 | 33.43 |
| Qwen2.5-7B · **AgeMem** | **41.07** | **35.55** | 17.31 | **61.42** | **54.44** | **41.96** |
| Qwen3-4B · No-Memory | 38.51 | 47.89 | 30.14 | 55.83 | 47.48 | 43.97 |
| Qwen3-4B · LangMem | 40.89 | 50.42 | 28.42 | 53.80 | 42.70 | 43.25 |
| Qwen3-4B · A-Mem | 34.31 | 50.14 | 34.41 | 61.35 | 48.48 | 45.74 |
| Qwen3-4B · Mem0 | 41.17 | 51.38 | 31.72 | 60.05 | 39.16 | 44.70 |
| Qwen3-4B · Mem0g | 36.69 | 47.76 | 29.61 | 57.59 | 38.12 | 41.95 |
| Qwen3-4B · AgeMem-noRL | 38.02 | 50.42 | 27.52 | 57.48 | 54.49 | 45.59 |
| Qwen3-4B · **AgeMem** | **48.97** | **59.48** | **35.07** | **72.56** | **55.49** | **54.31** |

**저장 LTM의 품질.** HotpotQA의 정답 근거 사실과 저장 기억의 관련성을 LLM으로 평가했다. 그림 2에서 AgeMem의 MQ는 두 백본에서 각각 0.533, 0.605로 가장 높았다. 즉 통합 관리는 과제 성능뿐 아니라 고품질·재사용 가능 지식의 선택적 저장도 촉진한다.

> 그림 2. HotpotQA에서 방법별 Memory Quality(MQ). 점수가 높을수록 저장 기억과 정답 근거 사실의 관련성이 높다.

**STM 관리 효과.** 그림 3은 AgeMem이 STM 도구 없이 RAG를 쓰는 변형보다 프롬프트 토큰을 줄임을 보인다. Qwen2.5-7B에서 AgeMem은 평균 2,117토큰, AgeMem-RAG는 2,186토큰(3.1% 감소)이었다. Qwen3-4B에서는 2,191 대 2,310토큰(5.1% 감소)이었다. 학습된 STM 도구가 과제 성능을 유지하면서 컨텍스트 확장을 통제한다.

> 그림 3. HotpotQA에서 STM 구성별 평균 프롬프트 토큰 수. `-RAG` 접미사는 STM 도구 기반 관리를 RAG로 대체했음을 뜻한다.

**도구 사용 분석.** RL 후 LTM 도구, 특히 `ADD`와 `UPDATE` 사용이 크게 늘었다. Qwen2.5-7B의 `ADD`는 0.92에서 1.64, `UPDATE`는 거의 0에서 0.13이 됐다. `FILTER`도 0.02에서 0.31로 증가했다. 반면 `RETRIEVE`는 Qwen2.5에서 2.31→1.95, Qwen3에서 4.62→4.35로 줄었다. 이는 학습 부족이 아니라, 더 좋은 1단계 저장 덕분에 검색이 반복적·반응적 호출에서 선택적·질의 중심 호출로 바뀌었음을 뜻한다.

> 표 3. HotpotQA 에피소드당 평균 도구 호출 수.

| 도구 | Qwen2.5 noRL | Qwen2.5 GRPO | Qwen3 noRL | Qwen3 GRPO |
| --- | ---: | ---: | ---: | ---: |
| `ADD_MEMORY` | 0.92 | 1.64 | 2.49 | 2.64 |
| `UPDATE_MEMORY` | 0.00 | 0.13 | 0.13 | 0.34 |
| `DELETE_MEMORY` | 0.00 | 0.08 | 0.00 | 0.22 |
| `RETRIEVE_MEMORY` | 2.31 | 1.95 | 4.62 | 4.35 |
| `SUMMARY_CONTEXT` | 1.08 | 0.82 | 0.11 | 0.96 |
| `FILTER_CONTEXT` | 0.02 | 0.31 | 0.15 | 0.16 |
| 전체 호출 | 4.33 | 4.92 | 7.50 | 8.67 |

### 4.3 절제 연구

**LTM·STM 구성 요소.** Qwen2.5-7B에서 LTM만 더한 `+LT`는 기준선 대비 ALFWorld·SciWorld·HotpotQA에 +10.6%, +14.2%, +7.4%의 큰 향상을 냈다. RL을 추가한 `+LT/RL`은 특히 HotpotQA에서 +6.3%를 더 개선했다. LTM·STM·RL을 모두 사용한 AgeMem은 세 벤치마크에서 +13.9%, +21.7%, +16.1%로 최고 성능을 달성했다. STM 도구는 SciWorld(+3.1%)와 HotpotQA(+2.4%)에서 특히 기여해, 학습된 컨텍스트 관리가 정적 RAG보다 낫다는 점을 보인다.

> 그림 4. LTM, STM, RL 구성요소 절제(Qwen2.5-7B-Instruct). Base: 메모리 없는 기준선. `+LT`: LTM 도구만인 AgeMem-noRL-RAG. `+LT/RL`: LTM 도구와 RL의 AgeMem-RAG. `+LT/ST/RL`: RL을 적용한 완전 AgeMem. 녹색 화살표는 기준선 대비 향상이다.

**보상 함수.** 전체 보상(All-Returns)은 과제 보상만 쓰는 Answer-Only보다 더 빠르게 수렴하고 더 높은 최종 성능을 보였다. All-Returns는 J=0.544, MQ=0.533으로 Answer-Only(J=0.509, MQ=0.479)보다 높았다. 토큰은 2,117 대 2,078로 약간 더 썼지만, 추가 컨텍스트·메모리 연산이 추론 품질에 의미 있게 기여했다.

> 표 4. Qwen2.5-7B HotpotQA의 보상 함수 절제. $N$은 토큰 수, $C$는 도구 호출 수다.

| 전략 | J(↑) | N(↓) | MQ(↑) | C(↓) |
| --- | ---: | ---: | ---: | ---: |
| Answer-Only | 0.509 | 2078 | 0.479 | 3.93 |
| All-Returns | 0.544 | 2117 | 0.533 | 4.92 |

**`FILTER` 임계값 $\theta_f$.** $\theta_f\in[0.4,0.8]$에서 성능은 안정적이다. 너무 낮으면 유용한 컨텍스트까지 지나치게 버리고, 너무 높으면 경계선 정보를 통과시켜 메모리 품질을 조금 낮춘다. 설정별 평균 토큰 수가 유사하므로 차이는 컨텍스트 길이가 아니라 선택 품질에서 비롯된다.

> 표 5. HotpotQA에서 `FILTER` 임계값 민감도.

| $\theta_f$ | J(↑) | MQ(↑) | 평균 토큰 |
| ---: | ---: | ---: | ---: |
| 0.4 | 0.524 | 0.511 | 2089 |
| 0.5 | 0.551 | 0.550 | 2116 |
| 0.6 | 0.544 | 0.533 | 2117 |
| 0.7 | 0.530 | 0.526 | 2149 |
| 0.8 | 0.531 | 0.510 | 2134 |

> 그림 5. Qwen2.5-7B-Instruct의 GRPO 학습 보상 수렴. 실선은 All-Returns, 점선은 Answer-Only 보상 전략이다.

## 5. 결론

본 논문은 LLM 기반 에이전트가 학습 가능한 도구 기반 행동으로 장기·단기 메모리를 공동 제어하게 하는 통합 메모리 관리 프레임워크 AgeMem을 제안했다. 메모리 연산을 에이전트 정책에 직접 통합하고 점진적 강화학습으로 훈련함으로써, 휴리스틱 메모리 파이프라인을 종단 간 최적화 해법으로 대체한다. 다양한 장기 시간 범위 벤치마크에서 AgeMem은 효율적 컨텍스트 사용을 유지하면서 과제 성능과 메모리 품질을 모두 높였다. 이는 확장 가능하고 적응적인 장기 추론 LLM 에이전트를 위한 통합·에이전트 중심 메모리 정책의 중요성을 보인다.

## 감사의 글

이 연구는 중국 국가자연과학재단(62441237, U24A20336, 62272348, U22B2022) 및 위성-지상 통합 차세대 무선통신 산업 우한시 공동혁신연구소(4050902040448)의 지원을 받았다.

## 한계

AgeMem은 여러 설정에서 강한 성능을 보였지만 확장 여지가 있다. 현재 구현은 고정된 메모리 관리 도구 집합을 사용한다. 이는 명확하고 효과적인 추상화이나, 앞으로 더 세밀한 제어를 지원하도록 확장할 수 있다. 또한 5개 대표 장기 벤치마크와 도메인 간 zero-shot 전이를 평가했지만, 설정은 개방형 실제 배포보다 여전히 통제되어 있다. 지속적인 장기 대화와 실제 사용자 상호작용 평가는 중요한 다음 단계다. 마지막으로, 현재 학습은 HotpotQA에서 3단계 궤적을 얻는다. 더 풍부한 상호작용 구조를 가진 다른 데이터 소스로 교육과정을 확장하면 적용 범위를 넓힐 수 있다.

## 부록 A. AgeMem의 상세 설계와 구현

이 부록은 본문에서 공간상 생략한 기술 세부 사항을 제공한다. A.1은 각 도구의 정확한 정의와 시스템 프롬프트, A.2는 보상 성분의 구현 가능한 수식, A.3은 전체 알고리즘 명세를 다룬다.

### A.1 메모리 관리 도구

시점 $t$의 장기 저장소는 $M_t=\{m_i\}_{i=1}^{|M_t|}$이며 각 기억은 콘텐츠 문자열과 선택적 메타데이터를 갖는다. 단기 컨텍스트는 메시지 목록 $C_t=[u_1,u_2,\ldots,u_{n_t}]$이고, $enc(\cdot)$는 조밀 임베딩을 반환하는 텍스트 인코더다. 프레임워크 전반에 코사인 유사도를 사용한다.

**`RETRIEVE`.** 질의 $q$와 가장 유사한 상위 $k$개 기억을 가져와 활성 컨텍스트에 넣는다.

$$RETRIEVE(q,k)=TopK(M_t,sim(q,m_i),k),\qquad sim(q,m_i)=\frac{enc(q)^\top enc(m_i)}{\|enc(q)\|\|enc(m_i)\|}.\tag{8--9}$$

실험에서 $k$는 관련성과 컨텍스트 크기의 균형을 위해 보통 3~5로 둔다.

**`ADD`.** `ADD`는 향후 사용을 위해 새 정보를 LTM에 저장한다. 새 기억 항목은 다음과 같이 만든다.

$$m_{new}=(c,enc(c),metadata),\tag{10}$$

여기서 $c$는 저장할 내용, $enc(c)$는 임베딩 벡터이며, `metadata`에는 타임스탬프, 출처 정보, 선택적 태그가 들어간다. 저장소는 다음처럼 갱신된다.

$$M_{t+1}=M_t\cup\{m_{new}\}.\tag{11}$$

에이전트는 보상 함수를 통해 저장할 가치가 있는 두드러진 정보를 식별한다. 보상은 고품질·재사용 가능 지식의 저장을 장려하고, 중복되거나 무관한 항목에는 불이익을 준다.

**`UPDATE`와 `DELETE`.** 유지보수 연산은 LTM 저장소를 최신의 관련 상태로 유지하게 한다. `UPDATE`는 새 정보가 이전 지식을 대체하거나 보완할 때 기존 기억을 수정한다. 기존 기억 $m_i$에 대해 다음과 같이 정의한다.

$$m_i\leftarrow(c',enc(c'),metadata').\tag{12}$$

$c'$는 갱신된 내용이고, $metadata'$에는 수정 시각이 반영된다. `DELETE`는 오래되었거나 잘못된 기억을 제거한다.

$$M_{t+1}=M_t\setminus\{m_i\}.\tag{13}$$

이 연산들은 정보가 오래되거나 초기에 한 오류를 수정해야 하는 장기 과제에서 특히 중요하다. 보상 함수는 시간이 흐르면서 메모리 품질을 개선하는 의미 있는 갱신과 삭제를 장려한다.

**`SUMMARY`.** 지정 인덱스 $s$의 대화 이력을 요약으로 치환한다.

$$C'_t=C_t\setminus\{u_i\mid i\in s\}\cup\{Summarize(\{u_i\}_{i\in s})\}.\tag{14}$$

`span`은 모든 비시스템 메시지(`all`) 또는 최근 $N$개 메시지가 될 수 있다. 요약 프롬프트는 주요 주제·행동·결과·미해결 문제를 식별하고, 인사·군더더기·중복을 제외한 명확하고 사실적인 요약을 만들도록 지시한다. 원본 대화를 대체하므로 핵심 정보가 빠지지 않아야 한다.

**`FILTER`.** 어떤 기준 $c$와의 의미 유사도가 $\theta_f$ 이상인 메시지를 제거한다.

$$C'_t=\{u_i\in C_t\mid sim(c,u_i)<\theta_f\}.\tag{15}$$

기본값은 $\theta_f=0.6$이다. 기준은 에이전트가 지정하거나 현재 과제에서 자동 도출할 수 있다. 이는 방해 요소로 관련 없는 정보를 걸러내는 2단계에서 특히 유용하다.

**구조화된 행동으로서의 도구 호출.** 각 도구는 함수명과 필수 인수를 지정한 스키마로 노출된다. 에이전트 정책은 텍스트 생성용 언어 토큰 또는 메모리 연산용 구조화된 도구 호출을 출력한다. 시스템 프롬프트는 모든 과제를 `<think>...</think>` 블록으로 시작해 다음 단계를 계획하도록 한다. 도구가 필요하면 그 뒤에 하나 이상의 호출을 JSON 배열로 넣은 `<tool_call>...</tool_call>` 블록을, 최종 출력이 준비됐으면 완전한 응답을 넣은 `<answer>...</answer>` 블록을 둔다. 각 `<think>` 뒤에는 이 두 블록 중 정확히 하나만 와야 하며, 같은 사고 블록 직후에 둘을 동시에 둘 수 없다. 필요한 만큼 `<think> → <tool_call>` 순서를 반복한 뒤 `<think> → <answer>`로 마무리한다. 모든 추론은 `<think>` 태그 안에, 모든 도구 사용은 하나의 `<tool_call>` 태그 안에, 최종 해법은 `<answer>` 태그 안에 있어야 하며 태그 밖에는 텍스트를 쓰지 않는다. 이 구조는 RL 학습 중 신뢰할 수 있는 파싱과 보상 계산을 보장하고, 한 추론 단계에서 여러 메모리 연산을 조정하게 한다.

> 그림 6. STM 관리 도구 스키마. `Summary_context(span)`, `Filter_context(criteria)`, `Retrieve_memory(query, top_k, metadata_filter)`는 각각 대화 요약, 무관·오래된 내용 필터링, 관련 기억의 현재 컨텍스트 추가를 담당한다.

> 그림 7. LTM 관리 도구 스키마. `Add_memory(content, metadata, memory_type)`, `Update_memory(memory_id, content, metadata)`, `Delete_memory(memory_id, confirmation)`은 대화 간 지속 정보를 추가·수정·삭제한다.

### A.2 보상 함수 설계

별도로 언급하지 않는 한 모든 성분 점수는 안정적 가중을 위해 $[0,1]$로 정규화한다. 전체 궤적 보상은 다음과 같다.

$$R(\tau)=\mathbf w^\top\mathbf R+P_{penalty},\tag{16}$$

여기서 $\mathbf w=[w_{task},w_{context},w_{memory}]^\top$는 조정 가능한 가중치이고, $\mathbf R=[R_{task},R_{context},R_{memory}]^\top$는 각각 과제 완료·컨텍스트 관리·메모리 관리 보상이며, $P_{penalty}$는 바람직하지 않은 행동에 벌점을 준다.

**과제 완료 보상 $R_{task}$.** 에이전트가 최종 답 $A_{pred}$를 생성하면 평가자(LLM 심사자)를 통해 $S_{judge}(A_{pred},A_q)\in[0,1]$을 얻는다. $A_q$는 기대 정답이다.

$$R_{task}=\begin{cases}S_{judge}(A_{pred},A_q),&\text{답이 있을 때},\\P_{no\text{-}answer},&\text{그 외}.\end{cases}\tag{17}$$

기본값은 $P_{no\text{-}answer}=-1.0$이다.

**컨텍스트 관리 보상 $R_{context}$.** 컴팩트하면서도 정보를 보존하는 컨텍스트 상태를 얼마나 잘 유지하는지 평가하기 위해 세 정규화 성분으로 분해한다.

$$R_{context}=\sum_{i=1}^{3}\alpha_iR_i,\quad R_i\in\{R_{compression},R_{preventive},R_{preservation}\},\quad\sum_i\alpha_i=1.\tag{18}$$

별도 설정이 없으면 $\alpha_i=1/3$이다. 압축 효율은 최종 답 생성 시 컨텍스트의 토큰 수 $T_{used}$와 허용 예산 $T_{max}$로 계산한다.

$$R_{compression}=\max\left(0,1-\frac{T_{used}}{T_{max}}\right).\tag{19}$$

선제 관리 보상은 토큰 한도에 도달하기 전에 컨텍스트 축소 도구를 호출하면 1, 그렇지 않으면 0이다.

$$R_{preventive}=\mathbb{1}[\text{overflow 전에 도구를 호출함].\tag{20}$$

정보 보존을 위해 질의 $q$에서 개체명·시간·공간 표현 같은 핵심 토큰 또는 구절 집합 $K_q$를 뽑는다. 답 생성 시 이 항목들이 원문 또는 유지된 요약에 남아 있으면 $\mathbb{1}_{preserve}=1$로 둔다.

$$R_{preservation}=\mathbb{1}_{preserve}.\tag{21}$$

**메모리 관리 보상 $R_{memory}$.** 저장 품질, 유지보수, 의미 관련성의 세 성분을 결합한다.

$$R_{memory}=\sum_{j=1}^{3}\beta_jR_j,\quad R_j\in\{R_{storage},R_{maintenance},R_{relevance}\},\quad\sum_j\beta_j=1.\tag{22}$$

별도 설정이 없으면 $\beta_j=1/3$이다. 1단계 저장 중 전체 $N_{total}$개 기억 중, 입력 질의 $q$와 기대 답 $A_q$에 대한 LLM 분석에서 고품질로 판정된 기억이 $N_{high\_quality}$개이면 저장 품질은 다음과 같다.

$$R_{storage}=\frac{N_{high\_quality}}{\max(1,N_{total})}.\tag{23}$$

이는 가치 있는 정보는 저장하되 중복·저품질 기억의 축적은 피하게 한다. 메모리 뱅크를 능동적으로 유지하게 하기 위한 보상은 다음과 같다.

$$R_{maintenance}=\mathbb{1}[\text{UPDATE 또는 DELETE 수행}].\tag{24}$$

검색된 기억 집합 $R$와 질의 $q$ 사이의 의미 일치를 계량하기 위해, $[0,1]$로 정규화한 LLM 기반 관련성 점수 $S_{LLM}(R,q)$를 사용한다.

$$R_{relevance}=S_{LLM}(R,q).\tag{25}$$

**벌점 $P_{penalty}$.** 지정 한계를 준수하게 하기 위해 주요 제약 위반에 벌점을 준다.

$$P_{penalty}=\sum_{k=1}^{2}P_k\cdot\mathbb{1}[violation_k].\tag{26}$$

$P_k\in\{P_{rounds},P_{overflow}\}$이고, 위반은 $\{\mathbb{1}[N_{rounds}>N_{max}],\mathbb{1}[T_{used}>T_{max}]\}$이다. $N_{rounds}$는 상호작용 라운드 수, $N_{max}$는 최대 라운드 수, $T_{used}$는 총 토큰 사용량, $T_{max}$는 토큰 예산이다. 기본 벌점 계수는 $P_{rounds}=-1$, $P_{overflow}=-0.5$이다.

### A.3 학습 절차

학습은 생성 후 최적화(generate-then-optimize) 방식이다. 학습 배치 $B$의 각 과제 $q$마다 현재 정책 $\pi_\theta$로 독립 rollout $K$개 $\{\tau_k^{(q)}\}_{k=1}^K$를 생성한다. 각 궤적 $\tau_k^{(q)}=(\tau_k^{(1)},\tau_k^{(2)},\tau_k^{(3)})$는 세 단계의 경험을 연결해, 초기 메모리 구성부터 최종 과제 완료까지 하나의 에피소드를 이룬다. 에이전트는 먼저 문맥 정보 $I_q$에서 LTM을 구성하고, 다음으로 방해 정보를 걸러내면서 유용한 컨텍스트를 유지하는 법을 배우며, 마지막으로 저장 지식을 검색해 목표 과제를 완료한다. 모든 경험은 여러 과제와 rollout에 걸친 통합 버퍼 $E$에 수집된다.

rollout 후에는 과제별 보상 스케일이 달라도 공정히 비교할 수 있도록 그룹 기반 이점 정규화를 적용한다. 각 과제 그룹 $G_q$에서 종료 보상 $\{r_T^{(k,q)}\}_{k=1}^K$를 평균 0, 분산 1로 정규화하여 상대 성능을 나타내는 $A_T^{(k,q)}$를 얻는다. 이 종료 이점은 동일 궤적의 모든 시점에 균일하게 방송되어, 초기 단계 메모리 결정과 최종 과제 결과를 잇는 일관된 학습 신호를 만든다. 이후 참조 정책 $\pi_{ref}$와의 거리를 제한하는 KL 항으로 정규화한 기대 이점에 대해 경사 상승을 수행한다.

1단계에서는 $T_1$회의 탐색 대화 동안 문맥 정보 $I_q$를 점진적으로 제시한다. 에이전트는 두드러진 정보를 가려내고 `ADD`, `UPDATE`, `DELETE`를 언제 어느 기억에 호출할지 결정해 초기 LTM $M$을 구성한다. 이 단계의 검색은 아직 공개되지 않은 과제 질의를 풀기 위한 것이 아니라, 현재 LTM 내용을 계속 인식하여 오래된 항목을 갱신·폐기하고 새 기억이 기존 지식과 일관되게 유지되도록 하는 성찰적 연산이다. 따라서 에이전트는 질의별 지름길이 아니라 나중에 재사용 가능한 구조화된 기억 흔적을 만든다.

2단계에서는 정보 누출을 막고 STM 관리 학습을 분리하기 위해 단기 컨텍스트 $C$를 초기화하지만, 1단계 LTM $M$은 유지한다. $T_2$회의 턴 동안 의미상 그럴듯하지만 목표 질의에는 무관한 방해 메시지를 넣는다. 에이전트는 의미 유사도 임계값을 사용해 저관련 내용을 `FILTER`로 선제 제거하거나, 토큰 예산이 조여질 때 `SUMMARY`로 누적 컨텍스트를 압축해야 한다. 이 단계의 보상 신호는 3단계 최종 과제 성능에서 오므로 단순 휴리스틱을 넘어서는 견고한 필터링 전략을 학습한다.

3단계에서는 목표 질의 $q$를 받은 뒤, LTM $M$의 검색, $C$에 대한 컨텍스트 관리, 다단계 추론을 조정해 최종 답 $A_{pred}$를 생성한다. 관련 저장 사실은 `RETRIEVE`로 가져오고, 필요한 경우 `SUMMARY`로 컨텍스트 창을 관리한다. 답을 생성하거나 최대 단계에 도달하면 A.2의 복합 보상 함수가 세 단계 전체 궤적을 평가한다. 이 종료 보상 $R(\tau)$는 최종 시점에 부여되며 이점 계산을 통해 모든 단계로 전파된다.

> 그림 8. AgeMem의 주 학습 절차. 명료성을 위해 rollout 단계(왼쪽)와 이점 계산 및 정책 갱신 단계(오른쪽)로 나누어 보인다. 각 과제의 문맥 $I_q$와 `DISTRACTOR_GEN(q)`으로 $K$개 궤적을 생성하고, 종료 보상을 그룹 안에서 정규화한 뒤 모든 시점에 방송하여 정책을 갱신한다.

> 그림 8. AgeMem의 주요 학습 절차. 명확성을 위해 rollout 단계와 GRPO 업데이트 단계로 나누어 표시한다. rollout은 3단계 궤적과 경험을 만들고, 업데이트는 종료 보상을 모든 과거 단계에 전파해 통합 메모리 정책을 최적화한다.

## 부록 B. 사례 연구: 동작 중인 AgeMem

### B.1 사례 1: 장기 메모리의 선택적 저장과 유지보수

이 절에서는 확장 대화에 걸쳐 AgeMem이 LTM을 선택적으로 구성·갱신·유지하는 방식을 보인다. 사용자: “저는 시각 학습자이고 60분 학습 세션을 선호합니다. Python 기초는 알지만 ML 경험은 없습니다. 특히 얼굴 인식 같은 컴퓨터 비전 응용에 관심이 있습니다.” RL 전 기준선은 이 선호를 저장하지 않고 “컴퓨터 비전에 초점을 둔 실습 프로젝트부터 시작할 수 있다”고만 응답한다. 따라서 뒤이어 사용자가 “60분은 너무 짧고 120분 심층 집중 블록에서 더 잘 일한다”고 말하면, 기존 선호를 메모리에 보유하지 않아 변경을 확인할 수 없고 120분 세션으로 계획하겠다고만 답한다.

RL 후 AgeMem은 처음에 시각 학습자·60분 세션 선호를 하나의 `Add_memory`로, Python 기초·ML 초보·컴퓨터 비전 및 얼굴 인식 관심을 다른 `Add_memory`로 저장한다. 사용자가 120분 선호를 밝히면 “60분에서 120분으로 세션 길이 선호가 바뀌었으므로 중복을 만들지 말고 기존 항목을 갱신해야 한다”고 판단하고, 이전 항목의 `memory_id`에 `Update_memory`를 호출하여 “120분 심층 집중 블록을 선호함(60분에서 갱신됨)”으로 바꾼다.

더 많은 성공적 세션 뒤 사용자가 “120분 세션을 한동안 꾸준히 사용했고 내 학습 방식에 완벽하다. 더 짧은 세션을 시험할 일은 없다”고 확정하면, AgeMem은 먼저 세션 길이·학습 방식 선호를 `Retrieve_memory(top_k=5)`로 검색한다. 검색된 항목에 “60분에서 갱신됨”이라는 과거 참조가 남은 것을 확인하고, 이제 그 참조는 필요 없다고 판단한다. 이어 해당 `memory_id`를 `Delete_memory(confirmation=true)`로 삭제하고, “사용자는 학습 세션에 120분 심층 집중 블록을 선호하는 시각 학습자”라는 깨끗한 현재 선호 항목을 `Add_memory`로 새로 저장한다. 따라서 이 사례에서 학습된 에이전트는 초기 지식 저장뿐 아니라 오래된 이력의 제거와 최신 상태 유지를 수행한다.

### B.2 사례 2: 방해 요소 아래 단기 컨텍스트 관리

이 사례는 과제 초점을 흐릴 수 있는 무관 정보가 있을 때 STM을 선제 관리하는 법을 보인다. 사용자: “얼굴 인식을 위한 집중 3일 ML 속성 과정을 원합니다. 그런데 양자 컴퓨팅, 블록체인, 로보틱스도 탐색하고 있고, 사워도우 빵과 라테아트도 배우고 있습니다.” RL 전 기준선은 모든 관심사를 동등하게 인정하고 양자 컴퓨팅·블록체인·로보틱스·빵·커피를 언급한 뒤 ML 계획을 시작한다. 대화가 계속되면 이 무관한 내용도 전부 컨텍스트에 남아 과제 관련 정보가 희석되고 결국 컨텍스트가 넘친다.

RL 후 AgeMem은 현재 과제에 관련된 것은 ML 속성 과정과 얼굴 인식뿐이고 나머지는 방해 요소라고 판별한다. 그래서 `Filter_context`에 `criteria="quantum computing blockchain robotics sourdough latte"`를 주어 이를 제거한 뒤, Python 배경과 시각 학습 방식에 맞춘 3일 얼굴 인식 프로그램을 설계한다. 이후 여러 번의 대화로 일별 세부 일정, 도구 목록, 자원 URL이 쌓여 사용자가 “모든 세부를 통합한 최종 계획을 달라”고 요청하면, 에이전트는 중복된 목록과 자원이 누적됐음을 인식하고 `Summary_context(span="full")`를 호출한다. 요약에는 3일 구조, 120분 세션, 1일차 ML 입문·Python, 2일차 선형 회귀, 3일차 얼굴 인식, Jupyter·Python3·NumPy·Pandas·scikit-learn·OpenCV가 남는다. 즉 `FILTER_CONTEXT`는 잡음을 일찍 제거하고 `SUMMARY_CONTEXT`는 필수 정보를 보존한 채 오버플로를 막는다.

### B.3 사례 3: 메모리 조정을 통한 통합 과제 실행

사용자가 “지금까지 말한 학습 방식과 선호를 바탕으로, 구체적 시간 블록·주제·자원을 포함한 개인화된 Day 1 학습 일정을 만들어 달라”고 요청한다. RL 전 기준선은 선호를 체계적으로 저장·검색하지 못했으므로, 9:00–10:30 ML 개념 입문, 10:45–12:15 Python 기초 복습, 13:00–14:30 NumPy·Pandas, 14:45–16:15 연습 문제라는 일반적 일정을 낸다. 이 일정은 사용자가 밝힌 120분 심층 집중 블록과 시각 학습 방식을 무시한다.

학습된 AgeMem은 먼저 `Retrieve_memory(query="user learning preferences study duration visual", top_k=3)`를 호출한다. 검색 결과는 (1) 시각 학습자이며 120분 심층 집중 블록을 선호함, (2) Python 기초는 있으나 ML 경험은 없음, (3) 컴퓨터 비전과 얼굴 인식에 관심이 있다는 내용이다. 이를 바탕으로 오전 9:00–11:00에는 다이어그램과 플로차트를 활용한 ML 기초, 지도·비지도 학습의 상호작용 시연, 3Blue1Brown Neural Networks 영상 시리즈를 포함한 “ML Foundations”를 배치한다. 11:00–11:30은 휴식이다. 오후 13:00–15:00에는 matplotlib 플롯을 곁들인 Python 복습, 시각적 행렬 표현을 통한 NumPy 배열, 실제 데이터셋과 시각화를 이용한 Pandas DataFrame, 내장 플롯이 있는 Jupyter 노트북 실습, *Python Data Science Handbook*의 시각 자료 장을 포함한 “Python for ML”을 배치한다. 저녁 17:00–19:00에는 시각 피드백이 있는 자율 연습과 2일차 환경 준비를 선택 활동으로 둔다. 이렇게 검색 기억과 현재 질의를 결합하므로 120분 세션과 시각적 학습 선호를 반영한 개인화된 답이 나온다. 세 사례는 각각 LTM의 저장·유지보수, STM의 필터·요약, 검색된 지식과 현재 과제의 통합을 보인다.

## 부록 C. 실험 구현

### C.1 데이터셋 상세

**ALFWorld**는 자연어 지시를 따라 시뮬레이션 가정 환경의 과제를 수행하는 체화 AI 벤치마크다. pick and place, examine in light, clean/heat/cool and place, pick two and place의 6개 과제 유형이 있으며, 물체와 긴 시간 상호작용해야 한다.

**SciWorld**는 물리·화학·생물 등에 걸친 다단계 과학 실험을 수행해 질문에 답하는 상호작용 시뮬레이션이다. 절차적 추론과 가설 기반 탐색, 긴 상호작용에서의 지식 보존·검색을 평가한다.

**PDDL**은 Planning Domain Definition Language로 정식화된 계획 벤치마크 집합이다. 여러 도메인에서 목표 상태를 이루는 유효한 행동열을 생성하는 능력, 구조화 추론과 중간 계획 상태 활용을 평가한다.

**BabyAI**는 자연어 지시가 있는 격자 세계 탐색 벤치마크다. 에이전트는 구성적 언어 명령을 충족하도록 이동·물체 상호작용을 수행한다. 순차 의사결정 구조 때문에 STM 추적과 지시 grounding 평가에 쓰인다.

**HotpotQA**는 여러 Wikipedia 문단에 걸친 다중 홉 추론을 요구하는 QA 데이터셋이다. 약 9만 개 학습 질문과 검증·시험 분할을 가지며 질문마다 근거 사실이 주석된다. 본 실험은 이 구조화 문맥 정보를 1단계 감독에 쓰기 위해 HotpotQA에서 RL 학습을 수행했다.

### C.2 LLM 기반 평가 상세

MQ 평가기는 질문, 정답, 정답 근거 사실, 모델이 LTM에 저장한 예측 근거 사실을 입력으로 받고, (1) 모든 기대 사실의 포괄, (2) 질문에 대한 관련성, (3) 무관 사실 존재를 평가한다. 저장 항목과 HotpotQA 근거 사실을 독립적으로 비교하며 Qwen-Max를 평가 모델로 사용했다. 원문의 평가 프롬프트는 다음과 같다.

> 당신은 질의응답을 위한 근거 사실의 품질을 평가하는 전문가 심사자입니다.  
> 질문: `[QUESTION]`  
> 정답: `[ANSWER]`  
> 정답 근거 사실(식별되어야 하는 사실):  
> - `[FACT_1]`  
> - `[FACT_2]`  
> …  
> 모델이 예측하여 장기 메모리에 저장한 근거 사실:  
> - `[PREDICTED_FACT_1]`  
> - `[PREDICTED_FACT_2]`  
> …  
> 예측 근거 사실이 정답 근거 사실과 얼마나 일치하는지 평가하세요. (1) 모든 기대 사실을 포괄하는가? (2) 예측 사실이 질문에 실제로 관련되는가? (3) 예측에 무관한 사실이 있는가?  
> 0.0~1.0 척도로 점수를 매기세요. 1.0은 모든 기대 사실을 정확히 식별했고 무관한 사실이 없는 완전 일치, 0.8~0.9는 사소한 누락 또는 무관 사실 하나가 있는 대체로 정확한 경우, 0.6~0.7은 일부 관련 사실을 식별했으나 중요한 사실이 빠진 부분 정답, 0.4~0.5는 일부 정답 요소가 있으나 상당한 오류·누락, 0.2~0.3은 소수만 맞은 대부분 오답, 0.0~0.1은 완전히 틀렸거나 무관한 경우입니다.  
> 0.0과 1.0 사이 숫자 하나만 답하세요(예: `0.85`).

HotpotQA LLM-as-a-Judge도 Qwen-Max로 질문·정답·에이전트 답을 비교한다. 프롬프트는 다음과 같다.

> 당신은 질문에 대한 답의 정답성을 평가하는 전문가 심사자입니다.  
> - 질문: `[QUESTION]`  
> - 정답: `[GROUND_TRUTH]`  
> - 에이전트의 답: `[AGENT_ANSWER]`  
> 생성된 답을 0.0~1.0 척도로 평가하세요. 1.0은 완전 일치 또는 동등한 정답, 0.8~0.9는 사소한 차이만 있는 대체로 정답, 0.6~0.7은 부분 정답 또는 근접한 근사, 0.4~0.5는 일부 정답 요소가 있으나 상당한 오류, 0.2~0.3은 소수만 맞은 대부분 오답, 0.0~0.1은 완전히 틀렸거나 무관한 답입니다.  
> 0.0과 1.0 사이 숫자 하나만 답하세요(예: `0.85`).

### C.3 기준선 설정

모든 기준선은 공정 비교를 위해 각 공식 오픈소스 구현을 따른다. LangMem은 기본 하이퍼파라미터와 기본 저장·검색 방식을, A-Mem은 공식 저장소의 Zettelkasten 기반 지식 연결·통합 설정을 사용한다. Mem0은 기본 추출-갱신 파이프라인을, Mem0g는 권장 그래프 구성 파라미터를 쓴다. AgeMem-noRL은 같은 도구 인터페이스를 쓰되 RL은 수행하지 않는다. RAG 변형(AgeMem-noRL-RAG, AgeMem-RAG)은 STM 도구를 표준 RAG 파이프라인으로 바꾸며, 매 단계 현재 컨텍스트와 저장 기억의 코사인 유사도로 관련 기억을 찾아 컨텍스트에 붙인다.

### C.4 구현 상세

정책 최적화는 Trinity RL 프레임워크와 방법 절의 단계별 GRPO로 수행한다. 그룹 정규화용 독립 rollout 수는 과제당 $K=8$, KL 발산 계수 $\beta=0.1$이다. 보상 가중치는 $w_{task}=w_{context}=w_{memory}=1/3$으로 동일하게 둔다. 최대 컨텍스트 길이는 8,192토큰, 최대 응답 길이는 2,048토큰이다. 컨텍스트가 한도를 넘으면 벌점을 주어 STM 도구의 선제적 사용을 유도한다. 모든 실험은 메모리 48GB의 NVIDIA RTX 4090 GPU 8개에서 수행했다.

## 부록 D. 추가 결과

### D.1 Qwen3-4B 절제 연구

그림 9는 Qwen3-4B-Instruct에서 세 대표 데이터셋에 대한 LTM·STM·RL의 점진적 기여를 보인다. Qwen2.5-7B 결과와 일관된 경향을 보여, 제안 방식이 서로 다른 모델 크기에도 일반화됨을 확인한다.

> 그림 9. Qwen3-4B-Instruct 절제 결과. Base는 메모리 없는 기준선, `+LT`는 LTM 도구, `+LT/RL`은 LTM 도구와 RL, `+LT/ST/RL`은 완전 AgeMem이다.

### D.2 Qwen3-4B의 보상 함수 절제

서로 다른 모델 구조·규모에서도 다성분 보상 설계가 일반화되는지 확인하기 위해, 본문의 Qwen2.5-7B 실험과 같은 보상 함수 절제를 Qwen3-4B-Instruct에서 수행했다. 그림 10에서 All-Returns는 학습 전반에 걸쳐 Answer-Only보다 일관되게 높다. 특히 70~100단계의 후반 학습에서는 분산이 낮고 진행이 더 매끄러워, Qwen3 구조가 이 보상 학습 과제에 더 나은 귀납 편향을 가질 수 있음을 시사한다. 절대 향상 폭은 Qwen2.5-7B보다 작지만 우위가 학습 내내 유지되어 보상 설계의 견고성을 뒷받침한다.

정량적으로 All-Returns는 Answer-Only보다 높은 LLM-as-a-Judge 점수(0.555 대 0.546)와 훨씬 높은 MQ(0.605 대 0.415)를 냈다. 도구 호출도 8.67 대 7.21로 늘었으며, 이는 중간 보상을 최적화할 때 메모리 연산을 더 효과적으로 활용함을 뜻한다. 토큰 소비 증가는 2,164에서 2,191로 작아서, 성능 향상이 과도한 컨텍스트 확장이 아니라 더 효율적인 메모리 사용에서 왔음을 보인다. 이 경향은 Qwen2.5-7B 결과와도 일치한다.

> 표 6. Qwen3-4B-Instruct HotpotQA의 보상 함수 절제 결과.

| 전략 | J(↑) | TN(↓) | MQ(↑) | TC(−) |
| --- | ---: | ---: | ---: | ---: |
| Answer-Only | 0.546 | 2164 | 0.415 | 7.21 |
| All-Returns | 0.555 | 2191 | 0.605 | 8.67 |

> 그림 10. Qwen3-4B-Instruct의 GRPO 학습 수렴 곡선. All-Returns가 Answer-Only보다 더 빠르고 높은 수렴을 보인다.

### D.3 확장 기준선 비교

AgeMem의 향상이 STM 도구나 RL 최적화를 더한 효과에 불과한지를 확인하기 위해, 각 기존 LTM 전용 기준선에 AgeMem과 같은 ST/RL 확장(`+ST/RL`)을 붙여 Qwen2.5-7B-Instruct의 세 벤치마크에서 평가했다. 같은 확장을 붙이면 선행 방법도 향상되지만 완전한 AgeMem에는 여전히 미치지 못한다. 이는 이점이 어느 한 모듈의 추가가 아니라 이질적 메모리 행동 전반에 대한 통합 정책에서 비롯됨을 시사한다.

> 표 7. 기준선과 확장 기준선의 통합 비교(Qwen2.5-7B-Instruct). 최고 및 차상위 결과를 원문에서 표시했다.

| 방법 | ALFWorld | SciWorld | HotpotQA | 평균 |
| --- | ---: | ---: | ---: | ---: |
| No-Memory | 27.16 | 13.80 | 38.36 | 26.44 |
| LangMem | 38.27 | 28.29 | 37.43 | 34.66 |
| LangMem + ST/RL | 41.32 | 33.58 | 49.77 | 41.56 |
| A-Mem | 34.68 | 28.06 | 43.95 | 35.56 |
| A-Mem + ST/RL | 39.86 | 31.71 | 53.52 | 41.70 |
| Mem0 | 37.49 | 26.99 | 46.66 | 37.05 |
| Mem0 + ST/RL | 35.02 | 34.40 | 52.59 | 40.67 |
| AgeMem | 41.07 | 35.55 | 54.44 | 43.69 |

### D.4 하이퍼파라미터 민감도 분석

**DistractorGen 민감도.** `DISTRACTOR_GEN`은 목표 질의를 조건으로 하되 의미적으로는 무관한 짧은 사용자식 발화를 외부 LLM이 생성하게 하는 전용 모듈이다. 프롬프트는 목표 질문과 개체·핵심 개념을 공유하지 않을 것, 자연스러운 대화 턴처럼 보일 것, 주제가 다양할 것의 세 조건을 강제한다. 이에 따라 과제 관련 정보를 누출하지 않고 현실적인 다중 턴 간섭 신호를 만들며, 2단계는 적대적 판별이 아니라 STM 제어(필터링·요약·선택적 검색)에 집중한다. 난이도는 주로 방해 요소 수 $N$과 주제 다양성, 즉 관리해야 하는 경쟁 정보의 양으로 결정된다.

다른 설정을 고정한 채 $N$을 바꾼 HotpotQA 결과는 표 8과 같다. $N=3$과 $N=5$ 사이 성능은 안정적이고 $N=7$에서만 완만하게 줄어, 2단계 학습이 특정 방해 수준에 맞춰진 것이 아니라 방해 강도에 견고함을 보인다. 토큰 수가 거의 변하지 않는 점은 효과가 단순 길이 차이가 아니라 컨텍스트 관리 방식에서 온다는 뜻이다.

> 표 8. 2단계 방해 요소 수 $N$에 대한 AgeMem 민감도(HotpotQA).

| 방해 요소 수 $N$ | J(↑) | MQ(↑) | 평균 토큰 |
| ---: | ---: | ---: | ---: |
| 3 | 0.549 | 0.541 | 2105 |
| 5 | 0.544 | 0.533 | 2117 |
| 7 | 0.537 | 0.532 | 2113 |

## 참고문헌

Prateek Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, and Deshraj Yadav. 2025. Mem0: Building production-ready AI agents with scalable long-term memory. *arXiv preprint arXiv:2504.19413*.

Chia-Yuan Chang, Zhimeng Jiang, Vineeth Rakesh, Menghai Pan, Chin-Chia Michael Yeh, Guanchu Wang, Mingzhi Hu, Zhichao Xu, Yan Zheng, Mahashweta Das, and 1 others. 2025. Main-rag: Multi-agent filtering retrieval-augmented generation. In *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 2607–2622.

Ma Chang, Junlei Zhang, Zhihao Zhu, Cheng Yang, Yujiu Yang, Yaohui Jin, Zhenzhong Lan, Lingpeng Kong, and Junxian He. 2024. Agentboard: An analytical evaluation board of multi-turn llm agents. *Advances in Neural Information Processing Systems*, 37:74325–74362.

Shreyas Chaudhari, Pranjal Aggarwal, Vishvak Murahari, Tanmay Rajpurohit, Ashwin Kalyan, Karthik Narasimhan, Ameet Deshpande, and Bruno Castro da Silva. 2025. Rlhf deciphered: A critical analysis of reinforcement learning from human feedback for llms. *ACM Computing Surveys*, 58(2):1–37.

Maxime Chevalier-Boisvert, Dzmitry Bahdanau, Salem Lahlou, Lucas Willems, Chitwan Saharia, Thien Huu Nguyen, and Yoshua Bengio. 2018. Babyai: A platform to study the sample efficiency of grounded language learning. *arXiv preprint arXiv:1810.08272*.

Yihong Dong, Xue Jiang, Jiaru Qian, Tian Wang, Kechi Zhang, Zhi Jin, and Ge Li. 2025. A survey on code generation with llm-based agents. *arXiv preprint arXiv:2508.00083*.

Dawei Gao, Zitao Li, Yuexiang Xie, Weirui Kuang, Liuyi Yao, Bingchen Qian, Zhijian Ma, Yue Cui, Haohao Luo, Shen Li, and 1 others. 2025a. Agentscope 1.0: A developer-centric framework for building agentic applications. *arXiv preprint arXiv:2508.16279*.

Pengyu Gao, Jinming Zhao, Xinyue Chen, and Yilin Long. 2025b. An efficient context-dependent memory framework for llm-centric agents. In *Proceedings of the 2025 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 3: Industry Track)*, pages 1055–1069.

Javier Garcia Gilabert, Carlos Escolano, Xixian Liao, and Maite Melero. 2025. Terminology-constrained translation from monolingual data using grpo. In *Proceedings of the Tenth Conference on Machine Translation*, pages 1335–1343.

Lyle Goodyear, Rachel Guo, and Ramesh Johari. 2025. The effect of state representation on llm agent behavior in dynamic routing games. *arXiv preprint arXiv:2506.15624*.

Yuanzhe Hu, Yu Wang, and Julian McAuley. 2025. Evaluating memory in llm agents via incremental multi-turn interactions. *arXiv preprint arXiv:2507.05257*.

Xun Jiang, Feng Li, Han Zhao, Jiahao Qiu, Jiaying Wang, Jun Shao, Shihao Xu, Shu Zhang, Weiling Chen, Xavier Tang, and 1 others. 2024. Long term memory: The foundation of ai self-evolution. *arXiv preprint arXiv:2410.15665*.

Hongye Jin, Xiaotian Han, Jingfeng Yang, Zhimeng Jiang, Zirui Liu, Chia-Yuan Chang, Huiyuan Chen, and Xia Hu. 2024. Llm maybe longlm: Self-extend llm context window without tuning. *arXiv preprint arXiv:2401.01325*.

Bowen Jin, Hansi Zeng, Zhenrui Yue, Jinsung Yoon, Sercan Arik, Dong Wang, Hamed Zamani, and Jiawei Han. 2025. Search-r1: Training llms to reason and leverage search engines with reinforcement learning. *arXiv preprint arXiv:2503.09516*.

Tomoyuki Kagaya, Thong Jing Yuan, Yuxuan Lou, Jayashree Karlekar, Sugiri Pranata, Akira Kinose, Koki Oguri, Felix Wick, and Yang You. 2024. Rap: Retrieval-augmented planning with contextual memory for multimodal llm agents. *arXiv preprint arXiv:2402.03610*.

Jiazheng Kang, Mingming Ji, Zhe Zhao, and Ting Bai. 2025. Memory os of ai agent. *arXiv preprint arXiv:2506.06326*.

LangChain Team. 2025. Langmem sdk for agent long-term memory. https://blog.langchain.com/langmem-sdk-launch/. Accessed: 2025-12-03.

Hao Li, Chenghao Yang, An Zhang, Yang Deng, Xiang Wang, and Tat-Seng Chua. 2025. Hello again! llm-powered personalized agent for long-term dialogue. In *Proceedings of the 2025 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)*, pages 5259–5276.

Hao Ma, Tianyi Hu, Zhiqiang Pu, Liu Boyin, Xiaolin Ai, Yanyan Liang, and Min Chen. 2024. Coevolving with the other you: Fine-tuning llm with sequential cooperative multi-agent reinforcement learning. *Advances in Neural Information Processing Systems*, 37:15497–15525.

Qianou Ma, Weirui Peng, Chenyang Yang, Hua Shen, Ken Koedinger, and Tongshuang Wu. 2025. What should we engineer in prompts? training humans in requirement-driven llm use. *ACM Transactions on Computer-Human Interaction*, 32(4):1–27.

Xuchen Pan, Yanxi Chen, Yushuo Chen, Yuchang Sun, Daoyuan Chen, Wenhao Zhang, Yuexiang Xie, Yilun Huang, Yilei Zhang, Dawei Gao, and 1 others. 2025a. Trinity-rft: A general-purpose and unified framework for reinforcement fine-tuning of large language models. *arXiv preprint arXiv:2505.17826*.

Zhuoshi Pan, Qianhui Wu, Huiqiang Jiang, Xufang Luo, Hao Cheng, Dongsheng Li, Yuqing Yang, Chin-Yew Lin, H Vicky Zhao, Lili Qiu, and 1 others. 2025b. On memory construction and retrieval for personalized conversational agents. *arXiv preprint arXiv:2502.05589*.

Cheng Qian, Emre Can Acikgoz, Qi He, Hongru Wang, Xiusi Chen, Dilek Hakkani-Tür, Gokhan Tur, and Heng Ji. 2025. Toolrl: Reward is all tool learning needs. *arXiv preprint arXiv:2504.13958*.

Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, and Daniel Chalef. 2025. Zep: a temporal knowledge graph architecture for agent memory. *arXiv preprint arXiv:2501.13956*.

Rana Salama, Jason Cai, Michelle Yuan, Anna Currey, Monica Sunkara, Yi Zhang, and Yassine Benajiba. 2025. Meminsight: Autonomous memory augmentation for llm agents. *arXiv preprint arXiv:2503.21760*.

Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang, YK Li, Yang Wu, and 1 others. 2024. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. *arXiv preprint arXiv:2402.03300*.

Mohit Shridhar, Xingdi Yuan, Marc-Alexandre Côté, Yonatan Bisk, Adam Trischler, and Matthew Hausknecht. 2020. Alfworld: Aligning text and embodied environments for interactive learning. *arXiv preprint arXiv:2010.03768*.

Chuanneng Sun, Songjun Huang, and Dario Pompili. 2024. Llm-based multi-agent reinforcement learning: Current and future directions. *arXiv preprint arXiv:2405.11106*.

Hongcheng Wang, Yinuo Huang, Sukai Wang, Guanghui Ren, and Hao Dong. 2025a. Grpo-ma: Multi-answer generation in grpo for stable and efficient chain-of-thought training. *arXiv preprint arXiv:2509.24494*.

Ruoyao Wang, Peter Jansen, Marc-Alexandre Côté, and Prithviraj Ammanabrolu. 2022. Scienceworld: Is your agent smarter than a 5th grader? In *Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing*, pages 11279–11298.

Yu Wang and Xi Chen. 2025. Mirix: Multi-agent memory system for llm-based agents. *arXiv preprint arXiv:2507.07957*.

Zixuan Wang, Bo Yu, Junzhe Zhao, Wenhao Sun, Sai Hou, Shuai Liang, Xing Hu, Yinhe Han, and Yiming Gan. 2025b. Karma: Augmenting embodied ai agents with long-and-short term memory systems. In *2025 IEEE International Conference on Robotics and Automation (ICRA)*, pages 1–8. IEEE.

Zora Zhiruo Wang, Apurva Gandhi, Graham Neubig, and Daniel Fried. 2025c. Inducing programmatic skills for agentic tasks. *arXiv preprint arXiv:2504.06821*.

Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, and Graham Neubig. 2024. Agent workflow memory. *arXiv preprint arXiv:2409.07429*.

Xixi Wu, Kuan Li, Yida Zhao, Liwen Zhang, Litu Ou, Huifeng Yin, Zhongwang Zhang, Xinmiao Yu, Dingchu Zhang, Yong Jiang, and 1 others. 2025a. Resum: Unlocking long-horizon search intelligence via context summarization. *arXiv preprint arXiv:2509.13313*.

Yaxiong Wu, Sheng Liang, Chen Zhang, Yichao Wang, Yongyue Zhang, Huifeng Guo, Ruiming Tang, and Yong Liu. 2025b. From human memory to ai memory: A survey on memory mechanisms in the era of llms. *arXiv preprint arXiv:2504.15965*.

Zidi Xiong, Yuping Lin, Wenya Xie, Pengfei He, Zirui Liu, Jiliang Tang, Himabindu Lakkaraju, and Zhen Xiang. 2025. How memory management impacts llm agents: An empirical study of experience-following behavior. *arXiv preprint arXiv:2505.16067*.

Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, and Yongfeng Zhang. 2025. A-mem: Agentic memory for llm agents. *arXiv preprint arXiv:2502.12110*.

Sikuan Yan, Xiufeng Yang, Zuchao Huang, Ercong Nie, Zifeng Ding, Zonggen Li, Xiaowen Ma, Kristian Kersting, Jeff Z Pan, Hinrich Schütze, and 1 others. 2025. Memory-r1: Enhancing large language model agents to manage and utilize memories via reinforcement learning. *arXiv preprint arXiv:2508.19828*.

Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William Cohen, Ruslan Salakhutdinov, and Christopher D Manning. 2018. Hotpotqa: A dataset for diverse, explainable multi-hop question answering. In *Proceedings of the 2018 conference on empirical methods in natural language processing*, pages 2369–2380.

Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik R Narasimhan, and Yuan Cao. 2023. React: Synergizing reasoning and acting in language models. In *The eleventh international conference on learning representations*.

Yuxiang Zhang, Jiangming Shu, Ye Ma, Xueyuan Lin, Shangxi Wu, and Jitao Sang. 2025a. Memory as action: Autonomous context curation for long-horizon agentic tasks. *arXiv preprint arXiv:2510.12635*.

Zeyu Zhang, Quanyu Dai, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Jieming Zhu, Zhenhua Dong, and Ji-Rong Wen. 2025b. A survey on the memory mechanism of large language model-based agents. *ACM Transactions on Information Systems*, 43(6):1–47.

Wanjun Zhong, Lianghong Guo, Qiqi Gao, He Ye, and Yanlin Wang. 2024. Memorybank: Enhancing large language models with long-term memory. In *Proceedings of the AAAI Conference on Artificial Intelligence*, volume 38, pages 19724–19731.
