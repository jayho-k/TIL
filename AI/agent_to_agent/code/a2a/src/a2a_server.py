import re
import uuid
import store
import artifacts
import adapter
import json
import time
import runner
import push

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

import rpc
from card import AGENT_CARD, extended_card

import os
from contextlib import asynccontextmanager

class InvalidParams(Exception):
    pass

class TaskNotFound(Exception):
    pass

class AuthRequired(Exception):
    pass

class UnsupportedOperation(Exception):
    pass

class TaskNotCancelable(Exception):
    pass

# INPUT_REQUIRED : 승인이나 무언가 추가적인 정보처럼 사용자의 답을 줘
# AUTH_REQUIRED : 우리가 무언가 실행하려고 하는데, 너 권한있어?

# 그래프 관련 코드
# 1. state.py -> 상태   
# 2. nodes.py -> 모델, compute, excalate, suimmarize
# 3. collector.py -> 수집기를 위한 서브 그래프
# 4. tools.py -> 우리가 사용하는 도구들의 모음
# 5. graph.py -> 부모 그래프

# 서버 관련 코드
# 1. rpc.py -> JSON RPC
# 2. card.py -> Agnet Card
# 3. store.py -> 테스크를 관리
# 4. artifacts.py -> 결과물에대한 관리
# 5. a2a_server.py 

# message Artifact {
#   string artifact_id = 1 [(google.api.field_behavior) = REQUIRED];
#   string name = 2;
#   string description = 3;
#   repeated Part parts = 4 [(google.api.field_behavior) = REQUIRED];
#   google.protobuf.Struct metadata = 5;
#   repeated string extensions = 6;
# }

# message StreamResponse {
#   oneof payload {
#     Task task = 1;
#     Message message = 2;
#     TaskStatusUpdateEvent status_update = 3;
#     TaskArtifactUpdateEvent artifact_update = 4;
#   }
# }

# message TaskStatusUpdateEvent {
#   string task_id = 1;
#   string context_id = 2;
#   TaskStatus status = 3;
#   google.protobuf.Struct metadata = 4;
# }


# app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    import grpc_server
    server = grpc_server.start(int(os.environ.get("GRPC_PORT", "50051")))
    yield
    server.stop(0)

app = FastAPI(lifespan=lifespan)

TRIP_PATTERN = re.compile(r"T-\d{4}-\d{2}") # T-2026-04

VALID_TOKENS = {"finance-token-abc123"}
PROTECTED_WORDS = ("지급", "송금",  "정산 근거", "상세 내역")

def bearer_of(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:]
    return None

# FAKE_RESULTS = {
#     "T-2026-03": {"trip_id": "T-2026-03", "total": 2483000,
#                   "violations": ["호텔 1620000원은 한도 1500000원을 넘습니다"], "receipts": 3},
#     "T-2026-04": {"trip_id": "T-2026-04", "total": 50000, "violations": [], "receipts": 2},
# }

@app.get("/.well-known/agent-card.json")
def agent_card():
    return AGENT_CARD

def read_text(message: dict) -> str:
    """

    :rtype: object
    """
    return " ".join(part["text"] for part in message.get("parts", []) if "text" in part)

def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

def events(task_id: str, context_id: str, seconds: float = 300):
    sent_artifacts: set[str] = set()
    last_state = None
    for _ in range(int(seconds * 2)):
        task = store.get(task_id)
        state = task["status"]["state"]

        for artifact in task["artifacts"]:
            if artifact["artifactId"] in sent_artifacts:
                continue
            sent_artifacts.add(artifact["artifactId"])
            yield "artifactUpdate", {
                "taskId": task_id, "contextId": context_id,
                "artifact": artifact, "lastChunk": True}

        if state != last_state:
            last_state = state
            yield "statusUpdate", {
                "taskId": task_id, "contextId": context_id,
                "status": task["status"]}

        if state in store.TERMINAL or state in store.INTERRUPTED:
            return
        time.sleep(0.5)

def watch(req_id, task_id: str, context_id: str, seconds: float = 300):
    for kind, payload in events(task_id, context_id, seconds):
        yield sse(rpc.ok(req_id, {kind: payload}))

# def watch(req_id, task_id: str, context_id: str, seconds: float = 300):
#     """저장소를 지켜보며 바뀐 것만 흘린다."""
#     sent_artifacts: set[str] = set()
#     last_state = None
#     for _ in range(int(seconds * 2)):
#         task = store.get(task_id)
#         state = task["status"]["state"]

#         for artifact in task["artifacts"]:
#             if artifact["artifactId"] in sent_artifacts:
#                 continue
#             sent_artifacts.add(artifact["artifactId"])
#             yield sse(rpc.ok(req_id, {"artifactUpdate": {
#                 "taskId": task_id, "contextId": context_id,
#                 "artifact": artifact, "lastChunk": True}}))

#         if state != last_state:
#             last_state = state
#             yield sse(rpc.ok(req_id, {"statusUpdate": {
#                 "taskId": task_id, "contextId": context_id,
#                 "status": task["status"]}}))

#         if state in store.TERMINAL or state in store.INTERRUPTED:
#             return
#         time.sleep(0.5)

def stream_subscribe(req_id, params: dict):
    """SubscribeToTask. 이미 있는 태스크에 다시 붙는다."""
    task_id = params.get("id")
    task = store.get(task_id) if task_id else None
    if task is None:
        yield sse(rpc.err(req_id, rpc.INVALID_PARAMS, "Invalid params",
                          "TaskNotFoundError", f"태스크 {task_id}를 찾을 수 없습니다"))
        return

    state = task["status"]["state"]
    if state in store.TERMINAL:
        yield sse(rpc.err(req_id, rpc.UNSUPPORTED_OPERATION,
                          "This operation is not supported",
                          "UnsupportedOperationError",
                          f"{state} 상태라 구독할 수 없습니다"))
        return

    # 붙는 순간의 상태를 먼저 준다. 놓친 구간을 메우는 자리다.
    yield sse(rpc.ok(req_id, {"task": task}))
    if state in store.INTERRUPTED:
        return

    yield from watch(req_id, task_id, task["contextId"])

def handle_cancel_task(params: dict) -> dict:
    task_id = params.get("id")
    if not task_id:
        raise InvalidParams("id가 없습니다")

    task = store.get(task_id)
    if task is None:
        raise TaskNotFound(f"태스크 {task_id}를 찾을 수 없습니다")

    state = task["status"]["state"]
    if state in store.TERMINAL:
        raise TaskNotCancelable(f"{state}는 종료 상태라 취소할 수 없습니다")

    runner.request_cancel(task_id)

    if runner.is_running(task_id):
        # 돌고 있는 그래프는 끊지 못한다. 표시만 하고 기다린다.
        task["status"]["message"] = {
            "messageId": str(uuid.uuid4()),
            "taskId": task_id,
            "contextId": task["contextId"],
            "role": "ROLE_AGENT",
            "parts": [{"text": "취소를 접수했습니다. 실행 중인 작업이 끝나면 결과를 버리고 취소합니다",
                       "mediaType": "text/plain"}],
        }
        return task

    cancelled = store.set_state(task_id, "TASK_STATE_CANCELED")
    push.notify(cancelled)
    return cancelled

def handle_get_extended_agent_card(
    params: dict, token: str | None = None
) -> dict:
    if not AGENT_CARD["capabilities"].get("extendedAgentCard"):
        raise UnsupportedOperation("확장 카드를 지원하지 않습니다")
    if token not in VALID_TOKENS:
        raise AuthRequired(
            "확장 카드는 인증이 필요합니다. finance_token을 사용하세요"
        )
    return extended_card()

def handle_create_push_config(params: dict) -> dict:
    task_id = params.get("taskId")
    if not task_id:
        raise InvalidParams("taskId가 없습니다")
    if store.get(task_id) is None:
        raise TaskNotFound(f"태스크 {task_id}를 찾을 수 없습니다")
    if not params.get("url"):
        raise InvalidParams("url이 없습니다")
    return push.save({
        "id": params.get("id") or str(uuid.uuid4()),
        "taskId": task_id,
        "url": params["url"],
        "token": params.get("token", ""),
        "authentication": params.get("authentication") or {},
    })

def handle_get_push_config(params: dict) -> dict:
    config = push.get(params.get("taskId"))
    if config is None:
        raise TaskNotFound(f"태스크 {params.get('taskId')}의 웹훅 설정이 없습니다")
    return config

def finish(task_id: str, state: dict) -> dict:
    """어댑터가 준 상태를 태스크에 반영한다."""
    task = store.get(task_id)

    if runner.is_cancelled(task_id):
        cancelled = store.set_state(task_id, "TASK_STATE_CANCELED")
        push.notify(cancelled)
        return cancelled

    # if state["waiting"]:
    #     store.set_state(task_id, "TASK_STATE_INPUT_REQUIRED")
    #     task["status"]["message"] = {
    #         "messageId": str(uuid.uuid4()),
    #         "role": "ROLE_AGENT",
    #         "parts": [{"text": state["question"]}],
    #     }
    #     return task

    if state["waiting"]:
        store.set_state(task_id, "TASK_STATE_INPUT_REQUIRED")
        ask = state["ask"] or {}
        task["status"]["message"] = {
            "messageId": str(uuid.uuid4()),
            "taskId": task_id,
            "contextId": task["contextId"],
            "role": "ROLE_AGENT",
            "parts": [
                {"text": ask.get("question", ""), "mediaType": "text/plain"},
                {"data": {"expects": "one_of",
                          "options": ["approve", "reject"],
                          "reason": ask.get("violations", []),
                          "total": ask.get("total")},
                 "mediaType": "application/json"},
            ],
        }
        push.notify(task)
        return task

    verdict = ""
    if state["approved"] is not None:
        verdict = "승인됨" if state["approved"] else "반려됨"
    for artifact in artifacts.summary_and_detail(state["result"], verdict):
        store.add_artifact(task_id, artifact)

    # return store.set_state(task_id, "TASK_STATE_COMPLETED")
    done = store.set_state(task_id, "TASK_STATE_COMPLETED")
    push.notify(done)
    return done

def handle_send_message(params: dict, token: str | None = None) -> dict:
    message = params.get("message")
    if not message:
        raise InvalidParams("message가 없습니다")
    if not message.get("messageId"):
        raise InvalidParams("messageId가 없습니다")
    if message.get("role") != "ROLE_USER":
        raise InvalidParams(
            f"role은 ROLE_USER여야 합니다. 받은 값: {message.get('role')}"
        )

    given = message.get("taskId")
    if given:
        existing = store.get(given)
        if existing is None:
                raise TaskNotFound(f"태스크 {given}을 찾을 수 없습니다.")
        return continue_task(existing, message, token)

    text = read_text(message)
    found = TRIP_PATTERN.search(text)
    if not found:
        raise InvalidParams(f"출장 번호를 찾지 못했습니다: {text!r}")

    # given = message.get("taskId")
    # if given and store.get(given) is None:
    #     raise TaskNotFound(f"태스크 {given}를 찾을 수 없습니다")

    task_id = str(uuid.uuid4())

    context_id = message.get("contextId") or str(uuid.uuid4())
    task = store.create(task_id, context_id, message)

    if any(word in text for word in PROTECTED_WORDS) and token not in VALID_TOKENS:
        store.set_state(task_id, "TASK_STATE_AUTH_REQUIRED")
        task["status"]["message"] = {
            "messageId": str(uuid.uuid4()),
            "taskId": task_id,
            "contextId": task["contextId"],
            "role": "ROLE_AGENT",
            "parts": [
                {"text": "지급 전 정산을 확정하려면 재무 권한이 필요합니다",
                 "mediaType": "text/plain"},
                {"data": {"scheme": "finance_token", "skill": "settle_and_pay"},
                 "mediaType": "application/json"},
            ],
        }
        return task    

    config = params.get("configuration") or {}
    if config.get("returnImmediately"):
        store.set_state(task_id, "TASK_STATE_WORKING")
        runner.run_in_background(task_id, found.group(), finish)
        return store.get(task_id)

    store.set_state(task_id, "TASK_STATE_WORKING")
    state = adapter.start(task_id, found.group())
    return finish(task_id, state)


    # result = FAKE_RESULTS[found.group()]

    # if result["violations"]:
    #     store.set_state(task_id, "TASK_STATE_INPUT_REQUIRED")
    #     task["status"]["message"] = {
    #         "messageId": str(uuid.uuid4()),
    #         "role": "ROLE_AGENT",
    #         "parts": [{"text": f"규정 위반 {len(result['violations'])}건입니다. "
    #                            "승인하시겠습니까? approve 또는 reject"}],
    #     }
    #     task["metadata"] = {"pending": result}
    #     return task


    # # result = {
    # #     "trip_id": found.group(),
    # #     "total": 50000,
    # #     "violations": [],
    # #     "receipts": 2,
    # # }

    # # store.add_artifact(task_id, {
    # #     "artifactId": str(uuid.uuid4()),
    # #     "name": "정산 요약",
    # #     "description": "사람이 읽는 요약",
    # #     "parts": [{
    # #         "text": (
    # #             f"출장 {result['trip_id']} 원화 합계 {result['total']}원, "
    # #             f"규정 위반 {len(result['violations'])}건"
    # #         )
    # #     }],
    # # })
    # # store.add_artifact(task_id, {
    # #     "artifactId": str(uuid.uuid4()),
    # #     "name": "정산 내역",
    # #     "description": "프로그램이 읽는 데이터",
    # #     "parts": [{"data": result, "mediaType": "application/json"}],
    # # })
    # # return store.set_state(task_id, "TASK_STATE_COMPLETED")

    # for artifact in artifacts.summary_and_detail(result):
    #     store.add_artifact(task_id, artifact)
    # return store.set_state(task_id, "TASK_STATE_COMPLETED")

def stream_send_message(req_id, params: dict, token: str | None = None):
    """SendStreamingMessage. SSE로 흘려보낸다."""
    message = params.get("message") or {}
    text = read_text(message)
    found = TRIP_PATTERN.search(text)
    if not found:
        yield sse(rpc.err(req_id, rpc.INVALID_PARAMS, "Invalid params",
                          "InvalidParamsError", f"출장 번호를 못 찾았습니다: {text!r}"))
        return

    if any(word in text for word in PROTECTED_WORDS) and token not in VALID_TOKENS:
        # SendMessage와 같은 토큰 검사를 탄다. AUTH_REQUIRED 태스크를 주고 닫는다.
        yield sse(rpc.ok(req_id, {"task": handle_send_message(params, token)}))
        return

    task_id = str(uuid.uuid4())
    context_id = message.get("contextId") or str(uuid.uuid4())
    task = store.create(task_id, context_id, message)
    yield sse(rpc.ok(req_id, {"task": task}))

    store.set_state(task_id, "TASK_STATE_WORKING")

    store.set_state(task_id, "TASK_STATE_WORKING")
    yield sse(rpc.ok(req_id, {"statusUpdate": {
        "taskId": task_id, "contextId": context_id,
        "status": store.get(task_id)["status"]}}))

    # 작업은 따로 돈다. 이 스트림이 끊겨도 계속된다.
    runner.run_in_background(task_id, found.group(), finish)

    yield from watch(req_id, task_id, context_id)


    # yield sse(rpc.ok(req_id, {"statusUpdate": {
    #     "taskId": task_id, "contextId": context_id,
    #     "status": task["status"]}}))

    # for node, _ in adapter.start_stream(task_id, found.group()):
    #     yield sse(rpc.ok(req_id, {"statusUpdate": {
    #         "taskId": task_id, "contextId": context_id,
    #         "status": {"state": "TASK_STATE_WORKING", "timestamp": store.now()},
    #         "metadata": {"node": node}}}))

    # final = finish(task_id, adapter.read(task_id))
    # for artifact in final["artifacts"]:
    #     yield sse(rpc.ok(req_id, {"artifactUpdate": {
    #         "taskId": task_id, "contextId": context_id,
    #         "artifact": artifact, "lastChunk": True}}))
    # yield sse(rpc.ok(req_id, {"statusUpdate": {
    #     "taskId": task_id, "contextId": context_id,
    #     "status": final["status"]}}))

def handle_get_task(params: dict) -> dict:
    task_id = params.get("id")
    if not task_id:
        raise InvalidParams("id가 없습니다")

    task = store.get(task_id) # graph.get_stat
    if task is None:
        raise TaskNotFound(f"태스크 {task_id}를 찾을 수 없습니다")

    limit = params.get("historyLength")
    if limit is None:
        return task
    return {**task, "history": task["history"][-int(limit):] if int(limit) > 0 else []}

def continue_task(
    task: dict, message: dict, token: str | None = None
) -> dict:
    """중단된 태스크에 필요한 값이나 권한을 주고 이어간다."""
    last = task["history"][-1] if task["history"] else None
    if last and last.get("messageId") == message.get("messageId"):
        return task

    state = task["status"]["state"]
    if state not in store.INTERRUPTED:
        raise InvalidParams(f"{state} 상태라 이어갈 게 없습니다")

    if state == "TASK_STATE_AUTH_REQUIRED":
        if token not in VALID_TOKENS:
            raise InvalidParams("유효한 재무 토큰이 필요합니다")
        found = TRIP_PATTERN.search(read_text(task["history"][0]))
        if not found:
            raise InvalidParams("처음 요청에서 출장 번호를 찾지 못했습니다")
        task["history"].append(message)
        store.set_state(task["id"], "TASK_STATE_WORKING")
        return finish(task["id"], adapter.start(task["id"], found.group()))

    answer = read_text(message).strip()
    if answer not in ("approve", "reject"):
        raise InvalidParams(
            f"답은 approve 또는 reject여야 합니다. 받은 값: {answer!r}"
        )

    task["history"].append(message)
    store.set_state(task["id"], "TASK_STATE_WORKING")
    state = adapter.resume(task["id"], answer)
    return finish(task["id"], state)

# def continue_task(task: dict, message: dict) -> dict:
#     """중단된 태스크에 답을 주고 이어간다."""
#     last = task["history"][-1] if task["history"] else None
#     if last and last.get("messageId") == message.get("messageId"):
#         return task

#     state = task["status"]["state"]
#     if state not in store.INTERRUPTED:
#         raise InvalidParams(f"{state} 상태라 이어갈 게 없습니다")

#     answer = read_text(message).strip()
#     if answer not in ("approve", "reject"):
#         raise InvalidParams(
#             f"답은 approve 또는 reject여야 합니다. 받은 값: {answer!r}"
#         )

#     task["history"].append(message)
#     store.set_state(task["id"], "TASK_STATE_WORKING")
#     state = adapter.resume(task["id"], answer)
#     return finish(task["id"], state)

# def continue_task(task: dict, message: dict) -> dict:
#     """중단된 태스크에 답을 주고 이어간다."""
#     state = task["status"]["state"]
#     if state not in store.INTERRUPTED:
#         raise InvalidParams(f"{state} 상태라 이어갈 게 없습니다")

#     answer = read_text(message).strip()
#     task["history"].append(message)
#     store.set_state(task["id"], "TASK_STATE_WORKING")

#     state = adapter.resume(task["id"], answer)
#     return finish(task["id"], state)



    # pending = (task.get("metadata") or {}).get("pending", {})
    # verdict = "승인됨" if answer == "approve" else "반려됨"
    # # store.add_artifact(task["id"], {
    # #     "artifactId": str(uuid.uuid4()),
    # #     "name": "정산 요약",
    # #     "description": "사람이 읽는 한 줄",
    # #     "parts": [{"text": f"출장 {pending.get('trip_id')} 원화 합계 "
    # #                        f"{pending.get('total')}원, {verdict}"}],
    # # })
    # # return store.set_state(task["id"], "TASK_STATE_COMPLETED")

    # for artifact in artifacts.summary_and_detail(pending, verdict):
    #     store.add_artifact(task["id"], artifact)
    # return store.set_state(task["id"], "TASK_STATE_COMPLETED")

def handle_list_tasks(params: dict) -> dict:
    tasks = list(store.all_tasks())

    if params.get("contextId"):
        tasks = store.by_context(params["contextId"])
    if params.get("status"):
        tasks = [t for t in tasks if t["status"]["state"] == params["status"]]

    tasks.sort(key=lambda t: t["status"]["timestamp"], reverse=True)

    page_size = int(params.get("pageSize") or 50)
    start = int(params.get("pageToken") or 0)
    page = tasks[start:start + page_size]

    out = {"tasks": [{**t, "history": []} for t in page]}
    if start + page_size < len(tasks):
        out["nextPageToken"] = str(start + page_size)
    return out

HANDLERS = {
    "SendMessage": handle_send_message,
    "GetTask": handle_get_task,
    "ListTasks" : handle_list_tasks,
    "GetExtendedAgentCard": handle_get_extended_agent_card,
    # "CreatePushNotificationConfig": handle_create_push_config,
    # "GetPushNotificationConfig": handle_get_push_config,
    "CreateTaskPushNotificationConfig": handle_create_push_config,
    "GetTaskPushNotificationConfig": handle_get_push_config,
    "CancelTask": handle_cancel_task
}

NEEDS_TOKEN = {handle_send_message, handle_get_extended_agent_card}

@app.post("/")
async def jsonrpc(request: Request):
    try:
        body = await request.json()
    except Exception:
        return rpc.err(None, rpc.PARSE_ERROR, "Parse error")

    if body.get("jsonrpc") != "2.0" or "method" not in body:
        return rpc.err(body.get("id"), rpc.INVALID_REQUEST, "Invalid Request")

    if body["method"] == "SendStreamingMessage":
        return StreamingResponse(
            stream_send_message(body.get("id"), body.get("params") or {},
                                bearer_of(request)),
            media_type="text/event-stream") 

    if body["method"] == "SubscribeToTask":
        return StreamingResponse(
            stream_subscribe(body.get("id"), body.get("params") or {}),
            media_type="text/event-stream")

    handler = HANDLERS.get(body["method"])
    if handler is None:
        return rpc.err(
            body.get("id"), rpc.METHOD_NOT_FOUND, "Method not found",
            "UnsupportedOperationError", f"{body['method']}은 지원하지 않습니다",
        )

    try:
        params = body.get("params") or {}
        if handler in NEEDS_TOKEN:
            token = bearer_of(request)
            result = handler(params, token)
        else:
            result = handler(params)
        if body["method"] == "SendMessage":
            result = rpc.send_message_result(result)
    # except InvalidParams as error:
    #     return rpc.err(
    #         body.get("id"), rpc.INVALID_PARAMS, "Invalid params",
    #         "InvalidParamsError", str(error),
    #     )
    except TaskNotCancelable as error:
        return rpc.err(
            body.get("id"),
            rpc.TASK_NOT_CANCELABLE,
            "Task cannot be canceled",
            "TaskNotCancelableError",
            str(error),
        )
    except UnsupportedOperation as error:
        return rpc.err(
            body.get("id"),
            rpc.UNSUPPORTED_OPERATION,
            "This operation is not supported",
            "UnsupportedOperationError",
            str(error),
        )    
    except AuthRequired as error:
        return JSONResponse(
            status_code=401,
            headers={"WWW-Authenticate": 'Bearer realm="extended-agent-card"'},
            content=rpc.err(
                body.get("id"),
                rpc.INVALID_REQUEST,
                "Authentication required",
                "AuthenticationRequiredError",
                str(error),
            ),
        )
    except InvalidParams as e:
        return rpc.err(body.get("id"), rpc.INVALID_PARAMS, "Invalid params",
                       "InvalidParamsError", str(e))
    except TaskNotFound as e:
        return rpc.err(body.get("id"), rpc.INVALID_PARAMS, "Invalid params",
                       "TaskNotFoundError", str(e))
    except store.IllegalTransition as e:
        return rpc.err(body.get("id"), rpc.INTERNAL_ERROR, "Internal error",
                       "InternalError", str(e))
    return rpc.ok(body.get("id"), result)