from __future__ import annotations

import numpy as np
import pandas as pd


def make_trending_ohlcv(n: int = 500, seed: int = 1) -> pd.DataFrame:
    """Synthetic OHLCV with an uptrend + noise."""
    rng = np.random.default_rng(seed)
    drift = np.linspace(0, 1.0, n)
    noise = rng.normal(0, 0.01, size=n).cumsum()
    close = 100.0 * np.exp(drift + noise)
    high = close * (1 + rng.uniform(0, 0.005, size=n))
    low = close * (1 - rng.uniform(0, 0.005, size=n))
    open_ = close * (1 + rng.uniform(-0.002, 0.002, size=n))
    volume = rng.uniform(10, 100, size=n)
    ts = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "timestamp": ts,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
