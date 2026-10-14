import importlib
import threading
from collections.abc import Iterator
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from fastapi.testclient import TestClient

import app.main


@pytest.fixture
def otlp_receiver() -> Iterator[tuple[str, list[str]]]:
    received: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            received.append(self.path)
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(HTTPStatus.OK)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", received
    finally:
        server.shutdown()
        thread.join()


def test_traces_are_not_exported_when_the_environment_asks_fastapi_to(
    monkeypatch: pytest.MonkeyPatch, otlp_receiver: tuple[str, list[str]]
) -> None:
    url, received = otlp_receiver
    monkeypatch.setenv("FASTAPI_OTEL_AUTO_CONFIGURE", "true")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", url + "/v1/traces")
    # FastAPI reads the auto-configuration switch when the App is constructed.
    app_built_in_this_environment = importlib.reload(app.main).app

    with TestClient(app_built_in_this_environment) as client:
        client.get("/no-such-route")

    assert received == []
