from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from benchflow.application.services.auth import (
    AuthService,
    EmailAlreadyExistsError,
)
from benchflow.presentation.dependencies.auth import get_auth_service
from benchflow.presentation.schemas.auth import (
    RegisterRequest,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
        data: RegisterRequest,
        auth_service: Annotated[
            AuthService,
            Depends(get_auth_service),
        ],
) -> UserResponse:
    """Register a new user."""

    try:
        user = await auth_service.register(
            email=str(data.email),
            password=data.password,
        )
    except EmailAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from error

    return UserResponse(
        id=user.id,
        email=user.email,
    )
