from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel


class Liveness(BaseModel):
    status: Literal["ok"]


app = FastAPI()


@app.get("/health/live")
def liveness() -> Liveness:
    return Liveness(status="ok")
