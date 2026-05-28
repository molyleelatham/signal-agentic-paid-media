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

export interface FullDashboard {
  header_stats: HeaderStats;
  channel_metrics: ChannelMetric[];
  campaign_signals: CampaignSignal[];
  agent_logs: AgentLog[];
  algorithm_scores: AlgorithmScore[];
}
