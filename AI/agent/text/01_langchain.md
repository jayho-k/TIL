# 01_langchain

## 01_LangChaing이란

- LLMs 로 구동되는 애플리케이션을 개발하기 위한 프레임워크
- temperature  : 0~0.2 사이에서 선택
- max_tokens : 답변에 대한 최대 출력 토큰 수
- System Prompt
  - 전역으로 들어가는 것이기 때문에 **페리소나, 임무** 를 주로 넣어준다.

**LogProb**

- 주어진 텍스트에 대한 모델의 토큰 확률의 로그 값을 의미
- 0에 가까운 값일 수록 높은 확률
- 확률이 낮을수록 음수(-무한대)로 가게 된다.

```python
# LogProb 활성화
llm_with_logprob = ChatOpenAI(
    temperature=0.1,
    max_tokens=2028,
    model_name=""
).bind(logprobs=True)

response2 = llm_with_logprob.invoke(question)
print(response2)

```

- 이렇게 하면 각 토큰별로 확률이 나오게 된다.
  - temperature에 따라서 각 값이 다르게 설정되어 나올 듯
- ex)
  - 우리 / 집 / 은 ...
  - 우리 : 0.01
  - 집  : -0.001



## Multimodal

- 멀티모달은 여러가지 형태의 정보를 통합하여, 처리하는 기술이나 접근 방식
- 해상도가 높을수록 잘 인식하기 때문에 이미지를 넣을 때 어떤 해상도로 넣을지 확인하는것이 중요할 듯

```python
class MultiModal:
    def __init__(self, model, system_prompt=None, user_prompt=None):
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.init_prompt()

    def init_prompt(self):
        if self.system_prompt is None:
            self.system_prompt = "You are a helpful assistant on parsing images."
        if self.user_prompt is None:
            self.user_prompt = "Explain the given images in-depth."

    # 이미지를 base64로 인코딩하는 함수 (URL)
    def encode_image_from_url(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            image_content = response.content
            if url.lower().endswith((".jpg", ".jpeg")):
                mime_type = "image/jpeg"
            elif url.lower().endswith(".png"):
                mime_type = "image/png"
            else:
                mime_type = "image/unknown"
            return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"
        else:
            raise Exception("Failed to download image")

    # 이미지를 base64로 인코딩하는 함수 (파일)
    def encode_image_from_file(self, file_path):
        with open(file_path, "rb") as image_file:
            image_content = image_file.read()
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif file_ext == ".png":
                mime_type = "image/png"
            else:
                mime_type = "image/unknown"
            return f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"

    # 이미지 경로에 따라 적절한 함수를 호출하는 함수
    def encode_image(self, image_path):
        if image_path.startswith("http://") or image_path.startswith("https://"):
            return self.encode_image_from_url(image_path)
        else:
            return self.encode_image_from_file(image_path)

    def display_image(self, encoded_image):
        display(Image(url=encoded_image))

    def create_messages(
        self, image_url, system_prompt=None, user_prompt=None, display_image=True
    ):
        encoded_image = self.encode_image(image_url)
        if display_image:
            self.display_image(encoded_image)

        system_prompt = (
            system_prompt if system_prompt is not None else self.system_prompt
        )

        user_prompt = user_prompt if user_prompt is not None else self.user_prompt

        # 인코딩된 이미지를 사용하여 다른 처리를 수행할 수 있습니다.
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{encoded_image}"},
                    },
                ],
            },
        ]
        return messages

    def invoke(
        self, image_url, system_prompt=None, user_prompt=None, display_image=True
    ):
        messages = self.create_messages(
            image_url, system_prompt, user_prompt, display_image
        )
        response = self.model.invoke(messages)
        return response.content

    def batch(
        self,
        image_urls: list[str],
        system_prompts: list[str] = [],
        user_prompts: list[str] = [],
        display_image=False,
    ):
        messages = []
        for image_url, system_prompt, user_prompt in zip(
            image_urls, system_prompts, user_prompts
        ):
            message = self.create_messages(
                image_url, system_prompt, user_prompt, display_image
            )
            messages.append(message)
        response = self.model.batch(messages)
        return [r.content for r in response]

    def stream(
        self, image_url, system_prompt=None, user_prompt=None, display_image=True
    ):
        messages = self.create_messages(
            image_url, system_prompt, user_prompt, display_image
        )
        response = self.model.stream(messages)
        return response

```



## Prompt

- PromptTemplate
  - 사용자의 입력 변수를 사용하여 완전한 프롬프트 문자열을 만드는 데 사용되는 템플릿
  - 사용법
    - template : 템플릿 문자열. 이 문자열 내에서 중괄호 {} 는 변수를 나타낸다. 
    - input_variables : Prompttemplate에서 사용되는 변수의 이름을 정의하는 리스트

**LCEL (LangChain Expression Lnaguage)**

- **dict >> Prompt >> LLM >> OutputParser**
- 위와 같은 순서로 langchain을 이어 붙어붙여서 답변을 내놓게 된다.
- chain = prompt | model | ouptu_parser

```python
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

```



**OutputParser**

- 출력되는 타입이나, 형태 등을 만들어주는 역할을 한다.
- template에 # 등(markdown) 방식을 사용하게 되면 llm이 더 잘 인식하는 경향이 있음

```python
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
```



## LCEL 인터페이스

- 사용자 정의 체인을 가능한 쉽게 만들 수 있도록, Runnable 프로토콜을 구현
  - 표준 Interface
    - stream
    - invoke
    - batch
  - 비동기 메소드 
    - astream : 비동기적으로 응답의 청크를 스트리밍한다.
    - ainvoke : 비동기적으로 입력에 대해 체인을 호출 
    - abatch : 
    - astream_log : 최종 응답뿐만 아니라 발생하는 중간 단계를 스트리밍

```python
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
```



## Parallel

- 동시에 처리하는 병렬 방식

```python
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

```



## RunnablePassthrough

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
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
```



## RunnablParallel

- 예시

```python
# RunnablePassthrough 통합 예시
runnable = RunnableParallel(
    passed=RunnablePassthrough(), # {passed:1}
    extra=RunnablePassthrough.assign(multi=lambda x : x["num"] * 3),
    # {passed:1, extra:3}
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

```





## RunnableLambda

- 매개변수 하나를 무조건 가져야한다.

```python
# RunnableLambda
from langchain_core.runnables import RunnableLambda

def get_today(a):
    # RunnablePassthrough에 들어간 값이 들어가게 된다.
    # 따라서 invoke(3) 을 넣으주면 a의 값은 3이 들어가게된다.
    return datetime.today().strftime("%b-%d")

prompt = PromptTemplate.from_template(
    "{today} 가 생일인 유명인 {n} 명을 나열하세요. 생년월일을 표기해 주세요."
)
model = ChatOpenAI(temperature=0)
runnable_lambda_chain = (
    {"today": RunnableLambda(get_today), "n":{"n": RunnablePassthrough()}}
    | prompt
    | model
    | StrOutputParser()
)
print(runnable_lambda_chain.invoke(3))
```

```python
runnable_lambda_chain = (
    # {"today": RunnableLambda(get_today), "n":{"n": RunnablePassthrough()}}
    {"today": RunnableLambda(get_today), "n":{"n": itemgetter("n")}}
    | prompt
    | model
    | StrOutputParser()
)
print(runnable_lambda_chain.invoke({"n":3}))
```

- 만약에 dictionary 로 들어오게 되면 **itemgetter**를 통해서 여러 값을 가져올 수 있음



### 다중 인자 넣기

- 아래와 같이  여러 인자를 dict로 넣어줄 수 있다.

```python
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

```
