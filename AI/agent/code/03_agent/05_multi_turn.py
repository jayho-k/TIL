from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# key : session_id
store = {}

def get_session_history(session_ids):
    if session_ids not in store:
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]

# LLM 정의
llm = ChatOpenAI(temperature=0)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. "
            "Make sure to use the `search_news` tool for searching keyword related news.",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
# Agent 생성
tools = []
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
)

# 채팅 메시지 기록이 추가된 에이전트를 생성
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# config에 session_id와 같이 넣어주게 되면, 해당 내용을 기억하게 된다.
agent_with_chat_history.stream(
    {"input": "안녕? 내 이름은 000 이야."},
    config={"configurable":{"session_id":"123"}}
)


