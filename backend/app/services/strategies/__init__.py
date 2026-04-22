from app.services.strategies.base import Signal, Strategy
from app.services.strategies.bollinger import BollingerStrategy
from app.services.strategies.macd import MACDStrategy
from app.services.strategies.rsi import RSIStrategy
from app.services.strategies.sma_crossover import SMACrossoverStrategy

STRATEGY_REGISTRY: dict[str, type[Strategy]] = {
    "sma_crossover": SMACrossoverStrategy,
    "rsi": RSIStrategy,
    "macd": MACDStrategy,
    "bollinger": BollingerStrategy,
}


def get_strategy(name: str) -> Strategy:
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Unknown strategy: {name}")
    return STRATEGY_REGISTRY[name]()


def all_strategies() -> list[Strategy]:
    return [cls() for cls in STRATEGY_REGISTRY.values()]


__all__ = [
    "STRATEGY_REGISTRY",
    "Signal",
    "Strategy",
    "all_strategies",
    "get_strategy",
]
