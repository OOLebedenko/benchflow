from pathlib import Path

from alembic.config import Config
from psycopg import connect, sql
from sqlalchemy.engine import make_url

POSTGRES_IMAGE = "postgres:17"
POSTGRES_DRIVER = "psycopg"

REDIS_IMAGE = "redis:8-alpine"
REDIS_PORT = 6379

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


def create_alembic_config() -> Config:
    """Create Alembic configuration."""

    return Config(str(ALEMBIC_INI))


def create_test_database_url(
        database_url: str,
        database_name: str,
) -> str:
    """Create an isolated database on the test PostgreSQL server."""

    base_url = make_url(database_url)

    # CREATE DATABASE must run outside a transaction, so connect
    # to the built-in postgres database with autocommit enabled.
    admin_url = base_url.set(
        drivername="postgresql",
        database="postgres",
    )

    with connect(
            admin_url.render_as_string(hide_password=False),
            autocommit=True,
    ) as connection:
        connection.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(database_name)
            )
        )

    # Preserve the SQLAlchemy driver and change only the database name.
    return base_url.set(
        database=database_name
    ).render_as_string(
        hide_password=False
    )
