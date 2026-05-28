/**
 * API Client for Agent Triggers
 */

import { API_BASE } from "./client";

export interface TriggerResult {
  trigger_id: string;
  timestamp: string;
  success: boolean;
  agent_name: string;
  action: string;
  output?: any;
  error?: string;
  execution_time_ms: number;
  tokens_used: number;
  cost_usd: number;
}

export interface BidOptimizeParams {
  keyword: string;
  current_bid: number;
  platform?: string;
  campaign_id?: string;
}

export interface ContentGenerateParams {
  gap_topic: string;
  gap_score: number;
  platform?: string;
  business_goal?: string;
}

export interface CreativeOptimizeParams {
  creative_id: string;
  creative_type: string;
  platform?: string;
}

export interface MarketAnalyzeParams {
  query: string;
  time_range?: string;
  competitors?: string[];
}

export interface KeywordClassifyParams {
  query: string;
  use_disbert?: boolean;
}

export interface TavilyResearchParams {
  query: string;
  max_results?: number;
  extract_keywords?: boolean;
}

export interface OrchestrateParams {
  task_type: string;
  context: Record<string, any>;
  required_agents: string[];
}

/**
 * Trigger bid optimization
 */
export async function triggerBidOptimize(params: BidOptimizeParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/bid-optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger bid optimization: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Trigger content generation
 */
export async function triggerContentGenerate(params: ContentGenerateParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/content-generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger content generation: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Trigger creative optimization
 */
export async function triggerCreativeOptimize(params: CreativeOptimizeParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/creative-optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger creative optimization: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Trigger market analysis
 */
export async function triggerMarketAnalyze(params: MarketAnalyzeParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/market-analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger market analysis: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Trigger keyword classification
 */
export async function triggerKeywordClassify(params: KeywordClassifyParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/keyword-classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger keyword classification: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Trigger Tavily research
 */
export async function triggerTavilyResearch(params: TavilyResearchParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/tavily-research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Failed to trigger Tavily research: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Trigger orchestration
 */
export async function triggerOrchestrate(params: OrchestrateParams): Promise<TriggerResult> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/orchestrate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to trigger orchestration: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Get trigger history
 */
export async function getTriggerHistory(limit: number = 50): Promise<any> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/history?limit=${limit}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get trigger history: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Get trigger stats
 */
export async function getTriggerStats(days: number = 30): Promise<any> {
  const response = await fetch(`${API_BASE}/api/v1/agents/trigger/stats?days=${days}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get trigger stats: ${response.statusText}`);
  }
  
  return response.json();
}