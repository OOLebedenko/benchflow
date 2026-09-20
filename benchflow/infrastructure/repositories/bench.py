from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.domain.bench import Bench, BenchStatus
from benchflow.infrastructure.db.models.bench import BenchModel


class SqlAlchemyBenchRepository:
    """Read benches with SQLAlchemy."""

    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_all(self) -> list[Bench]:
        """Return all benches."""

        statement = select(BenchModel)
        result = await self._session.execute(statement)
        models = result.scalars().all()

        return [
            self._to_domain(model)
            for model in models
        ]

    async def find_by_id(
            self,
            bench_id: UUID,
    ) -> Bench | None:
        """Find a bench by its identifier."""

        statement = select(BenchModel).where(
            BenchModel.id == bench_id
        )
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_domain(model)

    @staticmethod
    def _to_domain(
            model: BenchModel,
    ) -> Bench:
        """Convert a persistence model to a domain bench."""

        return Bench(
            id=model.id,
            name=model.name,
            status=BenchStatus(model.status),
        )
