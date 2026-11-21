"""ADK 계층을 A2A로 열고, 정산 일은 A2A 너머 다른 에이전트에 먼저 맡긴다."""
import re
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

import artifacts
import remote
import rpc
import store
import tree

app = FastAPI()

TRIP_PATTERN = re.compile(r"T-\d{4}-\d{2}")


class InvalidParams(Exception):
    pass


def read_text(message: dict) -> str:
    return " ".join(part["text"] for part in message.get("parts", []) if "text" in part)


AGENT_CARD = {
    "name": "expense-adk",
    "description": "조정자 아래 담당자를 둔 계층이 정산한다. 정산 일은 다른 에이전트에 먼저 맡긴다",
    "version": "1.0.0",
    "supportedInterfaces": [
        {"url": "http://adk:8300", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}
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

    trip_id = found.group()
    task_id = str(uuid.uuid4())
    context_id = message.get("contextId") or str(uuid.uuid4())
    store.create(task_id, context_id, message)
    store.set_state(task_id, "TASK_STATE_WORKING")

    try:
        # 정산 일을 먼저 다른 에이전트에 맡긴다. 우리가 부르는 쪽이 된다.
        borrowed = remote.call_agent(remote.crew_url(), f"출장 {trip_id} 경비를 정리해 주세요")
        result = {**borrowed, "source": "remote:expense-crew"}
    except remote.RemoteFailed as e:
        # 상대가 응답하지 못하면 우리 계층으로 처리한다.
        result = {**tree.settle(trip_id), "source": f"local (원격 실패: {e})"}

    for artifact in artifacts.summary_and_detail(result):
        store.add_artifact(task_id, artifact)
    return store.set_state(task_id, "TASK_STATE_COMPLETED")


HANDLERS = {"SendMessage": handle_send_message}


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
    return rpc.ok(body.get("id"), result)