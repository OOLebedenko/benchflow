from typing import Protocol

from benchflow.domain.run import Run


class RunRepository(Protocol):
    """Define persistence operations for runs."""

    def add(
            self,
            run: Run,
    ) -> None:
        """Stage a run addition."""
        ...
