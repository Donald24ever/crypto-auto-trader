import pandas as pd

from app.services.strategies.base import Strategy


class MACDStrategy(Strategy):
    """MACD: long when MACD line crosses above its signal line."""

    name = "macd"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9) -> None:
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_positions(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        ema_fast = close.ewm(span=self.fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal, adjust=False).mean()
        positions = (macd_line > signal_line).astype(int)
        warmup = self.slow + self.signal
        positions[:warmup] = 0
        return positions
