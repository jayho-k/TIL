import asyncio
import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types

# app-2 -A2A-> adk -A2A-> crew

RECEIPTS = {
    "T-2026-03": [
        {"item": "항공권", "amount": 820000, "currency": "KRW"},
        {"item": "호텔", "amount": 1200, "currency": "USD"},
        {"item": "식비", "amount": 43000, "currency": "KRW"},
    ],
    "T-2026-04": [
        {"item": "택시", "amount": 32000, "currency": "KRW"},
        {"item": "식비", "amount": 18000, "currency": "KRW"},
    ],
}
RATES = {"USD": 1350}
LIMITS = {"항공권": 1000000, "호텔": 1500000, "식비": 50000, "택시": 50000}

# 마지막 실행에서 이벤트를 낸 에이전트 이름. 계층 안에서 누가 실행됐는지 확인할 때 쓴다.
LAST_AGENTS: list[str] = []


def list_receipts(trip_id: str) -> str:
    """출장 번호로 영수증 목록을 가져온다."""
    return str(RECEIPTS.get(trip_id, []))


def get_rate(currency: str) -> str:
    """통화 코드의 원화 환율을 가져온다."""
    return str(RATES.get(currency.upper(), 0))

def make_model() -> LiteLlm:
    return LiteLlm(model="ollama_chat/qwen2.5:3b",
                   api_base=os.environ["OLLAMA_URL"])


def build_tree() -> LlmAgent:
    collector = LlmAgent(
        name="collector",
        model=make_model(),
        description="영수증과 환율을 가져오는 담당자",
        instruction="도구로 영수증과 환율을 가져온다. 값을 지어내지 않는다.",
        tools=[list_receipts, get_rate],
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )
    reporter = LlmAgent(
        name="reporter",
        model=make_model(),
        description="모인 자료를 한 줄로 정리하는 담당자",
        instruction="주어진 자료를 한국어 한 줄로 정리한다. 숫자를 바꾸지 않는다.",
        disallow_transfer_to_parent=True,
        disallow_transfer_to_peers=True,
    )
    return LlmAgent(
        name="expense_root",
        model=make_model(),
        description="경비 정산을 조정한다",
        instruction="영수증이 필요하면 collector에게, 정리가 필요하면 reporter에게 넘긴다.",
        sub_agents=[collector, reporter],
    )



async def run_tree(trip_id: str) -> str:
    runner = InMemoryRunner(agent=build_tree(), app_name="expense")
    session = await runner.session_service.create_session(
        app_name="expense", user_id="u1")
    text = f"출장 {trip_id}의 영수증을 가져오고 한 줄로 정리해 줘"
    out = []
    LAST_AGENTS.clear()
    async for event in runner.run_async(
        user_id="u1", session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=text)]),
    ):
        if event.author not in LAST_AGENTS:
            LAST_AGENTS.append(event.author)
        if event.content and event.content.parts:
            for p in event.content.parts:
                if p.text:
                    out.append(p.text)
    return " ".join(out).strip()


def settle(trip_id: str) -> dict:
    """계산은 파이썬이 한다. 앞에서 정한 원칙 그대로."""
    receipts = RECEIPTS.get(trip_id, [])
    total, violations = 0, []
    for r in receipts:
        krw = r["amount"] if r["currency"] == "KRW" else r["amount"] * RATES.get(r["currency"], 0)
        total += krw
        limit = LIMITS.get(r["item"])
        if limit and krw > limit:
            violations.append(f"{r['item']} {krw}원은 한도 {limit}원을 넘습니다")
    note = asyncio.run(run_tree(trip_id))
    return {"trip_id": trip_id, "total": total, "violations": violations,
            "receipts": len(receipts), "note": note}