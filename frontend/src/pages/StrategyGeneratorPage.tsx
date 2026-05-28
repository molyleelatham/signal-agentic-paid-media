import { useEffect, useMemo, useState } from "react";
import { funnelStages } from "../data/adtec";
import { adtecLog } from "../lib/trace";
import { traceScripts } from "../data/adtec";
import { LineChart } from "../components/shared/charts";
import { useStrategyDocs } from "../hooks/useStrategyDocs";
import {
  computeKpisForSelection,
  logToneForQuarter,
  quarterRecords,
  quartersForChart,
  strategySectionsForSelection,
  type QuarterStatus,
} from "../lib/strategyQuarters";

const quarters = quartersForChart();

const STATUS_STYLE: Record<QuarterStatus, { dot: string; label: string; bg: string }> = {
  executed: { dot: "#888", label: "ARCHIVED", bg: "#88888818" },
  active: { dot: "#00FF88", label: "ACTIVE", bg: "#00ff8818" },
  planned: { dot: "#FFB800", label: "PLANNED", bg: "#ffb80018" },
};

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
          const rec = quarterRecords[i];
          const total = funnelStages.reduce(
            (s, st) => s + q.stages[st.id as keyof typeof q.stages],
            0,
          );
          const dim = sel.length > 0 && !sel.includes(i);
          const on = sel.includes(i);
          const st = STATUS_STYLE[rec.status];

          return (
            <div
              key={q.q}
              onClick={(e) => onBar(i, e.shiftKey)}
              className="flex h-full flex-1 cursor-pointer flex-col items-center justify-end gap-1.5"
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
                {funnelStages.map((stg) => {
                  const v = q.stages[stg.id as keyof typeof q.stages];
                  const faded = stageFilter && stageFilter !== stg.id;
                  return (
                    <div
                      key={stg.id}
                      title={`${stg.label} ${v}`}
                      style={{
                        height: `${(v / total) * 100}%`,
                        background: stg.color,
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
              <span
                className="max-w-[88px] truncate text-center text-[8px] text-[#666]"
                title={rec.strategy.theme}
              >
                {rec.strategy.theme}
              </span>
              <span
                className="rounded px-1 py-px text-[7px] font-medium tracking-wide"
                style={{ color: st.dot, background: st.bg }}
              >
                {st.label}
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

function PreviousStrategiesArchive({
  sel,
  onSelect,
}: {
  sel: number[];
  onSelect: (index: number) => void;
}) {
  const archived = quarterRecords.filter((q) => q.status === "executed");

  return (
    <div className="shrink-0 border-t border-[#1f1f1f] bg-[#0a0a0a] px-4 py-3">
      <div className="eyebrow mb-2">PREVIOUS STRATEGIES · EXECUTED QUARTERS</div>
      <div className="flex flex-wrap gap-2">
        {archived.map((rec) => {
          const idx = quarterRecords.indexOf(rec);
          const active = sel.length === 1 && sel[0] === idx;
          return (
            <button
              key={rec.q}
              type="button"
              onClick={() => onSelect(idx)}
              className="flex min-w-[200px] flex-1 flex-col rounded border px-3 py-2 text-left transition-colors"
              style={{
                borderColor: active ? "#888" : "#222",
                background: active ? "#161616" : "#111",
              }}
            >
              <div className="flex items-center gap-2">
                <span className="font-display text-sm font-bold text-white">{rec.q}</span>
                <span className="text-[9px] text-[#666]">{rec.period}</span>
              </div>
              <div className="mt-0.5 text-[10px] font-medium text-[#00d4ff]">{rec.strategy.theme}</div>
              <div className="mt-1 line-clamp-2 text-[9px] leading-snug text-[#777]">
                {rec.strategy.headline}
              </div>
              <div className="mt-1.5 flex flex-wrap gap-2 text-[8px] text-[#555]">
                <span>{rec.leads.toLocaleString()} leads</span>
                <span>·</span>
                <span>£{rec.cpl.toFixed(2)} CPL</span>
                <span>·</span>
                <span>{rec.roas.toFixed(1)}× ROAS</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function buildStrategySections(sel: number[], agentActions?: string[]) {
  const { sections, label, status } = strategySectionsForSelection(sel.length ? sel : [2]);
  const agentBlock =
    agentActions?.length ?
      {
        h: "AGENT ACTIONS (FROM API)",
        b: agentActions.slice(0, 4).map((a) => `• ${a}`).join("\n"),
      }
    : null;
  return {
    sections: agentBlock ? [...sections, agentBlock] : sections,
    label,
    status,
  };
}

function GeneratedStrategyInline({
  open,
  sel,
  agentActions,
}: {
  open: boolean;
  sel: number[];
  agentActions?: string[];
}) {
  const { sections, label, status } = useMemo(
    () => buildStrategySections(sel, agentActions),
    [sel, agentActions],
  );

  const accent = status === "executed" ? "#888" : status === "planned" ? "#FFB800" : "#00D4FF";
  const rec = sel.length === 1 ? quarterRecords[sel[0]] : quarterRecords[2];

  if (!open) return null;

  return (
    <div className="shrink-0 border-t border-[#1f1f1f] bg-[#0a0a0a]">
      <div className="flex items-center justify-between border-b border-[#1f1f1f] px-4 py-2.5">
        <div>
          <div className="eyebrow">GENERATED STRATEGY</div>
          <div className="mt-0.5 flex flex-wrap items-center gap-2">
            <span className="font-display text-base font-bold text-[#00d4ff]">
              {rec.strategy.theme}
            </span>
            <span className="text-[9px]" style={{ color: accent }}>
              {label}
            </span>
          </div>
        </div>
        <span className="text-[9px] text-[#555]">{rec.period}</span>
      </div>
      <div className="grid gap-3 px-4 py-3 md:grid-cols-2">
        {sections.map((s) => (
          <div
            key={s.h}
            className="rounded border border-[#1f1f1f] bg-[#111] px-3 py-2.5"
          >
            <div className="mb-1.5 text-[10px] tracking-widest text-[#00d4ff]">{s.h}</div>
            <div className="text-[11px] leading-relaxed text-[#ccc]">{s.b}</div>
          </div>
        ))}
      </div>
      <div className="border-t border-[#1f1f1f] px-4 py-2 text-[9px] text-[#555]">
        {status === "executed"
          ? "Archived quarter strategy · executed record"
          : status === "planned"
            ? "Forecast strategy · Q4 planning draft"
            : "Active Q3 strategy · grounded in Tavily + agent models"}
      </div>
    </div>
  );
}

function StrategyPanel({
  open,
  onClose,
  sel,
  agentActions,
}: {
  open: boolean;
  onClose: () => void;
  sel: number[];
  agentActions?: string[];
}) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const { sections, label, status } = useMemo(
    () => buildStrategySections(sel, agentActions),
    [sel, agentActions],
  );

  const allSections = sections;

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setText("");
    let cancelled = false;
    const full = allSections.map((s) => `§ ${s.h}\n${s.b}`).join("\n\n");
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
  }, [open, allSections]);

  const panelAccent =
    status === "executed" ? "#888" : status === "planned" ? "#FFB800" : "#00D4FF";

  return (
    <div
      className="absolute bottom-0 right-0 top-0 z-[70] flex w-[400px] flex-col border-l border-[#2a2a2a] bg-[#0a0a0a] shadow-2xl transition-transform duration-300"
      style={{ transform: open ? "translateX(0)" : "translateX(105%)" }}
    >
      <div className="flex items-center justify-between border-b border-[#1f1f1f] px-3.5 py-3">
        <div className="min-w-0 flex-1">
          <span className="text-[11px] tracking-widest text-[#ccc]">STRATEGY · claude-sonnet</span>
          <div className="mt-0.5 truncate text-[9px]" style={{ color: panelAccent }}>
            {label}
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="h-[22px] w-[22px] shrink-0 border border-[#2a2a2a] text-[11px] text-[#888]"
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
      <div className="border-t border-[#1f1f1f] px-3.5 py-2 text-[9px] text-[#555]">
        {status === "executed"
          ? "ⓘ Archived strategy — read-only record from executed quarter"
          : status === "planned"
            ? "ⓘ Forecast strategy — subject to Overmind reallocation"
            : "ⓘ Grounded via Tavily research + /terminal/strategy-docs"}
      </div>
    </div>
  );
}

export function StrategyGeneratorPage() {
  const { data: strategyDocs } = useStrategyDocs();
  const [sel, setSel] = useState<number[]>([2]);
  const [stageFilter, setStageFilter] = useState<string | null>(null);
  const [panel, setPanel] = useState(false);

  const [showStrategy, setShowStrategy] = useState(false);

  const kpiRows = useMemo(() => computeKpisForSelection(sel.length ? sel : [2]), [sel]);
  const strategyPreview = useMemo(
    () => buildStrategySections(sel.length ? sel : [2], strategyDocs?.agent_actions),
    [sel, strategyDocs?.agent_actions],
  );
  const selectedRec = sel.length === 1 ? quarterRecords[sel[0]] : quarterRecords[2];

  const lineSeries = useMemo(
    () => [
      { name: "Leads (k)", color: "#00D4FF", data: quarters.map((q) => q.leads / 1000) },
      { name: "Spend (£k)", color: "#8B5CF6", data: quarters.map((q) => q.spend / 1000) },
      { name: "CPL (×10)", color: "#FFB800", data: quarters.map((q) => q.cpl * 10) },
    ],
    [],
  );

  const selectedRecForHeader = sel.length === 1 ? quarterRecords[sel[0]] : null;

  const openStrategy = (indices?: number[]) => {
    if (indices) setSel(indices);
    setShowStrategy(true);
    setPanel(true);
    const q = indices?.length === 1 ? quarterRecords[indices[0]] : selectedRecForHeader ?? quarterRecords[2];
    adtecLog([
      {
        msg: q
          ? `Loading ${q.status === "executed" ? "archived" : q.status} strategy for ${q.q}…`
          : traceScripts.strategy[0].msg,
        tone: q ? logToneForQuarter(q.status) : "work",
      },
      ...(q?.status === "executed"
        ? [{ msg: `${q.q} delivered ${q.leads.toLocaleString()} leads at £${q.cpl.toFixed(2)} CPL.`, tone: "info" as const }]
        : traceScripts.strategy.slice(1)),
    ]);
  };

  return (
    <div className="relative flex h-full min-h-0 flex-col">
      <div className="absolute right-4 top-3 z-30 flex max-w-[min(420px,45vw)] items-start gap-2">
        {selectedRecForHeader?.status === "executed" && (
          <span className="mt-2 rounded border border-[#444] bg-[#222] px-2 py-1 text-[9px] text-[#aaa]">
            VIEWING ARCHIVE
          </span>
        )}
        <div className="flex min-w-0 flex-col items-end gap-2">
          <button
            type="button"
            className="btn btn-primary shrink-0"
            onClick={() => {
              if (showStrategy) {
                setShowStrategy(false);
                setPanel(false);
              } else {
                openStrategy();
              }
            }}
          >
            {showStrategy
              ? "HIDE STRATEGY ✕"
              : selectedRecForHeader?.status === "executed"
                ? "VIEW STRATEGY ↗"
                : "GENERATE STRATEGY ↗"}
          </button>
          {!showStrategy && (
            <div className="max-w-[320px] rounded border border-[#222] bg-[#111]/90 px-2.5 py-1.5 text-right text-[9px] leading-snug text-[#777]">
              <span className="text-[#00d4ff]">{selectedRec.strategy.theme}</span>
              {" · "}
              {strategyPreview.sections[0]?.b.slice(0, 72)}…
            </div>
          )}
        </div>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-1 md:grid-cols-2">
        <div className="flex min-h-0 flex-col border-r border-[#1f1f1f] p-4">
          <FunnelBars
            sel={sel}
            setSel={setSel}
            stageFilter={stageFilter}
            setStageFilter={setStageFilter}
          />
        </div>
        <div className="flex min-h-0 flex-col p-4">
          <div className="eyebrow mb-2">
            LEADS · SPEND · CPL
            {sel.length ? ` · ${sel.map((i) => quarterRecords[i].q).join(", ")}` : " · Q3 ACTIVE"}
          </div>
          {selectedRecForHeader && (
            <div className="mb-2 rounded border border-[#1f1f1f] bg-[#111] px-3 py-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[10px] font-medium text-[#00d4ff]">
                  {selectedRecForHeader.strategy.theme}
                </span>
                <span className="text-[9px] text-[#666]">{selectedRecForHeader.period}</span>
              </div>
              <div className="mt-1 text-[9px] leading-snug text-[#888]">
                {selectedRecForHeader.strategy.headline}
              </div>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {selectedRecForHeader.strategy.channelMix.map((c) => (
                  <span
                    key={c.channel}
                    className="rounded bg-[#1a1a1a] px-1.5 py-0.5 text-[8px] text-[#999]"
                  >
                    {c.channel} {c.pct}%
                  </span>
                ))}
              </div>
            </div>
          )}
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

      <GeneratedStrategyInline
        open={showStrategy}
        sel={sel.length ? sel : [2]}
        agentActions={strategyDocs?.agent_actions}
      />

      <PreviousStrategiesArchive
        sel={sel}
        onSelect={(idx) => {
          setSel([idx]);
          openStrategy([idx]);
        }}
      />

      <div
        className="flex shrink-0 flex-wrap overflow-hidden border-t border-[#1f1f1f] bg-[#0b0b0b] transition-[height] duration-300"
        style={{ height: sel.length ? "auto" : 0, minHeight: sel.length ? 92 : 0 }}
      >
        {kpiRows.map((k, i) => (
          <div
            key={i}
            className="min-w-[140px] flex-1 px-4 py-3"
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

      <StrategyPanel
        open={panel}
        onClose={() => setPanel(false)}
        sel={sel.length ? sel : [2]}
        agentActions={strategyDocs?.agent_actions}
      />
    </div>
  );
}
