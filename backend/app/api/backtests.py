from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.deps import get_current_user
from app.models import User
from app.schemas.strategy import BacktestRequest, BacktestResult
from app.services.exchanges import fetch_ohlcv
from app.services.selector import pick_best, rank_strategies

router = APIRouter(prefix="/api/backtests", tags=["backtests"])


@router.post("", response_model=BacktestResult)
def run_backtest(
    payload: BacktestRequest, _user: User = Depends(get_current_user)
) -> BacktestResult:
    try:
        df = fetch_ohlcv(payload.exchange, payload.symbol, payload.timeframe, payload.candles)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch OHLCV: {exc}"
        ) from exc
    if len(df) < 100:
        raise HTTPException(status_code=400, detail="Not enough candles returned")
    names = [s for s in (payload.strategies or [])] or None
    results = rank_strategies(df, timeframe=payload.timeframe, names=names)
    return BacktestResult(
        symbol=payload.symbol,
        timeframe=payload.timeframe,
        candles=len(df),
        results=results,
        best=pick_best(results),
    )
