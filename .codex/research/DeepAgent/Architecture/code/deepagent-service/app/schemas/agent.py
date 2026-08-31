from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)


class AgentRunResponse(BaseModel):
    agent: str
    thread_id: str
    output: str

