from langchain_core.output_parsers import E
from enum import Enum

from langchain_openai import ChatOpenAI


class Colors(Enum):
    RED = "빨간색"
    GREEN = "초록색"
    BLUE = "파란색"

llm = ChatOpenAI()
structured_llm = llm.with_structured_output(Colors)
response = structured_llm.invoke({"object": "하늘"})
print(response)
