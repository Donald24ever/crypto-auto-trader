# Crypto Auto-Trader

An end-to-end platform that evaluates several classical trading strategies on historical
data, picks the best-performing one per symbol on a risk-adjusted basis, and can
automatically execute trades on Binance, Coinbase, or Kraken via [ccxt](https://github.com/ccxt/ccxt).

> ⚠️ **Heavy financial-risk warning.** Automated trading of crypto with classical
> indicators is **not** a reliable path to profit. Historical backtests overfit easily and
> live market regimes change. Start in **paper mode**. Keep position sizes tiny.
> You are responsible for every order placed by this bot.

## Features

- **Multi-exchange** via ccxt: Binance (testnet supported), Coinbase, Kraken.
- **Strategy engine** with 4 classical strategies:
  - SMA crossover (fast/slow)
  - RSI mean-reversion
  - MACD signal
  - Bollinger-band breakout
- **Backtester** computing total return, Sharpe, max drawdown, win rate, and trade count.
- **Best-strategy selector** that ranks strategies per symbol on a composite score
  (Sharpe − drawdown penalty).
- **Paper + live trading modes**. Live trading is **off by default** and must be enabled
  per user and per exchange after explicit confirmation.
- **Hard server-side risk guards** that cannot be disabled from the UI:
  - Max position as % of equity
  - Per-trade stop-loss
  - Daily realized-loss kill-switch
  - Cooldown period after a stop-out
- **Scheduled auto-trader** (APScheduler) that re-evaluates the best strategy at every
  bar close and acts on the signal.
- **Multi-user** with JWT auth; each user stores encrypted API keys (Fernet).
- **Next.js dashboard** for signup/login, exchange-key management, backtest review,
  bot start/stop, and an order audit log.

## Repo layout

```
backend/   FastAPI + SQLAlchemy + ccxt + APScheduler
frontend/  Next.js 14 (App Router) + TypeScript + Tailwind
docs/      Architecture & safety notes
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# edit .env and set SECRET_KEY + FERNET_KEY (see .env.example for how to generate)
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend runs at http://localhost:3000.

## Safety model

See [`docs/SAFETY.md`](docs/SAFETY.md) for the complete safety model. Short version:

1. **Paper mode is default.** `live_enabled=False` for every user-exchange pair at creation.
2. The user must explicitly `POST /api/keys/{id}/enable-live` with the exchange
   credentials validated first.
3. Every order goes through `RiskEngine.validate()` before hitting the exchange.
4. The bot refuses to start if any of `max_position_pct`, `stop_loss_pct`,
   `daily_loss_kill_pct` are unset.
5. All orders — paper and live — are persisted to the `orders` table for audit.

## License

MIT — see [LICENSE](LICENSE). **No warranty.** Trading losses are yours alone.
