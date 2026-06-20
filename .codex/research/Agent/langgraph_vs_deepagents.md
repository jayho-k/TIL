# LangGraph vs Deep Agents 조사

> 조사일: 2026-06-06  
> 범위: LangGraph를 이미 사용 중인 상황에서 Deep Agents로 migration할 때 패러다임 차이, 효과, 비용, 판단 기준 정리  
> 주요 출처: LangChain 공식 문서, LangChain Deep Agents GitHub

## 결론

Deep Agents는 LangGraph의 대체재라기보다 LangGraph 위에 올라간 opinionated agent harness다. 따라서 migration의 본질은 "LangGraph를 버리는 것"이 아니라, 직접 설계하던 agent orchestration 위에 planning, filesystem, subagent, context management, skills, human approval 같은 기본 장비가 포함된 상위 계층을 채택하는 것이다.

현재 학습/실습 코드처럼 `StateGraph`, node, edge, reducer, conditional edge, interrupt, subgraph를 직접 이해하고 제어하는 단계에서는 LangGraph를 계속 학습하는 가치가 크다. 반대로 실제 제품에서 장시간 실행, 대량 tool output, 파일 기반 작업, subagent 위임, context 격리, 작업 계획 추적이 반복된다면 Deep Agents를 검토할 가치가 있다.

## 출처 우선순위

1. LangChain 공식 문서
   - LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
   - Deep Agents overview: https://docs.langchain.com/oss/python/deepagents/overview
   - Frameworks, runtimes, and harnesses: https://docs.langchain.com/oss/python/concepts/products
   - Deep Agents customization: https://docs.langchain.com/oss/python/deepagents/customization
   - Deep Agents subagents: https://docs.langchain.com/oss/python/deepagents/subagents
2. 공식 GitHub
   - https://github.com/langchain-ai/deepagents

## 공식 문서 기준 관계

LangChain 문서는 LangGraph를 "low-level orchestration framework and runtime"으로 설명한다. 핵심은 durable execution, streaming, human-in-the-loop, persistence 같은 agent orchestration runtime 기능이다.

Deep Agents는 "agent harness"로 설명된다. LangChain core building blocks와 LangGraph runtime 위에서 planning, filesystem, subagents, context management, skills 등을 기본 제공한다.

계층 관계는 다음과 같이 보는 것이 정확하다.

```text
LangGraph = runtime / orchestration layer
LangChain = agent framework / model-tool-agent loop abstraction
Deep Agents = batteries-included harness on LangGraph + LangChain
```

즉 Deep Agents를 쓴다고 LangGraph 개념이 사라지는 것이 아니다. `create_deep_agent(...)`의 반환 타입도 공식 customization 문서 기준 `CompiledStateGraph`다. Deep Agents 내부 결과물은 여전히 LangGraph 실행 모델 위에서 움직인다.

## 패러다임 차이

### LangGraph 패러다임

LangGraph는 "내가 graph를 설계한다"는 방식이다.

- 상태 스키마를 직접 정의한다.
- node를 직접 작성한다.
- edge와 conditional edge로 흐름을 명시한다.
- reducer로 상태 병합 규칙을 정한다.
- interrupt, checkpoint, subgraph, stream mode를 필요한 만큼 직접 조합한다.

장점은 제어권이다. RAG, routing, approval, retry, fan-out/fan-in, deterministic step과 agentic step의 혼합 같은 구조를 정확히 모델링할 수 있다.

단점은 agent 제품에서 자주 필요한 부가 기능을 매번 직접 만들어야 한다는 점이다. 예를 들어 todo/planning, 파일 기반 context offload, tool output 압축, subagent context 격리, shell/sandbox, permission, skill loading 같은 것들은 LangGraph만 쓰면 애플리케이션 계층에서 직접 설계해야 한다.

### Deep Agents 패러다임

Deep Agents는 "이미 정해진 agent harness를 가져와서 커스터마이징한다"는 방식이다.

공식 문서 기준 기본 제공되는 축은 다음이다.

- planning and task decomposition: `write_todos` 같은 계획 도구
- context management: filesystem tools, long thread summarization, large output offload
- subagent spawning: `task` tool 기반 context isolation
- pluggable filesystem backends: in-memory, local disk, LangGraph store, sandbox, custom backend
- shell execution: backend에 따라 `execute` tool 제공
- long-term memory: LangGraph Memory Store 활용
- human-in-the-loop: LangGraph interrupt 기반 approval
- skills: 재사용 가능한 workflow/domain instruction
- middleware: todo, filesystem, subagent, summarization, memory, skills 등

장점은 agent 앱에서 반복되는 scaffold가 이미 들어 있다는 점이다. 특히 long-horizon task, coding/research assistant, 많은 파일/검색 결과/DB 결과를 다루는 agent에서 빠르게 출발할 수 있다.

단점은 agent loop의 기본 모양이 Deep Agents의 harness에 묶인다는 점이다. 이미 복잡한 custom graph가 있고 각 node/edge의 의미가 도메인 로직과 강하게 결합되어 있다면, Deep Agents로 옮기는 것은 단순 라이브러리 교체가 아니라 architecture 재배치가 된다.

## 기능별 비교

| 관점 | LangGraph 직접 사용 | Deep Agents 사용 |
| --- | --- | --- |
| 추상화 수준 | 낮음. graph runtime 직접 설계 | 높음. agent harness 기본 제공 |
| 핵심 사고방식 | state, node, edge, reducer | agent, tools, files, subagents, skills |
| 제어권 | 가장 높음 | 기본 harness 안에서 확장 |
| planning | 직접 구현 | built-in todo/planning |
| context 관리 | 직접 summary/delete/offload 구현 | summarization, filesystem offload 제공 |
| subagent | subgraph/tool/node로 직접 설계 | built-in task tool, sync/async subagents |
| human-in-the-loop | interrupt 직접 구성 | `interrupt_on` 등으로 구성 |
| filesystem/shell | 직접 tool/backend 구현 | built-in filesystem, shell-capable backend |
| deterministic workflow | 강함 | 가능하지만 harness 중심 |
| 제품화 속도 | 설계 비용 큼 | 빠름 |
| custom orchestration | 강함 | 필요하면 LangGraph subagent로 끼우는 방식 |

## Migration할 때 기대 효과

### 1. 반복 구현 감소

현재 LangGraph 노트에는 message delete, summary node, human-in-the-loop, subgraph, streaming을 직접 구현하는 예제가 있다. Deep Agents를 쓰면 이 중 일부는 middleware나 parameter로 흡수된다.

예:

- message summary/delete 로직 일부 -> SummarizationMiddleware, context management
- human approval graph 설계 일부 -> `interrupt_on`
- subgraph 기반 위임 일부 -> subagents / `task` tool
- 파일 read/write tool 설계 -> FilesystemMiddleware

### 2. long-horizon agent에 유리

Deep Agents는 장시간 실행되는 multi-step task에 맞춰 planning, task decomposition, subagent isolation, context management를 기본값으로 둔다. 일반 chatbot이나 단순 tool-calling agent보다 "작업을 진행하는 agent"에 더 적합하다.

### 3. context bloat 완화

Deep Agents subagent 문서는 subagent의 핵심 장점을 context quarantine으로 설명한다. 큰 tool output이나 여러 단계 검색 결과를 main context에 모두 남기지 않고 subagent 결과만 parent에게 전달하는 패턴이다.

LangGraph에서도 같은 패턴을 만들 수 있지만 직접 설계해야 한다. Deep Agents는 이를 harness의 기본 설계로 제공한다.

### 4. 파일/코드 작업 agent로 확장 쉬움

Deep Agents는 filesystem backend, shell execution, sandbox, permission, skills 같은 기능을 제공한다. 그래서 Claude Code류의 coding agent, research report agent, artifact-producing agent를 만들 때 출발점이 빠르다.

### 5. 기존 LangGraph 자산을 완전히 버리지 않아도 됨

공식 Deep Agents subagents 문서 기준 `CompiledSubAgent`로 compiled LangGraph graph를 subagent로 넣을 수 있다. 즉 기존 custom LangGraph workflow를 Deep Agents의 worker로 편입하는 방식이 가능하다.

## Migration 비용과 리스크

### 1. 제어권 손실

LangGraph에서는 edge 하나하나가 application architecture다. Deep Agents는 기본 agent loop, middleware, prompt assembly, subagent tool 방식이 있다. 특정 domain workflow를 엄격하게 보장해야 한다면 Deep Agents의 기본 loop가 오히려 불투명해질 수 있다.

### 2. prompt/middleware 동작 이해 필요

Deep Agents는 built-in system prompt와 profile suffix, middleware가 agent 행동을 형성한다. 공식 customization 문서는 system prompt가 `USER -> BASE/CUSTOM -> SUFFIX` 순서로 조립된다고 설명한다. 이 계층을 이해하지 않고 migration하면 기존 prompt와 다른 행동이 나올 수 있다.

### 3. 평가 기준 재설계 필요

Deep Agents는 더 많은 자율성을 제공한다. 따라서 migration 후에는 "응답이 맞는가"뿐 아니라 다음을 평가해야 한다.

- 계획을 올바르게 세우는가
- subagent 사용이 비용 대비 유효한가
- 파일 쓰기/수정 범위가 안전한가
- tool approval 경계가 적절한가
- summarization 이후 중요한 context가 손실되지 않는가

### 4. 단순 workflow에는 과하다

공식 문서도 simpler use case는 LangChain `create_agent` 또는 custom LangGraph workflow를 고려하라고 한다. 단순 routing, RAG, 한두 개 tool 호출 정도라면 Deep Agents는 추상화가 과할 수 있다.

### 5. 보안 경계는 model이 아니라 tool/sandbox에서 강제해야 함

Deep Agents GitHub README는 "trust the LLM" 모델을 언급하며, agent가 tool이 허용하는 것은 무엇이든 할 수 있으므로 sandbox/tool permission에서 경계를 강제해야 한다고 설명한다. shell/filesystem을 켜는 migration은 반드시 permission 설계를 동반해야 한다.

## 현재 로컬 학습 코드 기준 판단

현재 로컬에는 다음 흐름이 있다.

- `AI/agent/text/04_langgraph.md`: State, node, edge, conditional edge, streaming, human-in-the-loop, delete message, fan-in/fan-out, summary, subgraph 정리
- `AI/agent/code/04_langgraph/*.py`: LangGraph 기초, chatbot, function calling, multiturn, streaming, human-in-the-loop 실습
- `AI/agent/code/05_langraph-structure/01_basic.py`: graph 구조 학습 초기 코드

이 상태에서는 바로 Deep Agents로 갈아타기보다 다음 순서가 좋다.

1. LangGraph 핵심 개념은 계속 학습한다.
   - Deep Agents 내부도 LangGraph runtime이므로, LangGraph 이해는 migration 후에도 유효하다.
2. Deep Agents는 별도 실험 폴더로 proof-of-concept를 만든다.
   - 예: `AI/agent/code/06_deepagents/`
3. 기존 LangGraph 예제 중 Deep Agents가 대체할 수 있는 부분을 mapping한다.
   - summary/delete -> context management
   - human-in-the-loop -> `interrupt_on`
   - subgraph -> subagents 또는 `CompiledSubAgent`
   - file/tool 작업 -> filesystem/tools/backend
4. 실제 migration은 "전체 교체"보다 "Deep Agents coordinator + 기존 LangGraph subagent" 방식으로 시작한다.

## 추천 migration 전략

### Phase 1: 비교 PoC

동일한 task를 LangGraph와 Deep Agents 양쪽으로 구현한다.

추천 task:

- "웹 검색 또는 문서 검색 후 요약 보고서 작성"
- "파일을 읽고 수정 계획을 세운 뒤 수정"
- "human approval이 필요한 tool call 포함"

비교 항목:

- 코드량
- prompt 관리 난이도
- state visibility
- streaming/debugging 편의성
- context overflow 처리
- tool permission 설정 난이도
- 결과 품질과 비용

### Phase 2: Hybrid 구조

Deep Agents를 top-level coordinator로 두고, 기존 LangGraph graph를 `CompiledSubAgent`로 편입한다.

```text
Deep Agent coordinator
  - planning
  - context management
  - filesystem/shell/approval
  - task delegation

Existing LangGraph subagent
  - deterministic domain workflow
  - RAG pipeline
  - strict validation / routing
```

이 방식은 기존 LangGraph 자산을 유지하면서 Deep Agents의 harness 효과를 시험할 수 있다.

### Phase 3: 선택적 migration

다음에 해당하는 부분만 Deep Agents로 이동한다.

- 장시간 multi-step task
- 파일/코드/문서 artifact를 생성하는 task
- main context가 쉽게 비대해지는 task
- subagent delegation이 자연스러운 task
- skills/memory가 유용한 반복 workflow

반대로 다음은 LangGraph 직접 구현을 유지한다.

- strict state transition이 중요한 workflow
- deterministic pipeline
- 도메인별 라우팅과 검증이 핵심인 graph
- runtime state를 세밀하게 inspect/update해야 하는 human-in-the-loop workflow

## 최종 판단

Deep Agents migration의 효과는 "더 똑똑한 LangGraph"가 아니라 "agent product scaffold를 덜 직접 만들게 되는 것"이다.

따라서 질문을 이렇게 바꾸면 판단이 명확하다.

- 우리가 원하는 것이 custom workflow engine인가? -> LangGraph 유지
- 우리가 원하는 것이 장시간 작업하는 file/subagent/planning 중심 agent인가? -> Deep Agents 검토
- 둘 다 필요한가? -> Deep Agents coordinator + LangGraph subagent hybrid

현재 학습 저장소 기준으로는 Deep Agents를 LangGraph 다음 장의 주제로 정리하고, 바로 기존 코드를 migration하기보다 비교 PoC를 만드는 것이 가장 낫다.

