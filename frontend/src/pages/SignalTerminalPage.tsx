import { useTerminalData } from "../hooks/useTerminalData";
import { AgentExecutionLog } from "../components/terminal/AgentExecutionLog";
import { AgentSignalsPanel } from "../components/terminal/AgentSignalsPanel";
import { CampaignPnLPanel } from "../components/terminal/CampaignPnLPanel";
import { MarketDataPanel } from "../components/terminal/MarketDataPanel";

export function SignalTerminalPage() {
  const { data, isLoading } = useTerminalData();

  if (isLoading && !data) {
    return (
      <div className="flex h-full items-center justify-center text-[#666]">
        Loading agent signals…
      </div>
    );
  }
  if (!data) return null;

  return (
    <div className="flex h-full min-h-0 flex-col gap-3 p-3">
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 md:grid-cols-3">
        <AgentSignalsPanel signals={data.campaign_signals} />
        <CampaignPnLPanel stats={data.header_stats} signals={data.campaign_signals} />
        <MarketDataPanel scores={data.algorithm_scores} />
      </div>
      <AgentExecutionLog logs={data.agent_logs} />
    </div>
  );
}
