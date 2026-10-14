import os
import socket
import subprocess
import sys
import time
from http import HTTPStatus

import httpx2
import pytest

STARTUP_TIMEOUT_SECONDS = 15


def app_environment(**settings: str) -> dict[str, str]:
    inherited = {
        name: value for name, value in os.environ.items() if not name.startswith("APP_")
    }
    return inherited | settings


def socket_for(host: str) -> socket.socket:
    return socket.socket(socket.AF_INET6 if ":" in host else socket.AF_INET)


def free_port(host: str) -> int:
    with socket_for(host) as probe:
        probe.bind((host, 0))
        port = probe.getsockname()[1]
        assert isinstance(port, int)
        return port


def is_in_use(host: str, port: int) -> bool:
    with socket_for(host) as probe:
        try:
            probe.bind((host, port))
        except OSError:
            return True
        return False


def liveness_once_serving(app: subprocess.Popen[str], url: str) -> httpx2.Response:
    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if app.poll() is not None:
            _, stderr = app.communicate()
            pytest.fail(f"the App exited before serving:\n{stderr}")
        try:
            return httpx2.get(url)
        except httpx2.TransportError:
            time.sleep(0.1)
    pytest.fail(f"the App did not serve {url} in time")


def serve_liveness(settings: dict[str, str], url: str) -> httpx2.Response:
    app = subprocess.Popen(
        [sys.executable, "-m", "app"],
        env=app_environment(**settings),
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        return liveness_once_serving(app, url)
    finally:
        app.terminate()
        app.communicate(timeout=STARTUP_TIMEOUT_SECONDS)


def test_the_app_serves_at_the_configured_listen_address() -> None:
    port = free_port("::1")

    response = serve_liveness(
        {"APP_LISTEN_ADDRESS__HOST": "::1", "APP_LISTEN_ADDRESS__PORT": str(port)},
        f"http://[::1]:{port}/health/live",
    )

    assert response.status_code == HTTPStatus.OK


def test_the_app_serves_on_localhost_port_8000_by_default() -> None:
    if is_in_use("127.0.0.1", 8000):
        pytest.skip("127.0.0.1:8000 is already in use")

    response = serve_liveness({}, "http://127.0.0.1:8000/health/live")

    assert response.status_code == HTTPStatus.OK


def test_an_invalid_setting_stops_the_app() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app"],
        env=app_environment(APP_LISTEN_ADDRESS__PORT="70000"),
        capture_output=True,
        text=True,
        timeout=STARTUP_TIMEOUT_SECONDS,
        check=False,
    )

    assert result.returncode != 0
    assert "listen_address.port" in result.stderr
