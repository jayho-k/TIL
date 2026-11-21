import os
from langgraph.types import interrupt

from langchain_ollama import ChatOllama

from state import ExpenseState

from tools import  check_policy

# 영수증 데이터를 딕셔너리에 박아넣는다.
RECEIPTS = {
    "T-2026-03": [
        {"item": "항공권", "amount": 820000},
        {"item": "호텔", "amount": 540000},
        {"item": "식비", "amount": 43000},
    ],
}

model = ChatOllama(
    model="gemma4:26b-a4b-it-qat",
    base_url=os.environ["OLLAMA_URL"],
    temperature=0,
)

def compute(state: ExpenseState) -> dict:
    # receipts = state["receipts"]
    # rates = state["rates"]

    receipts = state.get("receipts") or []
    rates = state.get("rates") or {}

    total = 0
    violations = []
    for r in receipts:
        cur = r.get("currency", "KRW")
        krw = r["amount"] if cur == "KRW" else r["amount"] * rates.get(cur, 0)
        total += krw
        verdict = check_policy.invoke({"item": r["item"], "amount": krw})
        if "넘습니다" in verdict:
            violations.append(verdict)
    return {"total": total, "violations": violations,
            "log": [f"영수증 {len(receipts)}건으로 원화 합계 {total}원 계산",
                    f"규정 위반 {len(violations)}건"]}

# def escalate(state: ExpenseState) -> dict:
#     report = (
#         f"출장 {state['trip_id']}의 원화 합계는 {state['total']}원입니다. "
#         "규정 위반이 있어 사람 승인이 필요합니다."
#     )
#     return {"report": report, "log": ["승인 필요"]}

def escalate(state: ExpenseState) -> dict:
    decision = interrupt({
        "trip_id": state["trip_id"],
        "total": state["total"],
        "violations": state["violations"],
        "question": "승인하시겠습니까? approve 또는 reject",
    })
    if decision == "approve":
        return {"approved": True,
                "report": f"출장 {state['trip_id']} 합계 {state['total']}원, 승인됨",
                "log": ["승인 받음"]}
    return {"approved": False,
            "report": f"출장 {state['trip_id']} 합계 {state['total']}원, 반려됨",
            "log": ["반려됨"]}


def summarize(state: ExpenseState) -> dict:
    prompt = (
        f"출장 {state['trip_id']}의 원화 합계는 {state['total']}원이고 규정 위반은 없습니다.\n"
        "위 사실만 써서 한국어 한 문장으로 보고하세요. 숫자를 바꾸지 마세요."
    )
    return {"report": model.invoke(prompt).content.strip(), "log": ["보고 작성"]}


def collect(state: ExpenseState) -> dict:
    receipts = RECEIPTS.get(state["trip_id"], [])
    return {"receipts": receipts, "log": [f"영수증 {len(receipts)}건 수집"]}

def tally(state: ExpenseState) -> dict:
    total = sum(r["amount"] for r in state["receipts"])
    return {"total": total, "log": [f"합계 {total}원 계산"]}

# def summarize(state: ExpenseState) -> dict:
#     lines = "\n".join(f"- {r['item']}: {r['amount']}원" for r in state["receipts"])
#     prompt = (
#         f"출장 {state['trip_id']}의 경비 내역입니다.\n"
#         f"{lines}\n"
#         f"합계는 {state['total']}원입니다.\n"
#         "이 내역을 한국어 한 문장으로 요약하세요. 숫자는 주어진 값을 그대로 쓰세요."
#     )
#     answer = model.invoke(prompt)
#     return {"report": answer.content.strip(), "log": ["요약 작성"]}