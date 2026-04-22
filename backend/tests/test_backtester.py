from __future__ import annotations

from app.services.backtester import backtest, score
from app.services.selector import pick_best, rank_strategies
from app.services.strategies import get_strategy
from tests._data import make_trending_ohlcv


def test_backtest_returns_positive_on_uptrend_for_sma() -> None:
    df = make_trending_ohlcv(n=500, seed=2)
    metrics = backtest(df, get_strategy("sma_crossover"), timeframe="1h")
    # With a persistent uptrend, a long-only trend follower should make money.
    assert metrics.total_return_pct > 0
    assert metrics.trade_count >= 1


def test_score_penalizes_zero_trades() -> None:
    from app.services.backtester import Metrics

    empty = Metrics(0.0, 0.0, 0.0, 0.0, 0)
    assert score(empty) < -1e8


def test_rank_strategies_returns_sorted_results() -> None:
    df = make_trending_ohlcv(n=500, seed=3)
    results = rank_strategies(df, timeframe="1h")
    assert len(results) == 4
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_pick_best_on_uptrend_is_not_none() -> None:
    df = make_trending_ohlcv(n=500, seed=4)
    results = rank_strategies(df, timeframe="1h")
    assert pick_best(results) is not None
