import type { AgentLog } from "../../types/terminal";

const AGENT_COLORS: Record<string, string> = {
  BID_STRATEGY: "#00bfff",
  CREATIVE_OPT: "#ff00ff",
  MARKET_ANALYSIS: "#00ffff",
  ORCHESTRATION: "#ffff00",
  THOMPSON_ALLOCATOR: "#00ff00",
};

export function AgentExecutionLog({ logs }: { logs: AgentLog[] }) {
  return (
    <section className="flex min-h-0 flex-1 flex-col overflow-hidden rounded border border-[#1f1f1f] bg-[#0a0a0a]">
      <div className="panel-header">
        <h2 className="panel-title">Agent Execution Log</h2>
        <span className="text-[10px] text-[#555]">{logs.length} events</span>
      </div>
      <div className="flex-1 overflow-y-auto p-3 font-mono text-[12px] leading-relaxed">
        {logs.map((log, i) => (
          <div
            key={`${log.timestamp}-${log.agent}-${i}`}
            className="mb-1 flex flex-wrap gap-x-2 gap-y-0"
          >
            <span className="tnum shrink-0 text-[#4a4a4a]">
              {log.timestamp}
            </span>
            <span
              className="shrink-0 text-[10px] font-semibold tracking-wide"
              style={{ color: AGENT_COLORS[log.agent] ?? "#888" }}
            >
              [{log.agent}]
            </span>
            <span className="text-[#e2e2e2]">
              {log.action}
              {log.campaign ? ` ${log.campaign}` : ""}
              {log.amount != null ? ` £${log.amount.toLocaleString()}` : ""}
              {log.result ? ` — ${log.result}` : ""}
              {log.confidence != null ? ` (${log.confidence}%)` : ""}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
