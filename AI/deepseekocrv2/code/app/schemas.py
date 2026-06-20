from pydantic import BaseModel, Field


class PageOCRResult(BaseModel):
    index: int = Field(ge=0)
    filename: str
    text: str
    elapsed_ms: int = Field(ge=0)
    error: str | None = None


class BatchOCRResponse(BaseModel):
    count: int = Field(ge=0)
    elapsed_ms: int = Field(ge=0)
    results: list[PageOCRResult]
