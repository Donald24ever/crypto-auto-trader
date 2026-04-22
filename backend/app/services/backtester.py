from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.services.strategies.base import Strategy

# annualization factors by timeframe string -> bars per year
_BARS_PER_YEAR = {
    "1m": 60 * 24 * 365,
    "5m": 12 * 24 * 365,
    "15m": 4 * 24 * 365,
    "30m": 2 * 24 * 365,
    "1h": 24 * 365,
    "2h": 12 * 365,
    "4h": 6 * 365,
    "1d": 365,
}


@dataclass
class Metrics:
    total_return_pct: float
    sharpe: float
    max_drawdown_pct: float
    win_rate_pct: float
    trade_count: int


def _trade_stats(positions: pd.Series, close: pd.Series) -> tuple[int, float]:
    """Count discrete trades and compute win rate from entry/exit pairs."""
    trades = 0
    wins = 0
    entry_price: float | None = None
    prev = 0
    for pos, price in zip(positions.values, close.values, strict=False):
        if prev == 0 and pos == 1:
            entry_price = float(price)
        elif prev == 1 and pos == 0 and entry_price is not None:
            trades += 1
            if price > entry_price:
                wins += 1
            entry_price = None
        prev = pos
    # Treat still-open position as an unclosed trade; don't count in win rate.
    win_rate = (wins / trades * 100.0) if trades > 0 else 0.0
    return trades, win_rate


def backtest(
    df: pd.DataFrame,
    strategy: Strategy,
    *,
    timeframe: str = "1h",
    fee_bps: float = 10.0,  # 10 bps = 0.10% per side, reasonable for spot
) -> Metrics:
    """Run a long-only backtest of a strategy on an OHLCV dataframe.

    Positions are applied with a one-bar lag so we don't use the close we're
    signalling from. Transaction costs are deducted on every position change.
    """
    if len(df) < 30:
        return Metrics(0.0, 0.0, 0.0, 0.0, 0)

    close = df["close"].astype(float).reset_index(drop=True)
    positions = strategy.generate_positions(df).astype(float).reset_index(drop=True)

    # one-bar execution lag
    exec_positions = positions.shift(1).fillna(0.0)

    returns = close.pct_change().fillna(0.0)
    strat_returns = exec_positions * returns

    # transaction cost on position changes
    changes = exec_positions.diff().abs().fillna(exec_positions.abs())
    costs = changes * (fee_bps / 10_000.0)
    strat_returns = strat_returns - costs

    equity = (1.0 + strat_returns).cumprod()
    total_return_pct = float((equity.iloc[-1] - 1.0) * 100.0)

    # max drawdown
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    max_dd_pct = float(drawdown.min() * 100.0) if len(drawdown) else 0.0

    # annualized Sharpe ratio (rf=0)
    bars_per_year = _BARS_PER_YEAR.get(timeframe, 24 * 365)
    mean = float(strat_returns.mean())
    std = float(strat_returns.std(ddof=0))
    sharpe = 0.0 if std == 0 or np.isnan(std) else mean / std * np.sqrt(bars_per_year)

    trades, win_rate = _trade_stats(positions, close)

    return Metrics(
        total_return_pct=total_return_pct,
        sharpe=float(sharpe),
        max_drawdown_pct=max_dd_pct,
        win_rate_pct=win_rate,
        trade_count=trades,
    )


def score(metrics: Metrics) -> float:
    """Composite score used to pick the best strategy.

    Biased toward risk-adjusted return: Sharpe minus a drawdown penalty, with a
    small bonus for actually having trades (so an all-flat "strategy" doesn't
    win by virtue of zero variance).
    """
    if metrics.trade_count == 0:
        return -1e9
    return metrics.sharpe - 0.5 * abs(metrics.max_drawdown_pct) / 100.0
