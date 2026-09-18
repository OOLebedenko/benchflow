from pathlib import Path

from alembic.config import Config

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


def create_alembic_config() -> Config:
    """Create Alembic configuration."""

    return Config(str(ALEMBIC_INI))
