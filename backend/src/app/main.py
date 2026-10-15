import gzip
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request, Response
from prometheus_client.exposition import choose_encoder, gzip_accepted
from prometheus_client.registry import Collector
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError

from app.database import database_engine, migrate
from app.settings import Settings
from app.telemetry import meter_provider, metrics_registry, tracer_provider

TELEMETRY_EXCLUDED_PATHS = frozenset({"/health/live", "/health/ready", "/metrics"})


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[dict[str, Engine]]:
    settings = Settings()  # validates the start-up Settings, however the App is started
    migrate()
    engine = database_engine(settings.database_file)
    yield {"engine": engine}
    engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    telemetry={
        "tracer_provider": tracer_provider,
        "meter_provider": meter_provider,
        "auto_configure": False,
        "exclude": lambda scope: scope["path"] in TELEMETRY_EXCLUDED_PATHS,
    },
)


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
def readiness(request: Request, response: Response) -> dict[str, str]:
    try:
        with request.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except DBAPIError:
        response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
        return {"status": "unavailable"}
    return {"status": "ok"}


# prometheus_client's ASGI app answers /metrics only when mounted, and a mount
# redirects /metrics with a 307, so its exposition is served here from its public parts
@app.get("/metrics")
def metrics(request: Request) -> Response:
    registry: Collector = metrics_registry
    if names := request.query_params.getlist("name[]"):
        registry = metrics_registry.restricted_registry(names)
    encoder, content_type = choose_encoder(request.headers.get("accept", ""))
    if gzip_accepted(request.headers.get("accept-encoding", "")):
        return Response(
            gzip.compress(encoder(registry)),
            media_type=content_type,
            headers={"Content-Encoding": "gzip"},
        )
    return Response(encoder(registry), media_type=content_type)
