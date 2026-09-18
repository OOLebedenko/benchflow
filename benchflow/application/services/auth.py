from uuid import uuid4

from benchflow.application.ports.password_hasher import PasswordHasher
from benchflow.application.ports.user_repository import UserRepository
from benchflow.domain.user import User


class EmailAlreadyExistsError(Exception):
    """Raised when a user with the given email already exists."""


class AuthService:
    """Provide authentication-related application operations."""

    def __init__(
            self,
            user_repository: UserRepository,
            password_hasher: PasswordHasher,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def register(
            self,
            email: str,
            password: str,
    ) -> User:
        """Register a new user."""

        existing_user = await self.user_repository.find_by_email(email)

        if existing_user is not None:
            raise EmailAlreadyExistsError

        password_hash = await self.password_hasher.hash(password)

        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
        )

        await self.user_repository.add(user)

        return user
