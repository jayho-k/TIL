
from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph

llm = ChatOpenAI()

# Status 정의
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]

# Node 정의
def chatbot(state:GraphState):
    return {"message":llm.invoke(state["messages"])}

# Graph 정의
graph_builder = StateGraph(GraphState)
graph_builder.add_node("chatbot", chatbot)

# Edge 추가
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile
graph = graph_builder.compile()

question = ""
# graph에서 stream은 중간 노드 단위를 출력하기 위한 것
for event in graph.stream({"messages":[("user", question)]}):
    for value in event.values():
        print("Assistant:", value["messages"][-1].content)
