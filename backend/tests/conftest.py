import os

import pytest


@pytest.fixture(autouse=True)
def valid_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in os.environ:
        if name.startswith("APP_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("APP_LISTEN_ADDRESS__HOST", "127.0.0.1")
    monkeypatch.setenv("APP_LISTEN_ADDRESS__PORT", "8000")
