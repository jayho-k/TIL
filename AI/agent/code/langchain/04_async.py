from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template("{topic}에 대해서 설명해주세요.")
model = ChatOpenAI()
output_parser = StrOutputParser()

chain = prompt | model | output_parser

# astream
async for token in chain.astream({"topic": "YouTube"}):
    print(token, end="", flush=True)

# ainvoke
my_process = chain.ainvoke({"topic": "NVIDIA"})
await my_process

# abatch
batch = chain.abatch({"topic": "NVIDIA"})
await batch