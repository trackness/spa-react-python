from http import HTTPStatus
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_liveness_reports_the_app_is_alive() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


def test_readiness_reports_the_app_is_ready() -> None:
    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


def test_readiness_fails_when_the_database_does_not_answer(database_file: Path) -> None:
    with TestClient(app) as client:
        database_file.write_bytes(b"not a database" * 1024)
        response = client.get("/health/ready")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {"status": "unavailable"}


def test_readiness_fails_when_the_database_breaks_while_the_app_runs(
    database_file: Path,
) -> None:
    with TestClient(app) as client:
        client.get("/health/ready")
        database_file.write_bytes(b"not a database" * 1024)
        response = client.get("/health/ready")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {"status": "unavailable"}


def test_readiness_fails_when_the_database_is_deleted_while_the_app_runs(
    database_file: Path,
) -> None:
    with TestClient(app) as client:
        client.get("/health/ready")
        database_file.unlink()
        response = client.get("/health/ready")

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {"status": "unavailable"}


@pytest.fixture
def openapi() -> dict[str, Any]:
    with TestClient(app) as client:
        return client.get("/openapi.json").json()


@pytest.mark.parametrize(
    ("path", "status", "body_status"),
    [
        ("/health/live", HTTPStatus.OK, "ok"),
        ("/health/ready", HTTPStatus.OK, "ok"),
        ("/health/ready", HTTPStatus.SERVICE_UNAVAILABLE, "unavailable"),
    ],
)
def test_the_api_contract_types_each_health_body(
    openapi: dict[str, Any], path: str, status: HTTPStatus, body_status: str
) -> None:
    response = openapi["paths"][path]["get"]["responses"][str(status)]
    reference = response["content"]["application/json"]["schema"]["$ref"]
    body = openapi["components"]["schemas"][
        reference.removeprefix("#/components/schemas/")
    ]

    assert body["required"] == ["status"]
    assert body["properties"]["status"]["const"] == body_status


@pytest.mark.parametrize(
    ("path", "operation_id"),
    [("/health/live", "liveness"), ("/health/ready", "readiness")],
)
def test_the_api_contract_names_each_operation_after_its_function(
    openapi: dict[str, Any], path: str, operation_id: str
) -> None:
    assert openapi["paths"][path]["get"]["operationId"] == operation_id
