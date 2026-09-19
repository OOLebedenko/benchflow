from typing import Protocol
from uuid import UUID


class InvalidTokenError(Exception):
    """Raised when an access token is invalid."""


class TokenProvider(Protocol):
    """Define token creation operations."""

    def create_access_token(
            self,
            user_id: UUID,
    ) -> str:
        """Create an access token for a user."""
        ...

    def validate_access_token(
            self,
            token: str,
    ) -> UUID:
        """Validate an access token and return its user identifier."""
        ...
