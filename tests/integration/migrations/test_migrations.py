import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config
from alembic.script import Script, ScriptDirectory

from tests.config import create_alembic_config


class MigrationRevision:
    """Represent a migration revision used by stairway tests."""

    _DOWNGRADE_ONE_REVISION = "-1"

    def __init__(self, script: Script) -> None:
        self.script = script

    @property
    def revision(self) -> str:
        """Return the current revision identifier."""

        return self.script.revision

    @property
    def downgrade_revision(self) -> str:
        """Return the revision to downgrade to."""

        previous_revision = self.script.down_revision

        # The first migration has no parent revision.
        # Alembic's "-1" value means to downgrade by one revision.
        if previous_revision is None:
            return self._DOWNGRADE_ONE_REVISION

        # Normalize one or multiple parent revisions
        # to the same representation.
        parent_revisions: tuple[str, ...] = (
            (previous_revision,)
            if isinstance(previous_revision, str)
            else tuple(previous_revision)
        )

        # Stairway tests currently expect a single parent revision.
        assert len(parent_revisions) == 1, (
            "Stairway test does not support merge revisions: "
            f"{self.revision!r} has parents {parent_revisions!r}"
        )

        return parent_revisions[0]

    @classmethod
    def get_all(
            cls,
            config: Config,
    ) -> list["MigrationRevision"]:
        """Return all migration revisions from first to last."""

        revisions_dir = ScriptDirectory.from_config(config)

        scripts = list(
            revisions_dir.walk_revisions("base", "heads")
        )
        scripts.reverse()

        return [cls(script) for script in scripts]


@pytest.mark.parametrize(
    "revision",
    MigrationRevision.get_all(create_alembic_config()),
)
def test_migrations_stairway(
        alembic_config: Config,
        revision: MigrationRevision,
) -> None:
    """Check migration upgrade, downgrade, and repeated upgrade."""

    upgrade(alembic_config, revision.revision)

    downgrade(
        alembic_config,
        revision.downgrade_revision,
    )

    upgrade(alembic_config, revision.revision)
