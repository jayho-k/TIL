from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_teddynote.messages import AgentStreamParser, AgentCallbacks


def tool_callback(tool) -> None:
    print(tool.get('tool'))

def observation_callback(observation) -> None:
    print(observation.get('observation')[0])

def result_callback(result:str) -> None:
    print(result)
OLLAMA_BASE_URL = "https://jayho-macmini.tail60408a.ts.net/v1"
OLLAMA_MODEL = "gemma4:26b-a4b-it-qat"
llm = ChatOpenAI(
    api_key="ollama",
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=0.1,
    max_tokens=2028,
)
tools = [] # 각 도구 모음
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
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True,
)
agent_callbacks = AgentCallbacks(
    tool_callback=tool_callback,
    observation_callback=observation_callback,
    result_callback=result_callback,
)
agent_stream_parser = AgentStreamParser(agent_callbacks)

# 질의에 대한 답변을 스트리밍으로 출력 요청
result = agent_executor.stream({"input": "AI 투자관련 뉴스를 검색해 주세요."})

for step in result:
    # 중간 단계를 parser 를 사용하여 단계별로 출력
    agent_stream_parser.process_agent_steps(step)
