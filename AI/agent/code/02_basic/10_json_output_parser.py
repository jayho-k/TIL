# 프롬프트 템플릿을 설정합니다.
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.channels import Topic

# 질의 작성
question = "지구 온난화의 심각성 대해 알려주세요."
model = ChatOpenAI(temperature=0, model_name="gpt-4.1-mini")

# 파서를 설정하고 프롬프트 템플릿에 지시사항을 주입합니다.
parser = JsonOutputParser(pydantic_object=Topic)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절한 AI 어시스턴트 입니다. 질문에 간결하게 답변하세요."),
        ("user", "#Format: {format_instructions}\n\n#Question: {question}"),
    ]
)
prompt = prompt.partial(format_instructions=parser.get_format_instructions())

# 체인을 구성합니다.
chain = prompt | model | parser

# 체인을 호출하여 쿼리 실행
answer = chain.invoke({"question": question})