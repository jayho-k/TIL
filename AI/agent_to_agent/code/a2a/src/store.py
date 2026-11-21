# TASK_STATE_SUBMITTED → TASK_STATE_WORKING → TASK_STATE_COMPLETED

# 외부 (A2A)              내부 (LangGraph)
# taskId         ~~~     thread_id `trip-~~`
# contextId.     ~~~     여러개의 thread_id를 묶은 값

from datetime import datetime, timezone

TERMINAL = {
    "TASK_STATE_COMPLETED",
    "TASK_STATE_FAILED",
    "TASK_STATE_CANCELED",
    "TASK_STATE_REJECTED",
}

INTERRUPTED = {
    "TASK_STATE_INPUT_REQUIRED",
    "TASK_STATE_AUTH_REQUIRED",
}

class IllegalTransition(Exception):
    pass

TASKS: dict[str, dict] = {}

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def create(task_id: str, context_id: str, message: dict) -> dict:
    task = {
        "id": task_id,
        "contextId": context_id,
        "status": {"state": "TASK_STATE_SUBMITTED", "timestamp": now()},
        "artifacts": [],
        "history": [message],
    }
    TASKS[task_id] = task
    return task

def set_state(task_id: str, state: str) -> dict:
    task = TASKS[task_id]
    current = task["status"]["state"]
    if current in TERMINAL:
        raise IllegalTransition(f"{current}는 종료 상태라 {state}로 못 바꿉니다")
    task["status"] = {"state": state, "timestamp": now()}
    return task

def get(task_id: str) -> dict | None:
    return TASKS.get(task_id)

def all_tasks() -> list[dict]:
    return list(TASKS.values())

def by_context(context_id: str) -> list[dict]:
    return [t for t in TASKS.values() if t["contextId"] == context_id]

def add_artifact(task_id: str, artifact: dict) -> dict:
    TASKS[task_id]["artifacts"].append(artifact)
    return TASKS[task_id]