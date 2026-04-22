"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type Bot, type ExchangeKey, type Order } from "@/lib/api";

export default function OverviewPage() {
  const [keys, setKeys] = useState<ExchangeKey[]>([]);
  const [bots, setBots] = useState<Bot[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<ExchangeKey[]>("/api/keys"),
      api.get<Bot[]>("/api/bots"),
      api.get<Order[]>("/api/orders?limit=5"),
    ])
      .then(([k, b, o]) => {
        setKeys(k);
        setBots(b);
        setOrders(o);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-zinc-400">Loading...</p>;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Overview</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Quick status of your keys, bots, and recent trades.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Stat label="Exchange keys" value={keys.length} href="/dashboard/keys" />
        <Stat
          label="Active bots"
          value={bots.filter((b) => b.running).length}
          total={bots.length}
          href="/dashboard/bots"
        />
        <Stat label="Recent orders" value={orders.length} href="/dashboard/orders" />
      </div>

      <section>
        <h2 className="text-lg font-semibold">Recent orders</h2>
        {orders.length === 0 ? (
          <p className="mt-2 text-sm text-zinc-500">No orders yet.</p>
        ) : (
          <table className="table-base mt-3">
            <thead>
              <tr>
                <th>Time</th>
                <th>Symbol</th>
                <th>Side</th>
                <th>Mode</th>
                <th>Qty</th>
                <th>Quote</th>
                <th>Strategy</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>{new Date(o.created_at).toLocaleString()}</td>
                  <td>{o.symbol}</td>
                  <td className={o.side === "buy" ? "text-emerald-400" : "text-red-400"}>
                    {o.side}
                  </td>
                  <td>{o.mode}</td>
                  <td>{o.amount.toFixed(6)}</td>
                  <td>{o.quote_amount.toFixed(2)}</td>
                  <td>{o.strategy ?? "-"}</td>
                  <td>{o.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

function Stat({
  label,
  value,
  total,
  href,
}: {
  label: string;
  value: number;
  total?: number;
  href: string;
}) {
  return (
    <Link href={href} className="card block transition hover:border-zinc-600">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className="mt-2 text-2xl font-bold">
        {value}
        {total !== undefined ? (
          <span className="ml-1 text-sm font-normal text-zinc-500">/ {total}</span>
        ) : null}
      </p>
    </Link>
  );
}
