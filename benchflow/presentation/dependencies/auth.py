from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.application.ports.token_provider import TokenProvider
from benchflow.application.services.auth import AuthService
from benchflow.application.services.current_user import (
    AuthenticationError,
    CurrentUserService,
)
from benchflow.application.services.login import LoginService
from benchflow.domain.user import User
from benchflow.infrastructure.db.flusher import SqlAlchemyFlusher
from benchflow.infrastructure.db.transaction_manager import (
    SqlAlchemyTransactionManager,
)
from benchflow.infrastructure.repositories.user import (
    SqlAlchemyUserRepository,
)
from benchflow.infrastructure.security.password import PwdlibPasswordHasher
from benchflow.presentation.dependencies.database import get_session

bearer_scheme = HTTPBearer(auto_error=False)


def get_token_provider(request: Request) -> TokenProvider:
    """Provide the application token provider."""

    return cast(
        TokenProvider,
        request.app.state.token_provider,
    )


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


async def get_login_service(
        session: Annotated[AsyncSession, Depends(get_session)],
        token_provider: Annotated[
            TokenProvider,
            Depends(get_token_provider),
        ],
) -> LoginService:
    """Provide login service for the current request."""

    repository = SqlAlchemyUserRepository(session)
    password_hasher = PwdlibPasswordHasher()

    return LoginService(
        user_repository=repository,
        password_hasher=password_hasher,
        token_provider=token_provider,
    )


async def build_current_user_service(
        session: Annotated[AsyncSession, Depends(get_session)],
        token_provider: Annotated[
            TokenProvider,
            Depends(get_token_provider),
        ],
) -> CurrentUserService:
    """Provide current user service for the current request."""

    repository = SqlAlchemyUserRepository(session)

    return CurrentUserService(
        user_repository=repository,
        token_provider=token_provider,
    )


async def get_current_user(
        credentials: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(bearer_scheme),
        ],
        current_user_service: Annotated[
            CurrentUserService,
            Depends(build_current_user_service),
        ],
) -> User:
    """Provide the authenticated user for the current request."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        return await current_user_service.get_current_user(
            credentials.credentials
        )
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error
