"""CrewAI 팀을 우리 A2A 서버 골격 뒤에 세운다.

앞에서 만든 rpc·store·artifacts를 그대로 쓴다. 다른 건 팀을 부르는 한 줄이다.
"""
import re
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

import artifacts
import rpc
import store
import team

app = FastAPI()

TRIP_PATTERN = re.compile(r"T-\d{4}-\d{2}")


class InvalidParams(Exception):
    pass


class TaskNotFound(Exception):
    pass


def read_text(message: dict) -> str:
    return " ".join(part["text"] for part in message.get("parts", []) if "text" in part)

AGENT_CARD = {
    "name": "expense-crew",
    "description": "경비 수집과 규정 검토를 나눠 맡은 팀이 정산한다",
    "version": "1.0.0",
    "supportedInterfaces": [
        {"url": "http://crew:8200", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}
    ],
    "capabilities": {"streaming": False, "pushNotifications": False,
                     "extendedAgentCard": False},
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain", "application/json"],
    "skills": [{
        "id": "settle_expense",
        "name": "경비 정산",
        "description": "출장 번호를 주면 영수증을 모아 원화 합계와 규정 위반을 돌려준다",
        "tags": ["expense", "finance"],
    }],
}

@app.get("/.well-known/agent-card.json")
def agent_card():
    return AGENT_CARD

def handle_send_message(params: dict) -> dict:
    message = params.get("message")
    if not message or not message.get("messageId"):
        raise InvalidParams("message와 messageId가 필요합니다")
    if message.get("role") != "ROLE_USER":
        raise InvalidParams(f"role은 ROLE_USER여야 합니다. 받은 값: {message.get('role')}")

    found = TRIP_PATTERN.search(read_text(message))
    if not found:
        raise InvalidParams("출장 번호를 못 찾았습니다")

    task_id = str(uuid.uuid4())
    context_id = message.get("contextId") or str(uuid.uuid4())
    store.create(task_id, context_id, message)
    store.set_state(task_id, "TASK_STATE_WORKING")

    result = team.settle(found.group())          # 여기만 다르다
    for artifact in artifacts.summary_and_detail(result):
        store.add_artifact(task_id, artifact)
    return store.set_state(task_id, "TASK_STATE_COMPLETED")


def handle_get_task(params: dict) -> dict:
    task = store.get(params.get("id"))
    if task is None:
        raise TaskNotFound(f"태스크 {params.get('id')}를 찾을 수 없습니다")
    return task


HANDLERS = {"SendMessage": handle_send_message, "GetTask": handle_get_task}

class RpcBody(BaseModel):
    jsonrpc: str = ""
    id: str | int | None = None
    method: str = ""
    params: dict = {}

@app.post("/")
def jsonrpc(body_model: RpcBody):
    body = body_model.model_dump()
    if body.get("jsonrpc") != "2.0" or not body.get("method"):
        return rpc.err(body.get("id"), rpc.INVALID_REQUEST, "Invalid Request")

    handler = HANDLERS.get(body["method"])
    if handler is None:
        return rpc.err(body.get("id"), rpc.METHOD_NOT_FOUND, "Method not found",
                       "UnsupportedOperationError", f"{body['method']}은 지원하지 않습니다")
    try:
        result = handler(body.get("params") or {})
        if body["method"] == "SendMessage":
            result = rpc.send_message_result(result)
    except InvalidParams as e:
        return rpc.err(body.get("id"), rpc.INVALID_PARAMS, "Invalid params",
                       "InvalidParamsError", str(e))
    except TaskNotFound as e:
        return rpc.err(body.get("id"), rpc.INVALID_PARAMS, "Invalid params",
                       "TaskNotFoundError", str(e))
    return rpc.ok(body.get("id"), result)