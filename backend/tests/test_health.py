from http import HTTPStatus
from pathlib import Path

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


def test_the_api_contract_declares_the_body_readiness_fails_with() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    responses = response.json()["paths"]["/health/ready"]["get"]["responses"]
    schema = responses[str(HTTPStatus.SERVICE_UNAVAILABLE)]["content"][
        "application/json"
    ]["schema"]
    assert schema["type"] == "object"
    assert schema["additionalProperties"] == {"type": "string"}
