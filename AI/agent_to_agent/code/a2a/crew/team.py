import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool

# crewai.a2a

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


@tool("list_receipts")
def list_receipts(trip_id: str) -> str:
    """출장 번호로 영수증 목록을 가져온다."""
    return str(RECEIPTS.get(trip_id, []))


@tool("get_rate")
def get_rate(currency: str) -> str:
    """통화 코드의 원화 환율을 가져온다."""
    return str(RATES.get(currency.upper(), 0))




def make_llm(prefix: str = "ollama_chat") -> LLM:
    return LLM(model=f"{prefix}/qwen2.5:3b",
               base_url=os.environ["OLLAMA_URL"], temperature=0)

def build_crew(prefix: str = "ollama_chat") -> Crew:
    llm = make_llm(prefix)
    collector = Agent(
        role="영수증 수집",
        goal="출장 번호로 영수증과 환율을 모은다",
        backstory="경비 데이터를 다루는 담당자다. 도구만 쓰고 값을 지어내지 않는다.",
        tools=[list_receipts, get_rate], llm=llm, verbose=False,
    )
    reviewer = Agent(
        role="규정 검토",
        goal="모인 자료를 한 줄로 정리한다",
        backstory="사내 규정을 잘 아는 검토자다.",
        llm=llm, verbose=False,
    )
    collect = Task(description="출장 {trip_id}의 영수증을 가져오고, 외화가 있으면 환율도 가져와라.",
                   expected_output="영수증 목록과 환율", agent=collector)
    review = Task(description="모인 자료를 한국어 한 줄로 정리해라. 숫자를 지어내지 마라.",
                  expected_output="한국어 한 줄", agent=reviewer, context=[collect])
    return Crew(agents=[collector, reviewer], tasks=[collect, review],
                process=Process.sequential, verbose=False)


def settle(trip_id: str, prefix: str = "ollama_chat") -> dict:
    """계산은 파이썬이 한다. 앞에서 정한 원칙 그대로."""
    receipts = RECEIPTS.get(trip_id, [])
    total, violations = 0, []
    for r in receipts:
        krw = r["amount"] if r["currency"] == "KRW" else r["amount"] * RATES.get(r["currency"], 0)
        total += krw
        limit = LIMITS.get(r["item"])
        if limit and krw > limit:
            violations.append(f"{r['item']} {krw}원은 한도 {limit}원을 넘습니다")
    note = str(build_crew(prefix).kickoff(inputs={"trip_id": trip_id}))
    return {"trip_id": trip_id, "total": total, "violations": violations,
            "receipts": len(receipts), "note": note}