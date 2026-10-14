import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app


def test_an_invalid_setting_stops_the_app(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_LISTEN_ADDRESS__PORT", "70000")

    with pytest.raises(ValidationError) as invalid, TestClient(app):
        pass

    assert [error["loc"] for error in invalid.value.errors()] == [
        ("listen_address", "port")
    ]
