from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template("{num} 의 10배는?")
model = ChatOpenAI(temperature=0)
chain = prompt | model

# RunnablePassthrough
# 사용자가 값만 전달하게 되면 값이 RunnablePassthrough에 들어온다.
runnable_chain = {
    "num": RunnablePassthrough()
} | prompt | model

runnable_chain.invoke(10)

# RunnablePassthrough.assign()
# 입력으로 들어온 값 + 새로 할단된 값을 key/vlaude 쌍을 합치게 된다.
# 답변 : {num:1, new_num:3}
(RunnablePassthrough.assign(new_num= lambda x : x["num"] * 3)).invoke({"num": 1})


# RunnablePassthrough 통합 예시
runnable = RunnableParallel(
    passed=RunnablePassthrough(), # {passed:1}
    extra=RunnablePassthrough.assign(multi=lambda x : x["num"] * 3), # {passed:1, extra:3}
    modified=lambda x : x["num"] + 1 # 2
)
runnable.invoke({"num":1})

chain1 = (
    {"country": RunnablePassthrough()}
    | PromptTemplate.from_template("{country} 의 수도는 어디야?")
    | model
)
chain2 = (
    {"country": RunnablePassthrough()}
    | PromptTemplate.from_template("{country} 의 면적은 얼마야?")
    | model
)
combined = RunnableParallel(
    capital=chain1,
    area=chain2
)
combined.invoke("대한민국")

# RunnableLambda
from langchain_core.runnables import RunnableLambda
from operator import itemgetter

def get_today(a):
    # RunnablePassthrough에 들어간 값이 들어가게 된다.
    # 따라서 invoke(3) 을 넣으주면 a의 값은 3이 들어가게된다.
    return datetime.today().strftime("%b-%d")

prompt = PromptTemplate.from_template(
    "{today} 가 생일인 유명인 {n} 명을 나열하세요. 생년월일을 표기해 주세요."
)
model = ChatOpenAI(temperature=0)
runnable_lambda_chain = (
    # {"today": RunnableLambda(get_today), "n":{"n": RunnablePassthrough()}}
    {"today": RunnableLambda(get_today), "n":{"n": itemgetter("n")}}
    | prompt
    | model
    | StrOutputParser()
)
print(runnable_lambda_chain.invoke(3))

# + 다중 인자
def length_function(text):
    return len(text)
def _multiple_length_function(text1, text2):
    return len(text1) * len(text2)
def multiple_length_function(_dict):
    return _multiple_length_function(_dict["text1"], _dict["text2"])

prompt = PromptTemplate.from_template(
    "{} + {} 는 무엇인가요?"
)
model = ChatOpenAI(temperature=0)
runnable_lambda_chain = (
    {
        "a":itemgetter("word1") | RunnableLambda(length_function),
        "b": {"text1":itemgetter("word1"),"text2":itemgetter("word2")} | RunnableLambda(multiple_length_function)
    }
    | prompt
    | model
    | StrOutputParser()
)
print(runnable_lambda_chain.invoke(3))





