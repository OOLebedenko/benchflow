from typing import Protocol
from uuid import UUID


class TokenProvider(Protocol):
    """Define token creation operations."""

    def create_access_token(
            self,
            user_id: UUID,
    ) -> str:
        """Create an access token for a user."""
        ...
