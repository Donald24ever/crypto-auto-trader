from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.crypto.fernet import encrypt
from app.db import get_db
from app.models import ExchangeKey, User
from app.schemas.keys import EnableLiveRequest, ExchangeKeyCreate, ExchangeKeyOut
from app.services.exchanges import build_authed_client

router = APIRouter(prefix="/api/keys", tags=["exchange-keys"])


@router.get("", response_model=list[ExchangeKeyOut])
def list_keys(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ExchangeKey]:
    return list(db.scalars(select(ExchangeKey).where(ExchangeKey.user_id == user.id)).all())


@router.post("", response_model=ExchangeKeyOut, status_code=status.HTTP_201_CREATED)
def create_key(
    payload: ExchangeKeyCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExchangeKey:
    key = ExchangeKey(
        user_id=user.id,
        exchange=payload.exchange,
        label=payload.label,
        api_key_enc=encrypt(payload.api_key),
        api_secret_enc=encrypt(payload.api_secret),
        api_passphrase_enc=encrypt(payload.api_passphrase) if payload.api_passphrase else None,
        testnet=payload.testnet,
        live_enabled=False,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_key(
    key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
    key = db.get(ExchangeKey, key_id)
    if key is None or key.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(key)
    db.commit()


@router.post("/{key_id}/enable-live", response_model=ExchangeKeyOut)
def enable_live(
    key_id: int,
    payload: EnableLiveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExchangeKey:
    """Flip ``live_enabled`` on after validating the credentials actually work.

    The client must send ``confirm_phrase="I accept the risk"`` as an extra
    guardrail against accidental clicks.
    """
    if payload.confirm_phrase.strip() != "I accept the risk":
        raise HTTPException(status_code=400, detail='confirm_phrase must equal "I accept the risk"')
    key = db.get(ExchangeKey, key_id)
    if key is None or key.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        client = build_authed_client(key)
        client.fetch_balance()
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Credential validation failed: {exc}"
        ) from exc
    key.live_enabled = True
    db.commit()
    db.refresh(key)
    return key


@router.post("/{key_id}/disable-live", response_model=ExchangeKeyOut)
def disable_live(
    key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ExchangeKey:
    key = db.get(ExchangeKey, key_id)
    if key is None or key.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    key.live_enabled = False
    db.commit()
    db.refresh(key)
    return key
