from __future__ import annotations

import pandas as pd

from app.schemas.strategy import StrategyMetrics
from app.services.backtester import backtest, score
from app.services.strategies import STRATEGY_REGISTRY, get_strategy


def rank_strategies(
    df: pd.DataFrame,
    *,
    timeframe: str,
    names: list[str] | None = None,
) -> list[StrategyMetrics]:
    """Backtest all requested strategies and rank them by composite score."""
    names = names or list(STRATEGY_REGISTRY.keys())
    results: list[StrategyMetrics] = []
    for name in names:
        strategy = get_strategy(name)
        metrics = backtest(df, strategy, timeframe=timeframe)
        results.append(
            StrategyMetrics(
                name=name,
                total_return_pct=round(metrics.total_return_pct, 3),
                sharpe=round(metrics.sharpe, 3),
                max_drawdown_pct=round(metrics.max_drawdown_pct, 3),
                win_rate_pct=round(metrics.win_rate_pct, 2),
                trade_count=metrics.trade_count,
                score=round(score(metrics), 4),
            )
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def pick_best(results: list[StrategyMetrics]) -> str | None:
    if not results:
        return None
    top = results[0]
    if top.score <= -1e8:
        return None
    return top.name
