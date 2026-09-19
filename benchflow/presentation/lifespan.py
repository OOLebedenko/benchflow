from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from benchflow.config import load_settings
from benchflow.infrastructure.db.session import (
    create_engine,
    create_session_factory,
)
from benchflow.infrastructure.security.jwt import JwtTokenProvider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application-level resources."""

    settings = load_settings()

    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    token_provider = JwtTokenProvider(
        secret=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
    )

    app.state.session_factory = session_factory
    app.state.token_provider = token_provider

    try:
        yield
    finally:
        await engine.dispose()
