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
