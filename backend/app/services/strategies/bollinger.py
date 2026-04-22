import pandas as pd

from app.services.strategies.base import Strategy


class BollingerStrategy(Strategy):
    """Breakout: long when close pierces the upper band; exit when it touches the midline."""

    name = "bollinger"

    def __init__(self, period: int = 20, num_std: float = 2.0) -> None:
        self.period = period
        self.num_std = num_std

    def generate_positions(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        mid = close.rolling(self.period, min_periods=self.period).mean()
        std = close.rolling(self.period, min_periods=self.period).std(ddof=0)
        upper = mid + self.num_std * std
        positions = pd.Series(0, index=df.index)
        in_pos = 0
        for i in range(len(close)):
            c = close.iloc[i]
            m = mid.iloc[i]
            u = upper.iloc[i]
            if pd.isna(m) or pd.isna(u):
                positions.iloc[i] = 0
                continue
            if in_pos == 0 and c > u:
                in_pos = 1
            elif in_pos == 1 and c < m:
                in_pos = 0
            positions.iloc[i] = in_pos
        return positions
