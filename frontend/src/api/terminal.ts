import { apiFetch } from "./client";
import { MOCK_BUDGET_SCENARIOS, MOCK_DASHBOARD, MOCK_STRATEGY_DOCS } from "../lib/mockData";
import type { BudgetScenarios, FullDashboard, StrategyDoc } from "../types/terminal";

export async function fetchFullDashboard(): Promise<FullDashboard> {
  try {
    const res = await apiFetch("/terminal/full-dashboard", {
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as FullDashboard;
  } catch {
    return MOCK_DASHBOARD;
  }
}

export async function fetchBudgetScenarios(): Promise<BudgetScenarios> {
  try {
    const res = await apiFetch("/terminal/budget-scenarios", {
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as BudgetScenarios;
  } catch {
    return MOCK_BUDGET_SCENARIOS;
  }
}

export async function fetchStrategyDocs(): Promise<StrategyDoc> {
  try {
    const res = await apiFetch("/terminal/strategy-docs", {
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as StrategyDoc;
  } catch {
    return MOCK_STRATEGY_DOCS;
  }
}
