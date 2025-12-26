from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from app.container import Container
from app.services.user_service import UserService
from app.schemas.base import BaseResponse
from app.schemas.user import CreateUserRequest, UserResponse

router = APIRouter()

@router.post("/users", response_model=BaseResponse[UserResponse])
@inject
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.create_new_user(request.email, request.password)
    return BaseResponse(
        data=UserResponse.model_validate(user),
        message="User created successfully"
    )

@router.get("/users/{user_id}", response_model=BaseResponse[UserResponse])
@inject
async def get_user(
    user_id: int,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.get_user(user_id)
    if not user:
        # In a real app, you might want to return a BaseResponse with an error state_code 
        # instead of raising HTTPException, or handle exceptions globally to return BaseResponse.
        # For now, we raise 404 but the client expects BaseResponse structure on success.
        raise HTTPException(status_code=404, detail="User not found")
        
    return BaseResponse(data=UserResponse.model_validate(user))
