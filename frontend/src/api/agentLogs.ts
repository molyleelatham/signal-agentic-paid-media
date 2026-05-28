import { apiFetch } from "./client";
import type { TraceLine } from "../data/adtec";
import { MOCK_AGENT_LOGS } from "../lib/mockAgentLogs";

export interface AgentLogEntry {
  timestamp: string;
  agent: string;
  action: string;
  campaign?: string;
  channel?: string;
  amount?: number;
  result?: string;
  reasoning?: string;
  confidence?: number;
}

export async function fetchAgentLogs(limit = 25): Promise<AgentLogEntry[]> {
  try {
    const res = await apiFetch(`/terminal/agent-logs?limit=${limit}`);
    if (!res.ok) return MOCK_AGENT_LOGS.slice(0, limit);
    const data = (await res.json()) as AgentLogEntry[];
    return data.length ? data : MOCK_AGENT_LOGS.slice(0, limit);
  } catch {
    return MOCK_AGENT_LOGS.slice(0, limit);
  }
}

export function agentLogsToTrace(logs: AgentLogEntry[]): TraceLine[] {
  return logs.map((log) => {
    const parts = [
      log.action,
      log.campaign,
      log.channel ? `· ${log.channel}` : "",
      log.amount != null ? `£${Math.round(log.amount)}` : "",
      log.confidence != null ? `${Math.round(log.confidence)}%` : "",
      log.result ? `— ${log.result}` : "",
      log.reasoning && !log.result ? `— ${log.reasoning}` : "",
    ].filter(Boolean);
    const msg = `[${log.agent}] ${parts.join(" ")}`.trim();
    let tone: TraceLine["tone"] = "info";
    if (log.action === "BUY") tone = "ok";
    else if (log.action === "STOP" || log.action === "OPTIMIZE") tone = "work";
    else if (log.action === "HOLD") tone = "warn";
    else if (log.action === "MONITOR") tone = "info";
    return { msg, tone };
  });
}
