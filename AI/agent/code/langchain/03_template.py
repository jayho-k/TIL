from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template("{topic}에 대해 {how} 설명해주세요.")
model = ChatOpenAI()

chain = prompt | model

# 주의할 점 : 여기서 key값의 topic과 위의 {topic}은 세트이기 때문에 반드시 맞춰줘야 한다.
# 만약 how를 빼게 된다고 하더라도 에러가 나게 된다.
input = {
    "topic": "인공지능 모델의 학습 원리",
    "how": "간단하게"
}

chain.invoke(input)


# + output parser
output_parser = StrOutputParser()
template = """
당신은 영어를 가르치는 10년차 선생님입니다. 주어진 상황에 맞는 영어 호화를 작성해 주세요.
양식은 [FORMAT]을 참고하여 작성해 주세요.

# 상황
{question}

# FORMAT
- 영어 회화 :
- 한글 해석 :
"""

chain = prompt | model | output_parser
chain.invoke({"question":"저는 식당에 가서 음식을 주문하고 싶어요."})





