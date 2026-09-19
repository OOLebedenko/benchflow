from typing import Annotated

from fastapi import APIRouter, Depends

from benchflow.domain.user import User
from benchflow.presentation.dependencies.auth import get_current_user
from benchflow.presentation.schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
) -> UserResponse:
    """Return the authenticated user."""

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
    )
