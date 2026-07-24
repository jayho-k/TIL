# 추출 Prompt와 Fact 정책: Mem0가 “기억할 사실”을 판단하는 방식

> 분석 대상: `mem0/configs/prompts.py`, `mem0/memory/main.py`, `mem0/memory/utils.py`, `mem0/llms/vllm.py`  
> 기준 snapshot: `mem0ai 2.0.12` (upstream commit 미확인)

## 결론

Mem0에는 대화 내용을 점수화하여 장기 기억 승격 여부를 판정하는 별도 결정 알고리즘이 없다. 기본 `infer=True`에서는 **매우 긴 LLM 추출 프롬프트가 사실 후보를 생성**하고, 그 뒤 구현이 JSON 파싱·MD5 정확 중복 제거·저장을 수행한다.

따라서 “무엇을 Mem0에 넣을지”의 기준은 세 층으로 나뉜다.

```text
1. 우리 서비스 정책: 이 대화/agent 결과를 Memory.add()에 보낼 것인가?
2. Mem0 extraction prompt: 보낸 내용 중 어떤 사실을 JSON memory[]로 뽑을 것인가?
3. Mem0 후처리: 형식이 맞고 hash가 중복되지 않는가?
```

첫 번째는 Mem0가 대신 결정하지 않는다. Research Agent의 원문과 중간 결과를 전부 `add()`에 보내지 않고, LangGraph/MemoryService가 durable fact·결정·정책만 선택해야 하는 이유다.

## 1. 실제 추출 호출 계약

`Memory._add_to_vector_store()`는 아래처럼 LLM을 한 번 호출한다.

```python
response = self.llm.generate_response(
    messages=[
        {"role": "system", "content": ADDITIVE_EXTRACTION_PROMPT},
        {"role": "user", "content": generated_prompt},
    ],
    response_format={"type": "json_object"},
)
```

이후 Mem0가 실제로 소비하는 구조는 다음뿐이다.

```json
{
  "memory": [
    {"text": "독립적으로 이해 가능한 사실", "attributed_to": "선택값"}
  ]
}
```

코드는 각 원소에서 `text`와 선택적인 `attributed_to`만 읽는다. prompt는 `id`와 `attributed_to`를 요구하지만 코드가 저장에 필수로 보는 값은 사실상 `text`뿐이다. `linked_memory_ids`는 현재 write path에서 소비하지 않는다.

## 2. 기본 prompt가 요구하는 fact의 성격

`mem0/configs/prompts.py`의 `ADDITIVE_EXTRACTION_PROMPT`(468행부터)는 추출기에게 다음을 강하게 지시한다.

| 지시 | 의도 |
| --- | --- |
| user와 assistant 메시지 모두에서 추출 | 사용자 사실뿐 아니라 추천·합의·계획도 기억 |
| 모든 memorable information을 가능한 넓게 추출 | recall 손실보다 약간의 중복을 덜 위험하게 봄 |
| 하나의 주제마다 독립 메모리 | career, 가족, 선호처럼 여러 차원 분리 |
| self-contained 문장 | 대명사를 `User`/이름으로 바꿔 나중에도 단독 이해 가능 |
| 15~80단어 중심의 풍부한 문맥 | 너무 원자적인 facts 대신 사유·전환·수치·고유명사 보존 |
| 상대 시간의 절대 날짜화 | observation date 기준으로 “지난주”를 장기적으로 해석 가능하게 만듦 |
| no fabrication / no implicit inference | 입력에 없는 성별·나이·원인을 추론하지 말 것 |
| 기존 메모리와 의미적으로 같은 사실은 생략 | LLM 수준의 semantic dedup 유도 |

이 프롬프트는 “간단한 사용자 선호 저장”보다 훨씬 공격적인 추출 정책이다. 특히 assistant가 조사해 준 정보, 문서·데이터 본문 속 사실도 기억하라고 한다. Research Agent 결과를 무제한으로 `add()`에 전달하면, 사용자 장기 기억 collection이 리서치 지식 조각으로 오염될 수 있다.

## 3. prompt에 실제로 공급되는 문맥

`generate_additive_extraction_prompt()`는 형식상 다음 섹션을 만든다.

```text
Summary
Last k Messages
Recently Extracted Memories
Existing Memories
New Messages
Observation Date
Current Date
Custom Instructions (있을 때만)
```

그러나 현재 `main.py` 호출은 `existing_memories`, `new_messages`, `last_k_messages`, `custom_instructions`만 전달한다.

| prompt 섹션 | 현재 library 코드가 주는 값 |
| --- | --- |
| Summary | 전달하지 않음 → 비어 있음 |
| Recently Extracted Memories | 전달하지 않음 → 비어 있음 |
| Last k Messages | SQLite scope별 최근 최대 10개 |
| Existing Memories | 새 대화와 dense 유사한 최대 10개 |
| New Messages | role을 붙여 합친 문자열 |
| Observation Date | OSS `add(timestamp=...)`가 값을 거부하므로 호출 시점의 UTC 날짜 |
| Current Date | 호출 시점의 UTC 날짜 |

따라서 prompt는 “최대 20개 최근 메시지” 등 더 큰 문맥을 설명하지만, 이 OSS 호출 경로가 실제로 제공하는 최근 메시지는 10개이며 Summary/Recently Extracted Memories는 사용하지 않는다. 게다가 `_format_conversation_history()`는 과거 메시지 content를 각각 300자로 자른다. 문서/프롬프트의 이상적 계약과 실제 전달값을 구분해야 한다.

과거 대화를 import하면서 “지난주”를 원래 대화 시점 기준으로 해석시키는 것도 기본 API만으로는 불가능하다. timestamp를 metadata에 넣는 것과 prompt observation date를 바꾸는 것은 별개다.

## 4. `custom_instructions`의 위치와 한계

추출 규칙은 두 방식으로 넣을 수 있다.

```python
Memory.from_config({"custom_instructions": "..."})
# 또는
memory.add(messages, user_id="...", prompt="...")
```

`_add_to_vector_store()`는 `prompt or self.custom_instructions`를 사용한다. 즉 `add()`의 `prompt`가 있으면 config의 기본 지침을 **대체**하며 둘을 합치지 않는다.

`custom_instructions`는 생성된 user prompt의 마지막 `## Custom Instructions` 섹션에 추가된다. 기본 prompt는 이를 “highest priority”라고 표현하지만, code-level schema 검증·허용 카테고리 enforcement가 추가되는 것은 아니다. 모델이 지침을 따르는 정도는 모델과 serving runtime의 품질에 달려 있다. 빈 문자열 `prompt=""`는 `prompt or self.custom_instructions` 때문에 명시적 override가 아니라 config 지침 fallback으로 동작한다.

우리 서비스에서는 다음처럼 역할을 제한하는 지침이 필요하다.

```text
사용자 또는 에이전트의 이후 행동을 바꿀 수 있는 확정 사실, 정책, 결정만 추출한다.
조사 원문, 장문 요약, 추정, 일시적 tool 출력, 근거 없는 주장, 일반 지식은 추출하지 않는다.
각 사실에는 가능한 경우 source_id와 문서 버전을 metadata로 연결한다.
```

다만 `source_id` 같은 **구조화 metadata는 prompt가 아니라 `add(..., metadata=...)` 인자로 공급**해야 한다. 기본 LLM 출력의 임의 필드를 payload로 자동 승격하지 않기 때문이다.

## 5. JSON 내구성과 Gemma 4 31B의 검증 지점

### 코드가 하는 보호

`main.py`는 `response_format={"type": "json_object"}`를 LLM provider에 전달한다. vLLM 어댑터(`mem0/llms/vllm.py`)는 이를 OpenAI-compatible `chat.completions.create()`에 그대로 전달한다. Ollama 어댑터는 이를 `format="json"` 및 “valid JSON only” 추가 문장으로 바꾼다. 이것은 **JSON Schema 요청이 아니라 JSON object 외형만 요구**하는 계약이다.

응답 뒤에는 다음 복구를 시도한다.

1. markdown code fence와 `<think>...</think>` 제거
2. `json.loads(..., strict=False)`
3. 실패하면 첫 `{`부터 마지막 `}`까지 잘라 재파싱

### 코드가 보장하지 않는 것

- JSON object라는 외형과 `memory: list[object]`, 각 object의 `text: string`이라는 **세부 schema**는 별도로 검증하지 않는다.
- JSON 자체 또는 root object 파싱 실패는 로그 후 빈 결과가 된다. 이 경우 “유효하게 추출할 사실 없음”과 호출자 반환이 같을 수 있다. 단, LLM API 호출 예외 자체는 `LLMError`로 전파된다.
- `{"memory": "abc"}` 또는 `{"memory": ["abc"]}`처럼 `memory`가 truthy이지만 item이 object가 아니면 parsing try를 지난 뒤 `.get()`에서 `AttributeError`가 날 수 있다. malformed schema가 항상 빈 결과로 안전하게 축소되는 것은 아니다.
- `attributed_to`, `id`, 알 수 없는 추가 key도 Pydantic/JSON Schema로 검증하지 않는다. `attributed_to`는 있을 때만 payload로 복사하고 나머지 key는 버린다.
- `mem0/memory/utils.py`에 legacy `normalize_facts()` helper가 있지만 현재 V3 `_add_to_vector_store()`는 이를 호출하지 않는다. 따라서 이 helper의 string/dict normalization을 현재 write path의 보호 기능으로 계산하면 안 된다.
- `response_format`을 vLLM server가 실제로 지원·강제하는지, Gemma 4 31B가 한국어와 긴 prompt에서 잘 지키는지는 소스만으로 결론낼 수 없다.

따라서 Gemma 4 31B PoC는 JSON parse 성공률뿐 아니라 `memory[].text` 형식 준수율, 빈 결과율, 허위 사실률, 사실 누락률을 분리 측정해야 한다.

## 6. V3에서 사용되지 않는 Prompt 계약: LLM memory linking과 dead code

기본 prompt는 새 memory object에 `linked_memory_ids`를 넣으라고 지시한다. 하지만 sync 경로를 추적하면 다음 문제가 있다.

1. `main.py` 891~894행은 기존 메모리를 `"0"`, `"1"` 같은 임시 ID로 바꾸며 `uuid_mapping`을 만든다.
2. 같은 함수 안에서 `uuid_mapping`은 이후 사용되지 않는다.
3. Phase 4에서 LLM 결과 object 중 읽는 값은 `text`, `attributed_to`뿐이다.
4. 주 메모리 payload에 LLM 출력의 `linked_memory_ids`는 저장되지 않는다.

여기서 소스 주석의 `anti-hallucination`은 LLM이 긴 UUID를 한 글자 틀리게 복사하거나 존재하지 않는 UUID를 만들어 내지 않도록, 기존 UUID를 짧은 허용 목록 ID로 바꾼다는 의미다. 완성된 설계라면 LLM이 `linked_memory_ids: ["1"]`을 반환했을 때 `uuid_mapping["1"]`로 실제 UUID를 검증·복원해야 한다. 현재는 이 복원 단계가 없다.

또한 system prompt는 Existing Memories의 ID가 UUID라고 설명하지만 실제 builder 입력은 `"0"`, `"1"`이다. 새 extraction의 `id`도 같은 순번 문자열을 쓰므로 기존-memory handle과 새-output ID가 같은 문자열 공간을 공유한다. 필드 위치로 구분할 수는 있지만, prompt 계약 자체는 실제 입력과 일치하지 않는다. 전체 데이터 변환 예시는 `02_V3_쓰기_파이프라인.md`의 Phase 1에 정리했다.

즉 이 snapshot의 prompt 예시가 의도한 “새 memory ↔ 기존 memory” 직접 링크는 sync/async V3 write path에서 구현되어 있지 않다. 현재 실제 연결은 Phase 7의 **엔티티 collection `linked_memory_ids`**로 형성된다. 이는 같은 엔티티를 공유하는 메모리 집합 연결이지, LLM이 명시한 narrative/contradiction link를 그대로 보존하는 기능은 아니다.

### 6.1 Upstream에서도 알려진 상태인가

2026-07-18 기준 공식 Mem0 GitHub에는 이 불일치를 정확히 다루는 Issue와 PR이 여러 개 있다.

| 항목 | 상태 | 제안 방향 |
| --- | --- | --- |
| [Issue #4970](https://github.com/mem0ai/mem0/issues/4970) | Open | Python/TypeScript가 무시하는 `linked_memory_ids`를 prompt에서 제거해 token·latency·모델 혼란을 줄이자고 제안 |
| [PR #4977](https://github.com/mem0ai/mem0/pull/4977) | Open, 미병합 | prompt의 Memory Linking 지시, 예제, 출력 field를 제거 |
| [PR #5084](https://github.com/mem0ai/mem0/pull/5084) | Open, 미병합 | LLM의 임시 ID를 `uuid_mapping`으로 실제 UUID로 복원해 main-memory payload에 저장 |
| [PR #5085](https://github.com/mem0ai/mem0/pull/5085) | Closed, 미병합 | 저장한 직접 링크로 optional 1-hop graph expansion을 하자는 기능 |
| [PR #5906](https://github.com/mem0ai/mem0/pull/5906) | Open, 미병합 | 사용되지 않는 `uuid_mapping` 자체를 제거 |

서로 반대되는 두 해결 방향이 제안된 상태다.

```text
[제거 방향]
LLM direct link는 V3 기능이 아니다
  → prompt의 linked_memory_ids 제거
  → uuid_mapping 제거
  → 현재 entity linking만 유지

[구현 방향]
LLM direct link도 graph signal로 사용한다
  → 임시 ID 검증·UUID 복원
  → main payload에 저장
  → search에서 link traversal/boost 구현
```

`#5084`는 저장까지만 제안하며, PR 본문도 retrieval에서 이 field를 읽지 않는다고 명시한다. 따라서 저장 patch 하나만 적용하면 검색 동작은 달라지지 않는다. 이를 실제 retrieval에 쓰려던 `#5085`는 프로젝트 측에서 V3가 vector 기반이고 `linked_memory_ids` graph expansion은 현재 적용 대상이 아니라는 이유로 닫았다.

여기서 “graph가 적용 대상이 아니다”는 Phase 7 entity collection도 없다는 뜻이 아니다. 현재 유지되는 구조는 다음과 같다.

```text
entity text
  → entity collection
  → 같은 entity에 연결된 main-memory UUID[]
  → 검색 시 entity boost
```

닫힌 방향은 LLM이 주장한 `새 memory → 기존 memory` 직접 edge를 저장하고 traversal하는 별도 graph expansion이다.

최신 `main` commit [`ddaa655`](https://github.com/mem0ai/mem0/commit/ddaa655edf41e3ed375b263fb227da0bcd42ccb9)에서도 다음 상태가 그대로 확인된다.

- sync/async 모두 `uuid_mapping`을 생성하지만 다시 읽지 않는다.
- Phase 4는 LLM object에서 `text`, 선택적 `attributed_to`만 소비한다.
- extraction prompt는 여전히 `linked_memory_ids`와 UUID 형식을 요구한다.
- 위 제거/저장 PR 중 어느 것도 `main`에 병합되지 않았다.

### 6.2 버그인가, 고칠 필요가 없는가

두 층으로 판단해야 한다.

1. **Prompt 계약과 비용 관점에서는 고칠 문제다.** 사용하지 않는 field를 모델에 출력시키고 실제 UUID라고 설명하면서 임시 ID를 전달한다. 출력 token, latency, JSON 형식 이탈, 가짜 link 생성 가능성만 늘리는 dead contract다.
2. **V3 핵심 검색 기능의 누락으로 보기는 어렵다.** 현재 공식 동작은 semantic/BM25/entity 기반 vector retrieval이다. LLM direct memory edge는 저장되지도, 검색에 사용되지도 않으며 이를 검색에 쓰려던 PR도 채택되지 않았다.

따라서 이 항목은 “공식 graph 기능이 고장 났다”가 아니라 **현재 V3 설계에 사용되지 않는 prompt/코드 흔적이 남아 있다**고 정리하는 것이 타당하다. Upstream 커뮤니티는 알고 있지만, 제거와 구현 중 최종 방향은 병합된 코드로 확정되지 않았다.

우리 PoC에서 LLM direct graph를 요구하지 않는다면 제거 방향이 단순하다.

- `ADDITIVE_EXTRACTION_PROMPT`의 `linked_memory_ids` 지시·예제·출력 field 제거
- sync/async의 `uuid_mapping` 제거
- Phase 7 entity linking은 그대로 유지
- 제거 전후 Gemma 4 31B의 output token, schema 준수율, extraction precision을 비교

반대로 변화·모순·후속 사건 같은 narrative edge가 필요하다면 `#5084` 수준의 저장만으로 부족하다. UUID allowlist 복원, payload 또는 PostgreSQL relation 저장, update/delete cleanup, retrieval traversal/boost, ACL·scope 검증까지 하나의 기능으로 설계해야 한다.

## 7. 한국어 출력은 기본 코드가 강제하지 않는다

prompt builder에는 `use_input_language=True`일 때 “입력과 같은 언어·문자로 응답”하라는 섹션을 붙이는 기능이 있다. 그러나 기본값은 `False`이고, 현재 `Memory._add_to_vector_store()`는 이 인자를 전달하지 않는다. 기본 system prompt와 예시는 영어 중심이므로 한국어 입력에서 영어 memory가 생성될 가능성이 있다.

따라서 우리 환경에서는 다음 중 하나가 필요하다.

1. `custom_instructions`에 “한국어 입력은 한국어 memory로 출력”을 명시한다.
2. wrapper/fork에서 `generate_additive_extraction_prompt(..., use_input_language=True)`를 노출한다.
3. 한국어 평가셋으로 언어 보존율을 측정한다.

## 8. `AGENT_CONTEXT_SUFFIX`: 누구에 관한 기억으로 쓸 것인가

### 8.1 왜 별도 suffix가 필요한가

기본 `ADDITIVE_EXTRACTION_PROMPT`는 개인 비서형 user memory를 전제로 한다. 같은 문장이라도 기본 prompt는 주로 사용자 선호·계획·경험으로 표현한다.

하지만 `agent_id`만 사용해 저장할 때는 “특정 사용자가 무엇을 좋아하는가”보다 다음과 같은 agent 자체의 기억이 필요할 수 있다.

- agent가 받은 운영 지침
- agent가 수행하거나 추천한 행동
- agent의 전문 영역과 역할
- agent가 사용자에게서 전달받은 지식

`AGENT_CONTEXT_SUFFIX`는 새로운 추출 알고리즘이나 별도 LLM이 아니다. 기존 system prompt 끝에 다음 관점 지시를 추가하는 짧은 문자열이다.

```text
이 memory의 중심 대상은 AI agent다.
- user가 말한 사실: “Agent was informed that ...”처럼 agent가 전달받은 지식으로 표현
- agent 행동: “Agent recommended ...”, “Agent specializes in ...”처럼 직접 표현
- agent 설정·지침: “Agent is configured to ...”로 표현
```

즉 scope ID를 payload에 넣는 기능과 memory 문장을 어떤 주어로 작성할지는 별개다. suffix는 후자인 **LLM이 생성할 `text`의 서술 관점**을 바꾼다.

### 8.2 동일 입력이 어떻게 달라지는가

다음 대화를 예로 든다.

```text
user: 앞으로 조사 결과에는 반드시 출처와 확인 날짜를 포함해.
assistant: 알겠습니다. 이후 조사 결과에 출처와 확인 날짜를 포함하겠습니다.
```

실제 출력은 모델에 따라 달라지지만 prompt가 유도하는 관점은 다음과 같다.

```json
// user-scoped 기본 prompt가 유도하는 형태
{
  "text": "사용자는 조사 결과에 출처와 확인 날짜가 포함되기를 원한다.",
  "attributed_to": "user"
}
```

```json
// agent-scoped suffix가 유도하는 형태
{
  "text": "Agent는 조사 결과에 출처와 확인 날짜를 반드시 포함하도록 지시받았다.",
  "attributed_to": "user"
}
```

`attributed_to`는 memory 문장의 주어가 아니라 **원래 정보의 출처 역할**이다. 두 번째 문장의 주어는 Agent지만 지시를 말한 주체가 user이므로 `attributed_to="user"`다. Agent가 스스로 “논문과 공식 문서를 우선 조사하겠다”고 제안한 사실이라면 memory text는 Agent 행동으로 쓰고 `attributed_to="assistant"`가 될 수 있다.

### 8.3 실제 분기 조건

sync와 async 모두 다음 조건을 직접 사용한다.

```python
is_agent_scoped = bool(filters.get("agent_id")) and not filters.get("user_id")

system_prompt = ADDITIVE_EXTRACTION_PROMPT
if is_agent_scoped:
    system_prompt += AGENT_CONTEXT_SUFFIX
```

scope 조합별 결과는 다음과 같다.

| 전달한 ID | suffix | 기본 서술 관점 | SQLite recent-message scope |
| --- | --- | --- | --- |
| `user_id` | 없음 | User 중심 | user 조합 |
| `agent_id` | 추가 | Agent 중심 | agent 조합 |
| `run_id` | 없음 | 기본 User 중심 prompt | run 조합 |
| `user_id + agent_id` | 없음 | User 중심 | user+agent 조합 |
| `agent_id + run_id` | 추가 | Agent 중심 | agent+run 조합 |
| `user_id + run_id` | 없음 | User 중심 | user+run 조합 |
| 세 ID 모두 | 없음 | User 중심 | user+agent+run 조합 |

핵심은 `agent_id`가 있다는 사실만으로 agent 관점이 되는 것이 아니라는 점이다. `user_id`가 하나라도 같이 있으면 suffix가 꺼진다. `run_id`는 이 관점 선택에 영향을 주지 않는다.

따라서 다음 두 호출은 같은 `agent_id`를 사용해도 다른 memory 문장을 만들 수 있다.

```python
# Agent 자체에 관한 지속 memory
memory.add(messages, agent_id="research-agent")
# → Agent는 출처와 확인 날짜를 포함하도록 지시받았다.

# 특정 user와 agent 조합의 user memory
memory.add(messages, user_id="alice", agent_id="research-agent")
# → 사용자는 조사 결과에 출처와 확인 날짜가 포함되기를 원한다.
```

ID 조합은 서술 관점뿐 아니라 Phase 0의 `session_scope`, Phase 1 기존-memory filter, 새 payload의 scope에도 들어간다. user-only와 user+agent는 서로 다른 최근 대화 window와 dedup context를 사용한다. 호출마다 ID 조합을 바꾸면 같은 대화를 이어 가도 `Last k Messages`가 끊길 수 있다.

### 8.4 사용되지 않는 helper가 혼란을 만드는 이유

클래스에는 다음 helper도 정의돼 있다.

```python
def _should_use_agent_memory_extraction(self, messages, metadata):
    has_agent_id = metadata.get("agent_id") is not None
    has_assistant_messages = any(msg.get("role") == "assistant" for msg in messages)
    return has_agent_id and has_assistant_messages
```

이 helper만 읽으면 “agent_id가 있고 assistant message가 있을 때 agent memory를 사용한다”고 이해하게 된다. 그러나 현재 V3 add path는 이 함수를 호출하지 않는다. 실제 동작은 message role과 무관하게 `agent_id 존재 AND user_id 부재`만 본다.

따라서 다음처럼 helper의 설명과 반대되는 결과도 가능하다.

| 입력 | helper라면 | 실제 V3 분기 |
| --- | --- | --- |
| `agent_id`만 있고 user message만 있음 | agent mode 아님 | suffix 추가 |
| `user_id + agent_id`이고 assistant message 있음 | agent mode | suffix 미추가 |

이 helper는 현재 동작 근거가 아니라 사용되지 않는 과거/대안 설계 흔적으로 취급해야 한다.

### 8.5 우리 scope 사용 원칙

| 저장하려는 기억 | 권장 scope | 기대 관점 |
| --- | --- | --- |
| 여러 사용자에 공통인 Research Agent 운영 정책·능력 | `agent_id` | Agent 중심 |
| Alice의 선호·제약 | `user_id` | User 중심 |
| Alice에게만 적용되는 특정 agent의 개인화 기억 | `user_id + agent_id` | User 중심, agent별 scope |
| 한 run에서만 필요한 임시 조사 상태 | 우선 LangGraph state/PostgreSQL | Mem0 장기 사실로 승격하지 않는 것이 기본 |
| 불가피하게 run memory를 Mem0에 저장 | 목적에 따라 `agent_id + run_id` 또는 custom instructions | 기본 관점이 의도와 맞는지 별도 검증 |

`run_id`만 사용하면 suffix가 없으므로 기본 User 관점 prompt가 적용된다. 입력이 agent 작업 로그라면 “User가 조사했다”처럼 잘못 귀속될 가능성이 있다. run-scoped agent memory가 필요하면 `agent_id`도 함께 주거나 custom instructions로 주어와 attribution 규칙을 명시해야 한다.

## 9. 우리 시스템의 권장 판단 흐름

```text
Research Agent 결과
  → LangGraph 노드가 결과 종류·신뢰도·출처·현재성 평가
  ├─ 원문/첨부: MinIO
  ├─ 최신 요약·상태·버전·ACL: PostgreSQL
  ├─ 재사용 durable fact/정책/결정: custom_instructions + metadata와 함께 Mem0.add()
  └─ 불확실/일시적/중간 tool 출력: 저장하지 않음 또는 run-scoped 단기 상태
```

이렇게 해야 Mem0의 강점인 fact extraction을 활용하면서도, 기본 prompt의 광범위한 추출 정책이 시스템 장기 기억을 과도하게 넓히는 문제를 제어할 수 있다.
