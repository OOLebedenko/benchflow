from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from benchflow.config import load_settings
from benchflow.infrastructure.db.session import (
    create_engine,
    create_session_factory,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application-level resources."""

    settings = load_settings()

    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    app.state.session_factory = session_factory

    try:
        yield
    finally:
        await engine.dispose()
