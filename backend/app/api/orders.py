from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db import get_db
from app.models import Order, User
from app.schemas.order import OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    bot_id: int | None = Query(default=None),
    limit: int = Query(default=100, le=500),
) -> list[Order]:
    stmt = select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(limit)
    if bot_id is not None:
        stmt = stmt.where(Order.bot_id == bot_id)
    return list(db.scalars(stmt).all())
