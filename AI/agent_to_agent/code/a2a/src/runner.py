"""작업을 요청 처리와 분리한다. 호출한 쪽이 끊어도 계속 돈다."""
import threading
import uuid

import adapter
import store

# message CancelTaskRequest {
#   string tenant = 1;
#   string id = 2 [(google.api.field_behavior) = REQUIRED];
#   google.protobuf.Struct metadata = 3;
# }

_lock = threading.Lock()
_running: set[str] = set()

def run_in_background(task_id: str, trip_id: str, on_done) -> None:
    with _lock:
        if task_id in _running:
            return
        _running.add(task_id)

    def work():
        try:
            adapter.start(task_id, trip_id)
            on_done(task_id, adapter.read(task_id))
        except Exception as e:
            store.set_state(task_id, "TASK_STATE_FAILED")
            store.get(task_id)["status"]["message"] = {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_AGENT",
                "parts": [{"text": f"처리 중 오류: {e}", "mediaType": "text/plain"}],
            }
        finally:
            with _lock:
                _running.discard(task_id)

    threading.Thread(target=work, daemon=True).start()

def is_running(task_id: str) -> bool:
    with _lock:
        return task_id in _running

_cancelled: set[str] = set()

def request_cancel(task_id: str) -> None:
    with _lock:
        _cancelled.add(task_id)

def is_cancelled(task_id: str) -> bool:
    with _lock:
        return task_id in _cancelled