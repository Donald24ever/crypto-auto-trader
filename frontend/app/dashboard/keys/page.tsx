"use client";

import { useEffect, useState } from "react";
import { api, type Exchange, type ExchangeKey } from "@/lib/api";

const EXCHANGES: Exchange[] = ["binance", "coinbase", "kraken"];

export default function KeysPage() {
  const [keys, setKeys] = useState<ExchangeKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [exchange, setExchange] = useState<Exchange>("binance");
  const [label, setLabel] = useState("default");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [apiPassphrase, setApiPassphrase] = useState("");
  const [testnet, setTestnet] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  async function refresh() {
    setKeys(await api.get<ExchangeKey[]>("/api/keys"));
  }

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, []);

  async function addKey(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setSubmitting(true);
    try {
      await api.post("/api/keys", {
        exchange,
        label,
        api_key: apiKey,
        api_secret: apiSecret,
        api_passphrase: apiPassphrase || null,
        testnet,
      });
      setApiKey("");
      setApiSecret("");
      setApiPassphrase("");
      await refresh();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function deleteKey(id: number) {
    if (!confirm("Delete this key?")) return;
    await api.del(`/api/keys/${id}`);
    await refresh();
  }

  async function enableLive(id: number) {
    const phrase = prompt('Type "I accept the risk" to enable live trading:');
    if (!phrase) return;
    try {
      await api.post(`/api/keys/${id}/enable-live`, { confirm_phrase: phrase });
      await refresh();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Failed");
    }
  }

  async function disableLive(id: number) {
    await api.post(`/api/keys/${id}/disable-live`, {});
    await refresh();
  }

  if (loading) return <p className="text-zinc-400">Loading...</p>;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Exchange keys</h1>
        <p className="mt-1 text-sm text-zinc-400">
          API keys are stored encrypted with Fernet. Start on testnet; enable live only
          after reviewing backtest results.
        </p>
      </header>

      <form onSubmit={addKey} className="card grid grid-cols-2 gap-3">
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
          Label
          <input
            className="input mt-1"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
          />
        </label>
        <label className="col-span-2 text-sm">
          API key
          <input
            className="input mt-1"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            required
          />
        </label>
        <label className="col-span-2 text-sm">
          API secret
          <input
            className="input mt-1"
            value={apiSecret}
            onChange={(e) => setApiSecret(e.target.value)}
            type="password"
            required
          />
        </label>
        {exchange === "coinbase" && (
          <label className="col-span-2 text-sm">
            Passphrase (Coinbase Advanced)
            <input
              className="input mt-1"
              value={apiPassphrase}
              onChange={(e) => setApiPassphrase(e.target.value)}
              type="password"
            />
          </label>
        )}
        <label className="col-span-2 flex items-center gap-2 text-sm text-zinc-300">
          <input
            type="checkbox"
            checked={testnet}
            onChange={(e) => setTestnet(e.target.checked)}
          />
          Use testnet / sandbox when available
        </label>
        {err && <p className="col-span-2 text-sm text-red-400">{err}</p>}
        <div className="col-span-2">
          <button className="btn btn-primary" disabled={submitting}>
            {submitting ? "Saving..." : "Add key"}
          </button>
        </div>
      </form>

      <section>
        <h2 className="text-lg font-semibold">Your keys</h2>
        {keys.length === 0 ? (
          <p className="mt-2 text-sm text-zinc-500">No keys yet.</p>
        ) : (
          <table className="table-base mt-3">
            <thead>
              <tr>
                <th>Exchange</th>
                <th>Label</th>
                <th>Testnet</th>
                <th>Live</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {keys.map((k) => (
                <tr key={k.id}>
                  <td>{k.exchange}</td>
                  <td>{k.label}</td>
                  <td>{k.testnet ? "yes" : "no"}</td>
                  <td>
                    {k.live_enabled ? (
                      <span className="text-red-400">enabled</span>
                    ) : (
                      <span className="text-zinc-400">disabled</span>
                    )}
                  </td>
                  <td>{new Date(k.created_at).toLocaleDateString()}</td>
                  <td className="space-x-2 text-right">
                    {k.live_enabled ? (
                      <button className="btn" onClick={() => disableLive(k.id)}>
                        Disable live
                      </button>
                    ) : (
                      <button className="btn" onClick={() => enableLive(k.id)}>
                        Enable live
                      </button>
                    )}
                    <button className="btn btn-danger" onClick={() => deleteKey(k.id)}>
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
