from langchain_core.tools import tool

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

RATES = {"USD": 1350, "JPY": 9, "EUR": 1460}

# LIMITS = {"항공권": 1000000, "호텔": 2000000, "식비": 50000, "택시": 50000}
LIMITS = {"항공권": 1000000, "호텔": 1500000, "식비": 50000, "택시": 50000}


@tool
def list_receipts(trip_id: str) -> list[dict]:
    """출장 번호로 영수증 목록을 가져온다."""
    return RECEIPTS.get(trip_id, [])


@tool
def get_rate(currency: str) -> int:
    """통화 코드의 원화 환율을 가져온다."""
    return RATES.get(currency.upper(), 0)


@tool
def check_policy(item: str, amount: int) -> str:
    """항목과 원화 금액이 사내 규정 한도 안인지 확인한다."""
    limit = LIMITS.get(item)
    if limit is None:
        return f"{item}은 한도가 정해져 있지 않습니다"
    if amount > limit:
        return f"{item} {amount}원은 한도 {limit}원을 넘습니다"
    return f"{item} {amount}원은 한도 {limit}원 안입니다"


ALL_TOOLS = [list_receipts, get_rate, check_policy]