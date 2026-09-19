from uuid import uuid4

from benchflow.application.ports.flusher import (
    Flusher,
    UniqueConstraintViolationError,
)
from benchflow.application.ports.password_hasher import PasswordHasher
from benchflow.application.ports.transaction_manager import TransactionManager
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
            flusher: Flusher,
            transaction_manager: TransactionManager,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def register(
            self,
            email: str,
            password: str,
    ) -> User:
        """Register a new user."""

        existing_user = await self._user_repository.find_by_email(email)

        if existing_user is not None:
            raise EmailAlreadyExistsError

        password_hash = await self._password_hasher.hash(password)

        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
        )

        self._user_repository.add(user)

        try:
            await self._flusher.flush()
        except UniqueConstraintViolationError as error:
            raise EmailAlreadyExistsError from error

        await self._transaction_manager.commit()

        return user
