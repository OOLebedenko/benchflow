from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.domain.user import User
from benchflow.infrastructure.db.models.user import UserModel


class SqlAlchemyUserRepository:
    """Persist users with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find a user by identifier."""

        statement = select(UserModel).where(
            UserModel.id == user_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
        )

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email."""

        statement = select(UserModel).where(
            UserModel.email == email
        )

        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
        )

    def add(self, user: User) -> None:
        """Add a user to the current SQLAlchemy unit of work."""

        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
        )

        self._session.add(model)
