# message TaskPushNotificationConfig {
#   string tenant = 1;
#   string id = 2;
#   string task_id = 3;
#   string url = 4 [(google.api.field_behavior) = REQUIRED];
#   string token = 5;
#   AuthenticationInfo authentication = 6;
# }

# message AuthenticationInfo {
#   // HTTP Authentication Scheme from the [IANA registry](https://www.iana.org/assignments/http-authschemes/).
#   // Examples: `Bearer`, `Basic`, `Digest`.
#   // Scheme names are case-insensitive per [RFC 9110 Section 11.1](https://www.rfc-editor.org/rfc/rfc9110#section-11.1).
#   string scheme = 1 [(google.api.field_behavior) = REQUIRED];
#   // Push Notification credentials. Format depends on the scheme (e.g., token for Bearer).
#   string credentials = 2;
# }
# 헤더 키 값 = X-A2A-Notification-Token

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# 웹훅을 등록할 때 정해서 에이전트에 넘긴 값들
EXPECTED_CRED = "hook-cred-9"          # 에이전트가 자신을 증명할 때 쓴다
TASK_TOKENS: dict[str, str] = {}       # taskId → 이 태스크용 token

RECEIVED: list[dict] = []
REJECTED: list[dict] = []


@app.post("/hook")
async def hook(request: Request):
    body = await request.json()
    event = body.get("statusUpdate") or {}
    task_id = event.get("taskId")

    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {EXPECTED_CRED}":
        REJECTED.append({"why": "보낸 쪽을 못 믿음", "auth": auth})
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    token = request.headers.get("x-a2a-notification-token")
    expected = TASK_TOKENS.get(task_id)
    if expected is None or token != expected:
        REJECTED.append({"why": "모르는 태스크이거나 token 불일치", "taskId": task_id})
        return JSONResponse({"error": "unknown task"}, status_code=400)

    RECEIVED.append({
        "taskId": task_id,
        "state": (event.get("status") or {}).get("state"),
    })
    return {"ok": True}


@app.post("/expect/{task_id}/{token}")
def expect(task_id: str, token: str):
    TASK_TOKENS[task_id] = token
    return {"ok": True}


@app.get("/received")
def received():
    return {"ok": RECEIVED, "rejected": REJECTED}







# from fastapi import FastAPI, Request

# app = FastAPI()
# RECEIVED: list[dict] = []


# @app.post("/hook")
# async def hook(request: Request):
#     body = await request.json()
#     event = body.get("statusUpdate") or {}
#     RECEIVED.append({
#         "auth": request.headers.get("authorization"),
#         "token": request.headers.get("x-a2a-notification-token"),
#         "taskId": event.get("taskId"),
#         "state": (event.get("status") or {}).get("state"),
#     })
#     return {"ok": True}

# @app.get("/received")
# def received():
#     return RECEIVED