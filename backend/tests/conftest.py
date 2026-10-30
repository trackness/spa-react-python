import tomllib
from pathlib import Path

import pytest

from app import BACKEND


@pytest.fixture
def project_name() -> str:
    name = tomllib.loads((BACKEND / "pyproject.toml").read_text())["project"]["name"]
    assert isinstance(name, str)
    return name


@pytest.fixture
def release_version() -> str:
    return (BACKEND.parent / "version.txt").read_text().strip()


@pytest.fixture(params=["/health/live", "/health/ready", "/metrics"])
def excluded_path(request: pytest.FixtureRequest) -> str:
    """Each path kept out of traces and request metrics."""
    path = request.param
    assert isinstance(path, str)
    return path


@pytest.fixture
def database_file(tmp_path: Path) -> Path:
    return tmp_path / "app.db"


@pytest.fixture
def frontend_directory(tmp_path: Path) -> Path:
    """A built Frontend: its index.html."""
    directory = tmp_path / "frontend"
    directory.mkdir()
    (directory / "index.html").write_text("<p>The Frontend</p>")
    return directory


@pytest.fixture(autouse=True)
def valid_settings(
    monkeypatch: pytest.MonkeyPatch, database_file: Path, frontend_directory: Path
) -> None:
    monkeypatch.setenv("APP_LISTEN_ADDRESS__HOST", "127.0.0.1")
    monkeypatch.setenv("APP_LISTEN_ADDRESS__PORT", "8000")
    monkeypatch.setenv("APP_DATABASE_FILE", str(database_file))
    monkeypatch.setenv("APP_FRONTEND_DIRECTORY", str(frontend_directory))
