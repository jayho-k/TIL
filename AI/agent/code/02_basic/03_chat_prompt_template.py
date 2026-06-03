from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

# 대화형을 만들어두
chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절한 AI 어시스턴스입니다. 당신의 이름은 {name} 입니다."),
        ("human", "반가워요!"),
        ("ai", "안녕하세요! 무엇을 도와드릴까요?"),
        ("human", "{user_input}")
    ])

chat_template.format_messages(
    name="테디", user_input="당신의 이름은 무엇입니까?"
)

# + message placeholder
chat_prompt = ChatPromptTemplate.from_messages(
        [MessagesPlaceholder(variable_name="conversation"),
        ("human", "지금까지의 대화를 {word_count} 단어로 요약합니다.")]
)
chat_prompt.format(
    word_count=5,
    conversation=[
        ("human", "안녕하세요! 저는 오늘 새로 입사한 테디 입니다. 만나서 반갑습니다."),
        ("ai", "반가워요! 앞으로 잘 부탁 드립니다.")
    ]
)

# ----
llm = ChatOpenAI()

chain = chat_prompt | llm
chain.invoke(
    {
        "word_count":5,
        "conversation":[
        ("human", "안녕하세요! 저는 오늘 새로 입사한 테디 입니다. 만나서 반갑습니다."),
        ("ai", "반가워요! 앞으로 잘 부탁 드립니다.")
    ]
    }
)

