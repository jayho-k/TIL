import os
import uuid

import httpx
from langchain_ollama import ChatOllama

import registry

model = ChatOllama(model="qwen2.5:3b", base_url=os.environ["OLLAMA_URL"], temperature=0)


def summarize_cards(cards: list[dict]) -> str:
    """모델에게 보여 줄 만큼만 추린다. 카드를 통째로 넣지 않는다."""
    lines = []
    for c in cards:
        skills = ", ".join(f"{s['id']}({s['description']})" for s in c["skills"])
        on = [k for k, v in c["capabilities"].items() if v] or ["없음"]
        lines.append(f"- {c['name']}: 할 수 있는 일 = {skills} / 지원 = {', '.join(on)}")
    return "\n".join(lines)

def choose(question: str, cards: list[dict]) -> tuple[dict | None, str]:
    """모델이 고르되 코드가 검증한다. 앞에서 정한 원칙 그대로."""
    prompt = (
        "다음은 쓸 수 있는 에이전트 목록입니다.\n"
        f"{summarize_cards(cards)}\n\n"
        f"요청: {question}\n\n"
        "이 요청을 처리할 에이전트의 이름 하나만 답하세요. 설명하지 마세요."
    )
    said = model.invoke(prompt).content.strip()

    by_name = {c["name"]: c for c in cards}
    for name in by_name:
        if name in said:
            return by_name[name], f"모델이 고름: {said!r}"

    return None, f"모델 답을 못 알아들음: {said!r}"

def route(question: str, skill_id: str, cards: list[dict]) -> tuple[dict | None, str]:
    """모델이 고르고, 못 고르면 카드 조건으로 떨어뜨린다."""
    picked, why = choose(question, cards)
    if picked and registry.has_skill(picked, skill_id):
        return picked, why

    fallback = registry.pick(cards, skill_id)
    if picked:
        return fallback, f"{why} → {skill_id}가 없어 규칙으로 대체"
    return fallback, f"{why} → 규칙으로 대체"

class CallFailed(Exception):
    pass

def call(card: dict, text: str, timeout: float = 900) -> dict:
    """고른 에이전트를 A2A로 부르고 data 조각을 꺼낸다."""
    body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "SendMessage",
            "params": {"message": {"messageId": str(uuid.uuid4()), "role": "ROLE_USER",
                                   "parts": [{"text": text, "mediaType": "text/plain"}]}}}
    try:
        r = httpx.post(card["_base"] + "/", json=body, timeout=timeout).json()
    except (httpx.HTTPError, ValueError) as e:
        raise CallFailed(f"응답을 받지 못했습니다: {e}")

    if "error" in r:
        e = r["error"]
        raise CallFailed(f"{e.get('data', {}).get('a2aErrorCode', '?')}: {e['message']}")
    if "result" not in r.get("result", {}):
        raise CallFailed("JSON-RPC 응답이 아닙니다")

    task = r["result"]["task"]
    state = task["status"]["state"]
    if state != "TASK_STATE_COMPLETED":
        raise CallFailed(f"{card['name']}가 {state} 상태로 끝냈습니다")

    for a in task.get("artifacts", []):
        for p in a["parts"]:
            if "data" in p:
                return p["data"]
    raise CallFailed("data 조각이 없습니다")