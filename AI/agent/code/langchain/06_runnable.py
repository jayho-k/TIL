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
