from benchflow.application.ports.password_hasher import PasswordHasher
from benchflow.application.ports.token_provider import TokenProvider
from benchflow.application.ports.user_repository import UserRepository


class InvalidCredentialsError(Exception):
    """Raised when authentication credentials are invalid."""


class LoginService:
    """Authenticate users and issue access tokens."""

    def __init__(
            self,
            user_repository: UserRepository,
            password_hasher: PasswordHasher,
            token_provider: TokenProvider,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    async def login(
            self,
            email: str,
            password: str,
    ) -> str:
        """Authenticate a user and return an access token."""

        user = await self._user_repository.find_by_email(email)

        if user is None:
            raise InvalidCredentialsError

        password_is_valid = await self._password_hasher.verify(
            password,
            user.password_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsError

        return self._token_provider.create_access_token(user.id)
