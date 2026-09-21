from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class BenchStatus(StrEnum):
    """Represent the operational status of a bench."""

    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    BUSY = "busy"


@dataclass(slots=True)
class Bench:
    """Represent a bench in the domain."""

    id: UUID
    name: str
    status: BenchStatus
