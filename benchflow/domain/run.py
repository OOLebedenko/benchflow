from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class RunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Run:
    id: UUID
    bench_id: UUID
    status: RunStatus
