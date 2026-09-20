from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from benchflow.domain.bench import Bench, BenchStatus
from benchflow.infrastructure.db.models.bench import BenchModel
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


class SqlAlchemyBenchRepository:
    """Persist benches with SQLAlchemy."""

    def __init__(
            self,
            session: AsyncSession,
            unit_of_work: SqlAlchemyUnitOfWork,
    ) -> None:
        self._session = session
        self._unit_of_work = unit_of_work

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

    def add(self, bench: Bench) -> None:
        """Add a bench to the current SQLAlchemy unit of work."""

        model = BenchModel(
            id=bench.id,
            name=bench.name,
            status=bench.status.value,
        )

        self._session.add(model)

    def update(
            self,
            bench: Bench,
    ) -> None:
        """Stage a bench update in the current unit of work."""

        name = bench.name
        status = bench.status.value

        def apply(model: BenchModel) -> None:
            model.name = name
            model.status = status

        self._unit_of_work.stage_update(
            BenchModel,
            bench.id,
            apply,
        )

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
