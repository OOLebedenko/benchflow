from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class User:
    """Represent a user in the domain."""

    id: UUID
    email: str
    password_hash: str
