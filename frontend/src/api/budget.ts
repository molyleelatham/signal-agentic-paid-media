import { apiFetch } from "./client";

export interface BudgetAllocateRequest {
  total_budget: number;
  awareness: number;
  consideration: number;
  performance: number;
  channel_weights?: Record<string, number>;
}

export interface ChannelAllocationRow {
  channel: string;
  budget: number;
  percentage: number;
  expected_leads: number;
  expected_cpa: number;
  funnel_stage: string;
  risk_level: string;
}

export interface BudgetAllocateResponse {
  total_budget: number;
  funnel_allocation: { awareness: number; consideration: number; performance: number };
  channel_allocations: ChannelAllocationRow[];
  summary: {
    total_expected_leads: number;
    total_expected_revenue: number;
    overall_roas: number;
    risk_score: number;
    diversification_confidence: number;
  };
  recommendations: string[];
}

export async function allocateBudgetFlexible(
  body: BudgetAllocateRequest,
): Promise<BudgetAllocateResponse> {
  const res = await apiFetch("/terminal/budget-allocate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Budget allocate failed: ${res.status}`);
  }
  return res.json() as Promise<BudgetAllocateResponse>;
}
