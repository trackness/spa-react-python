from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.settings import Settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class Liveness(BaseModel):
    status: Literal["ok"]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    Settings()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/live")
def liveness() -> Liveness:
    return Liveness(status="ok")
