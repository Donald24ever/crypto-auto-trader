import pandas as pd

from app.services.strategies.base import Strategy


class SMACrossoverStrategy(Strategy):
    """Long when fast SMA > slow SMA, flat otherwise."""

    name = "sma_crossover"

    def __init__(self, fast: int = 20, slow: int = 50) -> None:
        if fast >= slow:
            raise ValueError("fast period must be less than slow period")
        self.fast = fast
        self.slow = slow

    def generate_positions(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        fast_sma = close.rolling(self.fast, min_periods=self.fast).mean()
        slow_sma = close.rolling(self.slow, min_periods=self.slow).mean()
        positions = (fast_sma > slow_sma).astype(int)
        # no position until both SMAs exist
        positions[: self.slow] = 0
        return positions
