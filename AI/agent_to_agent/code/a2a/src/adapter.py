import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

from graph import build_graph

_saver_cm = None
_graph = None

def get_graph():
    """서버가 실행되는 동안 그래프와 체크포인터 연결을 유지한다."""
    global _saver_cm, _graph
    if _graph is None:
        _saver_cm = PostgresSaver.from_conn_string(os.environ["POSTGRES_URL"])
        saver = _saver_cm.__enter__()
        saver.setup()
        _graph = build_graph(checkpointer=saver)
    return _graph

def thread_of(task_id: str) -> dict:
    """외부 taskId로 내부 thread_id 설정을 만든다."""
    return {"configurable": {"thread_id": f"task-{task_id}"}}

def start(task_id: str, trip_id: str) -> dict:
    graph = get_graph()
    graph.invoke({"trip_id": trip_id, "log": []}, thread_of(task_id))
    return read(task_id)

def resume(task_id: str, answer: str) -> dict:
    graph = get_graph()
    graph.invoke(Command(resume=answer), thread_of(task_id))
    return read(task_id)

def read(task_id: str) -> dict:
    """LangGraph 상태에서 외부로 전달할 값만 골라낸다."""
    snapshot = get_graph().get_state(thread_of(task_id))
    values = snapshot.values
    waiting = "escalate" in (snapshot.next or ())
    # step 4 -> 다음 노드 ('escalate')
    return {
        "waiting": waiting,
        # "question": (snapshot.interrupts[0].value.get("question")
        #              if waiting and snapshot.interrupts else None),
        "ask": (snapshot.interrupts[0].value
                if waiting and snapshot.interrupts else None),
        "result": {
            "trip_id": values.get("trip_id"),
            "total": values.get("total"),
            "violations": values.get("violations") or [],
            "receipts": len(values.get("receipts") or []),
        },
        "approved": values.get("approved"),
    }

def start_stream(task_id: str, trip_id: str):
    """노드가 끝날 때마다 하나씩 내보낸다. stream_mode="updates"를 그대로 쓴다."""
    graph = get_graph()
    for chunk in graph.stream({"trip_id": trip_id, "log": []},
                              thread_of(task_id), stream_mode="updates"):
        for node, update in chunk.items():
            if node == "__interrupt__":
                continue
            yield node, update