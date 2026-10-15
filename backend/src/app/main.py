from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request, Response
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError

from app.database import database_engine, migrate
from app.settings import Settings
from app.telemetry import meter_provider, metrics_endpoint, tracer_provider

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


@app.get(
    "/health/ready",
    responses={HTTPStatus.SERVICE_UNAVAILABLE: {"model": dict[str, str]}},
)
def readiness(request: Request, response: Response) -> dict[str, str]:
    try:
        with request.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except DBAPIError:
        response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
        return {"status": "unavailable"}
    return {"status": "ok"}


# add_route is annotated for request handlers only; the Route it builds serves ASGI too
app.add_route("/metrics", metrics_endpoint)  # ty: ignore[invalid-argument-type]
