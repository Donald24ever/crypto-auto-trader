import Link from "next/link";

export default function Landing() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
      <h1 className="text-4xl font-bold">Crypto Auto-Trader</h1>
      <p className="mt-3 text-lg text-zinc-400">
        Backtest four classical strategies on historical data, pick the best per symbol,
        and have the bot execute trades on Binance, Coinbase, or Kraken.
      </p>

      <div className="card mt-8 border-danger/50 bg-danger/5 text-sm text-red-200">
        <strong className="text-red-300">Risk warning.</strong> Automated crypto trading
        can and does lose money. Paper mode is the default and live trading must be
        explicitly enabled per exchange key. Server-side risk guards (max position,
        stop-loss, daily-loss kill-switch) cannot be disabled. You are responsible for
        every order placed. Start small.
      </div>

      <div className="mt-8 flex gap-3">
        <Link href="/signup" className="btn btn-primary">
          Create an account
        </Link>
        <Link href="/login" className="btn">
          Log in
        </Link>
      </div>

      <div className="mt-12 grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="card">
          <h2 className="text-lg font-semibold">Backtest engine</h2>
          <p className="mt-2 text-sm text-zinc-400">
            SMA crossover, RSI mean-reversion, MACD, Bollinger breakout — each scored by
            Sharpe minus a drawdown penalty.
          </p>
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold">Safety-first trading</h2>
          <p className="mt-2 text-sm text-zinc-400">
            Paper mode by default, Fernet-encrypted API keys, per-bot risk caps, kill
            switches, and a full order audit log.
          </p>
        </div>
      </div>
    </main>
  );
}
