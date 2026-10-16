import os
import sqlite3
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, closing
from http import HTTPStatus
from os import PathLike
from pathlib import Path
from typing import Literal, TypedDict, override

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, _is_frontend_navigation_request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from app.database import migrate
from app.settings import Settings
from app.telemetry import meter_provider, metrics_endpoint, tracer_provider

TELEMETRY_EXCLUDED_PATHS = frozenset({"/health/live", "/health/ready", "/metrics"})


class FrontendFiles(StaticFiles):
    """The built Frontend's files, with index.html for the pages the Frontend routes."""

    INDEX = "index.html"

    @override
    async def check_config(self) -> None:
        """Serve nothing while unbuilt: in development Vite serves the Frontend."""

    @override
    async def get_response(self, path: str, scope: Scope) -> Response:
        # the root, normalized to ".", is the index; Starlette's html mode would also
        # serve a build's 404.html in place of the fallback below
        if path == ".":
            path = self.INDEX
        try:
            return await super().get_response(path, scope)
        except HTTPException:
            # FastAPI's own test, as its frontend serving uses: a browser navigates
            # accepting HTML, so a missing asset stays a 404
            if not _is_frontend_navigation_request(scope):
                raise
            return await super().get_response(self.INDEX, scope)

    @override
    def file_response(
        self,
        full_path: PathLike[str] | str,
        stat_result: os.stat_result,
        scope: Scope,
        status_code: int = HTTPStatus.OK,
    ) -> Response:
        response = super().file_response(full_path, stat_result, scope, status_code)
        if Path(full_path).name == self.INDEX:
            # it names the assets of one release, so a cached copy outlives them
            response.headers["Cache-Control"] = "no-cache"
        return response


class LifespanState(TypedDict):
    """What every request finds in its state, set up at start-up."""

    database_file: Path
    frontend: FrontendFiles


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[LifespanState]:
    settings = Settings()  # validates the start-up Settings, however the App is started
    migrate()
    yield {
        "database_file": settings.database_file,
        "frontend": FrontendFiles(
            directory=settings.frontend_directory, check_dir=False
        ),
    }


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
    database = request.state.database_file.resolve().as_uri()
    try:
        # a connection of its own reads the file afresh, which a pooled one does not;
        # mode=rw never creates a file that has gone
        with closing(sqlite3.connect(f"{database}?mode=rw", uri=True)) as probe:
            probe.execute("PRAGMA schema_version")
    except sqlite3.DatabaseError:
        return JSONResponse(
            Unavailable(status="unavailable").model_dump(),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    return Healthy(status="ok")


# add_route is annotated for request handlers only; the Route it builds serves ASGI too
app.add_route("/metrics", metrics_endpoint, methods=["GET"])  # ty: ignore[invalid-argument-type]


async def frontend(scope: Scope, receive: Receive, send: Send) -> None:
    """Serve the built Frontend, whose directory is known once Settings are read."""
    if scope["type"] == "http" and scope["method"] in {"GET", "HEAD"}:
        await scope["state"]["frontend"](scope, receive, send)
    else:
        await scope["router"].not_found(scope, receive, send)


# what the router answers once no route, method or trailing-slash redirect applies
app.router.default = frontend
