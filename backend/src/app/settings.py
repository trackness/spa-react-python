from ipaddress import IPv4Address
from typing import Annotated

from pydantic import BaseModel, Field, IPvAnyAddress
from pydantic_settings import BaseSettings, SettingsConfigDict


class ListenAddress(BaseModel):
    host: IPvAnyAddress = IPv4Address("127.0.0.1")
    port: Annotated[int, Field(ge=1, le=65535)] = 8000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_nested_delimiter="__")

    listen_address: ListenAddress = ListenAddress()
