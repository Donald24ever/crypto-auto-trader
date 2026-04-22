from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    bot_id: Mapped[int | None] = mapped_column(
        ForeignKey("bots.id", ondelete="SET NULL"), nullable=True, index=True
    )

    exchange: Mapped[str] = mapped_column(String(32))
    symbol: Mapped[str] = mapped_column(String(32))
    side: Mapped[str] = mapped_column(String(8))  # 'buy' | 'sell'
    type: Mapped[str] = mapped_column(String(16), default="market")
    amount: Mapped[float] = mapped_column(Float)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    quote_amount: Mapped[float] = mapped_column(Float)

    mode: Mapped[str] = mapped_column(String(16), default="paper")
    status: Mapped[str] = mapped_column(String(32), default="filled")
    strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    signal_payload: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    exchange_order_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")
    bot = relationship("Bot", back_populates="orders")
