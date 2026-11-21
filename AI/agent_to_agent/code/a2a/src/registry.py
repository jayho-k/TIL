import httpx

KNOWN = [
    "http://worker:8000",
    "http://crew:8200",
    "http://adk:8300",
]

def fetch_cards(urls: list[str] | None = None) -> list[dict]:
    """각 주소의 .well-known에서 카드를 읽어 온다."""
    cards = []
    for base in urls or KNOWN:
        try:
            card = httpx.get(f"{base}/.well-known/agent-card.json", timeout=10).json()
            card["_base"] = base
            cards.append(card)
        except Exception as e:
            print(f"  {base} 카드 못 읽음: {type(e).__name__}")
    return cards

def has_skill(card: dict, skill_id: str) -> bool:
    return any(s["id"] == skill_id for s in card.get("skills", []))

def pick(cards: list[dict], skill_id: str, need_streaming: bool = False) -> dict | None:
    """카드에 적힌 것만 보고 고른다. 안은 안 본다."""
    fit = [c for c in cards if has_skill(c, skill_id)]
    if need_streaming:
        fit = [c for c in fit if c["capabilities"].get("streaming")]
    return fit[0] if fit else None