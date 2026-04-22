from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Bot, ExchangeKey, User
from app.services.risk import RiskEngine


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _make_bot(db) -> Bot:
    user = User(email="u@x.com", password_hash="x")
    db.add(user)
    db.flush()
    key = ExchangeKey(
        user_id=user.id,
        exchange="binance",
        api_key_enc="x",
        api_secret_enc="x",
        testnet=True,
        live_enabled=False,
    )
    db.add(key)
    db.flush()
    bot = Bot(
        user_id=user.id,
        exchange_key_id=key.id,
        symbol="BTC/USDT",
        timeframe="1h",
        quote_per_trade=50.0,
        max_position_pct=5.0,
        stop_loss_pct=2.0,
        daily_loss_kill_pct=4.0,
        cooldown_minutes=30,
        mode="paper",
        running=True,
    )
    db.add(bot)
    db.flush()
    return bot


def test_buy_within_cap_is_allowed(db_session) -> None:
    bot = _make_bot(db_session)
    engine = RiskEngine(db_session, bot)
    decision = engine.validate(side="buy", quote_amount=30.0, account_equity=1_000.0)
    assert decision.allowed


def test_buy_exceeding_cap_is_blocked(db_session) -> None:
    bot = _make_bot(db_session)
    engine = RiskEngine(db_session, bot)
    decision = engine.validate(side="buy", quote_amount=200.0, account_equity=1_000.0)
    assert not decision.allowed
    assert "exceeds max position" in decision.reason


def test_zero_guards_rejected(db_session) -> None:
    bot = _make_bot(db_session)
    bot.max_position_pct = 0.0
    with pytest.raises(ValueError):
        RiskEngine(db_session, bot)


def test_sell_always_allowed_when_no_stop_cooldown(db_session) -> None:
    bot = _make_bot(db_session)
    engine = RiskEngine(db_session, bot)
    decision = engine.validate(side="sell", quote_amount=1000.0, account_equity=500.0)
    assert decision.allowed
