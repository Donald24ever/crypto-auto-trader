const API_BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_BASE) ||
  "http://localhost:8000";

const TOKEN_KEY = "cat_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      // ignore
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

// Types mirroring backend schemas
export type Exchange = "binance" | "coinbase" | "kraken";

export interface User {
  id: number;
  email: string;
}

export interface ExchangeKey {
  id: number;
  exchange: Exchange;
  label: string;
  testnet: boolean;
  live_enabled: boolean;
  created_at: string;
}

export interface StrategyMetrics {
  name: string;
  total_return_pct: number;
  sharpe: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  trade_count: number;
  score: number;
}

export interface BacktestResult {
  symbol: string;
  timeframe: string;
  candles: number;
  results: StrategyMetrics[];
  best: string | null;
}

export interface Bot {
  id: number;
  exchange_key_id: number;
  symbol: string;
  timeframe: string;
  quote_per_trade: number;
  strategy: string;
  selected_strategy: string | null;
  max_position_pct: number;
  stop_loss_pct: number;
  daily_loss_kill_pct: number;
  cooldown_minutes: number;
  mode: "paper" | "live";
  running: boolean;
  last_run_at: string | null;
  last_error: string | null;
  created_at: string;
}

export interface Order {
  id: number;
  bot_id: number | null;
  exchange: string;
  symbol: string;
  side: string;
  type: string;
  amount: number;
  price: number | null;
  quote_amount: number;
  mode: string;
  status: string;
  strategy: string | null;
  exchange_order_id: string | null;
  error: string | null;
  created_at: string;
}
