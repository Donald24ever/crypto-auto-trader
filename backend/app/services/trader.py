from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models import Bot, ExchangeKey, Order
from app.services.exchanges import build_authed_client, fetch_ohlcv
from app.services.risk import RiskEngine
from app.services.selector import pick_best, rank_strategies
from app.services.strategies import get_strategy

logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    order: Order | None
    action: str
    reason: str


def _get_account_equity(bot: Bot, key: ExchangeKey) -> float:
    """Best-effort account equity in quote currency.

    For paper mode we use a fixed 1,000 quote-unit bankroll.
    For live mode we call ``fetchBalance`` and read the quote asset.
    """
    if bot.mode == "paper":
        return 1_000.0
    try:
        client = build_authed_client(key)
        balance = client.fetch_balance()
        quote = bot.symbol.split("/")[-1]
        total = balance.get("total", {}).get(quote) or 0.0
        return float(total)
    except Exception as exc:
        logger.exception("fetch_balance failed: %s", exc)
        return 0.0


def _resolve_strategy(bot: Bot, df) -> str | None:
    if bot.strategy == "auto":
        ranked = rank_strategies(df, timeframe=bot.timeframe)
        return pick_best(ranked)
    return bot.strategy


def _log_order(
    db: Session,
    *,
    bot: Bot,
    side: str,
    amount: float,
    price: float | None,
    quote_amount: float,
    status: str,
    strategy: str | None,
    signal: dict[str, Any] | None,
    exchange_order_id: str | None,
    error: str | None = None,
) -> Order:
    order = Order(
        user_id=bot.user_id,
        bot_id=bot.id,
        exchange=bot.exchange_key.exchange,
        symbol=bot.symbol,
        side=side,
        type="market",
        amount=amount,
        price=price,
        quote_amount=quote_amount,
        mode=bot.mode,
        status=status,
        strategy=strategy,
        signal_payload=json.dumps(signal) if signal else None,
        exchange_order_id=exchange_order_id,
        error=error,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def run_once(db: Session, bot: Bot) -> TradeResult:
    """One tick of the trading loop for a single bot."""
    if not bot.running:
        return TradeResult(order=None, action="skip", reason="bot not running")

    try:
        df = fetch_ohlcv(
            bot.exchange_key.exchange,
            bot.symbol,
            timeframe=bot.timeframe,
            limit=500,
        )
    except Exception as exc:
        bot.last_error = f"market data fetch failed: {exc}"
        db.commit()
        return TradeResult(order=None, action="error", reason=str(exc))

    strategy_name = _resolve_strategy(bot, df)
    if not strategy_name:
        bot.selected_strategy = None
        bot.last_run_at = datetime.now(UTC)
        db.commit()
        return TradeResult(order=None, action="hold", reason="no strategy qualified")

    bot.selected_strategy = strategy_name
    strategy = get_strategy(strategy_name)
    signal = strategy.latest_signal(df)

    if signal.action == "hold":
        bot.last_run_at = datetime.now(UTC)
        bot.last_error = None
        db.commit()
        return TradeResult(order=None, action="hold", reason=signal.reason)

    equity = _get_account_equity(bot, bot.exchange_key)
    risk = RiskEngine(db, bot)
    decision = risk.validate(
        side=signal.action, quote_amount=bot.quote_per_trade, account_equity=equity
    )
    if not decision.allowed:
        bot.last_error = f"risk blocked: {decision.reason}"
        db.commit()
        return TradeResult(order=None, action="blocked", reason=decision.reason)

    amount = bot.quote_per_trade / signal.price if signal.price > 0 else 0.0
    signal_dict = {
        "action": signal.action,
        "price": signal.price,
        "reason": signal.reason,
        "strategy": strategy_name,
    }

    if bot.mode == "paper":
        order = _log_order(
            db,
            bot=bot,
            side=signal.action,
            amount=amount,
            price=signal.price,
            quote_amount=bot.quote_per_trade,
            status="filled",
            strategy=strategy_name,
            signal=signal_dict,
            exchange_order_id=None,
        )
        bot.last_run_at = datetime.now(UTC)
        bot.last_error = None
        db.commit()
        return TradeResult(order=order, action=signal.action, reason="paper fill")

    # live mode
    try:
        client = build_authed_client(bot.exchange_key)
        resp = client.create_order(
            bot.symbol, "market", signal.action, amount, None, {"test": False}
        )
        exchange_order_id = str(resp.get("id") or "")
        status = str(resp.get("status") or "filled")
        order = _log_order(
            db,
            bot=bot,
            side=signal.action,
            amount=amount,
            price=signal.price,
            quote_amount=bot.quote_per_trade,
            status=status,
            strategy=strategy_name,
            signal=signal_dict,
            exchange_order_id=exchange_order_id,
        )
        bot.last_run_at = datetime.now(UTC)
        bot.last_error = None
        db.commit()
        return TradeResult(order=order, action=signal.action, reason="live fill")
    except Exception as exc:
        logger.exception("live order failed: %s", exc)
        order = _log_order(
            db,
            bot=bot,
            side=signal.action,
            amount=amount,
            price=signal.price,
            quote_amount=bot.quote_per_trade,
            status="error",
            strategy=strategy_name,
            signal=signal_dict,
            exchange_order_id=None,
            error=str(exc),
        )
        bot.last_error = f"live order failed: {exc}"
        db.commit()
        return TradeResult(order=order, action="error", reason=str(exc))
