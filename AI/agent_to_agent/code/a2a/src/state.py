import operator
from typing import Annotated, TypedDict

# 시작 -> plan -(1)-> tools -(1)-> tools --> compute

# class ExpenseState(TypedDict):
#     trip_id: str # 시작 할 떄 넣어주는 값
#     messages : Annotated[list, add_messages] # 모델과 주고받은 대화
#     steps: int # 몇 바퀴 돌았냐 -> 순환이 생기기 떄문에
#     receipts: list[dict] # 영수증 목록 -> 첫 번쨰 노드가 채운다.
#     rates : dict # 환율
#     total: int # 합계 -> 두 번쨰 노드가 계산
#     violations: list[str] # 규정 위반에 대한 목록
#     report: str # 사람이 읽는 한 줄 -> 모델이 작성
#     log: Annotated[list[str], operator.add] #
#     approved: bool | None

class ExpenseState(TypedDict):
    trip_id: str
    receipts: list[dict]
    rates: dict
    total: int
    violations: list[str]
    report: str
    approved: bool | None
    log: Annotated[list[str], operator.add]