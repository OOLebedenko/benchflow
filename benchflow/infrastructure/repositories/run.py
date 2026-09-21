from benchflow.domain.run import Run
from benchflow.infrastructure.db.models.run import RunModel
from benchflow.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


class SqlAlchemyRunRepository:
    """Persist runs with SQLAlchemy."""

    def __init__(
            self,
            unit_of_work: SqlAlchemyUnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    def add(
            self,
            run: Run,
    ) -> None:
        """Stage a run addition in the current unit of work."""

        model = RunModel(
            id=run.id,
            bench_id=run.bench_id,
            status=run.status.value,
        )

        self._unit_of_work.stage_add(model)
