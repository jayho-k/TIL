from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import ContainerDependency
from app.schemas.agent import AgentRunRequest, AgentRunResponse


router = APIRouter(prefix="/v1/agents", tags=["agents"])


@router.post("/{agent_name}/runs", response_model=AgentRunResponse)
async def run_agent(
    agent_name: str,
    request: AgentRunRequest,
    container: ContainerDependency,
) -> AgentRunResponse:
    try:
        runner = container.agents.get(agent_name)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"agent not found: {agent_name}",
        ) from None

    output = await runner.run(request.message, request.thread_id)
    return AgentRunResponse(
        agent=agent_name,
        thread_id=request.thread_id,
        output=output,
    )

