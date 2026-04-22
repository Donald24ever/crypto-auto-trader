from __future__ import annotations

from app.services.strategies import STRATEGY_REGISTRY, all_strategies
from tests._data import make_trending_ohlcv


def test_registry_has_four_strategies() -> None:
    assert set(STRATEGY_REGISTRY) == {"sma_crossover", "rsi", "macd", "bollinger"}


def test_strategies_produce_position_series_of_correct_length() -> None:
    df = make_trending_ohlcv(n=300)
    for strat in all_strategies():
        positions = strat.generate_positions(df)
        assert len(positions) == len(df)
        assert set(positions.unique()).issubset({0, 1})


def test_latest_signal_has_valid_action() -> None:
    df = make_trending_ohlcv(n=300)
    for strat in all_strategies():
        sig = strat.latest_signal(df)
        assert sig.action in {"buy", "sell", "hold"}
        assert sig.price > 0
