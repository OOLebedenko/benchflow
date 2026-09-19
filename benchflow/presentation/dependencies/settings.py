from typing import cast

from fastapi import Request

from benchflow.config import Settings


def get_settings(
        request: Request,
) -> Settings:
    """Provide application settings."""

    return cast(
        Settings,
        request.app.state.settings,
    )
