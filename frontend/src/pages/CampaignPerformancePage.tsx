import { useState } from "react";
import { adstock, advKpis, beforeAfter } from "../data/adtec";
import { DecayCurve, Spark } from "../components/shared/charts";

const SIGNAL = {
  BUY: { c: "#00FF88", bg: "rgba(0,255,136,.12)" },
  HOLD: { c: "#FFB800", bg: "rgba(255,184,0,.12)" },
  SELL: { c: "#FF4444", bg: "rgba(255,68,68,.12)" },
};

function KpiCard({
  k,
  expanded,
  onToggle,
}: {
  k: (typeof advKpis)[0];
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="min-w-0 flex-1 cursor-pointer border border-[#1f1f1f] bg-[#111] p-3.5 text-left"
      style={{ borderLeft: `3px solid ${k.cat}` }}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="text-[9.5px] uppercase tracking-wide text-[#777]">{k.title}</div>
          <div className="tnum font-display text-3xl font-extrabold text-white">{k.value}</div>
        </div>
        {"spark" in k && k.spark && <Spark data={k.spark} color={k.cat} w={56} h={26} />}
        {"delta" in k && k.delta && <span className="pill badge-up">{k.delta}</span>}
      </div>
      <div className="mt-1.5 text-[10px] text-[#666]">{k.sub}</div>
      {"heat" in k && k.heat && (
        <div className="mt-2 grid grid-cols-6 gap-0.5">
          {k.heat.map((v, i) => (
            <div
              key={i}
              title={`${v}%`}
              className="aspect-[1.6]"
              style={{ background: `rgba(16,185,129,${0.15 + v / 130})` }}
            />
          ))}
        </div>
      )}
      {"before" in k && k.before != null && (
        <div className="mt-2 flex items-center gap-2">
          <span className="tnum text-[11px] text-[#666]">{k.before}%</span>
          <span className="text-[#444]">→</span>
          <span className="tnum text-[11px] text-[#00ff88]">{k.after}%</span>
        </div>
      )}
      {expanded && (
        <div className="mt-2.5 border-t border-[#1f1f1f] pt-2.5 text-[10px] leading-snug text-[#888]">
          Detail drawer · synced from supabase.campaign_kpis
        </div>
      )}
    </button>
  );
}

function BeforeAfter() {
  return (
    <div className="flex h-full min-h-0 flex-col border-r border-[#1f1f1f]">
      <div className="shrink-0 px-4 pb-2 pt-3">
        <div className="eyebrow">SECTION B · SIGNAL COMPARISON</div>
        <div className="mt-0.5 text-[10px] text-[#555]">Overmind trace analysis · #1031 → #1042</div>
      </div>
      <div className="flex min-h-0 flex-1">
        <div className="flex flex-1 flex-col justify-center gap-3.5 px-4 opacity-60">
          <div className="eyebrow text-[#555]">BEFORE</div>
          {beforeAfter.map((b) => (
            <div key={b.k}>
              <div className="text-[9.5px] text-[#666]">{b.k}</div>
              <div className="tnum font-display text-xl font-bold text-[#999]">{b.before}</div>
            </div>
          ))}
        </div>
        <div className="w-px bg-gradient-to-b from-[#1f1f1f] via-[#333] to-[#1f1f1f]" />
        <div className="flex flex-1 flex-col justify-center gap-3.5 px-4">
          <div className="eyebrow text-[#00d4ff]">AFTER ▸</div>
          {beforeAfter.map((b) => (
            <div key={b.k}>
              <div className="text-[9.5px] text-[#666]">{b.k}</div>
              <div className="flex items-baseline gap-2">
                <div className="tnum font-display text-xl font-extrabold text-white">{b.after}</div>
                <span className="pill badge-up">{b.delta}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AdstockRow({ a }: { a: (typeof adstock)[0] }) {
  const s = SIGNAL[a.signal];
  return (
    <div className="flex items-center gap-3.5 border-b border-[#141414] px-4 py-2.5">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 shrink-0" style={{ background: a.platColor }} />
          <span className="truncate text-xs text-[#e2e2e2]">{a.name}</span>
        </div>
        <div className="pl-3.5 text-[9.5px] text-[#555]">{a.plat}</div>
      </div>
      <DecayCurve data={a.curve} color={s.c} />
      <span
        className="pill min-w-[54px] justify-center font-medium"
        style={{ color: s.c, background: s.bg, border: `1px solid ${s.c}44` }}
      >
        {a.signal}
      </span>
    </div>
  );
}

export function CampaignPerformancePage() {
  const [exp, setExp] = useState<number | null>(null);
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex shrink-0 gap-3 p-4">
        {advKpis.map((k, i) => (
          <KpiCard
            key={k.id}
            k={k}
            expanded={exp === i}
            onToggle={() => setExp((e) => (e === i ? null : i))}
          />
        ))}
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-1 border-t border-[#1f1f1f] lg:grid-cols-[1fr_1.15fr]">
        <BeforeAfter />
        <div className="flex min-h-0 flex-col">
          <div className="flex shrink-0 items-center justify-between px-4 pb-2 pt-3">
            <div>
              <div className="eyebrow">SECTION C · ADSTOCK DECAY</div>
              <div className="mt-0.5 text-[10px] text-[#555]">
                Overmind Optimizer + Thrads bid signal
              </div>
            </div>
            <div className="flex gap-2.5">
              {Object.entries(SIGNAL).map(([k, v]) => (
                <span key={k} className="flex items-center gap-1 text-[9px] text-[#888]">
                  <span className="h-2 w-2 rounded-full" style={{ background: v.c }} />
                  {k}
                </span>
              ))}
            </div>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {adstock.map((a, i) => (
              <AdstockRow key={i} a={a} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
