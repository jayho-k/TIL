# 01_basic



## 01) Template

```python
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
```

- 중간 과정에서 변수가 필요한 경우 또는 로직이 필요한 경우 변수 값 또는 함수 값을 넣어서 진행하면 된다.



## 02) 파일로 Template 읽어오기

```python
from langchain_core.prompts import load_prompt

prompt_fruit_color = load_prompt("prompts/fruit_color.yaml")
prompt_capital = load_prompt("prompts/capital.yaml")
```

- 이런식으로 미리 프롬프트를 가져와서 load 하면 된다.



## 03) ChatPromptTemplate

> - 대화형으로 답변을 낼 때 사용

- system : 시스템 설정 메시시. 주로 전역설정과 관련된 프롬프트
- human : 사용자 입력 메시지
- ai : AI 의 답변 메시지

```python
from langchain_core.prompts import ChatPromptTemplate

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
```



## 03_MessagePlaceholder

- 아직 확정된 메시지가 아니지만 나중에 추가될 메시지를 잡아두는 것
- 대화 내용을 기록하고자 할 때 

```python

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

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

```



## Few Shot

- few shot : 
  - 몇 개의 예시를 보여주면서 답변을 얻어내는 경우
  - 예시가 여러개 있으면 더 잘 답변하게된다.
  - 대화의 흐름으로 게속해서 질문 답변에 대한 예시를 주면서 다음 답을 원하는 답으로 추가하는 방법

```python
from langchain_core.prompts import FewShotPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

prompt = FewShotPromptTemplate(
    examples = examples,
    example_prompt=example_prompt,
    suffix = "Question: \n{question}\nAnswer:",
    input_variables=["question"],
)

question = "Google 이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"
final_prompt = prompt.format(question=question)
```



### Selector

- **MaxMarginaRelevanceExampleSelector**

  - 관련성 : 
    - 검색 쿼리나 주제와 문서의 관련성을 평가
    - 보통 문서가 주어진 쿼리와 얼마나 잘 일치하는지를 나타내ㅐ는 점수로 표현
  - 다양성 : 
    - 이미 선택된 문서와 유사성을 평가
    - 선택과정에서 문서 간의 다양성을 보장한다.
    - 문서간의 유사성을 계산하여, 이미 선택된 문서와 비슷한 새 문서의 선택 가능성을 낮춘다.

  - 과정
    - 가장 관련성이 높은 항목을 선택
    - 각 단계에서 현재 선택된 항목들과 관련성은 높으면서도 가장 파별화된 항목을 찾아 선택
    - 람다 값에 의해 조절되며, 이 값이 클수록 관련성, 작을수록 다양성을 중시

- **SemanticSimilarityExampleSelector**
  - 유사도 기준으로 select 하는 것
  - 문제 : 모든 예시가 



## FewShotChatMessagePrompt

```python
from langchain_core.prompts import FewShotPromptTemplate, ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI

# llm = ChatOpenAI()
#
# prompt = FewShotPromptTemplate(
#     examples = examples,
#     example_prompt=example_prompt,
#     suffix = "Question: \n{question}\nAnswer:",
#     input_variables=["question"],
# )
#
# question = "Google 이 창립된 연도에 Bill Gates의 나이는 몇 살인가요?"
# final_prompt = prompt.format(question=question)
#
# #

from langchain_core.example_selectors import (
    SemanticSimilarityExampleSelector
)
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

examples = [
    {
        "instruction": "당신은 회의록 작성 전문가 입니다. 주어진 정보를 바탕으로 회의록을 작성해 주세요",
        "input": "2023년 12월 25일, XYZ 회사의 마케팅 전략 회의가 오후 3시에 시작되었다. 회의에는 마케팅 팀장인 김수진, 디지털 마케팅 담당자인 박지민, 소셜 미디어 관리자인 이준호가 참석했다. 회의의 주요 목적은 2024년 상반기 마케팅 전략을 수립하고, 새로운 소셜 미디어 캠페인에 대한 아이디어를 논의하는 것이었다. 팀장인 김수진은 최근 시장 동향에 대한 간략한 개요를 제공했으며, 이어서 각 팀원이 자신의 분야에서의 전략적 아이디어를 발표했다.",
        "answer": """
회의록: XYZ 회사 마케팅 전략 회의
일시: 2023년 12월 25일
장소: XYZ 회사 회의실
참석자: 김수진 (마케팅 팀장), 박지민 (디지털 마케팅 담당자), 이준호 (소셜 미디어 관리자)

1. 개회
   - 회의는 김수진 팀장의 개회사로 시작됨.
   - 회의의 목적은 2024년 상반기 마케팅 전략 수립 및 새로운 소셜 미디어 캠페인 아이디어 논의.

2. 시장 동향 개요 (김수진)
   - 김수진 팀장은 최근 시장 동향에 대한 분석을 제시.
   - 소비자 행동 변화와 경쟁사 전략에 대한 통찰 공유.

3. 디지털 마케팅 전략 (박지민)
   - 박지민은 디지털 마케팅 전략에 대해 발표.
   - 온라인 광고와 SEO 최적화 방안에 중점을 둠.

4. 소셜 미디어 캠페인 (이준호)
   - 이준호는 새로운 소셜 미디어 캠페인에 대한 아이디어를 제안.
   - 인플루언서 마케팅과 콘텐츠 전략에 대한 계획을 설명함.

5. 종합 논의
   - 팀원들 간의 아이디어 공유 및 토론.
   - 각 전략에 대한 예산 및 자원 배분에 대해 논의.

6. 마무리
   - 다음 회의 날짜 및 시간 확정.
   - 회의록 정리 및 배포는 박지민 담당.
""",
    },
    {
        "instruction": "당신은 요약 전문가 입니다. 다음 주어진 정보를 바탕으로 내용을 요약해 주세요",
        "input": "이 문서는 '지속 가능한 도시 개발을 위한 전략'에 대한 20페이지 분량의 보고서입니다. 보고서는 지속 가능한 도시 개발의 중요성, 현재 도시화의 문제점, 그리고 도시 개발을 지속 가능하게 만들기 위한 다양한 전략을 포괄적으로 다루고 있습니다. 이 보고서는 또한 성공적인 지속 가능한 도시 개발 사례를 여러 국가에서 소개하고, 이러한 사례들을 통해 얻은 교훈을 요약하고 있습니다.",
        "answer": """
문서 요약: 지속 가능한 도시 개발을 위한 전략 보고서

- 중요성: 지속 가능한 도시 개발이 필수적인 이유와 그에 따른 사회적, 경제적, 환경적 이익을 강조.
- 현 문제점: 현재의 도시화 과정에서 발생하는 주요 문제점들, 예를 들어 환경 오염, 자원 고갈, 불평등 증가 등을 분석.
- 전략: 지속 가능한 도시 개발을 달성하기 위한 다양한 전략 제시. 이에는 친환경 건축, 대중교통 개선, 에너지 효율성 증대, 지역사회 참여 강화 등이 포함됨.
- 사례 연구: 전 세계 여러 도시의 성공적인 지속 가능한 개발 사례를 소개. 예를 들어, 덴마크의 코펜하겐, 일본의 요코하마 등의 사례를 통해 실현 가능한 전략들을 설명.
- 교훈: 이러한 사례들에서 얻은 주요 교훈을 요약. 강조된 교훈에는 다각적 접근의 중요성, 지역사회와의 협력, 장기적 계획의 필요성 등이 포함됨.

이 보고서는 지속 가능한 도시 개발이 어떻게 현실적이고 효과적인 형태로 이루어질 수 있는지에 대한 심도 있는 분석을 제공합니다.
""",
    },
    {
        "instruction": "당신은 문장 교정 전문가 입니다. 다음 주어진 문장을 교정해 주세요",
        "input": "우리 회사는 새로운 마케팅 전략을 도입하려고 한다. 이를 통해 고객과의 소통이 더 효과적이 될 것이다.",
        "answer": "본 회사는 새로운 마케팅 전략을 도입함으로써, 고객과의 소통을 보다 효과적으로 개선할 수 있을 것으로 기대된다.",
    },
]

chroma = Chroma("fewshot_chat", OpenAIEmbeddings())
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{instruction}:\n{input}"),
        ("ai", "{answer}")
    ]
)

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    chroma,
    k=1,
)

few_shot_prompt = FewShotChatMessagePromptTemplate(example_selector=example_selector, example_prompt=example_prompt)

final_template = ChatPromptTemplate.from_messages(
    [("system", "You are a helpful assistant."), few_shot_prompt, ("human", "{instruction}\n{input}")])

chain = final_template | llm
```



##  Output Parser

- 출력을 더 유용하고 구조화된 형태로 변환하는 컴포넌트

### PydanticOutputParser

- 유효성 검사 라이브러리
- 정보를 명확하고 체계적인 형태로 제공하기 위함

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# pydentic
email_conversation = """From: 김철수 (chulsoo.kim@bikecorporation.me)
To: 이은채 (eunchae@teddyinternational.me)
Subject: "ZENESIS" 자전거 유통 협력 및 미팅 일정 제안

안녕하세요, 이은채 대리님,

저는 바이크코퍼레이션의 김철수 상무입니다. 최근 보도자료를 통해 귀사의 신규 자전거 "ZENESIS"에 대해 알게 되었습니다. 바이크코퍼레이션은 자전거 제조 및 유통 분야에서 혁신과 품질을 선도하는 기업으로, 이 분야에서의 장기적인 경험과 전문성을 가지고 있습니다.

ZENESIS 모델에 대한 상세한 브로슈어를 요청드립니다. 특히 기술 사양, 배터리 성능, 그리고 디자인 측면에 대한 정보가 필요합니다. 이를 통해 저희가 제안할 유통 전략과 마케팅 계획을 보다 구체화할 수 있을 것입니다.

또한, 협력 가능성을 더 깊이 논의하기 위해 다음 주 화요일(1월 15일) 오전 10시에 미팅을 제안합니다. 귀사 사무실에서 만나 이야기를 나눌 수 있을까요?

감사합니다.

김철수
상무이사
바이크코퍼레이션
"""
class EmailSummary(BaseModel):
    person: str = Field(description="메일을 보낸 사람")
    email: str = Field(description="메일을 보낸 사람의 이메일 주소")
    subject: str = Field(description="메일 제목")
    summary: str = Field(description="메일 본문을 요약한 텍스트")
    date: str = Field(description="메일 본문에 언급된 미팅 날짜와 시간")

llm = ChatOpenAI(temperature=0)
prompt = PromptTemplate.from_template(
    """
You are a helpful assistant. Please answer the following questions in KOREAN.

QUESTION:
{question}

EMAIL CONVERSATION:
{email_conversation}

FORMAT:
{format}
"""
)

# format 에 PydanticOutputParser의 부분 포맷팅(partial) 추가
parser = PydanticOutputParser(pydantic_object=EmailSummary)
prompt = prompt.partial(format=parser.get_format_instructions())
chain = prompt | llm | parser

# chain 을 실행하고 결과를 출력.
response = chain.stream(
    {
        "email_conversation": email_conversation,
        "question": "이메일 내용 중 주요 내용을 추출해 주세요.",
    }
)

# 결과는 JSON 형태로 출력
output = ""
for res in response:
    output += res

# PydanticOutputParser 를 사용하여 결과를 파싱합니다.
structured_output = parser.parse(output)
print(structured_output)

```



### with_structured_output

- 다음은 위와 같이 parser를 따로 생성하지 않고 바로 함수로 사용하는 방법이다.
- **이 방법은 stream을 지원하지 않는다.** 

```python
llm_with_structered = ChatOpenAI(
    temperature=0, model_name="gpt-4.1-mini"
).with_structured_output(EmailSummary)

# invoke() 함수를 호출하여 결과를 출력합니다.
answer = llm_with_structered.invoke(email_conversation)
answer
```



### CommaSeparatedListOutputParser

- 쉼표로 구분된 항목 목록을 반환할 필요가 있을 때 사용함

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 콤마로 구분된 리스트 출력 파서 초기화
output_parser = CommaSeparatedListOutputParser()

# 출력 형식 지침 가져오기
format_instructions = output_parser.get_format_instructions()
# 프롬프트 템플릿 설정
prompt = PromptTemplate(
    # 주제에 대한 다섯 가지를 나열하라는 템플릿
    template="List five {subject}.\n{format_instructions}",
    input_variables=["subject"],  # 입력 변수로 'subject' 사용
    # 부분 변수로 형식 지침 사용
    partial_variables={"format_instructions": format_instructions},
)

# ChatOpenAI 모델 초기화
model = ChatOpenAI(temperature=0)

# 프롬프트, 모델, 출력 파서를 연결하여 체인 생성
chain = prompt | model | output_parser
chain.invoke({"subject": "대한민국 관광명소"})
```

- list 형식으로 나오게 된다.
- **stream 기능을 사용하지 않는 것이 맞음** 
  - 만약에 stream 으로 사용하게 되면 각각을 list 형태로 나오게 된다.
  - ex_[1], [2], [3] 이런식으로 나옴 >> 원래는 [1,2,3] 이렇게 나와야 함



### StructuredOuputParser

- LLM에 대한 답변을 dict 형식으로 구성할 때 사용
- Pydantic을 사용하지 못하고 StructuredOuputParser 를 사용해야할 때가 있음
- **local llm등을 사용할 때 제대로 parsing하지 못하는 경우가 있음.** 따라서 StructuredOuputParser 를 사용해서 진행할 때 사용하게 된다.
- **descroption 등도 영어로 작성하는 것이 좋음**
  - llm 성능이 낮게 되면 영어를 더 잘 알아듣기 때문

```python
from langchain_core.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 사용자의 질문에 대한 답변
response_schemas = [
    ResponseSchema(name="answer", description="사용자의 질문에 대한 답변"),
    ResponseSchema(
        name="source",
        description="사용자의 질문에 답하기 위해 사용된 `출처`, `웹사이트주소` 이여야 합니다.",
    ),
]
# 응답 스키마를 기반으로 한 구조화된 출력 파서 초기화
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 출력 형식 지시사항을 파싱합니다.
format_instructions = output_parser.get_format_instructions()
prompt = PromptTemplate(
    # 사용자의 질문에 최대한 답변하도록 템플릿을 설정합니다.
    template="answer the users question as best as possible.\n{format_instructions}\n{question}",
    # 입력 변수로 'question'을 사용합니다.
    input_variables=["question"],
    # 부분 변수로 'format_instructions'을 사용합니다.
    partial_variables={"format_instructions": format_instructions},
)

model = ChatOpenAI(temperature=0)  # ChatOpenAI 모델 초기화
chain = prompt | model | output_parser  # 프롬프트, 모델, 출력 파서를 연결
chain.invoke({"question": "대한민국의 수도는 어디인가요?"})
```



### JsonOuputParser

- json으로 진행하기 위해선 큰 용량의 LLM이 필요하게 된다.

```python
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
```



### DatetimeOutputParser

| 형식 코드 | 설명               | 예시                    |
| --------- | ------------------ | ----------------------- |
| %Y        | 4자리 연도         | 2024                    |
| %y        | 2자리 연도         | 24                      |
| %m        | 2자리 월           | 07                      |
| %d        | 2자리 일           | 04                      |
| %H        | 24시간제 시간      | 14                      |
| %I        | 12시간제 시간      | 02                      |
| %p        | AM 또는 PM         | PM                      |
| %M        | 2자리 분           | 45                      |
| %S        | 2자리 초           | 08                      |
| %f        | 마이크로초 (6자리) | 000123                  |
| %z        | UTC 오프셋         | +0900                   |
| %Z        | 시간대 이름        | KST                     |
| %a        | 요일 약어          | Thu                     |
| %A        | 요일 전체          | Thursday                |
| %b        | 월 약어            | Jul                     |
| %B        | 월 전체            | July                    |
| %c        | 전체 날짜와 시간   | Thu Jul 4 14:45:08 2024 |
| %x        | 전체 날짜          | 07/04/24                |
| %X        | 전체 시간          | 14:45:08                |

```python
from langchain.output_parsers import DatetimeOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 날짜 및 시간 출력 파서
output_parser = DatetimeOutputParser()
output_parser.format = "%Y-%m-%d"

# 사용자 질문에 대한 답변 템플릿
template = """Answer the users question:\n\n#Format Instructions: \n{format_instructions}\n\n#Question: \n{question}\n\n#Answer:"""

prompt = PromptTemplate.from_template(
    template,
    partial_variables={
        "format_instructions": output_parser.get_format_instructions()
    },  # 지침을 템플릿에 적용
)

chain = prompt | ChatOpenAI() | output_parser
output = chain.invoke({"question": "Google 이 창업한 연도"})
```



### EnumOutputParser

- 답변을 선택지 중 하나를 선택하게 끔 만들고 싶을 때 사용한다.
- 하지만 현재는 with_structured_output 를 사용하는 것을 권장한다.

```python
from langchain_core.output_parsers import E
from enum import Enum

from langchain_openai import ChatOpenAI


class Colors(Enum):
    RED = "빨간색"
    GREEN = "초록색"
    BLUE = "파란색"

llm = ChatOpenAI()
structured_llm = llm.with_structured_output(Colors)
response = structured_llm.invoke({"object": "하늘"})
print(response)

```

















