"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, getToken, setToken, type User } from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/keys", label: "Exchange keys" },
  { href: "/dashboard/backtest", label: "Backtest" },
  { href: "/dashboard/bots", label: "Bots" },
  { href: "/dashboard/orders", label: "Orders" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api
      .get<User>("/api/auth/me")
      .then(setUser)
      .catch(() => {
        setToken(null);
        router.replace("/login");
      })
      .finally(() => setLoading(false));
  }, [router]);

  function logout() {
    setToken(null);
    router.replace("/login");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-zinc-400">Loading...</p>
      </main>
    );
  }

  return (
    <div className="flex min-h-screen">
      <aside className="w-60 shrink-0 border-r border-border bg-panel p-4">
        <Link href="/dashboard" className="block text-lg font-bold">
          Auto-Trader
        </Link>
        <p className="mt-1 truncate text-xs text-zinc-500">{user?.email}</p>
        <nav className="mt-6 space-y-1">
          {NAV.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm ${
                  active ? "bg-black/40 text-white" : "text-zinc-400 hover:text-white"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button onClick={logout} className="btn mt-6 w-full text-sm">
          Log out
        </button>
      </aside>
      <main className="flex-1 px-8 py-8">{children}</main>
    </div>
  );
}
