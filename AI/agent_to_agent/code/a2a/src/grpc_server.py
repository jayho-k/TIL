from concurrent import futures

import grpc
from google.protobuf import json_format
from a2a.types import a2a_pb2 as pb
from a2a.types import a2a_pb2_grpc as pb_grpc

import a2a_server as logic
import store

STATUS = {
    logic.InvalidParams: grpc.StatusCode.INVALID_ARGUMENT,
    logic.TaskNotFound: grpc.StatusCode.NOT_FOUND,
    logic.TaskNotCancelable: grpc.StatusCode.FAILED_PRECONDITION,
    logic.UnsupportedOperation: grpc.StatusCode.FAILED_PRECONDITION,
    logic.AuthRequired: grpc.StatusCode.UNAUTHENTICATED,
    store.IllegalTransition: grpc.StatusCode.INTERNAL,
}

def run(context, handler, *args):
    """JSON 서버와 같은 핸들러를 부르고, 예외는 gRPC 상태 코드로 바꾼다."""
    try:
        return handler(*args)
    except tuple(STATUS) as e:
        context.abort(STATUS[type(e)], str(e))

def bearer_of(context) -> str | None:
    value = dict(context.invocation_metadata()).get("authorization", "")
    return value[7:] if value.lower().startswith("bearer ") else None

def to_dict(message) -> dict:
    return json_format.MessageToDict(message)

def to_proto(data: dict, message):
    return json_format.ParseDict(data, message)

class ExpenseService(pb_grpc.A2AServiceServicer):
    def SendMessage(self, request, context):
        task = run(context, logic.handle_send_message, to_dict(request), bearer_of(context))
        return pb.SendMessageResponse(task=to_proto(task, pb.Task()))

    def GetTask(self, request, context):
        task = run(context, logic.handle_get_task, to_dict(request))
        return to_proto(task, pb.Task())

    def ListTasks(self, request, context):
        page = run(context, logic.handle_list_tasks, to_dict(request))
        return to_proto(page, pb.ListTasksResponse())

    def CancelTask(self, request, context):
        task = run(context, logic.handle_cancel_task, to_dict(request))
        return to_proto(task, pb.Task())

    def GetExtendedAgentCard(self, request, context):
        card = run(context, logic.handle_get_extended_agent_card, {}, bearer_of(context))
        return to_proto(card, pb.AgentCard())

    def CreateTaskPushNotificationConfig(self, request, context):
        config = run(context, logic.handle_create_push_config, to_dict(request))
        return to_proto(config, pb.TaskPushNotificationConfig())

    def GetTaskPushNotificationConfig(self, request, context):
        config = run(context, logic.handle_get_push_config, to_dict(request))
        return to_proto(config, pb.TaskPushNotificationConfig())

    def SendStreamingMessage(self, request, context):
        params = to_dict(request)
        params.setdefault("configuration", {})["returnImmediately"] = True
        task = run(context, logic.handle_send_message, params, bearer_of(context))
        yield from stream(task)

    def SubscribeToTask(self, request, context):
        task = run(context, logic.handle_get_task, to_dict(request))
        state = task["status"]["state"]
        if state in store.TERMINAL:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, f"{state} 상태라 구독할 수 없습니다")
        yield from stream(task)

def stream(task: dict):
    yield pb.StreamResponse(task=to_proto(task, pb.Task()))
    state = task["status"]["state"]
    if state in store.TERMINAL or state in store.INTERRUPTED:
        return

    for kind, payload in logic.events(task["id"], task["contextId"]):
        if kind == "statusUpdate":
            event = to_proto(payload, pb.TaskStatusUpdateEvent())
            yield pb.StreamResponse(status_update=event)
        else:
            event = to_proto(payload, pb.TaskArtifactUpdateEvent())
            yield pb.StreamResponse(artifact_update=event)

def start(port: int) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb_grpc.add_A2AServiceServicer_to_server(ExpenseService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"gRPC 입구가 {port} 포트에서 열렸습니다", flush=True)
    return server