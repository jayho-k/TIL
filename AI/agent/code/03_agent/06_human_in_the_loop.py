from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def add_function(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

# 도구 정의
tools = [add_function]

# LLM 생성
gpt = ChatOpenAI(model="gpt-4o-mini")

# prompt 생성
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant.",
        ),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Agent 생성
gpt_agent = create_tool_calling_agent(gpt, tools, prompt)

# AgentExecutor 생성
agent_executor = AgentExecutor(
    agent=gpt_agent,
    tools=tools,
    verbose=False,
    max_iterations=10,
    handle_parsing_errors=True,
)

# 계산할 질문 설정
question = "114.5 + 121.2 + 34.2 + 110.1 의 계산 결과는?"

# agent_executor를 반복적으로 실행
for step in agent_executor.iter({"input": question}):
    if output := step.get("intermediate_step"):
        action, value = output[0]
        if action.tool == "add_function":
            # Tool 실행 결과 출력
            print(f"\nTool Name: {action.tool}, 실행 결과: {value}")
        # 사용자에게 계속 진행할지 묻습니다.
        _continue = input("계속 진행하시겠습니다? (y/n)?:\n") or "Y"
        # 사용자가 'y'가 아닌 다른 입력을 하면 반복 중단
        if _continue.lower() != "y":
            break

    # 최종 결과 출력
    if "output" in step:
        print(step["output"])