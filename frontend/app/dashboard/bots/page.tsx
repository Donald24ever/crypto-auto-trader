"use client";

import { useEffect, useState } from "react";
import { api, type Bot, type ExchangeKey } from "@/lib/api";

const STRATEGIES = ["auto", "sma_crossover", "rsi", "macd", "bollinger"];
const TIMEFRAMES = ["15m", "30m", "1h", "2h", "4h", "1d"];

export default function BotsPage() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [keys, setKeys] = useState<ExchangeKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [exchangeKeyId, setExchangeKeyId] = useState<number | "">("");
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [strategy, setStrategy] = useState("auto");
  const [quotePerTrade, setQuotePerTrade] = useState(50);
  const [maxPos, setMaxPos] = useState(5);
  const [stopLoss, setStopLoss] = useState(2);
  const [dailyKill, setDailyKill] = useState(4);
  const [cooldown, setCooldown] = useState(30);
  const [mode, setMode] = useState<"paper" | "live">("paper");

  async function refresh() {
    const [b, k] = await Promise.all([
      api.get<Bot[]>("/api/bots"),
      api.get<ExchangeKey[]>("/api/keys"),
    ]);
    setBots(b);
    setKeys(k);
    if (k.length > 0 && exchangeKeyId === "") setExchangeKeyId(k[0].id);
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createBot(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    if (exchangeKeyId === "") {
      setErr("Add an exchange key first");
      return;
    }
    try {
      await api.post("/api/bots", {
        exchange_key_id: exchangeKeyId,
        symbol,
        timeframe,
        strategy,
        quote_per_trade: quotePerTrade,
        max_position_pct: maxPos,
        stop_loss_pct: stopLoss,
        daily_loss_kill_pct: dailyKill,
        cooldown_minutes: cooldown,
        mode,
      });
      await refresh();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Failed");
    }
  }

  async function start(id: number) {
    try {
      await api.post(`/api/bots/${id}/start`, {});
      await refresh();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Failed");
    }
  }
  async function stop(id: number) {
    await api.post(`/api/bots/${id}/stop`, {});
    await refresh();
  }
  async function del(id: number) {
    if (!confirm("Delete this bot? Orders will be retained.")) return;
    await api.del(`/api/bots/${id}`);
    await refresh();
  }

  if (loading) return <p className="text-zinc-400">Loading...</p>;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Bots</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Each bot trades one symbol on one exchange with server-enforced risk caps.
        </p>
      </header>

      <form onSubmit={createBot} className="card grid grid-cols-3 gap-3">
        <label className="text-sm">
          Exchange key
          <select
            className="input mt-1"
            value={exchangeKeyId}
            onChange={(e) =>
              setExchangeKeyId(e.target.value ? parseInt(e.target.value, 10) : "")
            }
          >
            {keys.map((k) => (
              <option key={k.id} value={k.id}>
                {k.exchange} · {k.label} {k.live_enabled ? "· LIVE" : ""}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Symbol
          <input
            className="input mt-1"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
          />
        </label>
        <label className="text-sm">
          Timeframe
          <select
            className="input mt-1"
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
          >
            {TIMEFRAMES.map((x) => (
              <option key={x} value={x}>
                {x}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Strategy
          <select
            className="input mt-1"
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
          >
            {STRATEGIES.map((x) => (
              <option key={x} value={x}>
                {x}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Quote per trade (USDT)
          <input
            className="input mt-1"
            type="number"
            min={1}
            step={1}
            value={quotePerTrade}
            onChange={(e) => setQuotePerTrade(parseFloat(e.target.value))}
          />
        </label>
        <label className="text-sm">
          Mode
          <select
            className="input mt-1"
            value={mode}
            onChange={(e) => setMode(e.target.value as "paper" | "live")}
          >
            <option value="paper">Paper</option>
            <option value="live">Live</option>
          </select>
        </label>
        <label className="text-sm">
          Max position %
          <input
            className="input mt-1"
            type="number"
            min={0.1}
            step={0.1}
            value={maxPos}
            onChange={(e) => setMaxPos(parseFloat(e.target.value))}
          />
        </label>
        <label className="text-sm">
          Stop loss %
          <input
            className="input mt-1"
            type="number"
            min={0.1}
            step={0.1}
            value={stopLoss}
            onChange={(e) => setStopLoss(parseFloat(e.target.value))}
          />
        </label>
        <label className="text-sm">
          Daily loss kill %
          <input
            className="input mt-1"
            type="number"
            min={0.1}
            step={0.1}
            value={dailyKill}
            onChange={(e) => setDailyKill(parseFloat(e.target.value))}
          />
        </label>
        <label className="text-sm">
          Cooldown (min)
          <input
            className="input mt-1"
            type="number"
            min={0}
            step={1}
            value={cooldown}
            onChange={(e) => setCooldown(parseInt(e.target.value, 10))}
          />
        </label>
        {err && <p className="col-span-3 text-sm text-red-400">{err}</p>}
        <div className="col-span-3">
          <button className="btn btn-primary">Create bot</button>
        </div>
      </form>

      <section>
        <h2 className="text-lg font-semibold">Your bots</h2>
        {bots.length === 0 ? (
          <p className="mt-2 text-sm text-zinc-500">No bots yet.</p>
        ) : (
          <table className="table-base mt-3">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>TF</th>
                <th>Strategy</th>
                <th>Selected</th>
                <th>Mode</th>
                <th>Quote</th>
                <th>Running</th>
                <th>Last run</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {bots.map((b) => (
                <tr key={b.id}>
                  <td>{b.symbol}</td>
                  <td>{b.timeframe}</td>
                  <td>{b.strategy}</td>
                  <td>{b.selected_strategy ?? "-"}</td>
                  <td className={b.mode === "live" ? "text-red-400" : ""}>{b.mode}</td>
                  <td>{b.quote_per_trade}</td>
                  <td>
                    {b.running ? (
                      <span className="text-emerald-400">yes</span>
                    ) : (
                      <span className="text-zinc-400">no</span>
                    )}
                  </td>
                  <td>{b.last_run_at ? new Date(b.last_run_at).toLocaleString() : "-"}</td>
                  <td className="space-x-2 text-right">
                    {b.running ? (
                      <button className="btn" onClick={() => stop(b.id)}>
                        Stop
                      </button>
                    ) : (
                      <button className="btn btn-primary" onClick={() => start(b.id)}>
                        Start
                      </button>
                    )}
                    <button className="btn btn-danger" onClick={() => del(b.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
