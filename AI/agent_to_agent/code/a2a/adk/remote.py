import os
import uuid

import httpx


class RemoteFailed(Exception):
    pass


def call_agent(url: str, text: str, timeout: float = 600) -> dict:
    """A2A로 다른 에이전트를 부르고 data 조각을 꺼낸다."""
    body = {
        "jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "SendMessage",
        "params": {"message": {
            "messageId": str(uuid.uuid4()), "role": "ROLE_USER",
            "parts": [{"text": text, "mediaType": "text/plain"}],
        }},
    }
    try:
        r = httpx.post(url, json=body, timeout=timeout).json()
    except (httpx.HTTPError, ValueError) as e:
        raise RemoteFailed(f"응답을 받지 못했습니다: {e}")

    if "error" in r:
        e = r["error"]
        raise RemoteFailed(f"{e.get('data', {}).get('a2aErrorCode', '?')}: {e['message']}")
    if "result" not in r.get("result", {}):
        raise RemoteFailed("JSON-RPC 응답이 아닙니다")

    task = r["result"]["task"]
    state = task["status"]["state"]
    if state != "TASK_STATE_COMPLETED":
        raise RemoteFailed(f"상대가 {state} 상태로 끝냈습니다")

    for artifact in task.get("artifacts", []):
        for part in artifact["parts"]:
            if "data" in part:
                return part["data"]
    raise RemoteFailed("data 조각이 없습니다")


def crew_url() -> str:
    return os.environ.get("CREW_URL", "http://crew:8200") + "/"