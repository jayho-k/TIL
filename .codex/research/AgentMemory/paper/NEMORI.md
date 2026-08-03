# NEMORI

코드: <https://github.com/nemori-ai/nemori>

- 주제 : 뭘 냅둘건가? > 모두 저장할 순 없기에
- 일단은 방법론이다. 이걸 그대로 적용하기에는 무리가 있어 보이나, 아이디어는 가지고 있는편이 좋을 듯하다.

## 초록

- 기존 방법 :  중요도 점수, 감정 태그, 사실 템플릿처럼 미리 정한 휴리스틱에 의존 (설계자 직관)
- Episodic Memory Integration : 일관된 서사로 변경
- Semantic Knowledge Distillation : 예측 오차로 통찰을 추출



## 내용

> 1. 메모리 구성에서 증류(Distillation )와 관리(Management)를 구분 > 일반 데이터 성질·인지 아이디어에서 증류 설계를 위한 prior를 이끈다.
> 2. 관리(Management) 방식
> 3. 긴 컨텍스트에서 특히 두드러지는 성능을 실험으로 보인다. 타사 관리 시스템과 결합하면 성능을 유지하며 A-MEM·MemoryOS의 **저장량**을 45~54% 줄인다.

- 타사 메모리 시스템을 보완하는 증류층으로 사용가능
- 그러니 Memory Layer 앞단에 사용하는 용도로 보임



### Nemori

- Integrity of Episode: 잠재적 완결성을 존중하는 episode를 정의해야 하며 휴리스틱 chunking을 강제해서는 안 된다.
- Asymmetry of Perspective : 메모리는 회상을 위해 존재하는 것. 그리고 회상은 사건의 재구성이자 추론의 한 형태다. 따라서 원시 에피소드에서 중요한 세부적인 부분을 보존하면서 논리 구조를 부각하도록 변경해야한다.
- Predictability Implies Redundancy : 예상 밖 정보는 메모리 consolidation의 자연스러운 후보. 실제 상호작용과 기존 지식에서 만든 anticipatory schema의 의미 차이를 검사해 메모리를 증류한다. (미리 예측한다는 것인데 확인을 좀 더 해보는 편이 좋을 거 같음)



### Episodic Memory Integration

>  episodic memory로 통합하고 이후 증류를 준비
>
> - Local Message Partitioning
> - Narrative Episode Generation
> - Associative Memory Integration

**Local Message Partitioning**

- 시간으로 관리
- 아래는 codex한테 해당 내용 예시를 알려달라고 요청한 답변

```
  에이전트는 사용자·도구·다른 에이전트와 주고받는 메시지를 순서대로 임시 보
  관합니다.

  - 메시지 하나: m_i = (누가 보냈는지, 내용, 시간)
  - 버퍼 B: 최근 메시지를 잠시 쌓아 두는 대기열
  - w: 한 번에 묶어 분석할 메시지 수

  예를 들어 w = 6이면 최근 메시지 6개가 버퍼에 쌓일 때까지 기다립니다.

  1. 사용자: 다음 주 부산 여행을 계획해 줘.
  2. 에이전트: 예산은 어느 정도인가요?
  3. 사용자: 숙소 포함 50만 원 이하야.
  4. 에이전트: 이동 수단 선호가 있나요?
  5. 사용자: KTX를 이용하고 싶어.
  6. 에이전트: 알겠습니다. 일정과 숙소를 찾아볼게요.

  메시지가 6개 쌓이면 LLM은 단순히 “6개를 한 덩어리로 저장”하지 않습니다. 대
  화의 맥락을 보고 자연스러운 사건 단위, 즉 episode로 나눕니다.

  episode 1: 부산 여행 계획 요청
  - 여행지: 부산
  - 예산: 숙소 포함 50만 원 이하
  - 이동 수단: KTX

  episode 2: 일정·숙소 탐색 준비
  - 에이전트가 필요한 조건을 모두 수집함
  - 다음 행동: 일정과 숙소 제안

  여기서 “잠재적 완결성”은 하나의 대화 주제가 충분히 마무리됐는지를 뜻합니
  다. 예를 들어 여행 조건을 모두 확인했다면 하나의 episode가 될 수 있습니다.
  “국소 뉘앙스”는 바로 앞뒤 메시지 사이의 미묘한 연결입니다. “50만 원 이
  하”는 단독으로 보면 무엇의 예산인지 모르지만, 바로 앞의 부산 여행 메시지와
  붙여야 의미가 분명해집니다.

  수식은 아래 정도로 읽으면 됩니다.

  O ← LLM에게 (분할 지시문 + 현재 버퍼)를 넣어 얻은 결과

  - P_par: “대화를 의미 있는 사건 단위로 나눠라”라는 LLM 지시문
  - B_t: 현재 버퍼에 쌓인 메시지
  - ⊕: 둘을 이어 붙여 LLM 입력으로 만든다는 뜻
  - O: “몇 번째 메시지부터 몇 번째 메시지까지가 하나의 사건인지”에 대한 분할
    결과
```





**Narrative Episode Generation**
$$
(N_j,c_j)\leftarrow f_{LLM}(P_{nar}\oplus P_j),\qquad v_j\leftarrow f_{emb}(c_j\oplus N_j).
$$

- 지시문(P_nar) : 등장인물, 목표, 제약 조건, 결과 등 대화의 논리 구조를 중심으로 사건을 정리하라는 지시문
- 총 4개 요소를 보관
  - P_j : 원본 메시지 묶음
  - N_j : 서술형 요약
  - c_j : 짧은 검색 키워드
  - v_j : c_j, N_j를 숫자 벡터로 바꾼 검색 인덱스
- 현재 4개의 요소를 전부 넣음. 하지만 짧은 검색 키워드도 같이 포함해서 저장하는게 좋을 거 같음
- 왜냐하면 PoC 도중에 해당 내용이 있지만 검색을 못해오는 경우가 있었음 (내용은 맞는데 해당 키워드가 검색이 안되어서 그랬던 것으로 보임)

- narrative episode : 대화에서 무슨 일이 있었는지 정리한 사건 서술
- episodic cue : 나중에 이 사건을 찾기 위한 짧은 검색용 핵심 문구



**Associative Memory Integration**

- 끊어져 있는 메모리를 하나의 사건이라면 하나의 사건으로 통합
- 해당 부분은 무슨 말인지 알겠으나, 이렇게 되면 너무 느려질거 같은데... >> 이부분을 scheduling(+batch)으로 성찰할 때 진행하면 되지 않을까 싶음
- 과정 
  - 새로 생성된 메모리의 벡터 값을 사용
  - 기존 episodic database에서 top k 값 뽑음
  - LLM이 새 메모리와 후보 메모리가 정말 같은 사건의 연속인지 판단
  - 연속이면 합치고, 아니면 새 메모리로 저장

```
- cue: 검색용 핵심 단서
- narrative: 사건의 서술형 요약
- raw sequence: 원본 메시지 순서
- embedding: 통합된 사건을 나타내는 새 검색 벡터
```



### Semantic Knowledge Distillation

> episodic experience에서 semantic knowledge를 뽑는 부분
>
> - Anticipatory Schema Synthesis
> -  Prediction Error Distillation
> - Agnostic Knowledge Consolidation

```
이미 아는 정보 꺼내기
→ 이번 사건을 미리 추측하기
→ 실제와 비교해 새롭거나 바뀐 사실만 추출하기
→ 기존 지식에 추가·병합·갱신하기
```

**Anticipatory Schema Synthesis**

- 새 episode를 받았을 때, 먼저 현재 메모리 시스템이 이미 알고 있는 관련 정보를 가져온다.
- 새 episode와 의미적으로 비슷하면서 일정 유사도 임계값을 넘는 기존 semantic memory를 가져온다. 
- 새 episode의 짧은 단서·제목 + 이전부터 알고 있던 관련 지식 >> 이 두 정보로 실제 대화 내용을 추측한다. LLM(예측 지시문 + episode 단서 + 기존 지식)
- 이 예상 결과를 anticipatory schema 라고 한다.

 **Prediction Error Distillation**

-  실제 episode와 방금 만든 예측을 비교
- K_in : LLM(증류 지시문 + 실제 원문 episode + 사전 예측)
  - 실제 대화에는 있지만 예측에 없던 사실
  - 예측과 다르게 표현되었거나 틀린 사실
  - 시간이 지나도 유지될 가능성이 높은 구체적 정보
  - 이후 상호작용에 유용한 정보
- 위와 같은 정보를 K_in으로 추출하게 된다

**Agnostic Knowledge Consolidation**

- 실제 메모리 서비스 부분에 해당한다고 보면 된다. (NEMORI는 이부분이 구현되어있지 )
- 추출한 insight를 실제 메모리 시스템에 반영
- LLM이 관계를 세 가지 중 하나로 판정
  - new > 완전 새로 저장
  - merge > 통합
  - conflict > 교체



## 결론

- 가장 정확도가 높은 Full Context보다 좋은 기억력을 가지고 있음
- 하지만 multi hop은 여전히 Full Context가 높음
- NEMORI가 LLM 호출 횟수와 입출력이 낮아 토큰을 압도적(?)으로 덜 쓴다.
- top k : 10 까지는 빠르게 좋아짐 > 10이후부터는 큰 차이 없는듯
- 첫째, NEMORI는 증류에 초점을 맞추며 management·retrieval은 단순 전략을 채택하므로 더 정교한 memory reasoning이 필요한 과업에서 병목이 될 수 있다. 둘째, interface는 현재 개념적이며 표준 protocol이 없어 구체 통합은 case-by-case 구현을 요구한다.





**표 7. 타사 management 비교.** P=raw message, K=NEMORI distilled semantic knowledge, Core=Temporal을 제외한 가중 평균이다.

| 모델 / 시스템           | 입력 | LLM score | Average | Core | MemTokens |
| ----------------------- | ---- | --------: | ------: | ---: | --------: |
| gpt-4o-mini / A-MEM     | P    |      52.5 |    52.5 | 52.6 |      397K |
|                         | K    |      50.9 |    50.9 | 55.8 |  **142K** |
| gpt-4o-mini / MemoryOS  | P    |      54.6 |    54.6 | 59.2 |      405K |
|                         | K    |      54.0 |    54.0 | 60.3 |  **190K** |
| gpt-4.1-mini / A-MEM    | P    |      61.4 |    61.4 | 60.4 |      498K |
|                         | K    |      59.0 |    59.0 | 64.1 |  **243K** |
| gpt-4.1-mini / MemoryOS | P    |      60.7 |    60.7 | 66.9 |      354K |
|                         | K    |      61.4 |    61.4 | 69.2 |  **194K** |



## 부록



### 알고리즘 1. NEMORI 메모리 증류

```
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
```

### 알고리즘 2. NEMORI 응답 생성

```
**요구:** 질의 $Q$, episodic database $D_e$, semantic database $D_s$  
**보장:** 응답 $a$

1. $v_Q\leftarrow f_{emb}(Q)$를 계산한다.
2. $R'_e\leftarrow Search(D_e,v_Q,k)$를 검색하고 $R_e=\{N_i\}_{i=1}^k$, $R_p=\{P_d\}_{d=1}^r$를 추출한다.
3. $R'_s\leftarrow Search(D_s,v_Q,m)$를 검색하고 $R_s=\{s_j\}_{j=1}^m$를 추출한다.
4. $a\leftarrow f_{LLM}(P_{ans}\oplus Q\oplus R_e\oplus R_p\oplus R_s)$를 생성한다.
5. $a$를 반환한다.
```



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

## 

