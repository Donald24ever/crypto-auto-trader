"use client";

import { useEffect, useState } from "react";
import { api, type Order } from "@/lib/api";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Order[]>("/api/orders?limit=200")
      .then(setOrders)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-zinc-400">Loading...</p>;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Orders</h1>
        <p className="mt-1 text-sm text-zinc-400">
          Every order the bot placed (paper or live). This is the audit log.
        </p>
      </header>
      {orders.length === 0 ? (
        <p className="text-sm text-zinc-500">No orders yet.</p>
      ) : (
        <table className="table-base">
          <thead>
            <tr>
              <th>Time</th>
              <th>Exchange</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Mode</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Quote</th>
              <th>Strategy</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{new Date(o.created_at).toLocaleString()}</td>
                <td>{o.exchange}</td>
                <td>{o.symbol}</td>
                <td className={o.side === "buy" ? "text-emerald-400" : "text-red-400"}>
                  {o.side}
                </td>
                <td>{o.mode}</td>
                <td>{o.amount.toFixed(6)}</td>
                <td>{o.price?.toFixed(2) ?? "-"}</td>
                <td>{o.quote_amount.toFixed(2)}</td>
                <td>{o.strategy ?? "-"}</td>
                <td>
                  {o.status === "error" ? (
                    <span className="text-red-400" title={o.error ?? ""}>
                      error
                    </span>
                  ) : (
                    o.status
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
