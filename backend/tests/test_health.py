from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app


def test_liveness_reports_the_app_is_alive() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
