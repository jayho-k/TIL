from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    state_code: int = 200
    message: str = "Success"
    data: Optional[T] = None
