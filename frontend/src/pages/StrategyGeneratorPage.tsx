import { useEffect, useMemo, useState } from "react";
import { funnelStages, kpiRows, quarters } from "../data/adtec";
import { adtecLog } from "../lib/trace";
import { traceScripts } from "../data/adtec";
import { LineChart } from "../components/shared/charts";

function FunnelBars({
  sel,
  setSel,
  stageFilter,
  setStageFilter,
}: {
  sel: number[];
  setSel: React.Dispatch<React.SetStateAction<number[]>>;
  stageFilter: string | null;
  setStageFilter: React.Dispatch<React.SetStateAction<string | null>>;
}) {
  const maxTotal = Math.max(
    ...quarters.map((q) =>
      funnelStages.reduce((s, st) => s + q.stages[st.id as keyof typeof q.stages], 0),
    ),
  );

  const onBar = (i: number, shift: boolean) => {
    setSel((prev) => {
      if (shift) return prev.includes(i) ? prev.filter((x) => x !== i) : [...prev, i];
      return prev.length === 1 && prev[0] === i ? [] : [i];
    });
  };

  return (
    <div className="flex min-w-0 flex-1 flex-col">
      <div className="eyebrow mb-2">QUARTERLY CAMPAIGN VOLUME · CLICK BAR · SHIFT+CLICK MULTI</div>
      <div className="flex min-h-0 flex-1 items-end gap-4 px-2">
        {quarters.map((q, i) => {
          const total = funnelStages.reduce(
            (s, st) => s + q.stages[st.id as keyof typeof q.stages],
            0,
          );
          const dim = sel.length > 0 && !sel.includes(i);
          const on = sel.includes(i);
          return (
            <div
              key={q.q}
              onClick={(e) => onBar(i, e.shiftKey)}
              className="flex h-full flex-1 cursor-pointer flex-col items-center justify-end gap-2"
            >
              <div
                className="flex w-full max-w-[88px] flex-col-reverse transition-all"
                style={{
                  height: `${(total / maxTotal) * 100}%`,
                  outline: on ? "2px solid #fff" : undefined,
                  outlineOffset: 2,
                  transform: on ? "translateY(-3px)" : undefined,
                  opacity: dim ? 0.4 : 1,
                }}
              >
                {funnelStages.map((st) => {
                  const v = q.stages[st.id as keyof typeof q.stages];
                  const faded = stageFilter && stageFilter !== st.id;
                  return (
                    <div
                      key={st.id}
                      title={`${st.label} ${v}`}
                      style={{
                        height: `${(v / total) * 100}%`,
                        background: st.color,
                        opacity: faded ? 0.15 : 1,
                      }}
                    />
                  );
                })}
              </div>
              <span
                className={`tnum font-display text-sm font-bold ${on ? "text-white" : "text-[#888]"}`}
              >
                {q.q}
              </span>
            </div>
          );
        })}
      </div>
      <div className="flex flex-wrap gap-3 px-1 pt-3">
        {funnelStages.map((st) => (
          <button
            key={st.id}
            type="button"
            onClick={() => setStageFilter((f) => (f === st.id ? null : st.id))}
            className="flex items-center gap-1.5 border-0 bg-transparent"
            style={{ opacity: stageFilter && stageFilter !== st.id ? 0.4 : 1 }}
          >
            <span className="inline-block h-2.5 w-2.5" style={{ background: st.color }} />
            <span className="text-[9.5px] tracking-wide text-[#999]">{st.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function StrategyPanel({
  open,
  onClose,
  sel,
}: {
  open: boolean;
  onClose: () => void;
  sel: number[];
}) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const canned = useMemo(() => {
    const qs = (sel.length ? sel : [0, 1, 2, 3]).map((i) => quarters[i].q).join(", ");
    return [
      {
        h: "CAMPAIGN THEME",
        b: `"Squat-Proof Season" — lead with the scrunch leggings +34% signal across ${qs}.`,
      },
      {
        h: "CHANNEL MIX",
        b: "Shift 18% of Meta Advantage+ budget into TikTok Spark Ads.",
      },
      {
        h: "BUDGET REALLOCATION",
        b: "£62.4K → reweight: TikTok 32%, Meta 28%, Google 24%, Influencer 16%.",
      },
      {
        h: "RISK FLAGS",
        b: "⚠ Interest→Consideration drop-off at 34% — add mid-funnel retargeting.",
      },
    ];
  }, [sel]);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setText("");
    let cancelled = false;
    const full = canned.map((s) => `§ ${s.h}\n${s.b}`).join("\n\n");
    (async () => {
      for (let i = 0; i <= full.length; i += 3) {
        if (cancelled) return;
        setText(full.slice(0, i));
        await new Promise((r) => setTimeout(r, 8));
      }
      if (!cancelled) {
        setText(full);
        setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open, canned]);

  return (
    <div
      className="absolute bottom-0 right-0 top-0 z-[70] flex w-[380px] flex-col border-l border-[#2a2a2a] bg-[#0a0a0a] shadow-2xl transition-transform duration-300"
      style={{ transform: open ? "translateX(0)" : "translateX(105%)" }}
    >
      <div className="flex items-center justify-between border-b border-[#1f1f1f] px-3.5 py-3">
        <span className="text-[11px] tracking-widest text-[#ccc]">STRATEGY · claude-sonnet</span>
        <button
          type="button"
          onClick={onClose}
          className="h-[22px] w-[22px] border border-[#2a2a2a] text-[11px] text-[#888]"
        >
          ✕
        </button>
      </div>
      <div className="flex-1 overflow-y-auto whitespace-pre-wrap p-4 text-xs leading-relaxed text-[#d6d6d6]">
        {text.split("\n\n").map((blk, i) => {
          const lines = blk.split("\n");
          return (
            <div key={i} className="mb-3.5">
              {lines[0].startsWith("§ ") ? (
                <>
                  <div className="mb-1 text-[10px] tracking-widest text-[#00d4ff]">
                    {lines[0].slice(2)}
                  </div>
                  <div>{lines.slice(1).join("\n")}</div>
                </>
              ) : (
                <div>{blk}</div>
              )}
            </div>
          );
        })}
        {loading && (
          <span className="inline-block h-3 w-1.5 animate-pulse bg-[#00ff88] align-middle" />
        )}
      </div>
    </div>
  );
}

export function StrategyGeneratorPage() {
  const [sel, setSel] = useState<number[]>([2]);
  const [stageFilter, setStageFilter] = useState<string | null>(null);
  const [panel, setPanel] = useState(false);

  const lineSeries = useMemo(
    () => [
      { name: "Leads (k)", color: "#00D4FF", data: quarters.map((q) => q.leads / 1000) },
      { name: "Spend (£k)", color: "#8B5CF6", data: quarters.map((q) => q.spend / 1000) },
      { name: "CPL (×10)", color: "#FFB800", data: quarters.map((q) => q.cpl * 10) },
    ],
    [sel.join(",")],
  );

  return (
    <div className="relative flex h-full min-h-0 flex-col">
      <div className="absolute right-4 top-3 z-30">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => {
            setPanel(true);
            adtecLog(traceScripts.strategy);
          }}
        >
          GENERATE STRATEGY ↗
        </button>
      </div>
      <div className="grid min-h-0 flex-1 grid-cols-1 md:grid-cols-2">
        <div className="flex flex-col border-r border-[#1f1f1f] p-4">
          <FunnelBars
            sel={sel}
            setSel={setSel}
            stageFilter={stageFilter}
            setStageFilter={setStageFilter}
          />
        </div>
        <div className="flex flex-col p-4">
          <div className="eyebrow mb-2">
            LEADS · SPEND · CPL
            {sel.length ? ` · ${sel.length} period(s) selected` : " · FULL YEAR"}
          </div>
          <div className="flex min-h-0 flex-1 items-center">
            <LineChart
              series={lineSeries}
              labels={quarters.map((q) => q.q)}
              w={420}
              h={210}
              animateKey={sel.join(",")}
              highlight={sel}
            />
          </div>
        </div>
      </div>
      <div
        className="flex shrink-0 overflow-hidden border-t border-[#1f1f1f] bg-[#0b0b0b] transition-[height] duration-300"
        style={{ height: sel.length ? 92 : 0 }}
      >
        {kpiRows.map((k, i) => (
          <div
            key={i}
            className="flex-1 px-4 py-3"
            style={{ borderRight: i < kpiRows.length - 1 ? "1px solid #1A1A1A" : undefined }}
          >
            <div className="mb-1 text-[9.5px] uppercase tracking-wide text-[#666]">{k.k}</div>
            <div className="tnum font-display text-2xl font-bold text-white">{k.v}</div>
            <span
              className="pill mt-1 text-[10px]"
              style={{
                color: k.tone === "good" ? "#00FF88" : k.tone === "warn" ? "#FFB800" : "#999",
              }}
            >
              {k.b}
            </span>
          </div>
        ))}
      </div>
      <StrategyPanel open={panel} onClose={() => setPanel(false)} sel={sel} />
    </div>
  );
}
