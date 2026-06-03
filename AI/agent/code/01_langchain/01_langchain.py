from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    temperature=0.1,
    model_name=""
)

question = "대한민국의 수도는?"
response1 = llm.invoke(question)

# content : 답변
# response_metadata : 메타 data


# LogProb 활성화
llm_with_logprob = ChatOpenAI(
    temperature=0.1,
    max_tokens=2028,
    model_name=""
).bind(logprobs=True)

response2 = llm_with_logprob.invoke(question)
print(response2)


# streaminig 출력
answer = llm.stream(question)
for token in answer:
    print(token.content, end="", flush=True)








