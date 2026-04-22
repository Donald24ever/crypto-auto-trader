from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Exchange = Literal["binance", "coinbase", "kraken"]


class ExchangeKeyCreate(BaseModel):
    exchange: Exchange
    label: str = Field(default="default", max_length=64)
    api_key: str
    api_secret: str
    api_passphrase: str | None = None
    testnet: bool = True


class ExchangeKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange: Exchange
    label: str
    testnet: bool
    live_enabled: bool
    created_at: datetime


class EnableLiveRequest(BaseModel):
    confirm_phrase: str = Field(description='Must equal "I accept the risk"')
