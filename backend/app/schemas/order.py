from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bot_id: int | None
    exchange: str
    symbol: str
    side: str
    type: str
    amount: float
    price: float | None
    quote_amount: float
    mode: str
    status: str
    strategy: str | None
    exchange_order_id: str | None
    error: str | None
    created_at: datetime
