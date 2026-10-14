from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.settings import Settings
from app.telemetry import tracer_provider

UNTRACED_PATHS = frozenset({"/health/live"})


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    Settings()  # validates the start-up Settings, however the App is started
    yield


app = FastAPI(
    lifespan=lifespan,
    telemetry={
        "tracer_provider": tracer_provider,
        "auto_configure": False,
        "exclude": lambda scope: scope["path"] in UNTRACED_PATHS,
    },
)


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}
