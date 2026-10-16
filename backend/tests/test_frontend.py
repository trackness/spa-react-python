import shutil
from http import HTTPStatus
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

# the Accept header a browser navigates with, by the Fetch Standard; Sec-Fetch-Mode
# would say so too, but browsers send it only to secure origins
NAVIGATION = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def test_a_browser_navigating_to_the_app_gets_the_frontend() -> None:
    with TestClient(app) as client:
        response = client.get("/", headers=NAVIGATION)

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<p>The Frontend</p>"


def test_a_browser_navigating_to_a_page_gets_the_frontend() -> None:
    with TestClient(app) as client:
        response = client.get("/settings", headers=NAVIGATION)

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<p>The Frontend</p>"


def test_the_frontend_is_revalidated_so_a_new_release_reaches_the_browser() -> None:
    with TestClient(app) as client:
        response = client.get("/", headers=NAVIGATION)

    assert response.headers["Cache-Control"] == "no-cache"


def test_the_app_serves_the_api_while_the_frontend_is_unbuilt(
    frontend_directory: Path,
) -> None:
    shutil.rmtree(frontend_directory)

    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == HTTPStatus.OK


def test_a_page_is_not_found_while_the_frontend_is_unbuilt(
    frontend_directory: Path,
) -> None:
    shutil.rmtree(frontend_directory)

    with TestClient(app) as client:
        response = client.get("/settings", headers=NAVIGATION)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_an_api_path_still_rejects_a_method_it_does_not_serve() -> None:
    with TestClient(app) as client:
        response = client.post("/health/live")

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert response.headers["Allow"] == "GET"


def test_a_missing_asset_is_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/assets/missing.js")

    assert response.status_code == HTTPStatus.NOT_FOUND
