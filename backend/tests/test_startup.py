import os
import socket
import subprocess
import sys
import tempfile
import time
from http import HTTPStatus
from typing import IO

import httpx2
import pytest

STARTUP_TIMEOUT_SECONDS = 15
STARTUP_ATTEMPTS = 3
# Not uvicorn's own default host, 127.0.0.1, so an ignored host cannot pass.
HOST = "::1"


class AppExitedBeforeServingError(Exception):
    pass


def app_environment(**settings: str) -> dict[str, str]:
    inherited = {
        name: value for name, value in os.environ.items() if not name.startswith("APP_")
    }
    return inherited | settings


def free_port() -> int:
    with socket.socket(socket.AF_INET6) as probe:
        try:
            probe.bind((HOST, 0))
        except OSError:
            pytest.skip(f"{HOST} is unavailable")
        port = probe.getsockname()[1]
        assert isinstance(port, int)
        return port


def liveness_once_serving(
    app_process: subprocess.Popen[str], app_log: IO[str], url: httpx2.URL
) -> httpx2.Response:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if app_process.poll() is not None:
            app_log.seek(0)
            raise AppExitedBeforeServingError(app_log.read())
        try:
            return httpx2.get(url)
        except httpx2.TransportError:
            time.sleep(0.1)
    pytest.fail(f"the App did not serve {url} in time")


def serve_liveness(port: int) -> httpx2.Response:
    url = httpx2.URL(scheme="http", host=HOST, port=port, path="/health/live")
    with tempfile.TemporaryFile("w+") as app_log:
        app_process = subprocess.Popen(
            [sys.executable, "-m", "app"],
            env=app_environment(
                APP_LISTEN_ADDRESS__HOST=HOST, APP_LISTEN_ADDRESS__PORT=str(port)
            ),
            stderr=app_log,
            text=True,
        )
        try:
            return liveness_once_serving(app_process, app_log, url)
        finally:
            app_process.terminate()
            app_process.wait(timeout=STARTUP_TIMEOUT_SECONDS)


def serve_liveness_on_a_free_port() -> httpx2.Response:
    # A port free when probed can be taken before the App binds it, so a start
    # that fails is retried on a fresh port.
    app_log = ""
    for _ in range(STARTUP_ATTEMPTS):
        try:
            return serve_liveness(free_port())
        except AppExitedBeforeServingError as exited:
            app_log = str(exited)
    pytest.fail(f"the App exited before serving:\n{app_log}")


def test_the_app_serves_at_the_configured_listen_address() -> None:
    response = serve_liveness_on_a_free_port()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
