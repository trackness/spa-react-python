import shutil
from http import HTTPStatus
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

# the Accept header a browser navigates with, by the Fetch Standard
NAVIGATION_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}


def test_any_request_for_the_root_gets_the_frontend_index() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<p>The Frontend</p>"
    assert response.headers["Cache-Control"] == "no-cache"


def test_a_browser_navigating_to_a_page_gets_the_frontend() -> None:
    with TestClient(app) as client:
        response = client.get("/settings", headers=NAVIGATION_HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<p>The Frontend</p>"


def test_a_page_is_revalidated_so_a_new_release_reaches_the_browser() -> None:
    with TestClient(app) as client:
        response = client.get("/settings", headers=NAVIGATION_HEADERS)

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
        response = client.get("/settings", headers=NAVIGATION_HEADERS)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("method", ["POST", "HEAD"])
def test_an_api_path_still_rejects_a_method_it_does_not_serve(method: str) -> None:
    with TestClient(app) as client:
        response = client.request(method, "/health/live")

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert response.headers["Allow"] == "GET"


def test_an_api_path_with_a_trailing_slash_redirects_to_it() -> None:
    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/health/live/", headers=NAVIGATION_HEADERS)

    assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert response.headers["Location"].endswith("/health/live")


def test_another_method_on_an_unknown_path_is_not_found() -> None:
    with TestClient(app) as client:
        response = client.post("/nothing-here")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Not Found"}


def test_a_request_that_refuses_html_gets_no_page() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/settings", headers={"Accept": "text/html;q=0, application/json"}
        )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_a_browser_navigating_to_a_page_gets_the_frontend_despite_a_404_page(
    frontend_directory: Path,
) -> None:
    (frontend_directory / "404.html").write_text("<p>Not here</p>")

    with TestClient(app) as client:
        response = client.get("/settings", headers=NAVIGATION_HEADERS)

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<p>The Frontend</p>"


def test_a_missing_asset_is_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/assets/missing.js")

    assert response.status_code == HTTPStatus.NOT_FOUND
