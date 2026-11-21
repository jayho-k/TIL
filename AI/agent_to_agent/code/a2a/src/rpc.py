def ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}

def err(req_id, code, message, a2a_code=None, a2a_message=None):
    error = {"code": code, "message": message}
    if a2a_code:
        error["data"] = {
            "a2aErrorCode": a2a_code,
            "a2aErrorMessage": a2a_message or message,
        }
    return {"jsonrpc": "2.0", "id": req_id, "error": error}

def send_message_result(task: dict) -> dict:
    """SendMessage 응답은 태스크를 task 필드에 담는다."""
    return {"task": task}

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
UNSUPPORTED_OPERATION = -32004
TASK_NOT_CANCELABLE = -32002