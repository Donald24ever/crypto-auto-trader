# Safety model

Automated trading is dangerous. This document describes the guarantees the platform
enforces so you know exactly what the bot can and cannot do.

## Invariants

1. **Paper-mode default.** New exchange-key rows are persisted with `live_enabled=False`.
   The frontend cannot flip this bit; only `POST /api/keys/{id}/enable-live` can,
   and the server validates the API credentials before accepting.

2. **Server-side risk engine.** Before every order, `services/risk.py::RiskEngine`
   is called. It enforces:

   | Guard | Default | What it does |
   | --- | --- | --- |
   | `max_position_pct` | 5% | A single position cannot exceed this % of account equity. |
   | `stop_loss_pct` | 2% | Every live order ships with a matching stop-loss. |
   | `daily_loss_kill_pct` | 4% | If realized PnL for the day drops below this, the bot halts and will not re-arm until the next UTC day. |
   | `cooldown_minutes` | 30 | After a stop-out, no new orders for this window. |

   These values are per-user and per-exchange. **They cannot be disabled from the UI.**
   The API will reject writes that set them to 0 or null.

3. **Audit log.** Every decision (paper or live) writes an `Order` row with
   `mode ∈ {paper, live}`, the full strategy signal payload, and the exchange response.
   Nothing the bot does is silent.

4. **Kill switch.** `POST /api/bot/{id}/stop` halts the scheduler job and cancels
   open orders on the exchange. The UI exposes this as a single red button.

5. **No withdrawals, ever.** The exchange client is instantiated with spot-trading
   permissions only. The code never calls withdraw endpoints. If your API key has
   withdrawal permission, that's on you — revoke it on the exchange.

## What this platform does **not** protect you from

- Your strategy being wrong. Classical indicators lose money in choppy markets.
- Exchange outages / partial fills / funding-rate spikes.
- You giving the API key the wrong permissions.
- You enabling live mode with an over-leveraged account balance.
- Black-swan events (flash crashes, regulator halts, exchange insolvency).

Start small. Really small. A \$50 paper balance tells you as much as a \$5,000 one.
