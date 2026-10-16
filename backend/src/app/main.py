from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Literal, TypedDict, override

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from app.database import database_engine, migrate
from app.settings import Settings
from app.telemetry import meter_provider, metrics_endpoint, tracer_provider

TELEMETRY_EXCLUDED_PATHS = frozenset({"/health/live", "/health/ready", "/metrics"})


class FrontendFiles(StaticFiles):
    """The built Frontend's files, with index.html for the pages the Frontend routes."""

    @override
    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException:
            # a browser navigates with text/html in Accept; a missing asset stays a 404
            if "text/html" not in Headers(scope=scope).get("accept", ""):
                raise
            response = await super().get_response("index.html", scope)
            # it names the assets of one release, so a cached copy outlives them
            response.headers["Cache-Control"] = "no-cache"
            return response


class LifespanState(TypedDict):
    """What every request finds in its state, set up at start-up."""

    engine: Engine
    frontend: FrontendFiles


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[LifespanState]:
    settings = Settings()  # validates the start-up Settings, however the App is started
    migrate()
    engine = database_engine(settings.database_file)
    yield {
        "engine": engine,
        # in development Vite serves the Frontend, which is then never built
        "frontend": FrontendFiles(
            directory=settings.frontend_directory, check_dir=False
        ),
    }
    engine.dispose()


def operation_id(route: APIRoute) -> str:
    """Name each operation after its function, as the generated Client names it.

    The function names must therefore be unique across the App.
    """
    return route.name


app = FastAPI(
    lifespan=lifespan,
    generate_unique_id_function=operation_id,
    telemetry={
        "tracer_provider": tracer_provider,
        "meter_provider": meter_provider,
        "auto_configure": False,
        "exclude": lambda scope: scope["path"] in TELEMETRY_EXCLUDED_PATHS,
    },
)


class Healthy(BaseModel):
    status: Literal["ok"]


class Unavailable(BaseModel):
    status: Literal["unavailable"]


@app.get("/health/live")
def liveness() -> Healthy:
    return Healthy(status="ok")


@app.get(
    "/health/ready",
    response_model=Healthy,
    responses={HTTPStatus.SERVICE_UNAVAILABLE: {"model": Unavailable}},
)
def readiness(request: Request) -> Healthy | JSONResponse:
    try:
        with request.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except DBAPIError:
        return JSONResponse(
            Unavailable(status="unavailable").model_dump(),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    return Healthy(status="ok")


# add_route is annotated for request handlers only; the Route it builds serves ASGI too
app.add_route("/metrics", metrics_endpoint)  # ty: ignore[invalid-argument-type]


async def frontend(scope: Scope, receive: Receive, send: Send) -> None:
    """Serve the built Frontend, whose directory is known once Settings are read."""
    await scope["state"]["frontend"](scope, receive, send)


# mounted last, so every route above takes priority over it
app.mount("/", frontend)
