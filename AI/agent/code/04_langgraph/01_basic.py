from typing import TypedDict, Annotated

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import add_messages, StateGraph


# status
class GraphState(TypedDict):
    question: Annotated[list, add_messages]
    context: Annotated[str, "Context"]
    answer: Annotated[str, "Answer"]
    messages: Annotated[list, add_messages]
    relevance: Annotated[str, "Relevance"]

# Reducer
msg1 = [HumanMessage(content="안녕하세요?", id="1")]
msg2 = [AIMessage(content="반값습니다.", id="2")]
res = add_messages(msg1, msg2) # list로 합해진다.

# node
def retrieve_document(state: GraphState) -> GraphState:
    return GraphState(context=".pdf")

workflow = StateGraph(GraphState)
workflow.add_node("retrieve")