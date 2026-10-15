import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app


def settings_rejected_at_startup() -> list[tuple[str | int, ...]]:
    with pytest.raises(ValidationError) as rejected, TestClient(app):
        pass
    return [error["loc"] for error in rejected.value.errors()]


@pytest.mark.parametrize(
    ("variable", "value", "setting"),
    [
        ("APP_LISTEN_ADDRESS__PORT", "70000", ("listen_address", "port")),
        ("APP_LISTEN_ADDRESS__PORT", "0", ("listen_address", "port")),
        ("APP_LISTEN_ADDRESS__HOST", "not-an-ip", ("listen_address", "host")),
    ],
)
def test_an_invalid_setting_stops_the_app(
    monkeypatch: pytest.MonkeyPatch, variable: str, value: str, setting: tuple[str, ...]
) -> None:
    monkeypatch.setenv(variable, value)

    assert settings_rejected_at_startup() == [setting]


@pytest.mark.parametrize(
    ("variable", "setting"),
    [
        ("APP_LISTEN_ADDRESS__HOST", ("listen_address", "host")),
        ("APP_LISTEN_ADDRESS__PORT", ("listen_address", "port")),
        ("APP_DATABASE_FILE", ("database_file",)),
    ],
)
def test_a_missing_setting_stops_the_app(
    monkeypatch: pytest.MonkeyPatch, variable: str, setting: tuple[str, ...]
) -> None:
    monkeypatch.delenv(variable)

    assert settings_rejected_at_startup() == [setting]
