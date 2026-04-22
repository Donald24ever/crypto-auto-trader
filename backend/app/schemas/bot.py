from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BotCreate(BaseModel):
    exchange_key_id: int
    symbol: str = Field(description="e.g. BTC/USDT")
    timeframe: str = "1h"
    quote_per_trade: float = Field(default=50.0, gt=0)
    strategy: str = "auto"
    max_position_pct: float = Field(default=5.0, gt=0, le=100)
    stop_loss_pct: float = Field(default=2.0, gt=0, le=50)
    daily_loss_kill_pct: float = Field(default=4.0, gt=0, le=50)
    cooldown_minutes: int = Field(default=30, ge=0, le=24 * 60)
    mode: Literal["paper", "live"] = "paper"


class BotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_key_id: int
    symbol: str
    timeframe: str
    quote_per_trade: float
    strategy: str
    selected_strategy: str | None
    max_position_pct: float
    stop_loss_pct: float
    daily_loss_kill_pct: float
    cooldown_minutes: int
    mode: Literal["paper", "live"]
    running: bool
    last_run_at: datetime | None
    last_error: str | None
    created_at: datetime
