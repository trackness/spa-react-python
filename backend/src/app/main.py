from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.settings import Settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    Settings()  # validates the start-up Settings, however the App is started
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}
