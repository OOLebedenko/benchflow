from uuid import UUID

from pydantic import BaseModel, Field

from benchflow.domain.bench import BenchStatus


class BenchCreateRequest(BaseModel):
    """Represent test bench creation input."""

    name: str = Field(min_length=1, max_length=255)
    status: BenchStatus = BenchStatus.AVAILABLE


class BenchResponse(BaseModel):
    """Represent a test bench in an API response."""

    id: UUID
    name: str
    status: BenchStatus
