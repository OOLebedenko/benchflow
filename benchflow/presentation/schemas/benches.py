from uuid import UUID

from pydantic import BaseModel

from benchflow.domain.bench import BenchStatus


class BenchResponse(BaseModel):
    """Represent a test bench in an API response."""

    id: UUID
    name: str
    status: BenchStatus
