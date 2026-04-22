from __future__ import annotations

from typing import Any

import ccxt
import pandas as pd

from app.crypto.fernet import decrypt
from app.models import ExchangeKey

SUPPORTED_EXCHANGES = {"binance", "coinbase", "kraken"}


def build_public_client(exchange_id: str) -> ccxt.Exchange:
    """Public (no-auth) client, used for market data fetches."""
    if exchange_id not in SUPPORTED_EXCHANGES:
        raise ValueError(f"Unsupported exchange: {exchange_id}")
    klass = getattr(ccxt, exchange_id)
    client = klass({"enableRateLimit": True})
    return client


def build_authed_client(key: ExchangeKey) -> ccxt.Exchange:
    """Authenticated client built from an encrypted key row."""
    if key.exchange not in SUPPORTED_EXCHANGES:
        raise ValueError(f"Unsupported exchange: {key.exchange}")
    klass = getattr(ccxt, key.exchange)
    params: dict[str, Any] = {
        "apiKey": decrypt(key.api_key_enc),
        "secret": decrypt(key.api_secret_enc),
        "enableRateLimit": True,
    }
    if key.api_passphrase_enc:
        params["password"] = decrypt(key.api_passphrase_enc)
    client = klass(params)
    if key.testnet and hasattr(client, "set_sandbox_mode"):
        try:
            client.set_sandbox_mode(True)
        except Exception:
            # Not all exchanges implement sandbox mode; fall back silently.
            pass
    return client


def fetch_ohlcv(
    exchange_id: str,
    symbol: str,
    timeframe: str = "1h",
    limit: int = 500,
) -> pd.DataFrame:
    """Return an OHLCV dataframe with columns
    ``[timestamp, open, high, low, close, volume]``.
    """
    client = build_public_client(exchange_id)
    raw = client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = df[col].astype(float)
    return df
