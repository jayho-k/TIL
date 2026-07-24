# Gemma 4 31B 기반 Mem0 PoC 기준

> 목적: Gemma 4 31B가 Mem0 V3의 사실 추출·JSON 출력·한국어 recall에 운영 가능한 품질을 내는지 검증한다.  
> 코드 근거: `mem0/memory/main.py`, `mem0/configs/prompts.py`, `mem0/llms/vllm.py`  
> 기준 snapshot: `mem0ai 2.0.12` (upstream commit 미확인)  
> 외부 문서 확인일: `2026-07-18`  
> 모델/serving 참고: [Google Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4), [Gemma 4 function calling](https://ai.google.dev/gemma/docs/capabilities/text/function-calling-gemma4), [vLLM OpenAI-compatible server](https://docs.vllm.ai/en/v0.18.1/serving/openai_compatible_server/)

## 결론

Gemma 4 31B는 공식 model card상 native function calling과 다국어·장문 context를 지원하고, 현재 vLLM 문서는 OpenAI-compatible `json_object`/`json_schema` response format을 제공한다. 하지만 **모델의 function calling 지원 + serving API의 JSON mode**가 Mem0의 `memory[].text` schema와 한국어 extraction 품질을 보장하지는 않는다. Mem0의 기본 extraction prompt는 길고, assistant message·문서 내용까지 폭넓게 추출하며, 일부 JSON 파싱 실패는 빈 결과로 바뀐다.

따라서 PoC는 “응답이 나온다”가 아니라 아래 네 축을 수치화해야 한다.

```text
형식 안정성(JSON/schema) + 추출 품질(precision/recall) + 기억 안전성(오염/중복/모순) + 운영성(latency/오류)
```

## 1. 검증 대상 코드 계약

Mem0 V3 write path는 vLLM provider에 다음 요구를 보낸다.

```python
response_format={"type": "json_object"}
```

`mem0/llms/vllm.py`는 이 값을 OpenAI-compatible `chat.completions.create()`에 그대로 전달한다. 따라서 vLLM deployment가 이 JSON-object 요청을 실제 지원/강제하는지 먼저 확인해야 한다.

Mem0가 기대하는 최소 응답은 다음이다.

```json
{
  "memory": [
    {"text": "독립적으로 이해 가능한 사실"}
  ]
}
```

JSON object이더라도 `memory`가 없거나 item에 문자열 `text`가 없으면 저장 가능한 fact가 없다. 이 세부 schema는 source 코드에서 엄격히 검증하지 않으므로 테스트 harness가 별도로 검사해야 한다. `{"memory":"abc"}`나 string item 배열은 후속 `.get()`에서 예외를 낼 수도 있어 malformed response를 “빈 결과” 하나로만 테스트하면 부족하다.

또한 prompt builder의 같은-언어 출력 옵션은 기본값이 `False`이고 현재 `main.py`가 켜지 않는다. 한국어 입력이 한국어 memory로 남는지는 모델 자체 능력과 별도로 custom instruction 또는 wrapper 수정으로 보장해야 한다.

## 2. 단계별 PoC

### Phase A — serving 및 JSON contract

목표: Mem0를 거치기 전 Gemma 4 31B + vLLM 조합이 structured response를 안정적으로 반환하는지 확인한다.

| 테스트 | 입력 | 측정 |
| --- | --- | --- |
| 단순 JSON | 짧은 한국어 대화 100건 | JSON parse 성공률 |
| Mem0 실제 prompt | `ADDITIVE_EXTRACTION_PROMPT` 포함 | `memory` key 존재율, list 타입 비율 |
| 긴 입력 | 기존 메모리 10개 + 최근 메시지 10개 + 새 대화 | truncate/timeout/형식 이탈률 |
| 난해한 출력 유도 | markdown, 인용, code fence, empty response | Mem0 fallback 후 저장 결과 |
| schema 변형 | `memory` 누락/string/dict, item string, `text` 비문자열 | 빈 결과·예외·오저장 유형 분리 |
| 언어 보존 | 동일한 한국어/영어 facts | 출력 언어 일치율, 고유명사 보존율 |

통과 예시: JSON parse 성공률 99% 이상, `memory: list` schema 준수율 99% 이상. 이 수치는 초기 목표이며, 실제 운영 SLA와 비용을 보고 조정한다.

### Phase B — 한국어 fact extraction 품질

목표: 장기 기억에 넣을 가치가 있는 사실을 정확하게 뽑되, 불필요한 내용을 넣지 않는지 측정한다.

평가셋에는 최소 다음 유형을 넣는다.

| 유형 | 예시 확인점 |
| --- | --- |
| 사용자 선호 | “매운 음식은 싫고 채식 메뉴를 선호”를 하나 또는 적절한 facts로 |
| 날짜/시간 | “다음 주 화요일”을 관찰일 기준 날짜로 해석하는지 |
| 과거 transcript import | OSS `timestamp`가 거부되므로 절대 날짜 전처리 없을 때의 오해석률 |
| 대명사·문맥 | 이전 10개 메시지를 이용해 “그 프로젝트”를 올바르게 해석하는지 |
| bulk 대화 입력 | 한 호출에 10개 초과 메시지를 넣었을 때 SQLite에 의도한 마지막 10개와 순서가 남는지 |
| 여러 주제 | 한 turn의 경력·가족·일정이 모두 분리되는지 |
| assistant 신규 정보 | 사용자가 말하지 않은 추천/합의만 적절하게 저장하는지 |
| assistant echo | 사용자 말을 assistant가 반복한 것을 중복 저장하지 않는지 |
| 부정/변경 | “더는 X를 선호하지 않는다”, “A에서 B로 바꿨다”를 정확히 보존하는지 |
| 문서/조사 내용 | custom instruction으로 원문 사실 저장을 막을 때 잘 따르는지 |
| 빈 대화 | 인사·감사만 있을 때 빈 `memory`를 반환하는지 |

측정값은 단순 정확도 하나가 아니라 다음처럼 나눈다.

```text
fact precision = 저장된 사실 중 정답인 비율
fact recall    = 정답 사실 중 추출된 비율
false-memory rate = 저장하면 안 되는 사실이 들어간 대화 비율
temporal error rate = 날짜/기간 해석 오류 비율
```

초기 운영 권고 기준은 precision을 recall보다 우선한다. 장기 기억 오염은 나중에 검색·행동 전반에 남지만, 누락된 사실은 다시 질문하거나 PostgreSQL/MinIO 근거에서 회복할 수 있기 때문이다. 이 방향은 Mem0 기본 prompt의 “when in doubt, extract”와 다를 수 있으므로 `custom_instructions`로 보정해야 한다.

#### Scope 조합에 따른 memory 서술 관점

동일한 메시지를 다음 scope 조합으로 반복 입력해 `AGENT_CONTEXT_SUFFIX`의 영향을 분리 측정한다. 각 case는 서로 다른 실험용 ID와 collection을 사용하여 이전 memory가 결과에 섞이지 않게 한다.

```text
user: 앞으로 조사 결과에는 반드시 출처와 확인 날짜를 포함해.
assistant: 알겠습니다. 이후 조사 결과에 출처와 확인 날짜를 포함하겠습니다.
```

| Case | scope | 실제 suffix | 기대하는 주요 관점 |
| --- | --- | --- | --- |
| S1 | `user_id` | 없음 | “사용자는 ... 원한다” |
| S2 | `agent_id` | 추가 | “Agent는 ... 지시받았다” |
| S3 | `user_id + agent_id` | 없음 | User 중심, agent별 개인화 scope |
| S4 | `agent_id + run_id` | 추가 | Agent 중심 run memory |
| S5 | `run_id` | 없음 | 기본 prompt가 User로 오귀속하는지 확인 |
| S6 | `user_id + agent_id + run_id` | 없음 | User 중심 session memory |

message role이 실제 분기 조건이 아니라는 점도 별도 검증한다.

| Case | scope/messages | 확인할 실제 동작 |
| --- | --- | --- |
| R1 | `agent_id`, user message만 | assistant message가 없어도 suffix가 붙음 |
| R2 | `user_id + agent_id`, user+assistant messages | assistant message가 있어도 suffix가 붙지 않음 |

각 결과에서 다음 값을 평가한다.

- memory text의 주어가 User/Agent 중 의도한 대상인지
- `attributed_to`가 문장의 주어가 아니라 원래 발화 source를 가리키는지
- 동일 사실이 scope별로 의미가 달라지거나 과장되지 않는지
- user-only, agent-only, user+agent 호출 사이에서 `Last k Messages`와 기존-memory dedup context가 의도대로 분리되는지
- 실제 서비스가 사용할 고정 scope 정책을 적용했을 때 잘못된 귀속률

통과 기준은 scope별 문장 표현이 완전히 동일한지가 아니라, **기억의 주체와 정보 출처가 혼동되지 않는 것**이다. PoC 결과를 바탕으로 `agent_id` only에는 기본 suffix를 유지할지, 우리 한국어 `custom_instructions`로 Agent/User 서술 규칙을 명시적으로 교체할지 결정한다.

### Phase C — memory lifecycle 및 retrieval

목표: 추출 결과가 실제 Qdrant 저장과 이후 search에서 원하는 행동을 만드는지 본다.

1. 같은 표현을 두 번 넣어 MD5 duplicate가 억제되는지 확인한다.
2. 의미는 같지만 문장이 다른 중복과 모순 사실이 둘 다 쌓이는지 확인한다.
3. PostgreSQL current state 변경 뒤 Mem0 `update()`/`delete()` flow를 테스트한다.
4. semantic-only, BM25 on, entity boost on, reranker on/off를 같은 질의 집합으로 비교한다.
5. `explain=True`의 `score_details`를 저장해 score 변화 이유를 검토한다.
6. `add()`가 반환한 모든 ID를 즉시 `get()`하여 실제 Qdrant 저장 여부를 확인한다.
7. 100개가 넘는 scope에서 `delete_all()` 후 잔존 Qdrant point와 history/messages를 확인한다. stock SQLite baseline과 PostgreSQL adapter를 각각 검증한다.

특히 한국어에서는 현재 코드가 `en_core_web_sm`에 의존하므로 BM25 lemma와 entity boost가 개선이 아니라 노이즈가 될 수 있다. 다만 Mem0 public API에는 두 신호를 독립적으로 끄는 flag가 없다. dependency/collection이 다른 실험 환경을 분리하거나 MemoryService/fork에 feature gate를 먼저 추가해야 한다. `rerank`만 request별 flag가 있다.

### Phase D — 운영성

| 항목 | 측정 방법 |
| --- | --- |
| add latency | context retrieval, LLM extraction, embedding, Qdrant insert를 구간별 측정 |
| search latency | semantic/BM25/entity/rerank를 조합별 측정 |
| GPU/메모리 | Gemma 4 31B serving 시 동시 요청별 VRAM/RAM/queue 길이 |
| 오류 처리 | timeout, 429/5xx, malformed JSON, Qdrant batch·개별 insert 장애, history/message store 실패 주입 |
| DB adapter | 여러 worker의 같은 scope 문맥 공유, 재시작 후 보존, 순서·retention, scope별 삭제, connection pool 포화 측정 |
| 비용/처리량 | turn당 token, fact 수, QPS별 p50/p95/p99 |

Mem0 source는 LLM API 예외를 `LLMError`로 전파한다. 반면 많은 JSON parse 오류는 빈 추출 결과로 처리하고, schema type 오류 일부는 후속 예외가 된다. Mem0 public 반환은 raw LLM response나 parse-failure reason을 제공하지 않는다. 따라서 `LLMError`, parse failure, schema failure, valid empty extraction을 분리하려면 provider wrapper/log hook 또는 소스 instrumentation이 필요하다.

Qdrant batch 실패 뒤 일부 개별 insert도 실패하는 경우, 현재 코드는 실패 ID를 ADD 결과에서 제거하지 않는다. 반대로 마지막 `save_messages()` 실패는 이미 저장된 memory가 있어도 호출을 실패로 보이게 한다. fault injection에서는 API 응답만 보지 말고 Qdrant·history store·entity 실제 상태를 함께 비교한다. PostgreSQL adapter 적용 후에도 Qdrant와 PostgreSQL은 하나의 transaction이 아니므로 부분 성공 복구 시험은 그대로 필요하다.

## 3. `custom_instructions` 초기안

기본 prompt는 폭넓은 추출을 유도하므로, 우리 연구 agent용으로 아래 방향의 지침을 먼저 실험한다.

```text
다음 조건을 모두 만족하는 정보만 memory에 넣어라.
1. 사용자 또는 agent의 이후 의사결정·행동에 반복적으로 재사용된다.
2. 입력에 명시된 확정 사실, 정책, 결정, 선호, 제약이다.
3. 원문 전체, 긴 요약, tool의 일시적 출력, 일반 지식, 추측, 불확실한 가설은 제외한다.
4. 사실이 변경되었음을 말할 때는 이전 상태와 새 상태를 함께 보존한다.
5. 출력은 {"memory": [{"text": "..."}]} JSON만 사용한다.
```

이 지침은 초안이다. 평가셋에서 false-memory와 fact recall을 본 뒤, 도메인별 few-shot 예시를 추가해 다듬는다. `add(prompt=...)`가 config의 `custom_instructions`를 대체하므로, 공통 지침을 잃지 않도록 최종 prompt 조립 책임을 MemoryService에 둘지 결정해야 한다.

## 4. 최소 실험 결과 레코드

각 test case는 PostgreSQL 또는 실험용 CSV/JSONL에 아래를 남긴다.

```text
case_id, input_type, model/version, serving_config,
prompt_version, expected_facts, raw_llm_response,
json_valid, extracted_facts, precision, recall,
memory_ids, search_queries, retrieval_metrics,
latency_ms, error_type
```

`raw_llm_response`는 Mem0 기본 반환에서 얻을 수 없으므로 instrumented provider/wrapper가 capture한다. 원문과 대형 prompt/response artifact는 MinIO에 두고, 이 레코드에는 object key와 hash를 연결한다. 그러면 prompt/model 변경 전후를 재현하고 비교할 수 있다.

## 5. PoC 종료 판단

다음 네 질문에 근거 데이터가 생기면 첫 PoC를 종료할 수 있다.

1. Gemma 4 31B + 현재 vLLM이 Mem0의 JSON contract를 안정적으로 충족하는가?
2. 한국어 durable fact에서 우리 custom instruction이 허위/불필요 기억을 충분히 낮추는가?
3. hybrid signal이 semantic-only보다 실제 retrieval 품질을 높이는가?
4. latency·GPU 자원·실패율이 target traffic에서 허용 가능한가?

하나라도 부정적이면 Mem0 전체를 바로 포기할 문제가 아니라, model serving, prompt, wrapper feature gate(BM25/entity), public rerank flag, MemoryService 승격 기준 중 어느 계층을 조정할지 판별하는 근거가 된다.
