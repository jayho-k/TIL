# Zep: Agent Memory를 위한 시간 인지 지식 그래프 아키텍처

> Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef, *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*, arXiv:2501.13956v1 (2025-01-20).
>
> 원문 PDF 12쪽 전체를 기준으로 작성하는 한국어 번역본이다. 제품명·모델명·수식·변수명·Cypher·프롬프트의 구조화 키와 인용은 원문을 유지한다.

## 초록

저자들은 Deep Memory Retrieval(DMR) benchmark에서 당시 SOTA system인 MemGPT를 앞서는 AI agent용 새로운 memory layer service, **Zep**을 소개한다. Zep은 실제 enterprise use case를 더 잘 반영하는 DMR보다 포괄적이고 어려운 평가에서도 뛰어나다. 기존 LLM agent용 retrieval-augmented generation(RAG) framework는 static document retrieval에 한정되지만, enterprise application은 진행 중인 conversation과 business data 등 다양한 source의 dynamic knowledge integration을 요구한다.

Zep은 핵심 component인 **Graphiti**—시간을 인지하는 knowledge graph engine—로 이 한계를 해결한다. Graphiti는 unstructured conversational data와 structured business data를 모두 동적으로 종합하면서 historical relationship을 유지한다. MemGPT team이 primary metric으로 만든 DMR에서 Zep은 94.8% 대 93.4%로 더 높았다. 복잡한 temporal reasoning task를 통해 enterprise use case를 더 잘 반영하는 LongMemEval에서는 baseline implementation보다 accuracy를 최대 18.5% 높이고 response latency를 90% 줄였다. 이 결과는 cross-session information synthesis, long-term context maintenance처럼 enterprise에 중요한 task에서 특히 두드러져 실제 deployment에서의 효과를 보인다.

## 1. 서론

Transformer 기반 LLM은 industry·research community에 큰 영향을 주었고 [1], 그 주요 application 중 하나가 chat-based agent다. 하지만 agent capability는 LLM context window, context의 효과적 활용, pre-training에서 얻은 knowledge에 제한된다. 따라서 out-of-domain(OOD) knowledge를 제공하고 hallucination을 줄이려면 추가 context가 필요하다.

RAG는 지난 50년간 발전한 information retrieval(IR) 기법 [2]을 사용해 LLM에 필요한 domain knowledge를 공급하는 핵심 관심 분야가 되었다. 그러나 현 RAG는 넓은 domain knowledge와 대체로 static corpus에 집중한다. 즉 corpus에 넣은 document 내용은 좀처럼 바뀌지 않는다. Agent가 일상의 문제부터 매우 복잡한 문제까지 자율적으로 풀며 널리 쓰이려면, 사용자와의 interaction 및 연관 business·world data에서 오는 지속적으로 변화하는 대규모 data corpus에 접근해야 한다. 저자들은 agent에 이 넓고 dynamic한 “memory”를 부여하는 일이 이 비전의 핵심 building block이며, 현 RAG가 그 미래에 맞지 않는다고 주장한다. 전체 conversation history, business dataset, domain-specific content는 LLM context window에 효과적으로 들어갈 수 없으므로 agent memory의 새 접근이 필요하다. LLM agent에 memory를 추가하는 생각 자체는 MemGPT [3]가 이미 탐구했다.

최근에는 traditional IR의 약점을 해결하려고 knowledge graph(KG)를 RAG architecture에 사용한다 [4]. 본 논문은 dynamic·temporally-aware KG engine Graphiti [6]로 구동되는 memory layer service **Zep** [5]을 제안한다. Zep은 unstructured message data와 structured business data를 ingest하고 synthesis한다. Graphiti는 새 정보로 knowledge graph를 **non-lossy**하게 update하며, fact·relationship의 validity period를 포함한 timeline을 유지한다. 이에 따라 복잡하고 진화하는 세계를 graph로 표현할 수 있다.

Zep은 production system이므로 memory retrieval의 accuracy·latency·scalability에 집중한다. 이 효과는 MemGPT의 DMR task [3]와 LongMemEval benchmark [7]의 두 기존 benchmark로 평가한다.

## 2. Knowledge Graph 구성

Zep의 memory는 time-aware dynamic KG $G=(N,E,\phi)$로 구동된다. $N$은 node, $E$는 edge, $\phi:E\to N\times N$은 formal incidence function이다. Graph는 episode subgraph, semantic entity subgraph, community subgraph의 세 계층으로 구성된다.

1. **Episode subgraph $G_e$.** Episodic node(episode) $n_i\in N_e$는 message·text·JSON 형태의 raw input data를 담는다. Episode는 semantic entity·relation을 추출하는 non-lossy data store다. Episodic edge $e_i\in E_e\subseteq(N_e\times N_s)$는 episode와 그것이 참조하는 semantic entity를 연결한다.
2. **Semantic entity subgraph $G_s$.** episode subgraph 위에 쌓인다. Entity node $n_i\in N_s$는 episode에서 뽑아 기존 graph entity와 resolution한 entity이고, semantic edge $e_i\in E_s\subseteq(N_s\times N_s)$는 episode에서 추출한 entity 사이 relationship이다.
3. **Community subgraph $G_c$.** Zep KG의 최상위 level이다. Community node $n_i\in N_c$는 강하게 연결된 entity cluster를 나타낸다. Community는 cluster의 high-level summary를 담아 $G_s$ 구조를 더 포괄적이고 상호연결된 시각으로 보여준다. Community edge $e_i\in E_c\subseteq(N_c\times N_s)$는 community와 entity member를 잇는다.

raw episodic data와 derived semantic entity information을 함께 저장하는 이중 storage는 human memory의 심리학 model을 닮았다. 이 model은 distinct event를 나타내는 episodic memory와 concept·meaning의 association을 포착하는 semantic memory를 구별한다 [8]. Zep을 쓰는 LLM agent는 human memory system 이해에 더 맞는 정교하고 미묘한 memory structure를 만들 수 있다. Knowledge graph는 이를 효과적으로 표현한다. episode·semantic subgraph 분리는 AriGraph [9]의 유사 접근에서, high-level structure·domain concept을 나타내는 community node는 GraphRAG [4]에서 바탕을 얻었다. episode→fact→entity→community의 hierarchy는 기존 hierarchical RAG strategy [10, 11]를 확장한다.

### 2.1 Episode

Zep graph construction은 raw data unit인 **Episode**의 ingestion에서 시작한다. Episode에는 message, text, JSON의 세 core type이 있다. 각 type은 graph construction 중 고유 handling이 필요하지만, 실험이 conversation memory를 중심으로 하므로 논문은 message type에 집중한다. 여기서 message는 비교적 짧은 text(여러 message가 LLM context window에 들어갈 수 있음)와 utterance를 만든 actor를 함께 갖는다.

각 message에는 전송 시점을 나타내는 reference timestamp $t_{ref}$가 있다. 이는 “next Thursday”, “in two weeks”, “last summer” 같은 content의 relative/partial date를 정확히 식별·추출하게 한다. Zep은 bi-temporal model을 구현한다. timeline $T$는 event의 chronological ordering이고, $T'$는 Zep data ingestion의 transactional order다. $T'$는 database auditing의 전통적 용도를 맡고, $T$는 conversational data와 memory의 dynamic nature를 모델링하는 차원을 더한다. 이 bi-temporal approach는 LLM-based KG construction의 새 발전이며 기존 graph-based RAG와 비교되는 Zep 고유 능력의 기반이다.

episodic edge $E_e$는 episode와 추출된 entity node를 잇는다. Episode와 그것에서 유도된 semantic edge는 edge와 source episode 관계를 추적하는 bidirectional index를 유지한다. 이로써 Graphiti episodic subgraph의 non-lossy 성질이 강화된다. semantic artifact를 source로 거슬러 올라가 citation·quotation할 수 있고, episode도 관련 entity·fact를 빠르게 얻는다. 이 연결은 본 논문의 실험에서 직접 검토하지 않았으며 향후 연구에서 다룬다.

### 2.2 Semantic Entity와 Fact

#### 2.2.1 Entity

Entity extraction은 episode processing의 첫 단계다. ingestion 시 system은 named entity recognition context를 위해 현재 message와 마지막 $n$개 message를 함께 처리한다. 본 논문 및 일반 Zep implementation에서 $n=4$, 즉 context 평가에 두 complete conversation turn을 제공한다. Message processing에 집중하므로 speaker는 자동으로 entity로 추출한다. 초기 entity extraction 뒤에는 reflexion [12]에서 영감을 받은 reflection technique을 써 hallucination을 최소화하고 extraction coverage를 높인다. 후속 entity resolution·retrieval을 돕도록 episode의 entity summary도 뽑는다.

추출 뒤 system은 각 entity name을 1,024차원 vector space에 embed한다. 이 embedding은 기존 graph entity node 전체에서 cosine similarity search로 유사 node를 검색하게 한다. 기존 entity name·summary에는 별도의 full-text search도 수행해 추가 candidate node를 찾는다. Candidate와 episode context를 entity resolution prompt로 LLM에 넣는다. duplicate entity가 확인되면 updated name과 summary를 만든다.

entity extraction·resolution 뒤 data는 predefined Cypher query로 KG에 들어간다. LLM-generated database query보다 이 방식을 택한 이유는 schema format의 일관성을 보장하고 hallucination 가능성을 줄이기 위해서다. graph construction의 일부 prompt는 부록에 제시한다.

#### 2.2.2 Fact

Fact extraction은 episode에서 entity 사이 relationship을 뽑으며, 각 fact는 핵심 predicate를 포함한다. 같은 fact를 서로 다른 entity 사이에서 여러 번 추출할 수 있어 Graphiti는 hyper-edge 구현으로 복잡한 multi-entity fact를 모델링할 수 있다.

추출 뒤 system은 graph integration 준비를 위해 fact embedding을 만든다. Edge deduplication은 entity resolution과 유사한 과정으로 한다. Relevant edge의 hybrid search는 제안한 새 edge와 **같은 entity pair 사이에 이미 존재하는 edge**로 한정한다. 이는 서로 다른 entity pair 사이의 유사 edge를 잘못 합치는 일을 막고, search space를 그 entity pair의 edge subset으로 줄여 계산 복잡도도 크게 낮춘다.

#### 2.2.3 Temporal Extraction과 Edge Invalidation

Graphiti가 다른 KG engine과 구별되는 핵심은 temporal extraction·edge invalidation으로 dynamic information update를 관리하는 능력이다. System은 $t_{ref}$를 이용해 episode context에서 fact의 temporal information을 뽑는다. “Alan Turing was born on June 23, 1912” 같은 absolute timestamp와 “I started my new job two weeks ago” 같은 relative timestamp를 정확히 추출·datetime 표현할 수 있다.

Bi-temporal modeling과 일관되게 네 timestamp를 추적한다. $t'_{created}$, $t'_{expired}\in T'$는 system에서 fact가 생성·무효화된 시점을, $t_{valid}$, $t_{invalid}\in T$는 fact가 참인 temporal range를 나타낸다. 이 data point는 다른 fact 정보와 함께 edge에 저장된다.

새 edge는 database의 기존 edge를 invalidation할 수 있다. System은 LLM으로 새 edge와 의미상 관련된 기존 edge를 비교해 contradiction 가능성을 찾는다. 시간상 겹치는 contradiction을 찾으면, 무효화되는 edge의 $t_{invalid}$를 무효화 edge의 $t_{valid}$로 설정한다. Transactional timeline $T'$를 따르므로 Graphiti는 edge invalidation을 정할 때 새 정보를 일관되게 우선한다. 이 방식은 conversation이 진화하면서 data를 동적으로 더하면서도 현재 relationship state와 relationship evolution의 historical record를 모두 유지한다.

### 2.3 Community

episodic·semantic subgraph를 만든 뒤 system은 community detection으로 community subgraph를 구성한다. GraphRAG [4]의 기법을 바탕으로 하지만 Leiden algorithm [14] 대신 label propagation algorithm [13]을 쓴다. label propagation은 dynamic extension이 단순하여, 새 data가 들어와도 complete community refresh를 늦추면서 오랫동안 정확한 community representation을 유지할 수 있기 때문이다.

dynamic extension은 label propagation의 single recursive step 논리를 구현한다. 새 entity node $n_i\in N_s$를 graph에 추가하면 이웃 node의 community를 조사해, 이웃 중 plurality가 속한 community에 새 node를 배정하고 community summary와 graph를 갱신한다. Data flow 중 efficient extension을 가능하게 하지만 결과 community는 complete label propagation 결과에서 점차 벗어난다. 따라서 periodic community refresh는 여전히 필요하다. 그럼에도 이 dynamic update는 latency와 LLM inference cost를 크게 줄이는 실용적 heuristic이다.

GraphRAG [4]와 같이 community node에는 member node의 iterative map-reduce-style summary를 넣는다. 다만 retrieval은 GraphRAG의 map-reduce approach와 크게 다르다. Community summary에서 key term·relevant subject를 담은 community name을 만들고 embed해 cosine similarity search에 저장한다.

## 3. Memory Retrieval

Zep memory retrieval은 강력하고 복잡하며 고도로 configurable하다. Zep graph search API는 text-string query $q\in S$를 받아 text-string context $c\in S$를 돌려주는 $f:S\to S$를 구현한다. $c$에는 LLM agent가 $q$에 정확히 답하는 데 필요한 node·edge의 formatted data가 들어간다. $f(q)\mapsto c$는 세 단계다.

1. **Search($\sigma$):** 관련 정보를 가질 candidate node·edge를 찾는다. 여러 search method를 쓰지만 전체 함수는 $\sigma:S\to E_s^n\times N_s^n\times N_c^n$으로 나타낼 수 있다. 즉 query를 관련 textual information을 담는 semantic edge·entity node·community node list의 triple로 바꾼다.
2. **Reranker($\rho$):** search result를 재정렬한다. reranker function/model은 result list를 받아 관련도 순으로 다시 정렬한다.
3. **Constructor($\kappa$):** 관련 node·edge를 text context로 바꾼다. 각 $e_i\in E_s$에서는 fact와 $t_{valid},t_{invalid}$, 각 $n_i\in N_s$에서는 name·summary, 각 $n_i\in N_c$에서는 summary를 반환한다.

따라서 $f(q)=\kappa(\rho(\sigma(q)))=c$다. Context template은 다음과 같다.

```text
FACTS와 ENTITIES는 현재 대화와 관련된 context다.
다음은 가장 관련 있는 fact와 valid date range다. fact가 event에 관한 것이면 event는 이 시간에 일어난다.
형식: FACT (Date range: from - to)
<FACTS>
{facts}
</FACTS>
다음은 가장 관련 있는 entity다.
ENTITY_NAME: entity summary
<ENTITIES>
{entities}
</ENTITIES>
```

### 3.1 Search

Zep은 cosine semantic similarity search($\sigma_{cos}$), Okapi BM25 full-text search($\sigma_{bm25}$), breadth-first search($\sigma_{bfs}$)의 세 search function을 구현한다. 앞의 둘은 Neo4j의 Lucene implementation [15, 16]을 쓴다. Object type별 search field는 $E_s$=fact field, $N_s$=entity name, $N_c$=community name(community가 다루는 relevant keyword·phrase)이다. 독립적으로 개발했지만 community search는 LightRAG [17]의 high-level key search와 유사하다. LightRAG와 Graphiti 같은 graph system의 hybridization은 향후 연구 방향이다.

Cosine·full-text search는 RAG에서 확립되어 있지만 [18], KG의 BFS는 AriGraph [9], Distill-SynthKG [19] 등을 제외하면 RAG에서 관심을 덜 받았다. Graphiti의 BFS는 initial result를 $n$-hop 안의 추가 node·edge로 확장한다. Node도 parameter로 받으므로 search를 더 잘 제어하며, recent episode를 seed로 쓰면 최근 언급한 entity·relationship을 retrieved context에 넣을 수 있다. 세 방법은 word, semantic, contextual similarity(그래프상 가까운 node·edge가 더 유사한 conversation context에 나타남)를 각각 겨냥하여 optimal context 발견 가능성을 극대화한다.

### 3.2 Reranker

Initial search가 high recall을 목표로 한다면 reranker는 가장 관련 있는 result를 우선해 precision을 높인다. Zep은 Reciprocal Rank Fusion(RRF) [20], Maximal Marginal Relevance(MMR) [21]를 지원한다. Graph-based episode-mentions reranker는 conversation 내 entity·fact mention 빈도로 우선순위를 정해 자주 참조된 정보를 더 쉽게 접근하게 한다. Node distance reranker는 designated centroid node에서의 graph distance로 result를 정렬해 KG의 특정 area에 localize된 context를 준다. 가장 정교한 기능은 cross-encoder—cross-attention으로 query에 대한 node·edge relevance score를 만드는 LLM—이지만 계산 비용도 가장 크다.

## 4. 실험

두 LLM-memory benchmark를 분석한다. 첫 평가는 [3]의 DMR task로, “Beyond Goldfish Memory” [22]의 Multi-Session Chat dataset에서 500개 conversation을 뽑았다. 둘째는 평균 115,000 token의 광범위한 conversation context를 제공하는 LongMemEvals [7]다.

두 실험 모두 conversation history를 Zep API로 KG에 통합하고 3절 기법으로 가장 관련 있는 edge(fact) 20개와 entity node(entity summary)를 검색했다. 이를 Zep memory API와 같은 기능의 context string으로 재구성한다. 이는 Graphiti 전체 search 기능 중 일부만 평가하지만 기존 benchmark와 명확히 비교할 수 있다.

### 4.1 Model 선택

Embedding·reranking에는 BAAI BGE-m3 model [23, 24]을 쓴다. Graph construction에는 `gpt-4o-mini-2024-07-18`, context 답변 chat agent에는 `gpt-4o-mini-2024-07-18`와 `gpt-4o-2024-11-20`을 쓴다. MemGPT DMR result와 직접 비교하려고 `gpt-4-turbo-2024-04-09`도 DMR에 사용했다. Experimental notebook과 관련 prompt는 GitHub·부록에서 공개한다.

### 4.2 Deep Memory Retrieval(DMR)

DMR [3]은 최대 12 message의 5 chat session으로 된 500개 multi-session conversation과 memory evaluation Q/A pair로 이뤄진다. MemGPT는 `gpt-4-turbo`로 93.4% accuracy이며 recursive summarization baseline 35.3%를 크게 앞선다. 비교를 위해 full-conversation context와 session summary baseline도 구현했다. `gpt-4-turbo`에서는 각각 94.4%, 78.6%, `gpt-4o-mini`에서는 98.0%, 88.0%를 얻었다. 공개 연구의 방법론 세부가 부족하여 `gpt-4o-mini`로 MemGPT result는 재현하지 못했다.

Zep은 conversation을 ingest하고 top-10 relevant node·edge를 검색해 평가했다. LLM judge가 agent response와 golden answer를 비교한다. `gpt-4-turbo` 94.8%, `gpt-4o-mini` 98.2%로 MemGPT와 각 full-conversation baseline보다 소폭 높았다. 다만 각 conversation은 60 message뿐이어서 최신 LLM context window에 쉽게 들어간다는 점을 고려해야 한다.

DMR은 scale 외에도 한계가 있다. single-turn fact-retrieval question만 써 complex memory understanding을 평가하지 못하고, “favorite drink to relax with”, “weird hobby”처럼 conversation에서 그렇게 명시하지 않은 모호한 표현이 많다. 무엇보다 real-world enterprise LLM agent use case를 잘 대표하지 못한다. Modern LLM의 단순 full-context가 높은 성능을 내는 사실도 benchmark가 memory system을 평가하기 부적절함을 보인다. [7]은 conversation length 증가에 따라 LongMemEval에서 LLM 성능이 빠르게 줄어듦을 보였고, LongMemEval은 더 길고 coherent한 conversation·다양한 question으로 이 약점을 보완한다.

| Memory | Model | Score |
| --- | --- | ---: |
| Recursive Summarization | gpt-4-turbo | 35.3% |
| Conversation Summaries | gpt-4-turbo | 78.6% |
| MemGPT* | gpt-4-turbo | 93.4% |
| Full-conversation | gpt-4-turbo | 94.4% |
| **Zep** | gpt-4-turbo | **94.8%** |
| Conversation Summaries | gpt-4o-mini | 88.0% |
| Full-conversation | gpt-4o-mini | 98.0% |
| **Zep** | gpt-4o-mini | **98.2%** |

> 표 1. Deep Memory Retrieval. *는 [3]에서 보고한 결과.

### 4.3 LongMemEval(LME)

Zep은 현실 business application의 LLM agent conversation·question을 나타내는 LongMemEvals dataset으로 평가했다. 평균 약 115,000 token인 conversation은 현 LLM·commercial memory solution에 큰 난점이다 [7]. 길이는 크지만 current frontier model context window 안에 있으므로 Zep 평가의 의미 있는 baseline을 만든다.

Dataset에는 single-session-user, single-session-assistant, single-session-preference, multi-session, knowledge-update, temporal-reasoning의 6 question type이 있다. 각 category의 분포는 균등하지 않으며 상세는 [7]을 참조한다. 모든 실험은 2024년 12월~2025년 1월에 수행했다. Boston, MA의 residential location에서 consumer laptop으로 AWS `us-west-2`에 host된 Zep service에 연결했다. 이 distributed architecture는 Zep 평가에 추가 network latency를 넣었지만 baseline 평가에는 없었다. 답 평가는 [7]의 question-specific prompt를 사용한 GPT-4o로 했으며 human evaluator와 높은 상관을 보였다.

#### 4.3.1 LongMemEval과 MemGPT

현 SOTA MemGPT [3]와 비교하려고 LongMemEval로 MemGPT 평가를 시도했다. Current MemGPT framework는 existing message history의 direct ingestion을 지원하지 않으므로 conversation message를 archival history에 추가하는 workaround를 구현했다. 그러나 이 방식으로 성공적인 question response를 만들지 못했다. 저자들은 다른 연구 team의 benchmark evaluation이 memory system 발전에 도움이 되기를 기대한다고 밝힌다.

#### 4.3.2 LongMemEval 결과

Zep은 두 model variant 모두에서 baseline보다 accuracy·latency가 크게 개선됐다. `gpt-4o-mini`는 baseline보다 accuracy가 15.2%, `gpt-4o`는 18.5% 높았다. 더 작은 prompt가 baseline 대비 latency·cost도 크게 낮췄다.

| Memory | Model | Score | Latency | Latency IQR | 평균 context tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| Full-context | gpt-4o-mini | 55.4% | 31.3 s | 8.76 s | 115k |
| **Zep** | gpt-4o-mini | **63.8%** | **3.20 s** | **1.31 s** | **1.6k** |
| Full-context | gpt-4o | 60.2% | 28.9 s | 6.01 s | 115k |
| **Zep** | gpt-4o | **71.2%** | **2.58 s** | **0.684 s** | **1.6k** |

> 표 2. LongMemEvals. Zep은 accuracy를 높이면서 context를 약 115k에서 1.6k token으로 줄이고 response time을 약 90% 단축한다.

Question type 분석에서 `gpt-4o-mini`+Zep은 6 category 중 4개에서 개선됐고, 특히 single-session-preference, multi-session, temporal-reasoning 같은 complex type에서 가장 크게 좋아졌다. `gpt-4o`에서는 knowledge-update도 개선되어 더 유능한 model에서의 효과를 보인다. 다만 능력이 낮은 model의 Zep temporal data 이해는 추가 개발이 필요할 수 있다.

| Question type | Model | Full-context | Zep | Delta |
| --- | --- | ---: | ---: | ---: |
| single-session-preference | gpt-4o-mini | 30.0% | 53.3% | +77.7% |
| single-session-assistant | gpt-4o-mini | 81.8% | 75.0% | -9.06% |
| temporal-reasoning | gpt-4o-mini | 36.5% | 54.1% | +48.2% |
| multi-session | gpt-4o-mini | 40.6% | 47.4% | +16.7% |
| knowledge-update | gpt-4o-mini | 76.9% | 74.4% | -3.36% |
| single-session-user | gpt-4o-mini | 81.4% | 92.9% | +14.1% |
| single-session-preference | gpt-4o | 20.0% | 56.7% | +184% |
| single-session-assistant | gpt-4o | 94.6% | 80.4% | -17.7% |
| temporal-reasoning | gpt-4o | 45.1% | 62.4% | +38.4% |
| multi-session | gpt-4o | 44.3% | 57.9% | +30.7% |
| knowledge-update | gpt-4o | 78.2% | 83.3% | +6.52% |
| single-session-user | gpt-4o | 81.4% | 92.9% | +14.1% |

> 표 3. LongMemEvals question type별 결과.

이 결과는 model scale 전반에서 Zep이 성능을 높일 수 있음을 보이며, 더 강한 model과 결합할 때 complex·nuanced question에서 개선이 가장 두드러진다. 높은 accuracy를 유지하면서 response time을 약 90% 줄인 latency 개선도 특히 주목할 만하다. 예외적으로 single-session-assistant question은 `gpt-4o`에서 17.7%, `gpt-4o-mini`에서 9.06% 낮아졌고, 추가 연구·engineering이 필요하다.

## 5. 결론

Zep은 semantic·episodic memory를 entity·community summary와 함께 통합하는 graph-based LLM memory approach다. 평가는 기존 memory benchmark에서 SOTA 성능을 내면서 token cost를 줄이고 훨씬 낮은 latency로 동작함을 보인다.

Graphiti·Zep의 결과는 graph-based memory system의 초기 진전일 가능성이 크다. 다른 GraphRAG approach의 Zep paradigm 통합과 새 확장이 뒤따를 수 있다. Fine-tuned model이 GraphRAG의 LLM entity·edge extraction accuracy를 높이고 cost·latency를 줄인다는 연구 [19, 25]는 Graphiti prompt용 model fine-tuning이 특히 complex conversation에서 knowledge extraction을 개선할 수 있음을 시사한다. LLM-generated KG 연구는 대체로 formal ontology 없이 수행됐지만 [9, 4, 17, 19, 26], domain-specific ontology는 큰 가능성이 있다. Pre-LLM KG work의 기초인 graph ontology는 Graphiti framework에서 더 연구할 가치가 있다.

저자들은 적절한 memory benchmark가 적고, 기존 benchmark가 simple needle-in-a-haystack fact-retrieval question에 치우쳐 robustness·complexity가 부족함을 지적한다 [3]. Customer experience task 같은 business application을 반영한 benchmark가 memory approach를 효과적으로 평가·구분하려면 더 필요하다. Existing benchmark는 Zep이 conversation history와 structured business data를 함께 process·synthesize하는 능력을 적절히 평가하지 못한다. Zep은 LLM memory에 집중하지만, traditional RAG capability도 [17], [27], [28]의 established benchmark와 비교해야 한다. LLM memory·RAG 문헌은 production scalability의 cost·latency를 충분히 다루지 않으며, 저자들은 LightRAG처럼 이 metric을 우선하는 retrieval latency benchmark를 포함해 이 공백을 다루기 시작했다.

## 6. 부록 — Graph Construction Prompt

### 6.1.1 Entity Extraction

```text
<PREVIOUS MESSAGES>
{previous_messages}
</PREVIOUS MESSAGES>
<CURRENT MESSAGE>
{current_message}
</CURRENT MESSAGE>
위 대화에서 CURRENT MESSAGE에 명시적 또는 암묵적으로 언급된 entity node를 추출하라.
지침:
1. speaker/actor를 항상 첫 node로 추출한다. speaker는 각 dialogue line에서 colon 앞 부분이다.
2. CURRENT MESSAGE에 언급된 다른 중요한 entity, concept, actor를 추출한다.
3. relationship이나 action의 node를 만들지 않는다.
4. date·time·year 같은 temporal information node를 만들지 않는다(나중에 edge에 넣는다).
5. full name을 사용해 node name을 가능한 한 명시적으로 쓴다.
6. PREVIOUS MESSAGES에만 언급된 entity는 추출하지 않는다.
```

### 6.1.2 Entity Resolution

```text
<PREVIOUS MESSAGES>{previous_messages}</PREVIOUS MESSAGES>
<CURRENT MESSAGE>{current_message}</CURRENT MESSAGE>
<EXISTING NODES>{existing_nodes}</EXISTING NODES>
EXISTING NODES, MESSAGE, PREVIOUS MESSAGES를 바탕으로 conversation에서 추출한 NEW NODE가 EXISTING NODES 중 하나와 duplicate entity인지 판단하라.
<NEW NODE>{new_node}</NEW NODE>
1. 같은 entity면 응답에 "is_duplicate: true", 아니면 "is_duplicate: false"를 반환한다.
2. true이면 existing node의 uuid도 반환한다.
3. true이면 가장 완전한 full name을 node name으로 반환한다.
지침: entity가 duplicate인지 이름과 summary 모두로 판단한다. duplicate node는 다른 이름일 수 있다.
```

### 6.1.3 Fact Extraction

```text
<PREVIOUS MESSAGES>{previous_messages}</PREVIOUS MESSAGES>
<CURRENT MESSAGE>{current_message}</CURRENT MESSAGE>
<ENTITIES>{entities}</ENTITIES>
위 MESSAGE와 ENTITIES를 바탕으로 CURRENT MESSAGE에서 listed ENTITIES에 관한 모든 fact를 추출하라.
1. 제공한 entity 사이의 fact만 추출한다.
2. 각 fact는 두 DISTINCT node 사이의 명확한 relationship이어야 한다.
3. relation_type은 LOVES, IS_FRIENDS_WITH, WORKS_FOR처럼 간결한 ALL-CAPS fact description이다.
4. 모든 관련 정보를 담은 더 자세한 fact를 제공한다.
5. 관련되면 relationship의 temporal aspect를 고려한다.
```

### 6.1.4 Fact Resolution

```text
<EXISTING EDGES>{existing_edges}</EXISTING EDGES>
<NEW EDGE>{new_edge}</NEW EDGE>
New Edge가 Existing Edges 중 어느 edge와 같은 fact를 나타내는지 판단하라.
1. 같은 factual information이면 "is_duplicate: true", 아니면 false를 반환한다.
2. true이면 existing edge uuid도 반환한다.
지침: fact가 완전히 동일할 필요는 없고 같은 정보를 표현하면 duplicate다.
```

### 6.1.5 Temporal Extraction

```text
<PREVIOUS MESSAGES>{previous_messages}</PREVIOUS MESSAGES>
<CURRENT MESSAGE>{current_message}</CURRENT MESSAGE>
<REFERENCE TIMESTAMP>{reference_timestamp}</REFERENCE TIMESTAMP>
<FACT>{fact}</FACT>
중요: 제공된 fact의 일부일 때만 time information을 추출한다. 그렇지 않으면 언급된 시간을 무시한다. relative time(예: 10 years ago, 2 mins ago)만 있으면 reference timestamp로 최선의 date를 정한다. 관계가 spanning nature가 아니어도 date를 정할 수 있으면 valid_at만 설정한다.
valid_at은 edge fact relationship이 참이 되거나 성립한 datetime, invalid_at은 참이 아니게 되거나 끝난 datetime이다.
대화를 분석해 edge fact의 일부인 date가 있는지 판단한다. relationship 형성·변경에 직접 관련된 date만 설정한다.
1. datetime은 ISO 8601(YYYY-MM-DDTHH:MM:SS.SSSSSSZ)이다.
2. valid_at·invalid_at 계산의 current time은 reference timestamp다.
3. fact가 present tense면 valid_at에 Reference Timestamp를 쓴다.
4. relationship을 성립·변경하는 temporal information이 없으면 field는 null이다.
5. 관련 event에서 date를 추론하지 말고 relationship을 직접 성립·변경한 date만 쓴다.
6. relationship과 직접 관련된 relative time은 reference timestamp로 실제 datetime을 계산한다.
7. 시간 없는 date만 있으면 00:00:00을 쓴다.
8. year만 있으면 그해 1월 1일 00:00:00을 쓴다.
9. time zone offset을 항상 넣는다(특정 time zone이 없으면 UTC Z).
```

## 참고문헌

원문 서지 정보는 제목·저자·연도·출판 정보를 보존했다.

1. Ashish Vaswani et al. 2023. *Attention Is All You Need.*
2. K. Sparck Jones. 1972. *A statistical interpretation of term specificity and its application in retrieval.* Journal of Documentation, 28(1):11–21.
3. Charles Packer et al. 2024. *MemGPT: Towards LLMs as operating systems.*
4. Darren Edge et al. 2024. *From local to global: A GraphRAG approach to query-focused summarization.*
5. Zep. 2024. *Zep: Long-term memory for AI agents.* <https://www.getzep.com>. AI application용 commercial memory layer.
6. Zep. 2024. *Graphiti: Temporal knowledge graphs for agentic applications.* <https://github.com/getzep/graphiti>. 시간에 따라 진화하는 entity 간 복잡한 relationship을 표현하는 dynamic, temporally-aware KG를 구축한다.
7. Di Wu, Hongwei Wang, Wenhao Yu, Yuwei Zhang, Kai-Wei Chang, and Dong Yu. 2024. *LongMemEval: Benchmarking chat assistants on long-term interactive memory.*
8. Wong Gonzalez and Daniela. 2018. *The relationship between semantic and episodic memory: Exploring the effect of semantic neighbourhood density on episodic memory.* PhD thesis, University of Windsor.
9. Petr Anokhin et al. 2024. *AriGraph: Learning knowledge graph world models with episodic memory for LLM agents.*
10. Xinyue Chen, Pengyu Gao, Jiangjiang Song, and Xiaoyang Tan. 2024. *HiQA: A hierarchical contextual augmentation RAG for multi-documents QA.*
11. Krish Goel and Mahek Chandak. 2024. *HiRO: Hierarchical information retrieval optimization.*
12. Noah Shinn et al. 2023. *Reflexion: Language agents with verbal reinforcement learning.*
13. Xiaojin Zhu and Zoubin Ghahramani. 2002. *Learning from labeled and unlabeled data with label propagation.*
14. V. A. Traag, L. Waltman, and N. J. van Eck. 2019. *From Louvain to Leiden: Guaranteeing well-connected communities.* Scientific Reports, 9:5233.
15. Neo4j. 2012. *Neo4j — the world's leading graph database.*
16. Apache Software Foundation. 2011. *Apache Lucene — scoring.*
17. Zirui Guo, Lianghao Xia, Yanhua Yu, Tu Ao, and Chao Huang. 2024. *LightRAG: Simple and fast retrieval-augmented generation.*
18. Jimmy Lin, Ronak Pradeep, Tommaso Teofili, and Jasper Xian. 2023. *Vector search with OpenAI embeddings: Lucene is all you need.*
19. Prafulla Kumar Choubey et al. 2024. *Distill-SynthKG: Distilling knowledge graph synthesis workflow for improved coverage and efficiency.*
20. Gordon V. Cormack, Charles L. A. Clarke, and Stefan Buettcher. 2009. *Reciprocal rank fusion outperforms Condorcet and individual rank learning methods.* SIGIR 2009, pp. 758–759.
21. Jaime Carbonell and Jade Goldstein. 1998. *The use of MMR, diversity-based reranking for reordering documents and producing summaries.* SIGIR 1998, pp. 335–336.
22. Jing Xu, Arthur Szlam, and Jason Weston. 2021. *Beyond Goldfish Memory: Long-term open-domain conversation.*
23. Chaofan Li, Zheng Liu, Shitao Xiao, and Yingxia Shao. 2023. *Making large language models a better foundation for dense retrieval.*
24. Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, and Zheng Liu. 2024. *BGE M3-Embedding: Multilingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation.*
25. Shreyas Pimpalgaonkar, Nolan Tremelling, and Owen Colegrove. 2024. *Triplex: A SOTA LLM for knowledge graph construction.*
26. Shilong Li et al. 2024. *GraphReader: Building graph-based agent to enhance long-context abilities of large language models.*
27. Pranab Islam, Anand Kannappan, Douwe Kiela, Rebecca Qian, Nino Scherrer, and Bertie Vidgen. 2023. *FinanceBench: A new benchmark for financial question answering.*
28. Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, and Iryna Gurevych. 2021. *BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models.*
