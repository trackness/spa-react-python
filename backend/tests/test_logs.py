import json
import threading
import time
import tomllib
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import httpx2
import pytest
import uvicorn

BACKEND = Path(__file__).parents[1]
TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"
PARENT_SPAN_ID = "00f067aa0ba902b7"
UNTRACED = "0"
# Every path outside the untraced ones is traced, whether or not a route matches it.
UNROUTED_PATH = "/no-such-route"


@contextmanager
def running_app() -> Generator[str]:
    """Serve the App in-process, started the way the run task starts it."""
    config = uvicorn.Config(
        "app.main:app", port=0, log_config=str(BACKEND / "logging.json")
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run)
    thread.start()
    while thread.is_alive() and not server.started:
        time.sleep(0.01)
    assert server.started, "the App did not start"
    port = server.servers[0].sockets[0].getsockname()[1]
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join()


def log_lines(capfd: pytest.CaptureFixture[str]) -> list[dict[str, Any]]:
    return [json.loads(line) for line in capfd.readouterr().out.splitlines()]


def access_line(
    capfd: pytest.CaptureFixture[str], path: str, traceparent: str
) -> dict[str, Any]:
    with running_app() as url:
        httpx2.get(url + path, headers={"traceparent": traceparent})
    [line] = [
        line
        for line in log_lines(capfd)
        if line["name"] == "uvicorn.access" and path in line["message"]
    ]
    return line


def test_a_request_log_line_continues_the_incoming_trace(
    capfd: pytest.CaptureFixture[str],
) -> None:
    line = access_line(capfd, UNROUTED_PATH, f"00-{TRACE_ID}-{PARENT_SPAN_ID}-01")

    assert line["trace_id"] == TRACE_ID
    assert line["span_id"] not in {UNTRACED, PARENT_SPAN_ID}


def test_spans_are_recorded_even_when_the_caller_does_not_sample(
    capfd: pytest.CaptureFixture[str],
) -> None:
    line = access_line(capfd, UNROUTED_PATH, f"00-{TRACE_ID}-{PARENT_SPAN_ID}-00")

    assert line["trace_sampled"] is True


def test_liveness_is_not_traced(capfd: pytest.CaptureFixture[str]) -> None:
    line = access_line(capfd, "/health/live", f"00-{TRACE_ID}-{PARENT_SPAN_ID}-01")

    assert line["trace_id"] == UNTRACED


def test_every_log_line_names_the_project_and_release(
    capfd: pytest.CaptureFixture[str],
) -> None:
    project = tomllib.loads((BACKEND / "pyproject.toml").read_text())["project"]
    version = (BACKEND.parent / "version.txt").read_text().strip()

    with running_app() as url:
        httpx2.get(url + "/health/live")
    lines = log_lines(capfd)

    assert lines
    assert all(line["service.name"] == project["name"] for line in lines)
    assert all(line["service.version"] == version for line in lines)
