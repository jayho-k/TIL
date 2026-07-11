from time import time
from langchain_openai import ChatOpenAI

OLLAMA_BASE_URL = "https://jayho-macmini.tail60408a.ts.net/v1"
OLLAMA_MODEL = "gemma4:26b-a4b-it-qat"

llm = ChatOpenAI(
    api_key="ollama",
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=0.1,
    max_tokens=2028,
    reasoning_effort="none",
    # model_kwargs={"reasoning_effort": "none"}
)

start_time = time()
question = "나랑 게임하자: 안녕 클레오파트라"
response1 = llm.invoke(question)
end_time = time()

print(f"{end_time-start_time} s" )


# content: answer
# response_metadata: model/provider metadata
print(response1)


# Enable logprobs. Ollama support can vary by model/version.
llm_with_logprob = llm.bind(logprobs=True)

response2 = llm_with_logprob.invoke(question)
print(response2)


# Streaming output
answer = llm.stream(question)
for token in answer:
    print(token.content, end="", flush=True)
