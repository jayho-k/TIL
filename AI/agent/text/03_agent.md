# 03_Agent



```python
from langchain_core.tools import tool

@tool
def add_numbers(a:int, b:int) -> int:
    """Add two numbers"""
    return a+b

@tool
def multiply_numbers(a:int, b:int) -> int:
    """Multiply two numbers"""
    return a*b

add_numbers.invoke({
    "a":1,
    "b":2
})

multiply_numbers.invoke({
    "a":1,
    "b":2
})
```

- 위와 같이 def에 tool이라는 데코레이터를 만들면 된다.
- 또한 설명을 자세히 작성해줘야한다.



## Binding Tools

- LLM 모델이 도구를 호출할 수 있으려면 chat 요청을 할 때 모델에 도구 스키마를 전달해야한다.
- .bind_tools() 메서드를 구현하여 LangChain 도구 객체, Pydantic 클래스 또는 JSON 스키마 목록을 수신하고 공급자별 예상 형식으로 채팅 모델에 바인딩한다.

```python
import re
import requests
from langchain_core.output_parsers import JsonOutputToolsParser

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


# 도구를 정의합니다.
@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

@tool
def add_function(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

@tool
def naver_news_crawl(news_url: str) -> str:
    """Crawls a 네이버 (naver.com) news article and returns the body content."""
    # HTTP GET 요청 보내기
    response = requests.get(news_url)

    # 요청이 성공했는지 확인
    if response.status_code == 200:
        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # 원하는 정보 추출
        title = soup.find("h2", id="title_area").get_text()
        content = soup.find("div", id="contents").get_text()
        cleaned_title = re.sub(r"\n{2,}", "\n", title)
        cleaned_content = re.sub(r"\n{2,}", "\n", content)
    else:
        print(f"HTTP 요청 실패. 응답 코드: {response.status_code}")

    return f"{cleaned_title}\n{cleaned_content}"

def execute_tool_calls(tool_call_results):
    """
    도구 호출 결과를 실행하는 함수

    :param tool_call_results: 도구 호출 결과 리스트
    :param tools: 사용 가능한 도구 리스트
    """
    # 도구 호출 결과 리스트를 순회합니다.
    for tool_call_result in tool_call_results:
        # 도구의 이름과 인자를 추출합니다.
        tool_name = tool_call_result["type"]  # 도구의 이름(함수명)
        tool_args = tool_call_result["args"]  # 도구에 전달되는 인자

        # 도구 이름과 일치하는 도구를 찾아 실행합니다.
        # next() 함수를 사용하여 일치하는 첫 번째 도구를 찾습니다.
        matching_tool = next((tool for tool in tools if tool.name == tool_name), None)

        if matching_tool:
            # 일치하는 도구를 찾았다면 해당 도구를 실행합니다.
            result = matching_tool.invoke(tool_args)
            # 실행 결과를 출력합니다.
            print(f"[실행도구] {tool_name} [Argument] {tool_args}\n[실행결과] {result}")
        else:
            # 일치하는 도구를 찾지 못했다면 경고 메시지를 출력합니다.
            print(f"경고: {tool_name}에 해당하는 도구를 찾을 수 없습니다.")


tools = [get_word_length, add_function, naver_news_crawl]

llm = ChatOpenAI(temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 전체 조합
chain = llm_with_tools | JsonOutputToolsParser(tools=tools) | execute_tool_calls

# 1
chain.invoke("What is the length of the word 'teddynote'?")
# 2
chain.invoke("114.5 + 121.2")
print(114.5 + 121.2)
# 3
chain.invoke(
    "뉴스 기사 내용을 크롤링해줘: https://n.news.naver.com/mnews/hotissue/article/092/0002347672?type=series&cid=2000065"
)
```



## Tool Calling Agent

### AgentExecutor

- AgentExecutor는 도구를 사용하는 에이전트를 실행하는 클래스입니다.

**주요 속성**

- `agent`: 실행 루프의 각 단계에서 계획을 생성하고 행동을 결정하는 에이전트
- `tools`: 에이전트가 사용할 수 있는 유효한 도구 목록
- `return_intermediate_steps`: 최종 출력과 함께 에이전트의 중간 단계 경로를 반환할지 여부
- `max_iterations`: 실행 루프를 종료하기 전 최대 단계 수
- `max_execution_time`: 실행 루프에 소요될 수 있는 최대 시간
- `early_stopping_method`: 에이전트가 `AgentFinish`를 반환하지 않을 때 사용할 조기 종료 방법. ("force" or "generate")
  - `"force"` 는 시간 또는 반복 제한에 도달하여 중지되었다는 문자열을 반환합니다.
  - `"generate"` 는 에이전트의 LLM 체인을 마지막으로 한 번 호출하여 이전 단계에 따라 최종 답변을 생성합니다.
- `handle_parsing_errors`: 에이전트의 출력 파서에서 발생한 오류 처리 방법. (True, False, 또는 오류 처리 함수)
- `trim_intermediate_steps`: 중간 단계를 트리밍하는 방법. (-1 trim 하지 않음, 또는 트리밍 함수)

**주요 메서드**

1. `invoke`: 에이전트 실행
2. `stream`: 최종 출력에 도달하는 데 필요한 단계를 스트리밍

**주요 기능**

1. **도구 검증**: 에이전트와 호환되는 도구인지 확인
2. **실행 제어**: 최대 반복 횟수 및 실행 시간 제한 설정 가능
3. **오류 처리**: 출력 파싱 오류에 대한 다양한 처리 옵션 제공
4. **중간 단계 관리**: 중간 단계 트리밍 및 반환 옵션
5. **비동기 지원**: 비동기 실행 및 스트리밍 지원

**최적화 팁**

- `max_iterations`와 `max_execution_time`을 적절히 설정하여 실행 시간 관리
- `trim_intermediate_steps`를 활용하여 메모리 사용량 최적화
- 복잡한 작업의 경우 `stream` 메서드를 사용하여 단계별 결과 모니터링

```python
from langchain.tools import tool
from typing import List, Dict, Annotated

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_teddynote.tools import GoogleNews
from langchain_experimental.utilities import PythonREPL


# 도구 생성
@tool
def search_news(query: str) -> List[Dict[str, str]]:
    """Search Google News by input keyword"""
    news_tool = GoogleNews()
    return news_tool.search_by_keyword(query, k=5)


# 도구 생성
@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    result = ""
    try:
        result = PythonREPL().run(code)
    except BaseException as e:
        print(f"Failed to execute. Error: {repr(e)}")
    finally:
        return result

tools = [search_news, python_repl_tool]
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
# LLM 정의
llm = ChatOpenAI(temperature=0)

# Agent 생성
agent = create_tool_calling_agent(llm, tools, prompt)
# AgentExecutor 생성
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    max_execution_time=10,
    handle_parsing_errors=True,
)

# AgentExecutor 실행
result = agent_executor.invoke({"input": "AI 투자와 관련된 뉴스를 검색해 주세요."})
```



### + stream

- AgentExecutor의 `stream()` 메소드를 사용하여 에이전트의 중간 단계를 스트리밍을 사용하게 된다.
- 각 단계
  1. Action 출력
  2. Observation 출력
  3. <반복>
  4. 최종 답변

| 출력         | 내용                                                         |
| ------------ | ------------------------------------------------------------ |
| Action       | `actions`: AgentAction 또는 그 하위 클래스 <br>`messages`: 액션 호출에 해당하는 채팅 메시지 |
| Observation  | `steps`: 현재 액션과 그 관찰을 포함한 에이전트가 지금까지 수행한 작업의 기록 <br>`messages`: 함수 호출 결과(즉, 관찰)를 포함한 채팅 메시지 |
| Final Answer | `output`: AgentFinish <br>`messages`: 최종 출력을 포함한 채팅 메시지 |

```python
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

llm = ChatOpenAI()
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

```



## MultiTurn

- 

```python
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



```



### iter 함수

```python
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
```

