from sqlalchemy import create_engine, text


def test_postgres_connection(database_url: str) -> None:
    """Smoke test PostgreSQL container connectivity."""

    engine = create_engine(database_url)

    try:
        with engine.connect() as connection:
            result = connection.scalar(text("SELECT 1"))
    finally:
        engine.dispose()

    assert result == 1
