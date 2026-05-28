import { MOCK_DASHBOARD } from "../lib/mockData";
import type { FullDashboard } from "../types/terminal";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function fetchFullDashboard(): Promise<FullDashboard> {
  try {
    const res = await fetch(`${API_BASE}/terminal/full-dashboard`, {
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as FullDashboard;
  } catch {
    return MOCK_DASHBOARD;
  }
}
