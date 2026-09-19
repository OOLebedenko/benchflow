from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.services.auth import AuthService
from benchflow.infrastructure.db.flusher import SqlAlchemyFlusher
from benchflow.infrastructure.db.transaction_manager import (
    SqlAlchemyTransactionManager,
)
from benchflow.infrastructure.repositories.user import (
    SqlAlchemyUserRepository,
)
from benchflow.infrastructure.security.password import PwdlibPasswordHasher
from benchflow.presentation.dependencies.database import get_session


async def get_auth_service(
        session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthService:
    """Provide authentication service for the current request."""

    # All persistence adapters receive the same session, so they operate
    # inside the same unit of work and database transaction.
    repository = SqlAlchemyUserRepository(session)
    flusher = SqlAlchemyFlusher(session)
    transaction_manager = SqlAlchemyTransactionManager(session)

    password_hasher = PwdlibPasswordHasher()

    return AuthService(
        user_repository=repository,
        password_hasher=password_hasher,
        flusher=flusher,
        transaction_manager=transaction_manager,
    )
