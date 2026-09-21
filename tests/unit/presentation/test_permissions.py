from uuid import uuid4

import pytest
from fastapi import HTTPException

from benchflow.domain.user import User, UserRole
from benchflow.presentation.dependencies.permissions import require_admin


async def test_require_admin_allows_admin() -> None:
    """Allow an administrator."""

    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="hashed-password",
        role=UserRole.ADMIN,
    )

    assert await require_admin(user) == user


async def test_require_admin_rejects_user() -> None:
    """Reject a regular user."""

    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="hashed-password",
        role=UserRole.USER,
    )

    with pytest.raises(HTTPException) as exc_info:
        await require_admin(user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"
