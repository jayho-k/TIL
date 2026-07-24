# Hermes MemoryManager 코드 분석

조사일: 2026-07-11

## 대상 파일

- `.codex/research/AgentMemory/hermes_memory_manager.py`
- 파일 성격: Hermes Agent의 memory provider orchestration layer

## 한 줄 요약

`MemoryManager`는 memory를 직접 저장/검색하는 구현체가 아니라, built-in provider와 외부 memory provider를 agent runtime에 연결하는 조정자다. 핵심 역할은 provider 등록, tool schema 주입, prefetch/retrieval, turn sync, session boundary 처리, built-in memory write mirroring, context fencing/scrubbing이다.

즉 Hermes의 "3-layer memory" 설명 중 이 파일은 durable memory 자체나 session DB 자체라기보다, 여러 memory backend를 안전하게 agent loop에 붙이는 integration boundary에 가깝다.

## 주요 구성

### 1. Tool schema normalization

관련 함수:

- `normalize_tool_schema`
- `memory_provider_tools_enabled`
- `inject_memory_provider_tools`

역할:

- memory provider가 반환한 tool schema를 OpenAI function tool 형태에 맞게 정규화한다.
- 이미 wrapped 된 schema를 한 번 풀어서 중복 wrapping 문제를 막는다.
- 이름이 없는 tool schema는 request 전체를 망칠 수 있으므로 skip한다.
- agent의 tool surface에 memory provider tool을 주입한다.

의미:

- Hermes는 memory backend가 단순 저장소가 아니라 agent가 호출할 수 있는 tool을 제공할 수 있다고 본다.
- provider가 잘못된 schema를 반환해도 전체 agent 실행이 깨지지 않도록 방어한다.

Chat Portal 시사점:

- 외부 memory provider를 tool로 노출할 경우 schema validation layer가 반드시 필요하다.
- provider tool name이 core tool과 충돌하지 않도록 registry-level guard가 필요하다.

## 2. Context fencing과 scrubber

관련 함수/클래스:

- `sanitize_context`
- `StreamingContextScrubber`
- `build_memory_context_block`

역할:

- provider가 반환한 recalled memory context를 `<memory-context>...</memory-context>` 블록으로 감싼다.
- system note를 붙여 "이것은 새 user input이 아니라 persistent memory context"라고 명시한다.
- streaming 응답 중 memory-context 블록이 UI로 유출되지 않도록 scrubber가 태그 단위로 제거한다.

중요한 설계 포인트:

- retrieved memory는 model에게는 보여야 하지만 사용자 UI에 그대로 노출되면 안 되는 internal context일 수 있다.
- 일반 regex만으로는 streaming chunk boundary를 처리하기 어렵기 때문에 stateful scrubber를 둔다.
- memory context가 새 user input으로 오인되지 않도록 system note를 붙인다.

Chat Portal 시사점:

- RAG/memory retrieval context는 UI 표시용 메시지와 agent 내부 context를 분리해야 한다.
- streaming 응답을 지원한다면 "내부 context fence가 chunk boundary에서 새는 문제"를 별도로 처리해야 한다.
- memory context injection은 prompt injection 관점에서 방어 문구와 구조적 fencing이 필요하다.

## 3. Provider registration

관련 클래스/메서드:

- `MemoryManager`
- `add_provider`
- `providers`
- `get_provider`

핵심 정책:

- built-in provider는 항상 허용한다.
- external provider는 한 번에 하나만 허용한다.
- provider tool이 Hermes core tool 이름을 shadow하면 등록하지 않는다.
- provider tool name이 이미 등록된 경우 충돌 warning 후 무시한다.

의미:

- Hermes는 memory backend를 pluggable하게 만들지만, 동시에 여러 외부 backend가 동시에 tool과 write path를 장악하는 상황은 피한다.
- "Only one external memory provider" 정책은 schema bloat와 backend conflict를 줄이는 안전장치다.

Chat Portal 시사점:

- memory provider를 여러 개 동시에 붙일지, provider aggregator를 하나만 둘지 정책을 정해야 한다.
- 여러 provider를 허용한다면 routing priority, conflict resolution, write fan-out, consistency model이 필요하다.
- Hermes는 단순하고 보수적으로 "built-in + external 1개"를 택했다.

## 4. System prompt integration

관련 메서드:

- `build_system_prompt`

역할:

- 각 provider의 `system_prompt_block()`을 수집해 agent system prompt에 추가한다.
- provider 실패는 warning만 남기고 전체 실행은 계속한다.

의미:

- memory provider는 retrieval 결과뿐 아니라 agent의 memory 사용 방법/규칙을 system prompt에 주입할 수 있다.
- provider별 prompt block이 runtime policy의 일부가 된다.

Chat Portal 시사점:

- memory provider별 system instruction을 runtime prompt에 넣는 방식은 유연하지만, provider가 prompt policy를 과도하게 장악할 수 있다.
- provider prompt block은 review/audit 가능해야 한다.

## 5. Prefetch / recall

관련 메서드:

- `_strip_skill_scaffolding`
- `prefetch_all`
- `queue_prefetch_all`

흐름:

1. 사용자 입력에서 skill scaffolding을 제거한다.
2. 실제 user instruction만 memory provider에 보낸다.
3. 각 provider의 `prefetch(query, session_id=...)` 결과를 모은다.
4. `queue_prefetch_all`은 다음 turn을 위해 background prefetch를 실행한다.

중요한 설계:

- `/skill` 또는 `/bundle`이 확장한 긴 skill body를 memory provider에 그대로 넣지 않는다.
- skill 본문이 embedding/store에 섞이면 memory가 오염되므로 실제 사용자 instruction만 추출한다.
- prefetch 실패는 non-fatal이다.

Chat Portal 시사점:

- agent 내부 scaffold, tool result, skill prompt, system prompt를 memory write/retrieval query에 그대로 넣으면 memory 품질이 급격히 나빠진다.
- memory-worthy user text를 추출하는 normalization 단계가 필요하다.
- "무엇을 기억할 것인가"만큼 "무엇을 기억하지 않을 것인가"가 중요하다.

## 6. Turn sync

관련 메서드:

- `_provider_sync_accepts_messages`
- `sync_all`
- `_submit_background`
- `_get_sync_executor`
- `flush_pending`

흐름:

1. turn 완료 후 user/assistant content를 provider에 동기화한다.
2. provider가 `messages` keyword를 받을 수 있는지 signature로 확인한다.
3. sync는 inline이 아니라 background worker에서 수행한다.
4. worker는 single-thread라 turn N이 turn N+1보다 먼저 기록된다.
5. provider가 느리거나 hang되어도 user-facing turn completion을 막지 않는다.

중요한 설계:

- memory sync는 중요하지만 agent 응답 경로를 막으면 안 된다.
- 그러나 순서는 중요하므로 single-worker executor로 serialize한다.
- executor 생성 실패/종료 race 시에는 inline fallback으로 write 자체는 잃지 않으려 한다.

Chat Portal 시사점:

- memory write는 user request latency와 분리해야 한다.
- 하지만 동일 session의 write order는 보장해야 한다.
- provider timeout/hang을 agent 전체 장애로 전파하지 않는 격리가 필요하다.

## 7. Tool routing

관련 메서드:

- `get_all_tool_schemas`
- `get_all_tool_names`
- `has_tool`
- `handle_tool_call`

역할:

- provider tool schema를 수집한다.
- core tool name은 제외한다.
- tool call을 담당 provider로 route한다.
- provider tool 실행 실패는 `tool_error`로 감싸 반환한다.

의미:

- memory provider가 자체 tool을 제공할 수 있다.
- manager는 tool dispatch table 역할을 한다.

Chat Portal 시사점:

- memory provider를 tool provider로도 볼 수 있다면, memory layer와 tool registry 사이의 boundary가 필요하다.
- tool failure는 agent 전체 crash가 아니라 recoverable tool error여야 한다.

## 8. Session lifecycle

관련 메서드:

- `on_turn_start`
- `on_session_end`
- `commit_session_boundary_async`
- `on_session_switch`
- `on_pre_compress`

핵심:

- turn 시작, session 종료, session switch, compression 직전 이벤트를 provider에 전달한다.
- `/new` 같은 session rotation에서는 `on_session_end`가 `on_session_switch`보다 먼저 실행되어야 한다.
- 이 순서를 background single worker에서 하나의 task로 serialize한다.

중요한 문제의식:

- session end extraction은 LLM-bound call이라 느릴 수 있다.
- inline 실행하면 `/new`가 오래 block된다.
- 반대로 별도 thread로 아무렇게나 실행하면 provider 내부 session binding이 바뀐 뒤 old session extraction이 실행되어 transcript가 새 session에 잘못 귀속될 수 있다.

Chat Portal 시사점:

- session boundary는 memory 시스템에서 매우 중요하다.
- "세션 종료 요약/추출"과 "새 세션으로 provider state 전환"의 순서를 보장해야 한다.
- context compression과 memory extraction은 별도 lifecycle event로 모델링해야 한다.

## 9. Built-in memory write mirroring

관련 메서드:

- `_provider_memory_write_metadata_mode`
- `on_memory_write`
- `_memory_tool_result_succeeded`
- `notify_memory_tool_write`

역할:

- built-in `memory` tool이 실제 write에 성공하면 external provider에도 write event를 mirror한다.
- staged write나 실패한 write는 mirror하지 않는다.
- `add`, `replace`, `remove`만 mirror한다.
- batch operation도 풀어서 각각 전달한다.
- `old_text`와 provenance metadata를 함께 넘긴다.

중요한 설계:

- built-in memory tool이 source of truth 역할을 하고, external provider는 write event를 구독하는 구조다.
- 성공하지 않은 write를 외부 provider에 알리지 않는 fail-closed 정책을 사용한다.
- provider의 `on_memory_write` signature가 버전별로 다를 수 있어 introspection으로 호환성을 맞춘다.

Chat Portal 시사점:

- memory write path에는 "staged/approved/committed" 상태 구분이 필요하다.
- external provider sync는 committed write 이후에만 수행해야 한다.
- old value와 provenance metadata가 있어야 audit과 rollback이 가능하다.

## 10. Delegation / subagent event

관련 메서드:

- `on_delegation`

역할:

- subagent가 완료한 task/result를 provider에 전달한다.
- `child_session_id`를 함께 넘긴다.

의미:

- Hermes memory manager는 multi-agent/subagent 작업 결과도 memory provider가 관찰할 수 있게 한다.

Chat Portal + DeepAgents 시사점:

- DeepAgents를 쓴다면 sub-agent 실행 결과를 memory에 어떻게 반영할지 별도 정책이 필요하다.
- 모든 sub-agent 결과를 durable memory로 승격하면 안 되고, session history 또는 task artifact로 남긴 뒤 필요한 것만 추출해야 한다.

## 11. Shutdown / initialization

관련 메서드:

- `shutdown_all`
- `_drain_sync_executor`
- `initialize_all`

역할:

- 종료 시 background sync/prefetch를 제한 시간 안에서 drain한다.
- wedged provider가 process teardown을 무한정 막지 않도록 bounded wait를 사용한다.
- provider 초기화 시 `hermes_home`을 자동 주입해 profile-scoped storage path를 찾을 수 있게 한다.

의미:

- memory provider lifecycle이 agent lifecycle과 강하게 연결되어 있다.
- profile/home directory는 provider가 storage path를 결정하는 데 필요하다.

## Hermes 3-layer 글과 코드의 연결

블로그 글의 3계층:

1. Durable facts
2. Procedural skills
3. Session search

이 파일에서 직접 보이는 것:

- durable facts 자체의 storage 구현은 보이지 않는다. provider 뒤에 숨어 있다.
- skills와 memory의 경계는 `_strip_skill_scaffolding`에서 강하게 드러난다.
- session search와 session lifecycle은 `prefetch_all`, `on_session_end`, `on_session_switch`, `on_pre_compress`에서 드러난다.
- profile-scoped storage는 `initialize_all(... hermes_home ...)` 주석에서 힌트가 보인다.
- subagent/delegation event를 memory provider에 넘기는 구조가 있다.

따라서 이 파일은 3-layer memory의 "저장 엔진"이라기보다, 그 계층들이 agent runtime과 충돌하지 않게 연결되는 integration manager다.

## Chat Portal 설계로 가져갈 점

### 가져갈 만한 설계

- memory provider interface를 두고 backend를 교체 가능하게 만들기
- built-in provider와 external provider의 역할 분리
- 외부 provider는 처음에는 하나만 허용해 conflict를 줄이기
- memory context를 내부 fence로 감싸고 UI streaming에서 scrub하기
- skill prompt/scaffold를 memory input에서 제거하기
- memory sync를 background로 돌리되 single worker로 순서 보장
- session boundary event를 명시적으로 모델링하기
- committed write만 external provider에 mirror하기
- subagent completion event를 memory layer가 관찰 가능하게 만들기
- provider failure를 agent 전체 failure로 전파하지 않기

### 조심할 점

- manager만 봐서는 실제 memory quality를 판단할 수 없다. provider 구현을 봐야 한다.
- external provider 1개 제한은 단순하지만, Chat Portal이 multi-provider routing을 목표로 한다면 부족할 수 있다.
- retrieved memory를 "authoritative reference data"로 주입하는 것은 강력하지만, stale/wrong memory가 있으면 잘못된 행동을 강화할 수 있다.
- background sync는 latency를 줄이지만, 사용자가 즉시 다음 turn에서 memory 반영을 기대하면 race가 생길 수 있다. `flush_pending` 같은 명시적 barrier가 필요하다.
- session end extraction이 실패해도 agent는 계속 진행하므로, memory consistency 모니터링이 필요하다.

## DeepAgents와 비교할 때 볼 포인트

DeepAgents 분석 시 다음 항목을 Hermes MemoryManager와 비교한다.

- 장기 작업 상태를 어디에 저장하는가
- agent 내부 scratchpad / file / todo / plan이 memory provider로 오염되지 않도록 분리하는가
- sub-agent 결과를 parent memory/context에 어떻게 반영하는가
- session boundary 또는 task boundary에서 요약/추출 hook이 있는가
- tool execution 결과 중 무엇을 durable memory로 승격하는가
- provider 실패가 agent execution을 막는가
- retrieved memory context가 UI에 노출되지 않도록 분리하는가
- memory write approval/staging 개념이 있는가

## 다음에 추가로 봐야 할 파일

이 파일만으로는 실제 memory 저장 구조가 보이지 않는다. 다음 파일/인터페이스를 추가로 확인해야 한다.

- `agent.memory_provider.MemoryProvider`
- built-in memory provider 구현
- plugin provider 구현
- built-in `memory` tool 구현
- session DB 또는 transcript storage 구현
- skill loader / skill command parser
- profile/home path resolution 구현

