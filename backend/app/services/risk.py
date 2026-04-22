from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Bot, Order


@dataclass
class RiskDecision:
    allowed: bool
    reason: str
    max_quote: float = 0.0


class RiskEngine:
    """Server-side guardrails applied before every order.

    All thresholds live on the :class:`~app.models.bot.Bot` row and are
    required (non-nullable, non-zero) by the schema.
    """

    def __init__(self, db: Session, bot: Bot) -> None:
        if bot.max_position_pct <= 0 or bot.stop_loss_pct <= 0 or bot.daily_loss_kill_pct <= 0:
            raise ValueError("Risk guards must all be > 0")
        self.db = db
        self.bot = bot

    def _realized_pnl_today(self) -> float:
        since = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        q = select(Order).where(
            Order.bot_id == self.bot.id,
            Order.created_at >= since,
            Order.status == "filled",
        )
        orders = list(self.db.scalars(q).all())
        # Simple FIFO PnL: pair each sell's quote amount against the prior buy.
        buys: list[float] = []
        pnl = 0.0
        for o in sorted(orders, key=lambda x: x.created_at):
            if o.side == "buy":
                buys.append(o.quote_amount)
            elif o.side == "sell" and buys:
                entry_quote = buys.pop(0)
                pnl += o.quote_amount - entry_quote
        return pnl

    def _last_stop_out(self) -> datetime | None:
        q = (
            select(Order)
            .where(
                Order.bot_id == self.bot.id,
                Order.side == "sell",
                Order.strategy.like("%stop%"),
            )
            .order_by(Order.created_at.desc())
            .limit(1)
        )
        last = self.db.scalar(q)
        return last.created_at if last else None

    def validate(self, *, side: str, quote_amount: float, account_equity: float) -> RiskDecision:
        """Decide whether an order may be placed."""
        if account_equity <= 0:
            return RiskDecision(False, "Account equity unavailable or zero")

        # Daily-loss kill switch
        daily_pnl = self._realized_pnl_today()
        kill_threshold = -abs(self.bot.daily_loss_kill_pct) / 100.0 * account_equity
        if daily_pnl <= kill_threshold:
            return RiskDecision(
                False,
                f"Daily-loss kill-switch hit ({daily_pnl:.2f} <= {kill_threshold:.2f})",
            )

        # Cooldown after stop-out
        last_stop = self._last_stop_out()
        if last_stop:
            # make tz-aware for comparison
            if last_stop.tzinfo is None:
                last_stop = last_stop.replace(tzinfo=UTC)
            cooldown_end = last_stop + timedelta(minutes=self.bot.cooldown_minutes)
            if datetime.now(UTC) < cooldown_end:
                return RiskDecision(
                    False,
                    f"Cooling down until {cooldown_end.isoformat()}",
                )

        if side == "buy":
            max_quote = account_equity * (self.bot.max_position_pct / 100.0)
            if quote_amount > max_quote:
                return RiskDecision(
                    False,
                    f"Order size {quote_amount:.2f} exceeds max position {max_quote:.2f}",
                    max_quote=max_quote,
                )
            return RiskDecision(True, "ok", max_quote=max_quote)

        # sell orders reduce exposure and are always allowed past checks above
        return RiskDecision(True, "ok")
