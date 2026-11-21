import asyncio
import uuid

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.types import a2a_pb2 as pb

results: list[tuple[str, str, str]] = []

def ask(text: str) -> pb.SendMessageRequest:
    return pb.SendMessageRequest(message=pb.Message(
        message_id=str(uuid.uuid4()),
        role=pb.Role.ROLE_USER,
        parts=[pb.Part(text=text, media_type="text/plain")],
    ))

async def check(name: str, run) -> None:
    """검사 하나를 실행하고, 예외가 나면 실패로 적는다."""
    try:
        results.append((name, "통과", await run()))
    except Exception as e:
        results.append((name, "실패", f"{type(e).__name__}: {str(e)[:60]}"))

def show() -> None:
    for name, verdict, detail in results:
        print(f"{name:22} {verdict}  {detail}")
    failed = sum(1 for _, verdict, _ in results if verdict == "실패")
    print(f"\n{len(results)}개 중 {failed}개 실패")

async def main() -> None:
    headers = {"Authorization": "Bearer finance-token-abc123"}
    async with httpx.AsyncClient(timeout=900, headers=headers) as http:
        card = await A2ACardResolver(http, "http://worker:8000").get_agent_card() # @app.get("/.well-known/agent-card.json")를 호출해서 Agent Card를 인지하게 해준다.
        client = await create_client(card, ClientConfig(httpx_client=http)) # Streaming으로 호출
        plain = await create_client(card, ClientConfig(httpx_client=http, streaming=False)) # 일반 메시지로 호출
        text = "출장 T-2026-04 경비를 정리해 주세요"
        task_id = None

        async def send_streaming():
            nonlocal task_id
            count, state = 0, None
            async for event in client.send_message(ask(text)):
                count += 1
                kind = event.WhichOneof("payload")
                if kind == "task":
                    task_id, state = event.task.id, event.task.status.state
                elif kind == "status_update":
                    state = event.status_update.status.state
            return f"이벤트 {count}개 · {pb.TaskState.Name(state)}"

        async def send():
            async for event in plain.send_message(ask(text)):
                return pb.TaskState.Name(event.task.status.state)

        async def get_task():
            task = await client.get_task(pb.GetTaskRequest(id=task_id))
            return pb.TaskState.Name(task.status.state)

        async def list_tasks():
            page = await client.list_tasks(pb.ListTasksRequest())
            return "목록 받음"

        async def push_config():
            config = pb.TaskPushNotificationConfig(task_id=task_id, url="http://receiver:8100/hook")
            saved = await client.create_task_push_notification_config(config)
            return saved.url

        async def extended_card():
            extended = await client.get_extended_agent_card(pb.GetExtendedAgentCardRequest())
            return f"skill {len(extended.skills)}개"

        await check("SendStreamingMessage", send_streaming)
        await check("SendMessage", send)
        await check("GetTask", get_task)
        await check("ListTasks", list_tasks)
        await check("웹훅 설정 등록", push_config)
        await check("확장 카드", extended_card)
    show()


if __name__ == "__main__":
    asyncio.run(main())


# CreateTaskPushNotificationConfig : 웹훅 설정을 등록 할 떄 호출, 