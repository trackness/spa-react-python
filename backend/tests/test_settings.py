import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app


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

    with pytest.raises(ValidationError) as invalid, TestClient(app):
        pass

    assert [error["loc"] for error in invalid.value.errors()] == [setting]


@pytest.mark.parametrize(
    ("variable", "setting"),
    [
        ("APP_LISTEN_ADDRESS__HOST", ("listen_address", "host")),
        ("APP_LISTEN_ADDRESS__PORT", ("listen_address", "port")),
    ],
)
def test_a_missing_setting_stops_the_app(
    monkeypatch: pytest.MonkeyPatch, variable: str, setting: tuple[str, ...]
) -> None:
    monkeypatch.delenv(variable)

    with pytest.raises(ValidationError) as missing, TestClient(app):
        pass

    assert [error["loc"] for error in missing.value.errors()] == [setting]
