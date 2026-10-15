from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request, Response
from prometheus_client import CollectorRegistry, make_asgi_app
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

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


class PrometheusEndpoint:
    """prometheus_client's own endpoint, routed at exactly /metrics.

    A mount would redirect /metrics with a 307, and a route treats a function as a
    request handler, so the library's ASGI app is routed through this callable object.
    """

    def __init__(self, registry: CollectorRegistry) -> None:
        self.app = make_asgi_app(registry)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)


app.router.routes.append(Route("/metrics", PrometheusEndpoint(metrics_registry)))
