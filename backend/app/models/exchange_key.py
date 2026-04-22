from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ExchangeKey(Base):
    __tablename__ = "exchange_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exchange: Mapped[str] = mapped_column(String(32))  # 'binance' | 'coinbase' | 'kraken'
    label: Mapped[str] = mapped_column(String(64), default="default")
    api_key_enc: Mapped[str] = mapped_column(String(1024))
    api_secret_enc: Mapped[str] = mapped_column(String(1024))
    api_passphrase_enc: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    testnet: Mapped[bool] = mapped_column(Boolean, default=True)
    live_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="exchange_keys")
    bots = relationship("Bot", back_populates="exchange_key", cascade="all, delete-orphan")
