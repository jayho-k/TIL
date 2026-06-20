# 07_deep-agent

> - **DeepAgent 튜토리얼**
>   - https://github.com/braincrew-lab/deep-agents-from-scratch
> - **Lang Chain middleware**
>   - https://docs.langchain.com/oss/python/langchain/middleware/built-in

- 기존 멀티에이전트의 문제
  - 너무 많은 툴 호출을 하용하면서 window context가 넘치는 경우가 발생하게 된다.
  - 따라서 이를 해결하기 위한 방향으로 발전하게 된다.

- File System을 사용해서 정보를 가져온다.
  - 용도 : 
    - 버퍼용도로 사용해서 window context를 줄이는 방식을 사용하게 된다.
    - 기존 rag에 목차를 넣는 느낌
  - 단점 : 
    - latency가 늘어나게 된다.
    - 시멘틱 서치가 아니다. 따라서 서칭이 일어나지 않는다는 단점이 있다.
    - 오픈 모델을 사용할 경우 도구 호출의 정확도가 높아야한다.
    - 

- 주요특징
  - 작업 계획 (TODO), Recitation과 함께 사용된다.
  - 파일 시스템으로의 컨텍스트 오프로딩 (Context offloading)
  - 서브 에이전트 위임을 통한 컨텍스트 격리 (Context isolation)

- 현재 supervisor 패턴에서 변동이 생김
  - 각각의 서브 에이전트들이 결과값만 supervisor에 보내게 된다.
  - Lang Graph는 Tool 호출로 이 문제를 해결한다.



```python
def mehtod(
	state: Annotated[State, InjectedState], # LLM한테 전달 x
    tool_call_id: Annotated[str, InjectedToolCallId] # LLM한테 전달 x
)
```

- 위와 같은 2개 인자가 추가 됨
- **이때 중요한 점은 state, tool_call_id 는 LLM한테 전달되지 않는다.**
- 장점
  - 할루시네이션이 발생할 수 있는 부분을 막아준다.
  - 왜냐하면 state를 LLM이 주입하는게 아니라 LangGraph에서 직접 주입하기 때문에 



### Plan

- Todo List 를 만드는 Tool을 사용하여 Plan을 작성한다.

````python
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from deep_agents_from_scratch.prompts import WRITE_TODOS_DESCRIPTION
from deep_agents_from_scratch.state import DeepAgentState, Todo


# write_todos 툴 정의, LLM이 전달한 TODO 리스트를 state에 저장 및 메시지 기록
@tool(description=WRITE_TODOS_DESCRIPTION, parse_docstring=True)
def write_todos(
    todos: list[Todo], tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Create or update the agent's TODO list for task planning and tracking.

    Args:
        todos: List of Todo items with content and status
        tool_call_id: Tool call identifier for message response

    Returns:
        Command to update agent state with new TODO list
    """
    # TODO 리스트와 메시지 업데이트를 위한 Command 객체 반환
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(f"Updated todo list to {todos}", tool_call_id=tool_call_id)
            ],
        }
    )
````

```python
# read_todos 툴 정의, 현재 state의 TODO 리스트를 읽어 포맷된 문자열로 반환
@tool(parse_docstring=True)
def read_todos(
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Read the current TODO list from the agent state.

    This tool allows the agent to retrieve and review the current TODO list
    to stay focused on remaining tasks and track progress through complex workflows.

    Args:
        state: Injected agent state containing the current TODO list
        tool_call_id: Injected tool call identifier for message tracking

    Returns:
        Command to update agent state with ToolMessage containing formatted TODO list
    """
    # state에서 todos 리스트 추출, 없으면 빈 리스트 반환
    todos = state.get("todos", [])
    if not todos:
        # TODO 리스트가 비어 있을 때 안내 메시지 반환
        message_content = "현재 목록에 있는 모든 항목이 아닙니다."
    else:
        # 현재 TODO 리스트를 번호, 이모지, 상태와 함께 포맷팅하여 문자열로 생성
        result = "현재 TODO List:\n"
        for i, todo in enumerate(todos, 1):
            status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            emoji = status_emoji.get(todo["status"], "❓")
            result += f"{i}. {emoji} {todo['content']} ({todo['status']})\n"
        message_content = result.strip()

    # Command 객체로 래핑하여 ToolMessage와 함께 반환
    return Command(
        update={
            "messages": [ToolMessage(message_content, tool_call_id=tool_call_id)],
        }
    )
```

```python
import os
from IPython.display import display
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent
from utils import format_messages

from deep_agents_from_scratch.prompts import TODO_USAGE_INSTRUCTIONS
from deep_agents_from_scratch.state import DeepAgentState
from deep_agents_from_scratch.todo_tools import read_todos, write_todos

from langchain_teddynote.graphs import visualize_graph


# 웹 검색 툴 모킹: 실제 검색 대신 고정된 결과 반환
@tool(parse_docstring=True)
def web_search(
    query: str,
):
    """Search the web for information on a specific topic.

    This tool performs web searches and returns relevant results
    for the given query. Use this when you need to gather information from
    the internet about any topic.

    Args:
        query: The search query string. Be specific and clear about what
               information you're looking for.

    Returns:
        Search results from search engine.

    Example:
        web_search("machine learning applications in healthcare")
    """

    # 웹 검색 결과 모킹, 실제 검색 대신 고정된 결과 반환
    search_result = """모델 컨텍스트 프로토콜(MCP)은 Anthropic이 개발한 개방형 표준 프로토콜로,
AI 모델과 도구, 데이터베이스, 기타 서비스와 같은 외부 시스템 간의 원활한 통합을 가능하게 합니다.
이는 표준화된 통신 계층 역할을 하여 AI 모델이 다양한 출처의 데이터에 일관되고 효율적인 방식으로 접근하고 활용할 수 있도록 합니다.
본질적으로 MCP는 데이터 교환을 위한 통합 언어를 제공함으로써 AI 어시스턴트를 외부 서비스에 연결하는 과정을 단순화합니다."""

    return search_result


# LLM 모델 초기화
model = init_chat_model(model="anthropic:claude-sonnet-4-5", temperature=0.0)
# 에이전트에 사용할 툴 리스트 정의, TODO 관리 및 웹 검색 포함
tools = [write_todos, web_search, read_todos]

# 단일 웹 검색 호출만 허용하는 간단한 리서치 지침 문자열
SIMPLE_RESEARCH_INSTRUCTIONS = """IMPORTANT: Just make a single call to the web_search tool and use the result provided by the tool to answer the user's question. Answer in Korean."""

# create_agent 함수로 에이전트 생성, 시스템 프롬프트에 TODO 사용 지침 및 리서치 지침 포함
agent = create_agent(
    model,
    tools,
    system_prompt=TODO_USAGE_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + SIMPLE_RESEARCH_INSTRUCTIONS,
    state_schema=DeepAgentState,
)

# 에이전트 그래프 시각화, Mermaid PNG 포맷으로 출력
visualize_graph(agent)
```



### Offload

- File 목록들을 가져온다.
- 필요한 데이터를 가져오며, limit=2000과 같이 넣어서 2000줄만 읽는 등에서 진행 함 



### Sub-Agent

- lang chain에서는 sub agent 호출을 tool을 호출하는 식으로 구현하게 끔 한다.

```python
class SubAgent(TypedDict):
    name: str
    description: str
    prompt: str
    tools: NotRequired[list[str]]
```

- 구성 
  - name : 에이전트 식별자 (main agent에서 호출 시 사용)
  - description : 역할 설명 (main agent 에서 호출 시 사용)
  - prompt : 전용 시스템 프롬프트 (sub-agent 작업 지시)
  - tools : 사용가능한 도구 목록 (sub-agent 작업 지시)











