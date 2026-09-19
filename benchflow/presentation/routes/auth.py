from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from benchflow.application.services.auth import (
    AuthService,
    EmailAlreadyExistsError,
)
from benchflow.application.services.login import (
    InvalidCredentialsError,
    LoginService,
)
from benchflow.presentation.dependencies.auth import (
    get_auth_service,
    get_login_service,
)
from benchflow.presentation.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
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


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
        data: LoginRequest,
        login_service: Annotated[
            LoginService,
            Depends(get_login_service),
        ],
) -> TokenResponse:
    """Authenticate a user and issue an access token."""

    try:
        access_token = await login_service.login(
            email=str(data.email),
            password=data.password,
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    return TokenResponse(
        access_token=access_token,
    )
