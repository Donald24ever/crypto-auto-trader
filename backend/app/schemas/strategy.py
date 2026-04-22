from typing import Literal

from pydantic import BaseModel, Field

StrategyName = Literal["sma_crossover", "rsi", "macd", "bollinger"]


class BacktestRequest(BaseModel):
    exchange: Literal["binance", "coinbase", "kraken"]
    symbol: str = Field(description="e.g. BTC/USDT")
    timeframe: str = Field(default="1h")
    candles: int = Field(default=500, ge=100, le=2000)
    strategies: list[StrategyName] | None = None


class StrategyMetrics(BaseModel):
    name: StrategyName
    total_return_pct: float
    sharpe: float
    max_drawdown_pct: float
    win_rate_pct: float
    trade_count: int
    score: float


class BacktestResult(BaseModel):
    symbol: str
    timeframe: str
    candles: int
    results: list[StrategyMetrics]
    best: StrategyName | None
