from typing import TypedDict, Annotated

from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_teddynote.tools import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# 프로덕션 단계에서는 PostgresSaver 로 변경하고 자체 DB에 연결할 수 있음.
# https://github.com/redis-developer/langgraph-redis RedisSaver도 있음

memory = MemorySaver()

########## 1. 상태 정의 ##########
# 상태 정의
class State(TypedDict):
    # 메시지 목록 주석 추가
    messages: Annotated[list, add_messages]


########## 2. 도구 정의 및 바인딩 ##########
# 도구 초기화
tool = TavilySearch(max_results=3)
tools = [tool]

# LLM 초기화
llm = ChatOpenAI()

# 도구와 LLM 결합
llm_with_tools = llm.bind_tools(tools)

########## 3. 노드 추가 ##########
# 챗봇 함수 정의
def chatbot(state: State):
    # 메시지 호출 및 반환
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)

# start node
graph_builder.add_node("chatbot", chatbot)

# tool node 생성 및 추가
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# condition 노드
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# 엣지
# tools > chatbot
graph_builder.add_edge("tools", "chatbot")

# START > chatbot
graph_builder.add_edge(START, "chatbot")

# chatbot > END
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile(checkpointer=memory)

config = RunnableConfig(
    recursion_limit=10,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
    configurable={"thread_id": "1"},  # 스레드 ID 설정
)

question=""
for event in graph.stream(
        {"messages": [("user", question)]},
        config=config # 여기에 config를 넣어준다.
):
    for value in event.values():
        value["messages"][-1].pretty_print()


