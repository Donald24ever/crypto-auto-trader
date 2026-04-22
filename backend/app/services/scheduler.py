from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Bot
from app.services.trader import run_once

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None

_TIMEFRAME_SECONDS: dict[str, int] = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    "1d": 86400,
}


def _tick_bot(bot_id: int) -> None:
    db = SessionLocal()
    try:
        bot = db.get(Bot, bot_id)
        if bot is None or not bot.running:
            return
        try:
            result = run_once(db, bot)
            logger.info("bot=%s action=%s reason=%s", bot_id, result.action, result.reason)
        except Exception as exc:
            logger.exception("bot=%s tick failed: %s", bot_id, exc)
            bot.running = False
            bot.last_error = f"unhandled: {exc}"
            db.commit()
    finally:
        db.close()


def _job_id(bot_id: int) -> str:
    return f"bot-{bot_id}"


def schedule_bot(bot: Bot) -> None:
    if _scheduler is None:
        return
    interval = _TIMEFRAME_SECONDS.get(bot.timeframe, 3600)
    job_id = _job_id(bot.id)
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)
    _scheduler.add_job(
        _tick_bot,
        "interval",
        seconds=interval,
        id=job_id,
        args=[bot.id],
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    logger.info("scheduled bot=%s every %ss", bot.id, interval)


def unschedule_bot(bot_id: int) -> None:
    if _scheduler is None:
        return
    job_id = _job_id(bot_id)
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.start()

    # Re-arm any bots that were running at the time of last shutdown.
    db = SessionLocal()
    try:
        running_bots = list(db.scalars(select(Bot).where(Bot.running == True)).all())  # noqa: E712
        for bot in running_bots:
            schedule_bot(bot)
    finally:
        db.close()


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
