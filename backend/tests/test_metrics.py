from collections.abc import Iterator
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

from app.main import app

REQUEST_COUNT = "http_server_request_duration_seconds_count"
# Every path outside the excluded ones is measured, whether or not a route matches it.
UNROUTED_PATH = "/no-such-route"


def samples_in(text: str) -> list[Sample]:
    return [
        sample
        for family in text_string_to_metric_families(text)
        for sample in family.samples
    ]


def request_counts(samples: list[Sample]) -> list[Sample]:
    return [sample for sample in samples if sample.name == REQUEST_COUNT]


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A client of the App after one measured request."""
    # following a redirect would hide the 307 a mounted metrics app answers with
    with TestClient(app, follow_redirects=False) as client:
        client.get(UNROUTED_PATH)
        yield client


def scrape(client: TestClient) -> list[Sample]:
    response = client.get("/metrics")
    assert response.status_code == HTTPStatus.OK
    return samples_in(response.text)


def test_request_metrics_are_scrapeable(client: TestClient) -> None:
    assert request_counts(scrape(client))


def test_metrics_answer_a_head_request(client: TestClient) -> None:
    assert client.head("/metrics").status_code == HTTPStatus.OK


def test_metrics_refuse_any_other_method(client: TestClient) -> None:
    response = client.delete("/metrics")

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert set(response.headers["Allow"].split(", ")) == {"GET", "HEAD"}


def test_metrics_are_compressed_when_the_scraper_accepts_gzip(
    client: TestClient,
) -> None:
    response = client.get("/metrics", headers={"Accept-Encoding": "gzip"})

    assert response.headers["content-encoding"] == "gzip"


def test_metrics_are_uncompressed_when_the_scraper_does_not_accept_gzip(
    client: TestClient,
) -> None:
    response = client.get("/metrics", headers={"Accept-Encoding": "identity"})

    assert "content-encoding" not in response.headers
    assert request_counts(samples_in(response.text))


def test_metrics_can_be_narrowed_to_the_named_series(client: TestClient) -> None:
    response = client.get("/metrics", params={"name[]": REQUEST_COUNT})

    names = {sample.name for sample in samples_in(response.text)}
    assert names == {REQUEST_COUNT}


def test_a_blank_name_does_not_narrow_the_metrics(client: TestClient) -> None:
    response = client.get("/metrics", params={"name[]": ""})

    assert request_counts(samples_in(response.text))


def test_metrics_are_served_as_openmetrics_when_the_scraper_asks(
    client: TestClient,
) -> None:
    response = client.get(
        "/metrics", headers={"Accept": "application/openmetrics-text; version=1.0.0"}
    )

    assert response.headers["content-type"].startswith("application/openmetrics-text")
    assert response.text.endswith("# EOF\n")


def test_every_accept_header_is_weighed(client: TestClient) -> None:
    response = client.get(
        "/metrics",
        headers=[
            ("Accept", "text/plain"),
            ("Accept", "application/openmetrics-text; version=1.0.0"),
        ],
    )

    assert response.headers["content-type"].startswith("application/openmetrics-text")


def requests_measured(client: TestClient) -> float:
    return sum(sample.value for sample in request_counts(scrape(client)))


def test_health_and_metrics_requests_are_not_measured(
    client: TestClient, excluded_path: str
) -> None:
    before = requests_measured(client)
    client.get(excluded_path)

    assert requests_measured(client) == before


def test_every_metric_names_the_project_and_release(
    client: TestClient, project_name: str, release_version: str
) -> None:
    samples = scrape(client)

    assert samples
    assert all(sample.labels.get("service_name") == project_name for sample in samples)
    assert all(
        sample.labels.get("service_version") == release_version for sample in samples
    )
