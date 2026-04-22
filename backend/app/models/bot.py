from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exchange_key_id: Mapped[int] = mapped_column(
        ForeignKey("exchange_keys.id", ondelete="CASCADE"), index=True
    )

    symbol: Mapped[str] = mapped_column(String(32))  # e.g. 'BTC/USDT'
    timeframe: Mapped[str] = mapped_column(String(8), default="1h")
    quote_per_trade: Mapped[float] = mapped_column(Float, default=50.0)

    # strategy selection: 'auto' picks best; otherwise a specific strategy name
    strategy: Mapped[str] = mapped_column(String(32), default="auto")
    selected_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # risk guards (all required, server-enforced)
    max_position_pct: Mapped[float] = mapped_column(Float, default=5.0)
    stop_loss_pct: Mapped[float] = mapped_column(Float, default=2.0)
    daily_loss_kill_pct: Mapped[float] = mapped_column(Float, default=4.0)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=30)

    mode: Mapped[str] = mapped_column(String(16), default="paper")  # 'paper' | 'live'
    running: Mapped[bool] = mapped_column(Boolean, default=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="bots")
    exchange_key = relationship("ExchangeKey", back_populates="bots")
    orders = relationship("Order", back_populates="bot", cascade="all, delete-orphan")
