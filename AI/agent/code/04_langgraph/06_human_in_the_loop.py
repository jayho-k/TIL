from typing import TypedDict, Annotated

from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_teddynote.tools import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel


class HumanRequest(BaseModel):
    """Forward the conversation to an expert. Use when you can't assist directly or the user needs assistance that exceeds your authority.
    To use this function, pass the user's 'request' so that an expert can provide appropriate guidance.
    """
    request: str

class State(TypedDict):
    messages: Annotated[list, add_messages]
    ask_human: bool # 이 부분이 추가

def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"]
    )

tool = TavilySearch(max_results=3)
tools = [tool, HumanRequest]
llm = ChatOpenAI(temperature=0)
llm_with_tools = llm.bind_tools(tools)

class HumanInTheLoopNode:
    def __init__(self, state:State):
        state:State = state
        chatbot = self.chatbot(state)
        human_node = self.human_node(state)

    # Node 생성
    def chatbot(self, state:State):
        response = llm_with_tools.invoke(state["messages"])
        ask_human = False

        # 답변에서 HumanRequest 가 나왔다면, ask_human 모드로 들어간다.
        if response.tool_calls and response.tool_calls[0]["name"] == HumanRequest.__name__:
                ask_human = True
        return {
            "messages": [response],
            "ask_human": ask_human
        }


    def human_node(self, state: State):
        new_messages = []
        if not isinstance(state["messages"][-1], ToolMessage):
            # 사람으로부터 응답이 없는 경우
            new_messages.append(
                create_response("No response from human.", state["messages"][-1])
            )
        return {
            # 새 메시지 추가
            "messages": new_messages,
            # 플래그 해제
            "ask_human": False,
        }

class GraphBuilder:
    def __init__(self, nodes:HumanInTheLoopNode):
        self.nodes:HumanInTheLoopNode = nodes

    @staticmethod
    def _select_next_node(state: State): # 다음 노드 선택
        # 인간에게 질문 여부 확인
        if state["ask_human"]:
            return "human"
        # 이전과 동일한 경로 설정
        return tools_condition(state)

    def build(self):
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.nodes.chatbot)
        graph_builder.add_node("tools", ToolNode(tools=[tool]))
        graph_builder.add_node("human", self.nodes.human_node)
        graph_builder.add_conditional_edges(
            "chatbot",
            self._select_next_node,  # ask human이면 human 노드로 이동
            {"human": "human", "tools": "tools", END: END},  # human, tool, end 로 연결
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge("human", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        return graph_builder

    def compile(self):
        return self.build().compile(
            checkpointer=memory,
            # 'human' 이전에 인터럽트 설정할 수 있음
            interrupt_before=["human"],
        )


if __name__ == "__main__":
    memory = MemorySaver()
    nodes = HumanInTheLoopNode(State)
    graph = GraphBuilder(nodes).compile()

    # Output
    # user_input = "이 AI 에이전트를 구축하기 위해 전문가의 도움이 필요합니다. 검색해서 답변하세요" (Human 이 아닌 웹검색을 수행하는 경우)
    user_input = "이 AI 에이전트를 구축하기 위해 전문가의 도움이 필요합니다. 도움을 요청할 수 있나요?"

    # config 설정
    config = {"configurable": {"thread_id": "1"}}

    # 스트림 또는 호출의 두 번째 위치 인수로서의 구성
    events = graph.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    )
    for event in events:
        if "messages" in event:
            # 마지막 메시지의 예쁜 출력
            event["messages"][-1].pretty_print()


    # 그래프 상태 스냅샷 생성
    snapshot = graph.get_state(config)
    # AI 메시지 추출
    ai_message = snapshot.values["messages"][-1]

    # 인간 응답 생성
    human_response = (
        "전문가들이 도와드리겠습니다! 에이전트 구축을 위해 LangGraph를 확인해 보시기를 적극 추천드립니다. "
        "단순한 자율 에이전트보다 훨씬 더 안정적이고 확장성이 뛰어납니다. "
        "https://wikidocs.net/233785 에서 더 많은 정보를 확인할 수 있습니다."
    )

    # 도구 메시지 생성
    tool_message = create_response(human_response, ai_message)

    # 그래프 상태 업데이트
    graph.update_state(config, {"messages": [tool_message]})
