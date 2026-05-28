export type Trend = "up" | "down";
export type Signal = "BUY" | "HOLD" | "STOP";

export interface ChannelMetric {
  name: string;
  spend: number;
  leads: number;
  cpa: number;
  trend: Trend;
}

export interface CampaignSignal {
  name: string;
  signal: Signal;
  confidence: number;
  spend: number;
  roas: number;
}

export interface HeaderStats {
  budget: number;
  leads: number;
  roas: number;
  tokens: number;
}

export interface AgentLog {
  timestamp: string;
  agent: string;
  action: string;
  campaign?: string;
  channel?: string;
  amount?: number;
  confidence?: number;
  result?: string;
}

export interface AlgorithmScore {
  name: string;
  score: number;
  status: "optimal" | "good" | "needs_attention";
}

export type RiskLevel = "low" | "medium" | "high" | "flexible";
export type ApiScenarioName = "conservative" | "moderate" | "growth" | "flexible";

export interface PillarAllocation {
  awareness: number;
  consideration: number;
  performance: number;
}

export interface BudgetScenario {
  name: ApiScenarioName;
  roas: number;
  risk_level: RiskLevel;
  pillar_allocation: PillarAllocation;
  channel_allocation: Record<string, number>;
  expected_return: number;
}

export type BudgetScenarios = Record<ApiScenarioName, BudgetScenario>;

export interface StrategyDoc {
  previous_strategy: string;
  agent_actions: string[];
  algorithm_results: Record<string, string>;
  fine_tuning_applied: string[];
  last_updated: string;
}

export interface StrategyBrief {
  mode: "leads" | "revenue" | "spend";
  funnel: { awareness: number; consideration: number; performance: number };
  timeline: { month: string; value: number }[];
}

export interface FullDashboard {
  header_stats: HeaderStats;
  channel_metrics: ChannelMetric[];
  campaign_signals: CampaignSignal[];
  agent_logs: AgentLog[];
  algorithm_scores: AlgorithmScore[];
  budget_scenarios?: BudgetScenarios;
  strategy_docs?: StrategyDoc;
  strategy_brief?: {
    leads: StrategyBrief["funnel"];
    revenue: StrategyBrief["funnel"];
    spend: StrategyBrief["funnel"];
    timeline: StrategyBrief["timeline"];
  };
}
