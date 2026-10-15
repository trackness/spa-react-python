import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Engine, MetaData, create_engine, event
from sqlalchemy.orm import DeclarativeBase

from app import BACKEND


class Base(DeclarativeBase):
    # SQLite rebuilds a table for most schema changes, so every constraint is named
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_N_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def database_engine(database_file: Path) -> Engine:
    engine = create_engine(
        URL.create("sqlite+pysqlite", database=str(database_file)),
        # without it, the driver commits each schema change as soon as it runs
        connect_args={"autocommit": False},
    )
    event.listen(engine, "connect", enable_write_ahead_logging)
    return engine


def enable_write_ahead_logging(connection: sqlite3.Connection, _: object) -> None:
    # the journal mode cannot change inside a transaction
    connection.autocommit = True
    connection.execute("PRAGMA journal_mode=WAL")
    connection.autocommit = False


def alembic_config() -> Config:
    return Config(toml_file=str(BACKEND / "pyproject.toml"))


def migrate() -> None:
    command.upgrade(alembic_config(), "head")
