import uuid

import grpc
from a2a.types import a2a_pb2 as pb
from a2a.types import a2a_pb2_grpc as pb_grpc

def connect(target: str = "worker:50051") -> pb_grpc.A2AServiceStub:
    return pb_grpc.A2AServiceStub(grpc.insecure_channel(target))

def request(text: str) -> pb.SendMessageRequest:
    return pb.SendMessageRequest(message=pb.Message(
        message_id=str(uuid.uuid4()),
        role=pb.Role.ROLE_USER,
        parts=[pb.Part(text=text, media_type="text/plain")],
    ))