from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

import pandas as pd

Action = Literal["buy", "sell", "hold"]


@dataclass
class Signal:
    action: Action
    price: float
    reason: str


class Strategy(ABC):
    """Base class for a trading strategy.

    Strategies operate on an OHLCV DataFrame with columns
    ``[timestamp, open, high, low, close, volume]`` (timestamp in ms, UTC).

    ``generate_positions`` returns a 1/0/-1 position series of the same
    length as the input for use by the backtester. 1 = long, 0 = flat.
    For spot markets we do not use -1 (no short positions).

    ``latest_signal`` returns a discrete action for the most recent bar,
    used by the live trader.
    """

    name: str = "base"

    @abstractmethod
    def generate_positions(self, df: pd.DataFrame) -> pd.Series: ...

    def latest_signal(self, df: pd.DataFrame) -> Signal:
        positions = self.generate_positions(df)
        if len(positions) < 2:
            return Signal(action="hold", price=float(df["close"].iloc[-1]), reason="not enough data")
        prev, curr = positions.iloc[-2], positions.iloc[-1]
        price = float(df["close"].iloc[-1])
        if prev == 0 and curr == 1:
            return Signal(action="buy", price=price, reason=f"{self.name}: long entry")
        if prev == 1 and curr == 0:
            return Signal(action="sell", price=price, reason=f"{self.name}: long exit")
        return Signal(action="hold", price=price, reason=f"{self.name}: no edge")
