from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db import get_db
from app.models import Bot, ExchangeKey, User
from app.schemas.bot import BotCreate, BotOut
from app.services.scheduler import schedule_bot, unschedule_bot

router = APIRouter(prefix="/api/bots", tags=["bots"])


def _get_owned_bot(db: Session, user: User, bot_id: int) -> Bot:
    bot = db.get(Bot, bot_id)
    if bot is None or bot.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    return bot


@router.get("", response_model=list[BotOut])
def list_bots(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Bot]:
    return list(db.scalars(select(Bot).where(Bot.user_id == user.id)).all())


@router.post("", response_model=BotOut, status_code=status.HTTP_201_CREATED)
def create_bot(
    payload: BotCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Bot:
    key = db.get(ExchangeKey, payload.exchange_key_id)
    if key is None or key.user_id != user.id:
        raise HTTPException(status_code=404, detail="Exchange key not found")
    if payload.mode == "live" and not key.live_enabled:
        raise HTTPException(
            status_code=400,
            detail="Live mode requires enabling live trading on this exchange key first",
        )
    bot = Bot(
        user_id=user.id,
        exchange_key_id=key.id,
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        quote_per_trade=payload.quote_per_trade,
        strategy=payload.strategy,
        max_position_pct=payload.max_position_pct,
        stop_loss_pct=payload.stop_loss_pct,
        daily_loss_kill_pct=payload.daily_loss_kill_pct,
        cooldown_minutes=payload.cooldown_minutes,
        mode=payload.mode,
        running=False,
    )
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot


@router.post("/{bot_id}/start", response_model=BotOut)
def start_bot(
    bot_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Bot:
    bot = _get_owned_bot(db, user, bot_id)
    if bot.mode == "live" and not bot.exchange_key.live_enabled:
        raise HTTPException(
            status_code=400,
            detail="Live trading is not enabled on this exchange key",
        )
    bot.running = True
    bot.last_error = None
    db.commit()
    db.refresh(bot)
    schedule_bot(bot)
    return bot


@router.post("/{bot_id}/stop", response_model=BotOut)
def stop_bot(
    bot_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Bot:
    bot = _get_owned_bot(db, user, bot_id)
    bot.running = False
    db.commit()
    db.refresh(bot)
    unschedule_bot(bot.id)
    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bot(
    bot_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    bot = _get_owned_bot(db, user, bot_id)
    unschedule_bot(bot.id)
    db.delete(bot)
    db.commit()
