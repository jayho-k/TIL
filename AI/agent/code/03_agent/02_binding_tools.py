
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



