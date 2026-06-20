# LangGraph vs Deep Agents: 코드와 아키텍처 중심 보강

> 조사일: 2026-06-06  
> 목적: 기존 `langgraph_vs_deepagents.md`의 추상적인 비교를 보완하기 위해, 동일한 요구사항을 코드로 구현했을 때의 차이와 아키텍처 변화, 확장성/정확도 관점의 효과를 정리한다.  
> 용어: LangChain 공식 명칭은 `Deep Agents`이며, Python API는 `deepagents.create_deep_agent`다. 사용자가 말한 `DeepAgent`는 이 문서에서 `Deep Agents`로 표기한다.

## 참고한 공식 자료

- LangGraph quickstart: https://docs.langchain.com/oss/python/langgraph/quickstart
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- Deep Agents quickstart: https://docs.langchain.com/oss/python/deepagents/quickstart
- Deep Agents context engineering: https://docs.langchain.com/oss/python/deepagents/context-engineering
- Deep Agents subagents: https://docs.langchain.com/oss/python/deepagents/subagents
- Deep Agents human-in-the-loop: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
- Deep Agents customization: https://docs.langchain.com/oss/python/deepagents/customization

## 한 줄 결론

LangGraph와 Deep Agents의 차이는 "그래프를 직접 설계하느냐"와 "이미 설계된 장기 작업용 agent harness를 구성하느냐"의 차이다.

코드로 보면 LangGraph는 `State -> Node -> Edge -> Conditional Edge -> Compile`을 직접 만든다. Deep Agents는 `tools`, `system_prompt`, `subagents`, `interrupt_on`, `backend`, `skills`, `memory`를 넘겨서 harness가 기본 graph와 middleware를 구성하게 한다.

## 예시 요구사항

아래 요구사항을 기준으로 비교한다.

> 사용자가 주제를 주면 웹 검색을 수행하고, 중간 조사 결과를 관리하면서, 최종 Markdown 보고서를 작성한다. 필요하면 전문 subagent에게 일부 조사를 위임하고, 위험한 파일 삭제나 이메일 발송 같은 tool은 사람 승인을 받는다.

이 요구사항은 단순 chatbot이 아니라 다음 능력이 필요하다.

- tool calling
- multi-step planning
- context 관리
- subagent 위임
- streaming / tracing
- human approval
- report artifact 생성

## 1. 단순 tool-calling agent 구현 차이

### LangGraph 방식

LangGraph에서는 agent loop를 직접 만든다. LLM node, tool node, routing function, edge를 명시한다.

```python
from typing import Annotated, Literal
import operator

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END


@tool
def internet_search(query: str) -> str:
    """Search the web for a query."""
    return f"search results for: {query}"


tools = [internet_search]
tools_by_name = {tool.name: tool for tool in tools}

model = init_chat_model("openai:gpt-5.4", temperature=0)
model_with_tools = model.bind_tools(tools)


class AgentState(dict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def call_model(state: AgentState):
    response = model_with_tools.invoke(
        [
            SystemMessage(
                content=(
                    "You are a research assistant. Search when needed and answer "
                    "with concise source-grounded reasoning."
                )
            )
        ]
        + state["messages"]
    )
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def call_tools(state: AgentState):
    tool_messages = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return {"messages": tool_messages}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


builder = StateGraph(AgentState)
builder.add_node("model", call_model)
builder.add_node("tools", call_tools)
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue, ["tools", END])
builder.add_edge("tools", "model")

agent = builder.compile()

result = agent.invoke(
    {"messages": [HumanMessage(content="Research LangGraph and summarize it.")]}
)
print(result["messages"][-1].content)
```

구조:

```text
User
  |
  v
[model node] --tool calls?--> [tool node]
  ^                              |
  |                              v
  +----------- tool result -------+
  |
  v
 END
```

특징:

- loop의 제어권이 명확하다.
- tool 호출 후 다시 model로 돌아가는 구조가 코드에 그대로 드러난다.
- 대신 planning, file offload, subagent, summarization은 직접 추가해야 한다.

### Deep Agents 방식

Deep Agents에서는 같은 기본 loop를 직접 만들지 않는다. 도구와 역할을 넘기고, harness가 planning/filesystem/subagent/context middleware를 포함한 agent graph를 만든다.

```python
from deepagents import create_deep_agent


def internet_search(query: str, max_results: int = 5) -> str:
    """Search the web for a query and return relevant results."""
    return f"search results for: {query}, max_results={max_results}"


research_instructions = """
You are an expert research assistant.
When the task is broad, plan first, search iteratively, save useful notes,
and synthesize a Markdown report.
"""

agent = create_deep_agent(
    model="openai:gpt-5.4",
    tools=[internet_search],
    system_prompt=research_instructions,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Research LangGraph and summarize it."}]}
)
print(result["messages"][-1].content)
```

구조:

```text
User
  |
  v
[Deep Agent coordinator]
  |-- built-in planning tool: write_todos
  |-- user tools: internet_search
  |-- built-in filesystem tools: write_file/read_file/...
  |-- built-in context management
  |-- optional subagent task tool
  v
Final answer / artifact
```

차이:

- LangGraph 코드는 "agent loop를 만드는 코드"가 많다.
- Deep Agents 코드는 "agent에게 어떤 능력과 정책을 줄지 구성하는 코드"가 많다.
- Deep Agents quickstart 기준 agent는 자동으로 계획을 세우고, 검색하고, 파일 도구로 큰 결과를 offload하고, 필요하면 subagent에게 위임하도록 설계되어 있다.

## 2. 조사 보고서 agent: 아키텍처 차이

### LangGraph로 직접 만들 때

보고서 작성 agent를 제대로 만들려면 보통 다음 node가 필요하다.

```text
START
  |
  v
[plan_query]
  |
  v
[search]
  |
  v
[grade_sources]
  |       \
  |        \ insufficient
  |         v
  |       [rewrite_query] -> [search]
  |
  v sufficient
[summarize_findings]
  |
  v
[write_report]
  |
  v
END
```

코드 골격:

```python
from typing import Annotated, TypedDict, Literal
import operator

from langgraph.graph import StateGraph, START, END


class ResearchState(TypedDict):
    topic: str
    queries: list[str]
    search_results: Annotated[list[dict], operator.add]
    source_grade: str
    notes: Annotated[list[str], operator.add]
    report: str
    retry_count: int


def plan_query(state: ResearchState):
    return {"queries": [f"{state['topic']} official docs", f"{state['topic']} examples"]}


def search(state: ResearchState):
    results = []
    for query in state["queries"]:
        results.append({"query": query, "content": f"result for {query}"})
    return {"search_results": results}


def grade_sources(state: ResearchState):
    enough = len(state["search_results"]) >= 2
    return {"source_grade": "sufficient" if enough else "insufficient"}


def route_after_grading(state: ResearchState) -> Literal["summarize", "rewrite_query"]:
    if state["source_grade"] == "sufficient":
        return "summarize"
    return "rewrite_query"


def rewrite_query(state: ResearchState):
    return {
        "queries": [f"{state['topic']} architecture migration example"],
        "retry_count": state.get("retry_count", 0) + 1,
    }


def summarize(state: ResearchState):
    return {"notes": [f"summary from {len(state['search_results'])} results"]}


def write_report(state: ResearchState):
    return {"report": "\n".join(["# Report", *state["notes"]])}


builder = StateGraph(ResearchState)
builder.add_node("plan_query", plan_query)
builder.add_node("search", search)
builder.add_node("grade_sources", grade_sources)
builder.add_node("rewrite_query", rewrite_query)
builder.add_node("summarize", summarize)
builder.add_node("write_report", write_report)

builder.add_edge(START, "plan_query")
builder.add_edge("plan_query", "search")
builder.add_edge("search", "grade_sources")
builder.add_conditional_edges(
    "grade_sources",
    route_after_grading,
    {"summarize": "summarize", "rewrite_query": "rewrite_query"},
)
builder.add_edge("rewrite_query", "search")
builder.add_edge("summarize", "write_report")
builder.add_edge("write_report", END)

research_graph = builder.compile()
```

이 방식의 장점:

- 어떤 조건에서 재검색하는지 명시적이다.
- source grading, retry limit, validation을 deterministic하게 강제하기 쉽다.
- 각 node의 입력/출력 schema가 분리되어 테스트하기 쉽다.

단점:

- task planning, file output, context overflow, subagent 위임을 모두 직접 붙여야 한다.
- 요구사항이 늘수록 node/edge가 많아진다.
- agent가 새로운 조사 전략을 유연하게 고르는 능력은 prompt와 routing 설계에 의존한다.

### Deep Agents로 만들 때

Deep Agents에서는 위 graph 전체를 직접 만들기보다, coordinator의 지침과 도구, subagent를 구성한다.

```python
from deepagents import create_deep_agent


def internet_search(query: str, max_results: int = 5) -> str:
    """Search the web. Use for gathering current external evidence."""
    return f"results for {query}"


def fetch_url(url: str) -> str:
    """Fetch a URL and return its readable content."""
    return f"content from {url}"


researcher = {
    "name": "researcher",
    "description": (
        "Use for source gathering, fact checking, and comparing official docs. "
        "Return concise findings with source URLs."
    ),
    "system_prompt": """
You are a source-focused researcher.
Prefer official documentation and primary sources.
Return only the important findings and URLs.
Do not write the final report.
""",
    "tools": [internet_search, fetch_url],
    "model": "openai:gpt-5.4",
}

writer = {
    "name": "technical-writer",
    "description": (
        "Use for turning validated findings into a clear Markdown report."
    ),
    "system_prompt": """
You are a technical writer.
Write structured Markdown with assumptions, tradeoffs, and migration guidance.
Do not invent facts not present in the provided findings.
""",
}

agent = create_deep_agent(
    model="openai:gpt-5.4",
    tools=[internet_search, fetch_url],
    subagents=[researcher, writer],
    system_prompt="""
You are a research coordinator.
For broad technical comparison tasks:
1. Create a todo list.
2. Delegate source-heavy work to the researcher.
3. Use files to store large intermediate notes.
4. Ask the technical-writer subagent to draft the final report.
5. Verify the final report against gathered sources before answering.
""",
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Compare LangGraph and Deep Agents with code examples.",
            }
        ]
    }
)
```

구조:

```text
User
  |
  v
[Deep Agent coordinator]
  |-- write_todos
  |-- read_file/write_file/edit_file
  |-- internet_search/fetch_url
  |
  |-- task("researcher")
  |       |
  |       v
  |    [researcher context window]
  |       |-- internet_search
  |       |-- fetch_url
  |       v
  |    concise findings only
  |
  |-- task("technical-writer")
  |       |
  |       v
  |    [writer context window]
  |       v
  |    draft report
  |
  v
Final verified report
```

핵심 변화:

- LangGraph: 검색, 평가, 재검색, 요약, 작성 흐름을 graph로 직접 고정한다.
- Deep Agents: coordinator가 todo와 subagent delegation으로 동적으로 일을 나눈다.
- LangGraph: 확장할 때 node/edge를 추가한다.
- Deep Agents: 확장할 때 tool/subagent/skill/backend/permission을 추가한다.

## 3. Human-in-the-loop 구현 차이

### LangGraph 직접 구현

현재 로컬 `AI/agent/code/04_langgraph/06_human_in_the_loop.py`도 이 방향이다. 직접 state에 `ask_human`을 두고, conditional edge에서 human node로 라우팅한다.

```python
from typing import Annotated, TypedDict, Literal

from langchain.messages import ToolMessage
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver


class State(TypedDict):
    messages: Annotated[list, add_messages]
    ask_human: bool


def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    ask_human = bool(
        response.tool_calls
        and response.tool_calls[0]["name"] == "HumanRequest"
    )
    return {"messages": [response], "ask_human": ask_human}


def human_node(state: State):
    return {
        "messages": [
            ToolMessage(
                content="Human approved this action.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        ],
        "ask_human": False,
    }


def route(state: State) -> Literal["human", "tools", "__end__"]:
    if state["ask_human"]:
        return "human"
    if state["messages"][-1].tool_calls:
        return "tools"
    return END


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("human", human_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", route)
builder.add_edge("human", "chatbot")
builder.add_edge("tools", "chatbot")

graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human"],
)
```

장점:

- approval flow가 graph에 명확히 보인다.
- 어떤 node 앞에서 멈출지 직접 제어한다.
- human response를 state에 어떻게 반영할지 자유롭다.

단점:

- tool별 approve/edit/reject/respond 정책을 직접 설계해야 한다.
- 여러 tool call이 동시에 있을 때 처리 순서도 직접 설계해야 한다.
- subagent 내부 tool approval까지 확장하려면 graph 구조가 더 복잡해진다.

### Deep Agents 방식

Deep Agents는 `interrupt_on`으로 tool별 승인 정책을 선언한다. 공식 문서 기준 checkpointer가 필요하다.

```python
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent


@tool
def remove_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"


@tool
def fetch_file(path: str) -> str:
    """Read a file from the filesystem."""
    return f"Contents of {path}"


@tool
def notify_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Sent email to {to}"


agent = create_deep_agent(
    model="openai:gpt-5.4",
    tools=[remove_file, fetch_file, notify_email],
    interrupt_on={
        "remove_file": True,
        "fetch_file": False,
        "notify_email": {"allowed_decisions": ["approve", "reject"]},
    },
    checkpointer=MemorySaver(),
)
```

구조 변화:

```text
LangGraph 직접 구현
  tool risk 판단 -> state flag -> conditional edge -> human node -> update_state

Deep Agents
  tool별 interrupt_on 정책 선언 -> harness middleware가 interrupt 처리
```

장점:

- 위험한 tool별 정책을 코드 선언으로 관리한다.
- approval/edit/reject/respond 같은 decision type이 표준화된다.
- subagent와 함께 쓸 때도 같은 approval 모델로 확장하기 쉽다.

리스크:

- approval UX나 state update를 아주 특수하게 만들려면 직접 LangGraph가 더 낫다.
- side-effect tool은 `respond` 같은 decision을 잘못 쓰면 모델이 실행 성공으로 오해할 수 있으므로 정책 설계가 중요하다.

## 4. 기존 LangGraph를 Deep Agents에 편입하는 hybrid 예시

Deep Agents 공식 subagents 문서는 `CompiledSubAgent`로 LangGraph graph 또는 LangChain agent graph를 subagent로 넣을 수 있다고 설명한다. migration은 전체 교체가 아니라 hybrid로 시작할 수 있다.

### 기존 LangGraph: 엄격한 검증 graph

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


class ValidationState(TypedDict):
    messages: list
    answer: str
    verdict: str


def answer_question(state: ValidationState):
    return {"answer": "draft answer"}


def validate_answer(state: ValidationState):
    # deterministic validation, schema check, policy check, source check, etc.
    return {"verdict": "pass"}


def route(state: ValidationState) -> Literal["revise", "__end__"]:
    return END if state["verdict"] == "pass" else "revise"


def revise(state: ValidationState):
    return {"answer": state["answer"] + " revised"}


builder = StateGraph(ValidationState)
builder.add_node("answer", answer_question)
builder.add_node("validate", validate_answer)
builder.add_node("revise", revise)
builder.add_edge(START, "answer")
builder.add_edge("answer", "validate")
builder.add_conditional_edges("validate", route, {"revise": "revise", END: END})
builder.add_edge("revise", "validate")

validation_graph = builder.compile()
```

### Deep Agents coordinator에 연결

```python
from deepagents import create_deep_agent, CompiledSubAgent


validator_subagent = CompiledSubAgent(
    name="strict-validator",
    description=(
        "Use when an answer must pass deterministic validation before it is final."
    ),
    runnable=validation_graph,
)

agent = create_deep_agent(
    model="openai:gpt-5.4",
    tools=[internet_search],
    subagents=[validator_subagent],
    system_prompt="""
You coordinate research and writing.
Use the strict-validator subagent before finalizing answers that require validation.
""",
)
```

Hybrid 아키텍처:

```text
User
  |
  v
[Deep Agent coordinator]
  |-- planning
  |-- search tools
  |-- filesystem/context management
  |
  |-- task("strict-validator")
          |
          v
      [Existing LangGraph graph]
        answer -> validate -> revise loop
```

이 구조가 migration에 적합한 이유:

- LangGraph로 만든 deterministic workflow를 버리지 않는다.
- Deep Agents는 긴 작업의 coordinator와 context manager 역할만 맡는다.
- 검증, 정책, source grading처럼 정확도가 중요한 부분은 기존 graph에 남긴다.

## 5. 확장성 관점

### LangGraph의 확장성

LangGraph의 확장 단위는 node, edge, state schema, reducer, subgraph다.

좋은 경우:

- workflow가 명확한 상태 기계다.
- 각 단계가 테스트 가능한 함수다.
- business rule이 deterministic하다.
- "이 조건이면 반드시 이 경로"가 중요하다.

확장 예:

```text
기존:
retrieve -> generate

확장:
retrieve -> grade_docs -> rewrite_query -> retrieve
                    |
                    v
                generate -> validate_answer -> revise
```

문제:

- 기능이 늘수록 graph가 커진다.
- context compression, file artifact, subagent isolation 같은 cross-cutting concern이 여러 node에 퍼질 수 있다.
- 다수 전문 agent를 넣으려면 subgraph, tool-wrapped agent, state mapping을 직접 설계해야 한다.

### Deep Agents의 확장성

Deep Agents의 확장 단위는 tool, subagent, skill, backend, middleware, permission, memory다.

좋은 경우:

- task가 매번 조금씩 달라진다.
- 장시간 multi-step 작업이 많다.
- 파일/보고서/코드 같은 artifact를 만든다.
- 큰 tool output을 다룬다.
- 전문 역할을 나누는 것이 자연스럽다.

확장 예:

```python
agent = create_deep_agent(
    model="openai:gpt-5.4",
    tools=[internet_search, fetch_url, query_database],
    subagents=[researcher, sql_analyst, technical_writer, strict_validator],
    skills=["./skills/source-review", "./skills/report-writing"],
    permissions=[
        # filesystem permission rules
    ],
    memory=["./AGENTS.md"],
)
```

문제:

- coordinator가 어떤 subagent를 언제 부르는지 prompt/tool description 품질에 의존한다.
- hidden middleware와 built-in prompt를 이해해야 디버깅이 쉽다.
- strict workflow에는 graph만큼 예측 가능하지 않을 수 있다.

## 6. 정확도 관점

Deep Agents가 모델 자체의 지식 정확도를 자동으로 높여주는 것은 아니다. 정확도에 영향을 주는 지점은 다음과 같이 구분해야 한다.

### Deep Agents가 정확도를 개선할 수 있는 경우

1. Context bloat가 줄어드는 경우
   - subagent가 검색/파일 읽기/DB 조회의 상세 context를 격리한다.
   - parent는 최종 요약만 받으므로 main context가 덜 오염된다.
   - 긴 작업에서 이전 지시나 핵심 state가 밀려날 위험이 줄어든다.

2. 역할 분리가 품질을 높이는 경우
   - researcher는 source gathering만 한다.
   - writer는 보고서 구조화만 한다.
   - validator는 검증만 한다.
   - 한 agent가 모든 일을 하며 prompt 충돌을 일으키는 것보다 안정적일 수 있다.

3. planning이 누락을 줄이는 경우
   - built-in todo/planning이 task coverage를 추적한다.
   - 보고서 작성 전에 조사/검증/작성 단계를 명시적으로 관리할 수 있다.

4. filesystem offload가 긴 산출물에 유리한 경우
   - 큰 중간 결과를 메시지 context에 계속 넣지 않고 파일로 관리한다.
   - 최종 작성 시 필요한 파일만 다시 읽게 할 수 있다.

### LangGraph가 정확도에 유리한 경우

1. 경로 제어가 정확도인 경우
   - 예: "source가 2개 미만이면 절대 답하지 말 것"
   - 예: "검증 node가 pass할 때만 END"
   - 이런 조건은 LangGraph conditional edge가 더 명확하다.

2. schema와 validation이 중요한 경우
   - state schema를 명시하고 node별 출력 검증을 붙이기 쉽다.
   - deterministic validator/retry loop를 만들기 쉽다.

3. 평가와 테스트가 중요한 경우
   - node 단위 테스트가 가능하다.
   - 특정 state에서 다음 node가 무엇인지 재현하기 쉽다.

### 정확도 관련 결론

```text
Deep Agents = 긴 작업에서 context 관리와 역할 분리로 실수 가능성을 줄일 수 있음
LangGraph = 엄격한 상태 전이와 검증 루프로 정답 조건을 강제하기 좋음
```

가장 강한 구조는 둘을 섞는 것이다.

```text
Deep Agents: broad task coordination, files, subagents, context management
LangGraph: strict validation, deterministic routing, source grading, policy checks
```

## 7. 어떤 코드를 선택해야 하는가

### LangGraph를 유지하는 것이 좋은 경우

- RAG pipeline 구조가 이미 명확하다.
- 각 단계의 성공/실패 기준이 분명하다.
- human-in-the-loop state를 직접 inspect/update해야 한다.
- source grading, retry, validation을 코드로 강제해야 한다.
- agent가 자유롭게 계획을 바꾸면 안 된다.

예:

```text
retrieve -> grade -> rewrite -> retrieve -> generate -> validate -> END
```

이런 구조는 LangGraph가 더 자연스럽다.

### Deep Agents로 가는 것이 좋은 경우

- 사용자가 매번 다른 장기 작업을 준다.
- 파일을 읽고 쓰며 중간 산출물을 관리해야 한다.
- 검색 결과, DB 결과, 코드 파일 등 큰 context가 자주 생긴다.
- researcher/writer/reviewer/tester처럼 역할 분리가 자연스럽다.
- "작업 계획을 세우고 진행하는 agent"가 필요하다.

예:

```text
사용자: "이 저장소의 LangGraph 코드를 분석하고 Deep Agents migration 보고서를 만들어줘."

Deep Agent:
  1. todo 작성
  2. 파일 탐색
  3. researcher subagent 위임
  4. 기존 LangGraph validator 호출
  5. 보고서 파일 작성
  6. 최종 검증
```

이런 구조는 Deep Agents가 더 자연스럽다.

## 8. migration 판단표

| 질문 | Yes면 |
| --- | --- |
| workflow가 고정된 DAG/state machine인가? | LangGraph |
| node별 단위 테스트와 deterministic routing이 중요한가? | LangGraph |
| task가 장시간이고 매번 달라지는가? | Deep Agents |
| 큰 tool output 때문에 context가 자주 비대해지는가? | Deep Agents |
| 파일/코드/보고서 artifact를 agent가 직접 관리해야 하는가? | Deep Agents |
| 전문 역할 분리와 subagent 격리가 필요한가? | Deep Agents |
| 기존 LangGraph 자산이 이미 있는가? | Hybrid |
| 정확도 조건을 코드로 강제해야 하는가? | LangGraph 또는 Hybrid |

## 9. 추천 PoC

현재 저장소 기준으로는 바로 migration하지 말고 다음 3개 파일을 만들어 비교하는 것이 좋다.

```text
AI/agent/code/06_deepagents/
  01_research_agent_basic.py
  02_research_agent_subagents.py
  03_hybrid_langgraph_subagent.py
```

비교 task:

```text
"LangGraph와 Deep Agents의 차이를 공식 문서 기반으로 조사하고,
코드 예시와 migration 판단표를 Markdown으로 작성하라."
```

측정 항목:

- 구현 코드량
- 직접 작성한 orchestration 코드량
- tool output이 main context에 남는 양
- subagent별 역할 분리 여부
- 검증 실패 시 retry 가능성
- streaming/tracing에서 어느 단계가 보이는지
- 최종 보고서의 source 누락률
- 사람이 승인해야 하는 tool call을 제어하기 쉬운지

## 최종 보강 결론

Deep Agents의 장점은 "정확도가 무조건 오른다"가 아니다. 더 정확한 표현은 다음이다.

```text
Deep Agents는 긴 작업에서 필요한 운영 패턴을 기본 제공해서,
context 관리 실패, 계획 누락, 역할 혼합, 중간 산출물 관리 실패를 줄일 수 있다.
```

LangGraph의 장점은 다음이다.

```text
LangGraph는 상태 전이와 검증 조건을 코드로 고정할 수 있어서,
정확도 조건이 명확한 workflow를 강제하기 좋다.
```

따라서 실전 migration 방향은 전체 교체가 아니라 다음 hybrid가 가장 합리적이다.

```text
Deep Agents coordinator
  - planning
  - files
  - subagents
  - long context management
  - human approval policy

LangGraph subgraphs
  - RAG retrieval/grade/rewrite/generate
  - source validation
  - deterministic business workflow
  - policy checks
```

