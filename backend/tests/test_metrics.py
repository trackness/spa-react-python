from http import HTTPStatus

from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

from app.main import app

REQUEST_COUNT = "http_server_request_duration_seconds_count"
# Every path outside the excluded ones is measured, whether or not a route matches it.
UNROUTED_PATH = "/no-such-route"


def scrape(client: TestClient) -> list[Sample]:
    response = client.get("/metrics", follow_redirects=False)
    assert response.status_code == HTTPStatus.OK
    return [
        sample
        for family in text_string_to_metric_families(response.text)
        for sample in family.samples
    ]


def request_counts(samples: list[Sample]) -> list[Sample]:
    return [sample for sample in samples if sample.name == REQUEST_COUNT]


def test_request_metrics_are_scrapeable() -> None:
    with TestClient(app) as client:
        client.get(UNROUTED_PATH)
        samples = scrape(client)

    assert request_counts(samples)


def test_health_and_metrics_requests_are_not_measured() -> None:
    with TestClient(app) as client:
        client.get("/health/live")
        client.get("/health/ready")
        scrape(client)
        samples = scrape(client)

    routes = {sample.labels.get("http_route") for sample in request_counts(samples)}
    assert routes.isdisjoint({"/health/live", "/health/ready", "/metrics"})


def test_every_metric_names_the_project_and_release(
    project_name: str, release_version: str
) -> None:
    with TestClient(app) as client:
        client.get(UNROUTED_PATH)
        samples = scrape(client)

    assert samples
    assert all(sample.labels.get("service_name") == project_name for sample in samples)
    assert all(
        sample.labels.get("service_version") == release_version for sample in samples
    )
