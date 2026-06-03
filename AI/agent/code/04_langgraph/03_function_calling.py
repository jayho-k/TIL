import json
from typing import TypedDict, Annotated

from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_teddynote.tools import TavilySearch
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph


# LLM이 적절한 도구를 사용할 수 있도록 해야
tool = TavilySearch(max_results=3)
tools = [tool]

llm = ChatOpenAI()

class BasicToolNode:
    def __init__(self, tools: list):
        self.tools_list = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError()
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_list[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content=json.dumps(
                        tool_result, ensure_ascii=False
                    ),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
            )

# Status 정의
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]

def route_tools(state: GraphState):
    if messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError()
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

llm_with_tools = llm.bind_tools(tools)

# Node 정의
def chatbot(state:GraphState):
    return {"message":llm_with_tools.invoke(state["messages"])}

# Graph 정의
graph_builder = StateGraph(GraphState)
graph_builder.add_node("chatbot", chatbot)

# Edge 추가
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    source="chatbot",
    path=route_tools,
    path_map={"tools":"tools", END:END} # 위쪽에 route_tools에서 반환 값
)
graph_builder.add_edge("tools", "chatbot") # tools이면 > chatbot으로

# Compile
graph = graph_builder.compile()

question = ""
# graph에서 stream은 중간 노드 단위를 출력하기 위한 것
for event in graph.stream({"messages":[("user", question)]}):
    for value in event.values():
        print("Assistant:", value["messages"][-1].content)
