from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template("{topic}에 대해서 설명해주세요.")
model = ChatOpenAI()

chain1 = (
    PromptTemplate.from_template("{country} 의 수도는 어디야?")
    | model
    | StrOutputParser()
)
chain2 = (
    PromptTemplate.from_template("{country} 의 면적은 얼마야?")
    | model
    | StrOutputParser()
)

combined = RunnableParallel(
    capital=chain1,
    area=chain2
)

combined.invoke({"country":"대한민국"})

# + batch
combined.batch(
    {"country": "대한민국"},
    {"country": "미국"},
)
