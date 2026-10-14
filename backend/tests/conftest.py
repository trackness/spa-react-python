from pathlib import Path

import pytest


@pytest.fixture
def database_file(tmp_path: Path) -> Path:
    return tmp_path / "app.db"


@pytest.fixture(autouse=True)
def valid_settings(monkeypatch: pytest.MonkeyPatch, database_file: Path) -> None:
    monkeypatch.setenv("APP_LISTEN_ADDRESS__HOST", "127.0.0.1")
    monkeypatch.setenv("APP_LISTEN_ADDRESS__PORT", "8000")
    monkeypatch.setenv("APP_DATABASE_FILE", str(database_file))
