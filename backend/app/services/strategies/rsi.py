import numpy as np
import pandas as pd

from app.services.strategies.base import Strategy


class RSIStrategy(Strategy):
    """Mean-reversion RSI: long below ``oversold``, flat above ``overbought``."""

    name = "rsi"

    def __init__(self, period: int = 14, oversold: float = 30.0, overbought: float = 70.0) -> None:
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def _rsi(self, close: pd.Series) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1.0 / self.period, adjust=False, min_periods=self.period).mean()
        avg_loss = loss.ewm(alpha=1.0 / self.period, adjust=False, min_periods=self.period).mean()
        rs = avg_gain / avg_loss.replace(0.0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.fillna(50.0)

    def generate_positions(self, df: pd.DataFrame) -> pd.Series:
        rsi = self._rsi(df["close"])
        positions = pd.Series(0, index=df.index)
        in_pos = 0
        for i, value in enumerate(rsi):
            if in_pos == 0 and value <= self.oversold:
                in_pos = 1
            elif in_pos == 1 and value >= self.overbought:
                in_pos = 0
            positions.iloc[i] = in_pos
        positions[: self.period] = 0
        return positions
