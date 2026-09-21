from benchflow.application.ports.token_provider import (
    InvalidTokenError,
    TokenProvider,
)
from benchflow.application.ports.user_repository import UserRepository
from benchflow.domain.user import User


class AuthenticationError(Exception):
    """Raised when the current user cannot be authenticated."""


class CurrentUserService:
    """Resolve the authenticated user from an access token."""

    def __init__(
            self,
            user_repository: UserRepository,
            token_provider: TokenProvider,
    ) -> None:
        self._user_repository = user_repository
        self._token_provider = token_provider

    async def get_current_user(self, token: str) -> User:
        """Return the user authenticated by an access token."""

        try:
            user_id = self._token_provider.validate_access_token(token)
        except InvalidTokenError as error:
            raise AuthenticationError from error

        user = await self._user_repository.find_by_id(user_id)

        if user is None:
            raise AuthenticationError

        return user
