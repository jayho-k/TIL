from datetime import datetime

from langchain_core.prompts import PromptTemplate

# basic
prompt_basic = PromptTemplate.from_template("{country} 의 수도는?")

# input_variable
template = "{country} 의 수도는?"
prompt_input_variable = PromptTemplate(
    template=template,
    input_variables=["country"]
)

# partial_variable
# 중간 과정에서 변수를 결정할 경우에 사용하면 된다.
template = "{country1}와 {country2} 의 수도는?"
prompt_partial_variable = PromptTemplate(
    template=template,
    input_variables=["country1"],
    partial_variables={
        "country2":"미국"
    }
)
# 예시 - 보통은 함수를 넣어서 많이 사용한다.
def get_today():
    return datetime.now().strftime("%B %d")

prompt = PromptTemplate(
    template = "오늘 날짜는 {today} 입니다. 오늘이 생일인 유명인 3명을 나열해주세요.",
    input_variable=["n"],
    partial_variables={
        "today":get_today
    }
)












