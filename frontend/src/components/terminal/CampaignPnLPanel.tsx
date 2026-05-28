import type { CampaignSignal, HeaderStats } from "../../types/terminal";

export function CampaignPnLPanel({
  stats,
  signals,
}: {
  stats: HeaderStats;
  signals: CampaignSignal[];
}) {
  const spent = signals.reduce((a, s) => a + s.spend, 0);
  const remaining = Math.max(0, stats.budget - spent);
  const revenue = spent * stats.roas;
  const cpl = stats.leads > 0 ? stats.budget / stats.leads : 0;

  return (
    <section className="flex min-h-0 flex-col overflow-hidden rounded border border-[#1f1f1f] bg-[#1a1a1a]">
      <div className="panel-header">
        <h2 className="panel-title">Campaign P&amp;L</h2>
      </div>
      <div className="grid flex-1 grid-cols-2 gap-px bg-[#1f1f1f] p-px">
        <Metric label="ROAS" value={stats.roas.toFixed(2)} highlight />
        <Metric label="CPL" value={`£${cpl.toFixed(0)}`} />
        <Metric
          label="Revenue / wk"
          value={`£${(revenue / 1000).toFixed(0)}K`}
        />
        <Metric label="Budget" value={`£${(stats.budget / 1000).toFixed(0)}K`} />
        <Metric label="Spent" value={`£${(spent / 1000).toFixed(1)}K`} />
        <Metric
          label="Remaining"
          value={`£${(remaining / 1000).toFixed(1)}K`}
          warn={remaining < stats.budget * 0.15}
        />
      </div>
      <div className="border-t border-[#1f1f1f] px-3 py-2 text-[10px] text-[#666]">
        +55% vs baseline · {stats.leads.toLocaleString()} leads MTD
      </div>
    </section>
  );
}

function Metric({
  label,
  value,
  highlight,
  warn,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  warn?: boolean;
}) {
  return (
    <div className="bg-[#1a1a1a] p-3">
      <div className="text-[9px] tracking-widest text-[#666]">{label}</div>
      <div
        className={`tnum mt-0.5 font-display text-lg font-semibold ${
          highlight ? "text-[#00bfff]" : warn ? "text-[#ffff00]" : "text-white"
        }`}
      >
        {value}
      </div>
    </div>
  );
}
