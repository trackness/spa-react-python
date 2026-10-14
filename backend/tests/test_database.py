import shutil
import sqlite3
from collections import Counter
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKeyConstraint,
    Index,
    Integer,
    Table,
    UniqueConstraint,
    inspect,
)
from sqlalchemy.exc import OperationalError

from app import BACKEND
from app.database import Base, alembic_config, database_engine
from app.main import app

FAILING_MIGRATION = """
from alembic import op

revision = "failing"
down_revision = {head!r}


def upgrade() -> None:
    op.execute("CREATE TABLE half_done (id INTEGER)")
    op.execute("SELECT * FROM no_such_table")
"""


@pytest.fixture
def versions() -> Iterator[Path]:
    """The migrations directory, rid afterwards of whatever the test added."""
    versions = BACKEND / "migrations" / "versions"
    created = not versions.exists()
    versions.mkdir(exist_ok=True)
    before = set(versions.iterdir())
    try:
        yield versions
    finally:
        if created:
            shutil.rmtree(versions)
        else:
            for added in set(versions.iterdir()) - before:
                if added.is_dir():
                    shutil.rmtree(added)
                else:
                    added.unlink()


@pytest.fixture
def failing_migration(versions: Path) -> None:
    """Add a migration that changes the schema, then fails."""
    head = ScriptDirectory.from_config(alembic_config()).get_current_head()
    (versions / "failing.py").write_text(FAILING_MIGRATION.format(head=head))


@pytest.fixture
def widget(versions: Path) -> Iterator[Table]:  # noqa: ARG001
    """Declare tables with every kind of constraint, two of each sharing a column."""
    gadget = Table(
        "gadget",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("code", Integer),
    )
    widget = Table(
        "widget",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("a", Integer),
        Column("b", Integer),
        Column("c", Integer),
        UniqueConstraint("a", "b"),
        UniqueConstraint("a", "c"),
        Index(None, "a", "b"),
        Index(None, "a", "c"),
        CheckConstraint("a > 0", name="positive_a"),
        ForeignKeyConstraint(["a", "b"], ["gadget.id", "gadget.code"]),
        ForeignKeyConstraint(["a", "c"], ["gadget.id", "gadget.code"]),
    )
    try:
        yield widget
    finally:
        Base.metadata.remove(widget)
        Base.metadata.remove(gadget)


def migrate_to_the_models(message: str) -> None:
    """Create a migration from the models, then start the App, which applies it."""
    command.revision(alembic_config(), message=message, autogenerate=True)
    with TestClient(app):
        pass


def constraint_names(database_file: Path) -> list[str | None]:
    engine = database_engine(database_file)
    inspector = inspect(engine)
    names = [
        name
        for table in ("gadget", "widget")
        for name in [
            inspector.get_pk_constraint(table)["name"],
            *(c["name"] for c in inspector.get_unique_constraints(table)),
            *(c["name"] for c in inspector.get_indexes(table)),
            *(c["name"] for c in inspector.get_check_constraints(table)),
            *(c["name"] for c in inspector.get_foreign_keys(table)),
        ]
    ]
    engine.dispose()
    return names


@pytest.mark.usefixtures("widget")
def test_a_migration_names_every_constraint(database_file: Path) -> None:
    migrate_to_the_models("add widgets")

    assert Counter(constraint_names(database_file)) == Counter(
        [
            "pk_gadget",
            "pk_widget",
            "uq_widget_a_b",
            "uq_widget_a_c",
            "ix_widget_a_b",
            "ix_widget_a_c",
            "ck_widget_positive_a",
            "fk_widget_a_b_gadget",
            "fk_widget_a_c_gadget",
        ]
    )


def test_a_migration_can_drop_a_constraint(database_file: Path, widget: Table) -> None:
    migrate_to_the_models("add widgets")
    [unique_a_c] = [
        constraint
        for constraint in widget.constraints
        if isinstance(constraint, UniqueConstraint)
        and [column.name for column in constraint.columns] == ["a", "c"]
    ]
    widget.constraints.remove(unique_a_c)

    migrate_to_the_models("drop a unique constraint")

    assert "uq_widget_a_c" not in constraint_names(database_file)


@pytest.mark.usefixtures("failing_migration")
def test_a_failed_migration_leaves_the_database_unchanged(database_file: Path) -> None:
    with pytest.raises(OperationalError), TestClient(app):
        pass

    with closing(sqlite3.connect(database_file)) as database:
        tables = database.execute("SELECT name FROM sqlite_master").fetchall()

    assert ("half_done",) not in tables


def test_the_app_migrates_the_database_before_it_serves(database_file: Path) -> None:
    with TestClient(app), closing(sqlite3.connect(database_file)) as database:
        tables = database.execute("SELECT name FROM sqlite_master").fetchall()

    assert ("alembic_version",) in tables


def test_the_database_uses_write_ahead_logging(database_file: Path) -> None:
    with TestClient(app), closing(sqlite3.connect(database_file)) as database:
        [journal_mode] = database.execute("PRAGMA journal_mode").fetchone()

    assert journal_mode == "wal"
