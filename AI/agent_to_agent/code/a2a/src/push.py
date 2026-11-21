import httpx

CONFIGS: dict[str, dict] = {}


def save(config: dict) -> dict:
    CONFIGS[config["taskId"]] = config
    return config


def get(task_id: str) -> dict | None:
    return CONFIGS.get(task_id)


def notify(task: dict) -> None:
    """태스크가 종료·중단 상태가 되면 호출한 쪽에 알린다."""
    config = CONFIGS.get(task["id"])
    if not config:
        return

    headers = {"Content-Type": "application/a2a+json"}
    auth = config.get("authentication") or {}
    if auth.get("scheme") and auth.get("credentials"):
        headers["Authorization"] = f"{auth['scheme']} {auth['credentials']}"
    if config.get("token"):
        headers["X-A2A-Notification-Token"] = config["token"]

    # 스트리밍과 같은 StreamResponse 모양이다. 상태 변화는 statusUpdate에 담는다.
    body = {"statusUpdate": {
        "taskId": task["id"],
        "contextId": task["contextId"],
        "status": task["status"],
    }}

    try:
        httpx.post(config["url"], json=body, headers=headers, timeout=10)
    except Exception:
        # 한 번만 보낸다. 실패해도 태스크는 그대로다.
        pass