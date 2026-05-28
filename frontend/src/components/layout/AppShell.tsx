import { useEffect, useState } from "react";
import { pages, traceScripts, type PageId } from "../../data/adtec";
import { adtecLog } from "../../lib/trace";
import { useTerminalData } from "../../hooks/useTerminalData";
import { BudgetScenarioPage } from "../../pages/BudgetScenarioPage";
import { CampaignPerformancePage } from "../../pages/CampaignPerformancePage";
import { MarketIntelligencePage } from "../../pages/MarketIntelligencePage";
import { SignalTerminalPage } from "../../pages/SignalTerminalPage";
import { StrategyGeneratorPage } from "../../pages/StrategyGeneratorPage";
import { OrderFlowPanel } from "../orderflow/OrderFlowPanel";
import { OvermindTerminal } from "../terminal/OvermindTerminal";
import { Header } from "./Header";

function PageHeader({ n, title, sub }: { n: string; title: string; sub: string }) {
  return (
    <div className="flex shrink-0 items-center gap-3.5 border-b border-[#1f1f1f] px-5 py-2.5">
      <div
        className="font-display text-[40px] font-extrabold leading-none text-transparent"
        style={{ WebkitTextStroke: "1px #2a2a2a" }}
      >
        {n}
      </div>
      <div className="h-8 w-px bg-[#222]" />
      <div>
        <h2 className="font-display text-2xl uppercase leading-none text-white">{title}</h2>
        <div className="mt-0.5 text-[10.5px] tracking-wide text-[#666]">{sub}</div>
      </div>
    </div>
  );
}

function renderPage(id: PageId) {
  switch (id) {
    case "intel":
      return <MarketIntelligencePage />;
    case "strategy":
      return <StrategyGeneratorPage />;
    case "budget":
      return <BudgetScenarioPage />;
    case "perf":
      return <CampaignPerformancePage />;
    case "terminal":
      return <SignalTerminalPage />;
    default:
      return null;
  }
}

export function AppShell() {
  const [active, setActive] = useState<PageId>("intel");
  const { data } = useTerminalData();
  const page = pages.find((p) => p.id === active)!;

  useEffect(() => {
    adtecLog(traceScripts[active] || []);
  }, [active]);

  const channels = data?.channel_metrics ?? [];
  const campaigns = data?.campaign_signals ?? [];

  return (
    <div className="relative flex h-full flex-col overflow-hidden bg-black">
      <div
        className="pointer-events-none fixed inset-0 z-0 opacity-40"
        style={{
          background:
            "radial-gradient(120% 80% at 50% -10%, rgba(0,212,255,.06), transparent 60%)",
        }}
      />
      <div className="relative z-10 flex min-h-0 flex-1 flex-col">
        <Header stats={data?.header_stats} pages={pages} active={active} onNavigate={setActive} />
        <div className="flex min-h-0 min-w-0 flex-1 overflow-hidden">
          <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-[rgba(8,8,8,.94)]">
            <PageHeader n={page.n} title={page.title} sub={page.sub} />
            <div className="min-h-0 flex-1 overflow-hidden">{renderPage(active)}</div>
          </main>
          <OrderFlowPanel channels={channels} campaigns={campaigns} />
        </div>
        <OvermindTerminal activePage={active} />
      </div>
    </div>
  );
}
