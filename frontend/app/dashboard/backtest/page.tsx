"use client";

import { useState } from "react";
import { api, type BacktestResult, type Exchange } from "@/lib/api";

const EXCHANGES: Exchange[] = ["binance", "coinbase", "kraken"];
const TIMEFRAMES = ["15m", "30m", "1h", "2h", "4h", "1d"];

export default function BacktestPage() {
  const [exchange, setExchange] = useState<Exchange>("binance");
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [candles, setCandles] = useState(500);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<BacktestResult | null>(null);

  async function run(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await api.post<BacktestResult>("/api/backtests", {
        exchange,
        symbol,
        timeframe,
        candles,
      });
      setResult(r);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Backtest failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Backtest</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Rank four classical strategies on historical data. Higher score = better
          risk-adjusted return.
        </p>
      </header>

      <form onSubmit={run} className="card grid grid-cols-4 gap-3">
        <label className="text-sm">
          Exchange
          <select
            className="input mt-1"
            value={exchange}
            onChange={(e) => setExchange(e.target.value as Exchange)}
          >
            {EXCHANGES.map((x) => (
              <option key={x} value={x}>
                {x}
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
            required
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
          Candles
          <input
            className="input mt-1"
            type="number"
            min={100}
            max={2000}
            value={candles}
            onChange={(e) => setCandles(parseInt(e.target.value, 10))}
          />
        </label>
        {err && <p className="col-span-4 text-sm text-red-400">{err}</p>}
        <div className="col-span-4">
          <button className="btn btn-primary" disabled={loading}>
            {loading ? "Running..." : "Run backtest"}
          </button>
        </div>
      </form>

      {result && (
        <section>
          <h2 className="text-lg font-semibold">
            Results — {result.symbol} ({result.timeframe}, {result.candles} candles)
          </h2>
          <p className="mt-1 text-sm text-zinc-400">
            Best by composite score:{" "}
            {result.best ? (
              <span className="font-semibold text-emerald-400">{result.best}</span>
            ) : (
              <span className="text-zinc-500">none qualified</span>
            )}
          </p>
          <table className="table-base mt-3">
            <thead>
              <tr>
                <th>Strategy</th>
                <th>Return %</th>
                <th>Sharpe</th>
                <th>Max DD %</th>
                <th>Win %</th>
                <th>Trades</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {result.results.map((s) => (
                <tr
                  key={s.name}
                  className={s.name === result.best ? "bg-emerald-500/5" : ""}
                >
                  <td className="font-medium">{s.name}</td>
                  <td className={s.total_return_pct >= 0 ? "text-emerald-400" : "text-red-400"}>
                    {s.total_return_pct.toFixed(2)}
                  </td>
                  <td>{s.sharpe.toFixed(2)}</td>
                  <td className="text-red-400">{s.max_drawdown_pct.toFixed(2)}</td>
                  <td>{s.win_rate_pct.toFixed(1)}</td>
                  <td>{s.trade_count}</td>
                  <td className="font-semibold">{s.score.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
