# G-Memory: 다중 에이전트 시스템을 위한 계층형 메모리 추적

> Guibin Zhang, Muxin Fu, Guancheng Wan, Miao Yu, Kun Wang, Shuicheng Yan, *G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems*, arXiv:2506.07398v2 (2025-06-16).
>
> 원문 PDF 24쪽 전체를 기준으로 작성하는 한국어 번역본이다. 모델명·수식·변수명·데이터셋·인용·프롬프트의 구조화 키는 원문 표기를 보존한다.

## 초록

대규모 언어 모델(LLM) 기반 다중 에이전트 시스템(MAS)은 단일 LLM agent를 훨씬 뛰어넘는 인지·실행 능력을 보였지만, 자기 진화 능력은 미성숙한 memory architecture 때문에 여전히 제한된다. 저자들은 기존 MAS memory mechanism이 (1) 미묘한 agent 간 협업 궤적을 완전히 무시할 만큼 지나치게 단순하고, (2) 단일 agent용으로 발전한 풍부한 memory와 달리 trial 간 및 agent별 맞춤화가 없다는 점을 지적한다.

이를 메우기 위해 조직 memory 이론 [1]에서 영감을 받은 MAS용 계층적 agentic memory system **G-Memory**를 제안한다. G-Memory는 긴 MAS 상호작용을 insight graph, query graph, interaction graph의 3단 graph hierarchy로 관리한다. 새 사용자 질의가 오면 양방향 memory traversal을 수행하여, trial 간 지식을 활용할 수 있는 상위·일반화 가능한 insight와 이전 협업 경험을 압축해 부호화한 세밀한 interaction trajectory를 함께 검색한다. 과업 실행 뒤에는 새 협업 궤적을 동화하여 전체 hierarchy가 진화하고, 이에 따라 agent team이 점진적으로 발전한다. 5개 benchmark, 3개 LLM backbone, 3개 MAS framework에서의 광범위한 실험은 원래 framework를 수정하지 않고도 embodied action 성공률을 최대 20.89%, knowledge QA 정확도를 최대 10.12% 높임을 보인다. 코드: <https://github.com/bingreeky/GMemory>.

## 1. 서론

LLM은 인식 [2–5], 계획 [6–8], 추론 [9, 10], 행동 [11, 12]에서 전례 없는 능력을 보이며 code generation [13, 14], data analysis [15], embodied task [16], autonomous driving [3, 17, 18] 등 다양한 분야의 발전을 이끌었다. 단일 agent의 능력을 기반으로, LLM 기반 MAS는 단일 model 용량의 한계를 더 넓히는 것으로 나타났다 [19–21]. 인간의 사회적 협업에서 나오는 collective intelligence [22–24]와 마찬가지로, MAS는 협력 [28–31] 또는 경쟁 [32–34] 방식으로 여러 agent [25–27]를 조율하여 고립된 agent의 인지적·전문적 한계를 넘는다.

### 자기 진화 agent와 MAS memory의 공백

LLM agent를 특히 특징짓는 것은 환경과 상호작용하며 지속적으로 적응·개선하는 **자기 진화(self-evolving)** 능력이다. 선행 연구에서는 이 적응성이 2–3배의 정량적 향상으로 이어졌다 [35]. 이 능력의 중심 동력은 agent의 memory mechanism [36–38]이며, 이는 인간이 지식을 축적하고 과거 경험을 처리하며 관련 정보를 검색하는 능력과 평행한다. 한 trial의 문제를 푸는 동안 유지하는 inside-trial memory와 여러 task에서 축적하는 cross-trial memory [39]는 personalized chat [36, 40, 41], recommendation [42], embodied action [43, 16], social simulation [19, 44, 45]에서 agent가 경험적 학습자로 발전하도록 했다.

그러나 MAS에는 이런 자기 진화 능력이 대체로 없다. 대부분은 MetaGPT·ChatDev의 SOP처럼 수동 정의 workflow [21, 46]나 MacNet·AgentPrune의 미리 정한 communication topology [47, 30]에 묶여 있다. GPTSwarm [48], ADAS [49], AFlow [50], MaAS [51] 같은 자동화 MAS는 agent 간 topology나 prompt를 자동 최적화하지만, 결국 거대하고 둔중한 architecture를 만들며 축적된 협업 경험으로 민첩하게 자가 조정하지 못한다.

MAS 전용 memory의 부재가 이 문제의 뿌리다. MetaGPT·ChatDev·Exchange-of-Thought [52]에는 memory 관련 설계가 있지만 보통 inside-trial memory에 국한된다. cross-trial memory가 있더라도 final solution·execution result 같은 지나치게 압축된 artifact를 전달할 뿐 [21, 46, 47], 협업 경험에서 의미 있게 학습하지 못한다. 기존 single-agent memory를 그대로 MAS로 옮기는 일도 간단하지 않다. 여러 agent를 거치는 multi-turn orchestration [26, 27] 때문에 MAS의 task-solving trajectory는 단일 agent보다 훨씬 길다(그림 1 왼쪽처럼 token이 최대 10배). 협업 관점의 적절한 abstraction 없이 긴 trajectory 전체를 넣는 단순 retrieval 방식 [36, 37, 16]은 이점이 거의 없다.

> **핵심 질문:** agent team이 간결하고 교훈적인 경험·insight에서 이득을 얻도록, MAS의 길고 복잡한 interaction history를 저장·검색·관리하는 memory mechanism은 어떻게 설계할 수 있는가?

### 본 연구: G-Memory

이에 저자들은 **LLM 기반 MAS를 위한 graph-based agentic memory mechanism**, G-Memory를 제안한다. 복잡하고 긴 MAS interaction history를 다음 3계층 graph로 관리한다.

- **Insight Graph:** 역사적 경험에서 일반화 가능한 insight를 추상화한다.
- **Query Graph:** task query의 meta-information과 query 간 연결성을 부호화한다.
- **Interaction Graph:** agent 사이의 세밀한 textual communication log를 저장한다.

새 query가 오면 query graph topology로 관련 query record를 효율적으로 검색한다. 이어 query→insight graph 방향으로 올라가 상위 collective cognitive insight를 얻고, query→interaction graph 방향으로 내려가 현재 task에 가장 관련 있는 핵심 interaction subgraph를 찾는다. 이로써 information overload를 줄인다. 검색한 memory는 분업, task decomposition, 과거 실패의 교훈처럼 MAS에 행동 가능한 지침을 준다. task 종료 뒤에는 새로 증류한 insight, 풍부해진 query record, 상세 MAS trajectory 및 계층 간 연결을 모두 agentic하게 갱신한다. G-Memory는 mainstream MAS framework에 자연스럽게 삽입되는 plug-and-play module로서 agent 간 협업과 collective intelligence의 진화를 뒷받침한다.

저자의 기여는 다음과 같다.

1. **병목 식별:** 기존 MAS를 면밀히 검토해, 지나치게 단순한 memory architecture가 self-evolving capability의 근본 병목임을 보인다.
2. **실용 해법:** insight·query·interaction graph의 3계층 구조로 복잡하고 긴 agent 간 협업을 모델링하는 MAS용 hierarchical agentic memory architecture G-Memory를 제안한다.
3. **실험 평가:** 5개 benchmark에서 embodied action은 최대 20.89%, knowledge QA는 최대 10.12% 개선하면서 mainstream memory design과 비슷하거나 더 적은 token을 사용함을 보인다.

> 그림 1. (왼쪽) ALFWorld에서 여러 single-agent 및 MAS baseline의 token 비용. (오른쪽) insight graph, query graph, interaction(utterance) graph로 이루어진 G-Memory의 3계층 memory architecture 개요.

## 2. 관련 연구

### Single-Agent Memory

Memory는 agent가 환경과 상호작용하며 경험을 축적하고 세계를 탐색하게 하는 핵심 동력이다 [53–56]. task-solving과 social simulation LLM agent 모두에서 중요하며, 본 연구는 전자에 초점을 둔다. 초기 agent memory 연구는 chatbot의 LLM context window 한계를 다루는 단순 inside-trial memory에 머물렀다. MemoryBank [36], ChatDB [40], MemoChat [41], MemGPT [37]는 보통 RAG 스타일의 similarity 기반 chunk retrieval을 쓴다.

후속 연구는 더 인지적으로 영감받은 architecture로 발전했다. (1) ExpeL [43], Synapse [57]처럼 scope가 cross-trial memory로 확장되었고, (2) computer control [57], embodied action [58], scientific discovery [59], coding·reasoning [60]으로 domain이 넓어졌으며, (3) A-Mem [61], Mem0 [62], MemInsight [63]처럼 acquired knowledge·experience를 더 정교하게 추상화·요약하는 관리 기술로 옮겨갔다. 더 자세한 논의는 부록 D에 있다.

### Multi-Agent System의 Memory

MAS에 맞춘 memory mechanism은 여전히 충분히 탐구되지 않았다. LLM-Debate [20, 33], Mixture-of-Agent [64] 등은 memory component 자체가 없고, 다른 framework는 단순 inside-trial memory만 채택한다 [47, 52]. cross-trial memory를 시도한 framework [46]도 과거 query의 execution result만 압축해 보관하여 미묘한 agent interaction을 놓친다. 따라서 MAS 특유의 복잡한 task-solving process를 포착·조직·검색할 principled memory architecture가 시급하다 [39].

### LLM 기반 MAS

본 연구는 task-solving MAS를 대상으로 한다. 이는 single-agent와 달리 환경 상호작용을 통한 지속 진화 능력이 흔히 없다 [65, 66]. AutoGen [13], CAMEL [24], AgentVerse [67] 같은 초기 framework는 미리 정한 workflow에 전적으로 의존했다. 이후 연구 [68, 69, 50, 49, 70, 31]는 environmental feedback에 따라 dynamic MAS를 생성해 어느 정도 적응성을 도입했지만, 이 진화는 대개 one-shot이다. 예컨대 AFlow [50]는 특정 domain에 맞는 복잡한 MAS를 MCTS로 만들지만, task exposure가 늘면서 진화하거나 domain 간 전이할 능력은 없다 [51, 71]. 진정한 self-evolving capability를 지닌 MAS의 구성은 여전히 열린 난제다.

## 3. 사전 정의

이 절에서는 MAS와 G-Memory hierarchical memory architecture의 표기·핵심 개념을 정식화한다.

### Multi-agent system 정식화

MAS framework를 directed graph $G=(V,E)$로 둔다. $|V|=N$은 agent 수이고 $E\subseteq V\times V$는 communication channel이다. 각 node $C_i\in V$는 다음 quadruple의 개별 agent다.

$$C_i=(Base_i, Role_i, Mem_i, Plugin_i). \tag{1}$$

$Base_i$는 underlying LLM instance, $Role_i$는 지정된 role/persona, $Mem_i$는 과거 interaction·external knowledge store를 포함하는 memory state, $Plugin_i$는 web search engine 같은 auxiliary tool 집합이다.

사용자 query $Q$를 받으면 system은 $T$개의 synchronous communication epoch을 거친다. 각 epoch $t$에서 edge가 $\pi_j\to\pi_k$이면 $j<k$가 되도록 node의 topological ordering $\pi=[\pi_1,\ldots,\pi_N]$를 잡는다. 즉 각 agent는 모든 predecessor가 행동한 뒤에만 input을 처리한다. ordering 속 agent $C_i$의 $t$번째 output은 다음과 같다.

$$r_i^{(t)}=C_i\left(P_{sys}^{(t)},Q,\{r_j^{(t)}:C_j\in N^-(C_i)\}\right).$$

$r_i^{(t)}$에는 reasoning step, intermediate analysis, final proposal 등이 들어갈 수 있다. $P_{sys}^{(t)}$는 각 agent의 role을 포함하는 global instruction이고, $N^-(C_i)$는 output을 context로 주는 in-neighbor 집합이다. 모든 agent가 행동하면 global aggregation operator $A$가 response들을 interim solution으로 합친다.

$$a^{(t)}=A(r_1^{(t)},\ldots,r_N^{(t)}).$$

$A$의 구현은 majority voting [48], dedicated aggregator agent의 hierarchical summarization [13, 30], 마지막 agent output을 답으로 채택하는 방식 [47] 등이 있다. epoch은 preset limit 또는 early-stopping criterion [72]까지 $t=1,\ldots,T$로 반복되고, query $Q$의 final response $a^{(T)}$를 낸다.

### Memory Architecture

G-Memory는 MAS memory를 다음 세 hierarchical graph로 조율·관리한다.

1. **Interaction graph(utterance graph).** query $Q$에 대해 $G_{inter}^{(Q)}=(U^{(Q)},E_u^{(Q)})$로 둔다. node $U^{(Q)}=\{u_i\}$는 atomic utterance이며 $u_i=(A_i,m_i)$에서 $A_i\in V$는 발화 agent, $m_i$는 text content다. edge $(u_j,u_k)\in E_u^{(Q)}$는 시간 관계, 즉 $u_j$가 전달되어 $u_k$에 영감을 주었음을 뜻한다.
2. **Query graph.** 이전에 푼 query와 metadata를 저장하는 $G_{query}=(\mathcal Q,E_q)=\left(\{(Q_i,\phi_i,G_{inter}^{(Q_i)})\}_{i=1}^{|\mathcal Q|},E_q\right)$다. query node $q_i=(Q_i,\phi_i,G_{inter}^{(Q_i)})$는 원 query, task status $\phi_i\in\{Failed,Resolved\}$, 연결된 interaction graph로 구성된다. $E_q\subseteq\mathcal Q\times\mathcal Q$는 query의 semantic relationship을 부호화하며, 세밀한 topology를 통해 단순 embedding similarity보다 풍부한 retrieval을 가능하게 한다.
3. **Insight graph.** 최상위 graph는 $G_{insight}=(\mathcal I,E_i)=\left(\{(\omega_k,\mathcal Q_k)\}_{k=1}^{|\mathcal I|},E_i\right)$다. $\omega_k$는 distilled insight content, $\mathcal Q_k\subseteq\mathcal Q$는 이를 뒷받침하는 query 집합이다. $E_i\subseteq\mathcal I\times\mathcal I\times\mathcal Q$의 hyper-connection $(\iota_m,\iota_n,q_j)$는 insight $\iota_m$이 query $q_j$를 통해 $\iota_n$을 맥락화함을 나타낸다.

## 4. G-Memory

그림 2의 workflow처럼, 새 query $Q$가 오면 G-Memory는 먼저 관련 trajectory record를 coarse-grained retrieval로 찾는다(4.1절). 이어 upward traversal로 collective cognitive insight를 검색하고 downward traversal로 구체적 procedural trajectory를 증류한다(4.2절). memory-augmented MAS가 query를 실행한 뒤에는 environmental feedback에 기반해 hierarchical memory architecture 전체를 함께 갱신하여 group knowledge를 제도화한다(4.3절).

> 그림 2. 제안하는 G-Memory 개요. query graph의 similarity retrieval을 시작점으로, 위 방향 traversal은 insight graph의 추상적 지침을, 아래 방향 traversal은 interaction graph의 압축된 협업 궤적을 얻는다. agent별 memory augmentation 후 환경 feedback에 따라 insight·query·interaction graph를 갱신한다.

### 4.1 Coarse-grained Memory Retrieval

Mainstream MAS에 자연스럽게 통합되는 plug-in으로서 G-Memory는 MAS $G$가 새 사용자 query $Q$를 만날 때 실행된다. 조직 memory theory [1]가 강조하듯 효율적인 지식 retrieval은 보통 세밀한 접근보다 폭넓게 관련 있는 schema에서 시작한다. 따라서 G-Memory는 query graph $G_{query}$에서 similarity-based retrieval을 먼저 수행해 query의 sketch set $Q_S$를 얻는다.

$$Q_S=\underset{q_i\in\mathcal Q,\ |Q_S|=k}{\arg\operatorname{top-k}}\frac{v(Q)\cdot v(q_i)}{|v(Q)||v(q_i)|}. \tag{4}$$

$v(\cdot)$는 MiniLM [73] 같은 model로 query를 fixed-length embedding으로 바꾼다. 식 (4)는 의미상 유사한 역사적 query를 찾지만, 그 유사성은 피상적이거나 noisy할 수 있다. 그래서 G-Memory는 query graph에서 $Q_S$의 1-hop neighbor를 더해 관련 집합을 확장한다.

$$\tilde Q_S=Q_S\cup\{Q_k\in\mathcal Q\mid\exists Q_j\in Q_S,\ Q_k\in N^+(Q_j)\cup N^-(Q_j)\}. \tag{5}$$

이 record를 일부 single-agent memory system [41, 37]처럼 바로 input에 넣는 것은 최선이 아니다. context가 지나치게 길면 LLM을 압도하고, MAS의 agent들은 서로 다른 role이므로 기능에 맞춘 specialized memory가 필요하다. 다음 절의 bi-directional processing이 abstract·fine-grained level 모두에서 이를 해결한다.

### 4.2 Bi-directional Memory Traversal

확장된 relevant query node 집합 $\tilde Q_S$를 식별한 뒤 G-Memory는 multi-granularity memory support를 위한 양방향 traversal을 실행한다. 먼저 upward traversal($G_{query}\to G_{insight}$)은 현재 task의 전략 방향을 잡는 일반화된 insight node를 검색한다.

$$I_S=\mathcal P_{Q\to I}(\tilde Q_S),\qquad \mathcal P_{Q\to I}(S_q)\triangleq\{\iota_k\in\mathcal I\mid\mathcal Q_k\cap S_q\ne\varnothing\}.\tag{6}$$

$\mathcal P_{Q\to I}$는 입력 query set과 supporting query set이 교차하는 insight node를 찾는 query-to-insight projector다. $I_S$는 MAS $G$가 $Q$에 접근하는 방식을 이끌 수 있는 distilled, generalized knowledge다.

일반화 insight와 함께, 성공·실패한 협업을 낳은 reasoning pattern을 드러내는 agent의 세밀한 textual interaction history도 가치가 있다 [68, 74, 75]. downward traversal($G_{query}\to G_{interaction}$)에서 G-Memory는 LLM 기반 graph sparsifier $S_{LLM}(\cdot,\cdot)$로 필수 agent 협업을 담은 core subgraph를 뽑는다.

$$\{\tilde G_{inter}^{(Q_i)}\}_{i=1}^{M}=S_{LLM}\left(\{G_{inter}^{(Q_j)},Q\}\mid q_j\in\underset{q_k\in\tilde Q_S,\ |\cdot|=M}{\arg\operatorname{top-M}}R_{LLM}(Q,q_k)\right).\tag{7}$$

$R_{LLM}(Q,q_j)$는 과거 query의 $Q$에 대한 관련도를 평가한다. sparsifier는 원 interaction graph에서 필요한 dialogue element만 남긴 $\tilde G_{inter}^{(Q_j)}=(\tilde U^{(Q_j)},\tilde E_u^{(Q_j)})$를 만든다. 구현은 부록 C에 제시된다.

양방향 traversal 뒤에는 generalizable insight $I_S$와 상세 collaboration trajectory $\{\tilde G_{inter}^{(Q_i)}\}_{i=1}^M$를 얻는다. G-Memory는 MAS의 각 agent $C_i\in V$에 role별 memory support를 준다.

$$Mem_i\leftarrow\mathcal F\left(I_S,\{\tilde G_{inter}^{(Q_i)}\}_{i=1}^M;Role_i,Q\right),\quad C_i=(Base_i,Role_i,Mem_i,Plugin_i)\in V.\tag{8}$$

$\mathcal F$는 각 insight와 sparse interaction graph가 해당 agent의 role·task에 주는 효용·관련성을 평가한다. 이어 filtered insight, interaction snippet, 그 summary로 $Mem_i$를 초기화하여 agent가 reasoning epoch에 참여하기 전 관련 historical context를 제공한다. 논문 구현은 query $Q$ 풀이 시작 시 G-Memory를 부르지만, 실제 사용자는 MAS dialogue round마다 또는 특정 agent에만 호출하는 세밀한 전략을 선택할 수 있다.

### 4.3 Hierarchy Memory Update

각 agent memory augmentation 뒤 system $G$는 3절의 방식으로 실행되어 final solution $a^{(T)}$와 execution status $\phi\in\{Failed,Resolved\}$, token usage 등 environmental feedback을 받는다. G-Memory는 새 query를 통합하도록 3계층 memory architecture를 갱신한다.

interaction level에서는 각 agent utterance를 추적해 $G_{inter}^{(Q)}$를 만들고 저장한다. query level에서는 새 query node를 만들고 query graph에 더한다.

$$q_{new}\leftarrow(Q,\phi,G_{inter}^{(Q)}),\quad N_{conn}\leftarrow Q_R\cup\bigcup_{\iota_k\in I_S}\mathcal Q_k,$$
$$E_{new}\leftarrow\{(q_n,q_{new})\mid q_n\in N_{conn}\},\quad G_{query}\leftarrow(\mathcal Q\cup\{q_{new}\},E_q\cup E_{new}).\tag{9}$$

edge는 식 (7)의 top-$M$ relevant historical query 집합 $Q_R$ 및 $I_S$의 insight를 지지하는 query에 연결된다. insight level에서는 completed query의 learning을 insight graph에 합친다. summarization function $\mathcal J(\cdot,\cdot)$가 새 insight를 생성·연결한다.

$$\iota_{new}=\left(\mathcal J(G_{inter}^{(Q)},\phi),\{q_{new}\}\right),\quad E_{i,new}=\{(\iota_k,\iota_{new},q_{new})\mid\iota_k\in I_S\},$$
$$G_{insight}\leftarrow(\mathcal I\cup\{\iota_{new}\},E_i\cup E_{i,new}).\tag{10}$$

이전 insight가 새 task의 성공 또는 실패에 관련되었음을 반영하여, 사용한 insight의 supporting query set에도 $q_{new}$를 넣는다.

$$\mathcal I^{next}=(\mathcal I\setminus I_S)\cup\{(\omega_k,\mathcal Q_k\cup\{q_{new}\})\mid\iota_k=(\omega_k,\mathcal Q_k)\in I_S\}\cup\{\iota_{new}\},$$
$$G_{insight}\leftarrow(\mathcal I^{next},E_i\cup E_{i,new}).\tag{11}$$

모든 계층에서의 이 연속 갱신 cycle은 지속 경험에 따라 collective memory를 학습하고 적응적으로 정제하게 한다.

## 5. 실험

실험은 다음 질문을 다룬다. **RQ1:** G-Memory는 기존 single/multi-agent memory architecture와 비교해 어떤 성능을 내는가? **RQ2:** 과도한 resource overhead가 생기는가? **RQ3:** 핵심 component·parameter에 얼마나 민감한가?

### 5.1 실험 설정

**Dataset과 benchmark.** 세 domain의 널리 쓰이는 5개 benchmark를 사용한다. knowledge reasoning은 HotpotQA [76], FEVER [77], embodied action은 ALFWorld [78], SciWorld [79], game은 PDDL [80]이다. 상세는 부록 A.1에 있다.

**Baseline.** single-agent baseline은 no-memory, Voyager [16], MemoryBank [36], Generative Agents [19] 4개, multi-agent memory 구현은 MetaGPT [21], ChatDev [46], MacNet [47]에서 가져온 MetaGPT-M·ChatDev-M·MacNet-M 3개다.

**MAS와 backbone.** AutoGen [13], DyLAN [72], MacNet [47] 3개 MAS에 G-Memory·baseline을 통합한다. backbone은 Qwen-2.5-7b, Qwen-2.5-14b, `gpt-4o-mini`다. Qwen은 Ollama로 local deployment하고 GPT는 OpenAI API로 접근한다.

**Parameter.** 식 (4)의 $v(\cdot)$는 `all-MiniLM-L6-v2` [81]로 구현한다. 식 (7)의 relevant interaction graph 수 $M\in\{2,3,4,5\}$, 식 (4)의 relevant query 수 $k\in\{1,2\}$이며, hyperparameter ablation은 5.4절에 있다.

### 5.2 주요 결과(RQ1)

표 1–3은 3 LLM backbone과 3 MAS framework에서 memory architecture의 성능을 포괄적으로 보고한다. G-Memory는 모든 task domain·MAS framework에서 일관되게 성능을 높인다. Qwen-2.5-7b에서 AutoGen·MacNet과 결합할 때 최고 single/multi-agent memory baseline보다 평균 각각 6.8%, 5.5%를 앞선다. 더 강한 Qwen-2.5-14b에서는 개선이 더 뚜렷하다. 표 3에서 G-Memory는 MacNet의 ALFWorld 성능을 58.21%에서 79.10%로 20.89% 높인다.

기존 memory mechanism 대부분은 MAS에 일관되게 이득을 주지 못한다. 표 2에서 Voyager·MemoryBank는 AutoGen의 PDDL 성능을 각각 최대 4.17%, 1.34% 낮춘다. PDDL strategic game에서는 효과적인 분업이 핵심인데, 이 방법이 agent role별 memory support를 제공하지 못하기 때문이라고 저자들은 해석한다. MAS 지향 설계 ChatDev-M도 MacNet+SciWorld에서 2.32% 하락을 낸다. 과거 query의 execution result만 저장하는 좁은 memory scope가 information-rich embodied environment에서 제한적이기 때문이다. role-specific memory cue, 추상화한 high-level insight, trajectory condensation이 MAS memory에 필수임을 뒷받침한다.

**표 1. `gpt-4o-mini`에서 5 benchmark 성능 비교.** 수치는 평균±표준편차(%)이며 마지막 열은 평균이다.

| MAS | Memory | ALFWorld | SciWorld | PDDL | HotpotQA | FEVER | Avg. |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AutoGen | No-memory | 77.61±0.00 | 54.49±0.00 | 23.53±0.00 | 28.57±0.00 | 57.13±0.00 | 48.27±0.00 |
|  | Voyager | 85.07±0.46 | 62.36±0.87 | 24.56±0.03 | 32.32±0.75 | 63.27±0.14 | 53.52±0.25 |
|  | MemoryBank | 74.96±0.65 | 53.11±0.38 | 20.41±0.12 | 33.67±0.10 | 61.22±0.09 | 48.67±0.40 |
|  | Generative | 86.36±0.75 | 61.19±0.70 | 25.53±0.00 | 31.63±0.06 | 60.20±0.07 | 52.98±0.71 |
|  | MetaGPT-M | 81.34±0.73 | 61.91±0.42 | 21.63±0.90 | 32.67±0.10 | 62.67±0.54 | 52.04±0.77 |
|  | ChatDev-M | 79.85±0.24 | 50.96±0.53 | 16.65±0.88 | 24.49±0.08 | 59.18±0.05 | 46.23±0.04 |
|  | MacNet-M | 76.55±0.06 | 55.44±0.95 | 22.94±0.59 | 28.36±0.21 | 60.87±0.74 | 48.83±0.56 |
|  | **G-Memory** | **88.81±1.20** | **67.40±2.91** | **27.77±0.24** | **35.67±0.10** | **66.24±0.11** | **57.18±0.91** |
| DyLAN | No-memory | 56.72 | 55.38 | 11.62 | 31.69 | 60.20 | 43.12 |
|  | **G-Memory** | **70.90±4.18** | **65.64±0.26** | **18.95±0.33** | **34.69±0.00** | **64.22±0.02** | **50.88±0.76** |
| MacNet | No-memory | 51.49 | 57.53 | 12.18 | 28.57 | 60.29 | 42.01 |
|  | **G-Memory** | **67.16±5.67** | **68.11±0.58** | **24.33±2.15** | **35.69±0.12** | **64.44±0.15** | **51.95±0.94** |

### 5.3 비용 분석(RQ2)

그림 3·7은 여러 setting의 performance–token cost trade-off를 보여준다. G-Memory는 과도한 token 소비 없이 high-performing collective memory를 달성한다. 예를 들어 PDDL+AutoGen에서 no-memory보다 최고 개선(10.32%)을 내면서 token 증가는 $1.4\times10^6$에 불과했다. 반면 MetaGPT-M은 $2.2\times10^6$ token을 추가로 쓰고도 4.07% 향상에 그쳤다. 이는 G-Memory의 token efficiency를 보여준다.

> 그림 3. 여러 memory architecture와 결합했을 때 G-Memory의 performance 대 전체 system token cost 분석.

### 5.4 Framework 분석(RQ3)

**Sensitivity analysis.** 식 (5)의 hop expansion은 1-hop이 일관되게 최고 또는 근접 최고 성능을 냈다(AutoGen에서 ALFWorld 85.82%, PDDL 55.24%). 2-hop·3-hop은 종종 성능을 낮췄고, 예를 들어 PDDL은 2-hop에서 49.79%로 떨어진다. 과도한 hop expansion은 upward traversal 때 task와 무관한 insight를 넣어 reasoning을 방해할 수 있다. 식 (4)의 $k$도 $\{1,2\}$가 최적이며, $k=5$처럼 큰 값은 ALFWorld+AutoGen에서 7.71%, FEVER+DyLAN에서 2.5%까지 성능을 낮춘다. 이에 모든 실험에서 1-hop, $k\in\{1,2\}$를 쓴다.

**Ablation.** 그림 4c는 high-level insight module(식 (6)의 $I_S$)과 fine-grained interaction module(식 (7)의 core trajectory)을 분리한다. 어느 하나를 빼도 성능이 일관되게 하락한다. fine-grained interaction만 켜면 full method보다 AutoGen 평균 4.47%, DyLAN 평균 3.82% 낮고, insight만 켜면 하락 폭은 각각 3.95%, 3.39%다. 둘 다 기여하지만, 대화 수준의 세밀한 contextual grounding을 보존하는 interaction이 조금 더 큰 영향을 준다.

> 그림 4. (a) 식 (5)의 hop expansion sensitivity. (b) 식 (4)의 선택 query 수 $k$ sensitivity. (c) high-level insight만 또는 fine-grained interaction만 제공하는 두 G-Memory variant 절제 연구. 모두 Qwen-2.5-14b로 수행했다.

### 5.5 사례 연구

그림 5는 다양한 task에서 G-Memory가 주는 구체적 memory cue를 보인다. ALFWorld+AutoGen에서 “깨끗한 cloth를 countertop에 놓아라”라는 query에, G-Memory는 “깨끗한 egg를 microwave에 놓아라”라는 유사 과거 query를 검색한다. 둘 다 object가 clean state여야 한다. 또한 solver agent가 egg를 청소하기 전에 microwave에 두려 하자 ground agent가 개입한 핵심 trajectory segment를 제시해 현재 task에 행동 가능한 지침을 준다. HotpotQA web-search에서는 비슷한 이름의 인물을 잘못 가리키지 말라는 insight를 검색해 agent가 오류 답을 피하게 한다. embodied action·knowledge reasoning·game을 아우르는 multi-level memory support를 제공한다.

> 그림 5. ALFWorld+AutoGen, HotpotQA+DyLAN, PDDL+MacNet의 사례. 각 task에 대해 high-level insight와 압축한 fine-grained trajectory가 제시된다.

## 6. 결론과 한계

저자들은 MAS용 기존 memory architecture를 면밀히 검토해 과도하게 단순한 설계가 self-evolution을 근본적으로 막는다고 진단한다. 이를 위해 복잡하고 긴 MAS interaction trajectory를 insight·query·interaction graph의 3계층으로 조직하는 G-Memory를 제안한다. G-Memory는 추상적·일반화 가능한 insight부터 task-critical collaboration segment까지 각 agent에 맞춘 hierarchical memory cue를 제공하고 episode 간 knowledge base를 동적으로 진화시킨다. 실험은 이 module이 SOTA MAS framework에 자연스럽게 결합되어 embodied action에서 최대 20.89% 향상 등 self-evolution을 크게 높임을 보인다.

한계는 세 domain, 다섯 benchmark에서 평가했지만 medical QA 같은 더 다양한 task에서 검증하면 타당성이 더 강해진다는 점이다. 이는 향후 과제로 남긴다.

## 부록 A. 실험 세부 사항

### A.1 Dataset 설명

- **ALFWorld** [78](<https://alfworld.github.io/>, MIT license): agent가 자연어 command로 object를 탐색·상호작용하는 가정 작업 중심 text-based embodied environment다.
- **ScienceWorld** [79](<https://github.com/allenai/ScienceWorld>, Apache-2.0): agent가 방을 탐색하고 experiment를 수행하는 text-based interactive science task 환경이다. procedural reasoning과 scientific exploration을 시험한다.
- **PDDL** [80](<https://github.com/hkust-nlp/AgentBoard>, Custom properties): AgentBoard의 game dataset으로, agent가 PDDL expression을 사용해 복잡한 task를 끝내는 여러 strategic game으로 이뤄진다.
- **HotpotQA** [76](<https://hotpotqa.github.io/>, CC BY-SA 4.0): supporting fact의 강한 supervision을 갖춘 multi-hop QA dataset이다. 특히 web search tool을 통한 검색·정보 통합과 explainable reasoning 능력을 평가한다.
- **FEVER** [77](<https://fever.ai/dataset/fever.html>, CC BY-SA): web search API로 claim을 검증하는 knowledge-intensive fact verification dataset이며 evidence-based reasoning benchmark다.

평가 지표로 FEVER·HotpotQA는 exact-match accuracy, ScienceWorld·PDDL은 progress rate, ALFWorld는 success rate를 사용한다.

### A.2 Baseline 설정

- **Voyager:** Minecraft 환경에서 embodied agent가 계속 상호작용하며 새 artifact를 만들고, memory를 진화의 핵심 동력으로 쓰는 Voyager agent [16]의 설계다. 원래 single-agent 전용이므로 각 agent가 볼 수 있는 dialogue context에 따른 agent-specific history retrieval로 MAS에 맞췄다. 다른 single-agent memory도 같은 방식으로 adaptation했다.
- **MemoryBank:** Ebbinghaus forgetting curve에서 영감 받은 update mechanism으로 시간 감쇠와 저장 정보의 상대적 중요도에 따라 memory를 강화하거나 버린다. 선택적 보존·망각이라는 인간형 memory behavior를 모사한다 [36].
- **Generative:** raw observational memory와 high-level reflective memory를 모두 쓴다 [19]. 후자는 reflection을 통해 얻은 abstract thought로 경험을 더 구조적·개념적으로 나타낸다.
- **MetaGPT-M:** MetaGPT [21]에서 가져왔으며 여러 agent가 하나의 task를 푸는 동안 내부에 보관하는 inside-trial memory에만 초점을 둔다.
- **ChatDev-M:** ChatDev [46]에서 adaptation했다. inside-trial memory는 매 round 시작 시 central/initiating agent가 과거 interaction을 바탕으로 지침을 주도록 전달한다. cross-trial memory는 과거 query solution을 저장해 검색하지만, 본 task에서는 정보가 풍부한 inter-agent collaboration을 효과적으로 관리하지 못한다.
- **MacNet-M:** MacNet [47]의 설계다. inside-trial memory는 이전 round의 final answer뿐이고, artifact가 아닌 모든 dialogue context, 즉 agent 간 interaction trajectory는 전부 버린다.

### A.3 MAS 설정

**AutoGen.** AutoGen [13]의 A3: Decision Making structure를 쓴다. (1) “You are a smart agent designed to solve problems.”라는 system prompt로 초기화되어 solution을 만드는 Solver Agent, (2) reference standard를 바탕으로 solver output을 비판적으로 평가하고 오류를 찾는 Ground Truth Agent, (3) 검증한 solution을 executable command로 옮기는 Executor Agent로 구성된다. 이 modular design은 투명하고 검증 가능하며 실행 가능한 협업을 만든다.

**DyLAN.** LLM-Debate와 유사하지만 multi-turn interaction에서 더 효율적인 agent-wise early stopping을 넣은 debate-style framework다 [72]. task별 preliminary trial에서 가장 기여한 agent를 찾는 unsupervised metric, Agent Importance Score 기반 agent-selection algorithm을 쓴다. 논문 구현에서는 세 agent가 토론하고 ranker agent가 상대 중요도를 평가한다.

**MacNet.** Central agent가 없는 decentralized, scalable MAS [47]다. 이전 agent output을 바탕으로 다음 agent에 행동 가능한 instruction을 주는 edge agent를 agent interaction 사이에 호출한다. 다양한 scenario에서 견고한 random graph topology와 edge agent 외 5개 agent를 사용한다.

## 부록 B. 추가 실험 결과

### B.1 RQ1 결과

표 2·3은 각각 Qwen-2.5-7b와 Qwen-2.5-14b backbone의 추가 실험 결과다. 그림 6a–c은 ALFWorld에서 trial 수가 늘어날 때 서로 다른 memory architecture를 결합한 AutoGen·DyLAN·MacNet의 success-rate curve를 보인다. G-Memory는 일관되게 더 적은 trial로 성공하게 하며 더 높은 최종 performance ceiling에 도달한다.

### B.2 RQ2 결과

그림 7은 여러 benchmark·MAS framework에서 memory architecture별 token cost의 추가 비교다. G-Memory는 Generative·MetaGPT-M 같은 classical baseline보다 token cost 증가가 작거나 없으면서 가장 큰 performance improvement를 일관되게 제공한다.

### B.3 사례 연구

**Insight graph.** 그림 8은 ALFWorld에서 MAS framework·LLM backbone별로 G-Memory가 요약한 high-level insight를 시각화한다. ALFWorld는 다양한 task category로 자연스럽게 구성되므로, task type별 insight node의 연결도 살핀다. 유사 task에서 온 insight 사이에는 dense intra-category connection이 나타나며, 동시에 domain 간 전이 가능한 pattern을 반영하는 의미 있는 inter-category link도 생긴다.

**Query graph.** 그림 9–11은 ALFWorld, PDDL, SciWorld에서 G-Memory가 만든 query graph를 보여준다. 두 query node 사이 directed edge는 한 query의 historical trajectory가 다른 query 실행에 유용한 guidance를 준다는 뜻이다. 의미상 유사한 query가 dense subgraph를 이루는 emergent cluster와, cross-task inspiration을 담는 드문 cluster 간 edge가 관찰된다. 이는 structured memory reasoning으로 협업 경험을 효과적으로 조직·연관하는 능력을 보인다.

> 그림 6. ALFWorld에서 trial 수에 따른 (a) AutoGen, (b) DyLAN, (c) MacNet의 performance trajectory.
>
> 그림 7. 여러 benchmark에서 서로 다른 memory architecture와 결합한 G-Memory의 performance 대 전체 system token cost.
>
> 그림 8. LLM backbone·MAS·benchmark별 insight graph 시각화.
>
> 그림 9–11. 각각 ALFWorld, SciWorld, PDDL dataset에서 최적화한 query graph.

## 부록 C. Prompt Set

중괄호 변수·prompt 변수명은 구현 호환성을 위해 원문 그대로 보존한다.

### Query Relevance Filtration

```text
task_relevancy_system_prompt = """두 text 사이의 관련도를 점수화하도록 설계된 agent다."""

task_relevancy_user_prompt = """성공적으로 task를 완료한 성공 사례와 진행 중인 task를 제공한다. 두 사례를 요약하지 말고, 성공 사례가 진행 중인 task에 얼마나 관련 있고 도움이 되는지를 1–10 척도로 평가하라.

Success Case:
{trajectory}
Ongoing task:
{query_scenario}
Score:"""
```

### Graph Sparsifier

```text
extract_true_traj_system_prompt = """당신은 핵심 지점 추출에 능숙한 agent다.
task와 성공 execution trajectory가 주어진다. 덜 중요한 step은 걸러내고 task 완료에 필요한 critical step을 식별하라."""

extract_true_traj_user_prompt = """
Note:
- 반드시 원래 trajectory를 따르며, trajectory에 없는 step은 절대로 추가하지 마라.
- 성공 trajectory에도 잘못된 step이 있을 수 있다. 'Nothing happens' observation에 해당하는 action은 잘못됐을 가능성이 높으므로 걸러라.
- 각 step은 가장 세밀한 granularity여야 한다.
- example의 output format을 엄격히 따라라.

## Here is the task:
### Task
{task}
### Trajectory
{trajectory}
### Output
"""
```

### Insight Summarization Function

이 prompt는 일부 [43]에서 adaptation했으며, 저자들은 해당 구현에 감사를 표한다.

```text
learn_lessons_system_prompt_compare = """당신은 경험에서 배우는 분석 중심 agent다. 다음을 제공받는다.
- 실패 trajectory와 그 outcome
- 유사 task를 완료한 성공 trajectory

두 trajectory를 분석해 명확하고 행동 가능한 insight를 만들어라. 실패 trajectory가 무엇을 놓쳤고 성공 trajectory가 그 함정을 어떻게 해결하거나 피했는지 드러내라.

## Requirements:
- 모든 insight는 두 trajectory의 대비에서 직접 도출해야 한다.
- 성공 예가 뒷받침하지 않는 추측·step을 넣지 마라.
- 두 사례의 구체적 행동 또는 전략 차이에 집중하라.
- 각 insight는 간결하고 강한 효과가 있어야 한다.

Output Format:
- 번호 목록으로 즉시 시작한다.
- 도입·설명은 쓰지 않는다.
- 정확히 다음 형식을 쓴다.
1. Insight 1
2. Insight 2
3. Insight 3
..."""

learn_lessons_user_prompt_compare = """
## Successful trajectory
{true_traj}
## Failed trajectory
### trajectory
{false_traj}
Your output:
"""
```
