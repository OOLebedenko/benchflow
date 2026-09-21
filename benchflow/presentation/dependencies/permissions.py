from typing import Annotated

from fastapi import Depends, HTTPException, status

from benchflow.domain.user import User, UserRole
from benchflow.presentation.dependencies.auth import get_current_user


async def require_admin(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
) -> User:
    """Require administrator role."""

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return current_user
