import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { allocateBudgetFlexible } from "../api/budget";
import { adtecLog } from "../lib/trace";
import { useBudgetScenarios } from "../hooks/useBudgetScenarios";
import { useTerminalData } from "../hooks/useTerminalData";
import { useTriggerBidOptimize } from "../hooks/useAgentTriggers";
import {
  allChannelsFromMatrix,
  applyFlexibleAllocation,
  buildUiScenariosFromApi,
  channelColor,
  channelKeyFromDisplay,
  fallbackUiScenarios,
  pillarFromSliders,
  type MatrixRow,
  type UiScenario,
  type UiScenarioKey,
  type UiScenarioState,
} from "../lib/mapBudgetScenarios";

const fmt = (n: number) => "£" + Math.round(n).toLocaleString();

function ScenarioTab({
  s,
  id,
  active,
  onClick,
}: {
  s: UiScenario;
  id: UiScenarioKey;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex h-[74px] min-w-[180px] flex-1 flex-col justify-center rounded-sm px-4 text-left transition-all sm:max-w-[220px]"
      style={{
        background: s.bg,
        border: `1px solid ${active ? "#fff" : s.border}`,
        boxShadow: active ? "0 0 0 1px #fff, 0 8px 22px rgba(0,0,0,.5)" : undefined,
      }}
    >
      <div className="mb-1 flex items-center gap-1.5">
        <span
          className="h-1.5 w-1.5 shrink-0 rounded-full"
          style={{
            background:
              id === "conservative"
                ? "#888"
                : id === "optimistic"
                  ? "#00FF88"
                  : id === "flexible"
                    ? "#00D4FF"
                    : "#FF4444",
          }}
        />
        <span
          className={`font-display text-lg font-bold ${active ? "text-white" : "text-[#ccc]"}`}
        >
          {s.label}
        </span>
        <span className="ml-auto rounded bg-black/40 px-1.5 py-0.5 text-[8px] uppercase text-[#888]">
          {s.riskLevel}
        </span>
      </div>
      <div className="text-[10px] text-[#888]">{s.desc}</div>
    </button>
  );
}

function EditCell({
  value,
  display,
  onChange,
  color,
}: {
  value: number;
  display: (v: number) => string;
  onChange: (v: number) => void;
  color?: string;
}) {
  const [editing, setEditing] = useState(false);
  const [flash, setFlash] = useState(false);
  const [draft, setDraft] = useState("");
  const commit = () => {
    setEditing(false);
    const n = parseFloat(draft.replace(/[^0-9.]/g, ""));
    if (!isNaN(n)) {
      onChange(n);
      setFlash(true);
      setTimeout(() => setFlash(false), 500);
    }
  };
  return (
    <td
      onClick={() => {
        setDraft(String(value));
        setEditing(true);
      }}
      className="cursor-text border-b border-[#141414] px-3 py-1.5 text-right"
      style={{ color: color || "#D6D6D6", animation: flash ? "flash 0.5s" : undefined }}
    >
      {editing ? (
        <input
          autoFocus
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => e.key === "Enter" && commit()}
          className="w-16 border border-[#00d4ff] bg-black px-1 py-0.5 text-right text-xs text-white"
        />
      ) : (
        display(value)
      )}
    </td>
  );
}

function ModelInputsPanel({
  scenario,
  algorithmScores,
  fromApi,
}: {
  scenario: UiScenario;
  algorithmScores: { name: string; score: number; status: string }[];
  fromApi: boolean;
}) {
  const pillars = [
    { k: "Awareness", v: scenario.pillarAllocation.awareness, c: "#00D4FF" },
    { k: "Consideration", v: scenario.pillarAllocation.consideration, c: "#8B5CF6" },
    { k: "Performance", v: scenario.pillarAllocation.performance, c: "#00FF88" },
  ];

  return (
    <div className="mb-4 rounded border border-[#1f1f1f] bg-[#111] p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="eyebrow">MODEL INPUTS</span>
        {fromApi && (
          <span className="rounded bg-[#00ff8822] px-1.5 text-[8px] text-[#00ff88]">API</span>
        )}
      </div>
      <div className="mb-3 flex flex-col gap-1.5">
        {pillars.map((p) => (
          <div key={p.k} className="flex items-center gap-2">
            <span className="w-24 shrink-0 text-[9px] text-[#777]">{p.k}</span>
            <div className="h-1.5 min-w-0 flex-1 bg-[#1a1a1a]">
              <div className="h-full" style={{ width: `${p.v}%`, background: p.c }} />
            </div>
            <span className="tnum w-8 shrink-0 text-right text-[9px] text-[#aaa]">{p.v}%</span>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-2 border-t border-[#1f1f1f] pt-2">
        {algorithmScores.slice(0, 4).map((a) => (
          <div
            key={a.name}
            className="flex min-w-[72px] flex-1 flex-col rounded border border-[#222] px-2 py-1"
          >
            <span className="truncate text-[8px] text-[#666]">{a.name}</span>
            <span className="tnum text-[11px] font-bold text-white">{a.score}</span>
          </div>
        ))}
      </div>
      <div className="mt-2 flex justify-between text-[9px] text-[#555]">
        <span>ROAS {scenario.roas.toFixed(1)}×</span>
        <span>Return {fmt(scenario.expectedReturn)}</span>
      </div>
    </div>
  );
}

export function BudgetScenarioPage() {
  const { data: apiScenarios, isSuccess: scenariosLoaded } = useBudgetScenarios();
  const { data: dashboard } = useTerminalData();
  const bidOptimize = useTriggerBidOptimize();

  const [scn, setScn] = useState<UiScenarioKey>("flexible");
  const [matrix, setMatrix] = useState<UiScenarioState>(() => fallbackUiScenarios());
  const [weights, setWeights] = useState({ awareness: 30, loyalty: 50, timeline: 6 });
  const [channelsOn, setChannelsOn] = useState<Record<string, boolean>>({});
  const [totalBudget, setTotalBudget] = useState(54000);
  const [allocating, setAllocating] = useState(false);
  const [pillarSumWarning, setPillarSumWarning] = useState<string | null>(null);
  const allocateTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const channelList = useMemo(() => allChannelsFromMatrix(matrix), [matrix]);
  const isFlexible = scn === "flexible";

  useEffect(() => {
    const scenarios = apiScenarios ?? dashboard?.budget_scenarios;
    if (!scenarios) return;

    const budget = dashboard?.header_stats.budget ?? 54000;
    setTotalBudget(budget);
    const channelMetrics = dashboard?.channel_metrics ?? [];
    const built = buildUiScenariosFromApi(scenarios, channelMetrics, budget);
    setMatrix(JSON.parse(JSON.stringify(built)) as UiScenarioState);
  }, [apiScenarios, dashboard?.budget_scenarios, dashboard?.channel_metrics, dashboard?.header_stats.budget]);

  useEffect(() => {
    const active = matrix[scn];
    setWeights((w) => ({
      ...w,
      awareness: active.pillarAllocation.awareness,
      loyalty: Math.round(
        active.pillarAllocation.consideration * 0.55 + active.pillarAllocation.performance * 0.45,
      ),
    }));
  }, [scn, matrix]);

  useEffect(() => {
    setChannelsOn((prev) => {
      const next = { ...prev };
      let changed = false;
      for (const c of channelList) {
        if (!(c in next)) {
          next[c] = true;
          changed = true;
        }
      }
      return changed ? next : prev;
    });
  }, [channelList]);

  const activeScenario = matrix[scn];
  const rows = activeScenario.matrix;
  const fromApi = scenariosLoaded || !!dashboard?.budget_scenarios;

  const pillarSplit = useMemo(
    () => pillarFromSliders(weights.awareness, weights.loyalty),
    [weights.awareness, weights.loyalty],
  );

  const runFlexibleAllocate = useCallback(
    async (channelWeights?: Record<string, number>) => {
      const sum = pillarSplit.awareness + pillarSplit.consideration + pillarSplit.performance;
      if (sum < 99 || sum > 101) {
        setPillarSumWarning(`Funnel pillars sum to ${sum}% — adjust sliders to ~100%`);
        return;
      }
      setPillarSumWarning(null);
      setAllocating(true);
      try {
        const res = await allocateBudgetFlexible({
          total_budget: totalBudget,
          awareness: pillarSplit.awareness,
          consideration: pillarSplit.consideration,
          performance: pillarSplit.performance,
          channel_weights: channelWeights,
        });
        setMatrix((m) =>
          applyFlexibleAllocation(
            m,
            res.channel_allocations,
            res.funnel_allocation,
            res.summary.overall_roas,
          ),
        );
        adtecLog([
          { msg: "Flexible allocation recalculated via ScenarioModelingEngine", tone: "ok" },
          ...res.recommendations.slice(0, 2).map((r) => ({ msg: r, tone: "info" as const })),
        ]);
      } catch (e) {
        adtecLog([
          {
            msg: e instanceof Error ? e.message.slice(0, 120) : "Flexible allocation failed",
            tone: "err",
          },
        ]);
      } finally {
        setAllocating(false);
      }
    },
    [pillarSplit, totalBudget],
  );

  useEffect(() => {
    if (!isFlexible) return;
    if (allocateTimer.current) clearTimeout(allocateTimer.current);
    allocateTimer.current = setTimeout(() => {
      void runFlexibleAllocate();
    }, 450);
    return () => {
      if (allocateTimer.current) clearTimeout(allocateTimer.current);
    };
  }, [isFlexible, weights.awareness, weights.loyalty, totalBudget, runFlexibleAllocate]);

  const setCell = (ci: number, key: keyof MatrixRow, v: number) => {
    setMatrix((m) => {
      const n = JSON.parse(JSON.stringify(m)) as UiScenarioState;
      const scenarioRows = n[scn].matrix.filter((r) => channelsOn[r.channel] !== false);

      if (isFlexible && key === "spend") {
        const row = n[scn].matrix[ci];
        const oldSpend = row.spend;
        const delta = v - oldSpend;
        const otherSpend = scenarioRows
          .filter((r) => r.channel !== row.channel)
          .reduce((s, r) => s + r.spend, 0);
        const maxOther = Math.max(0, totalBudget - v);
        if (otherSpend > 0 && delta !== 0) {
          const scale = maxOther / otherSpend;
          for (const r of n[scn].matrix) {
            if (r.channel !== row.channel && channelsOn[r.channel] !== false) {
              r.spend = Math.round(r.spend * scale);
              r.leads = r.cpl > 0 ? Math.round(r.spend / r.cpl) : r.leads;
            }
          }
        }
        row.spend = Math.round(v);
        row.leads = row.cpl > 0 ? Math.round(row.spend / row.cpl) : row.leads;

        const weights: Record<string, number> = {};
        for (const r of n[scn].matrix) {
          if (channelsOn[r.channel] !== false) {
            weights[channelKeyFromDisplay(r.channel)] = r.spend;
          }
        }
        void runFlexibleAllocate(weights);
        return n;
      }

      n[scn].matrix[ci][key] = v as never;
      const r = n[scn].matrix[ci];
      if (key === "spend" || key === "cpl") {
        r.leads = r.cpl > 0 ? Math.round(r.spend / r.cpl) : r.leads;
      }
      return n;
    });
  };

  const totals = useMemo(() => {
    const on = rows.filter((r) => channelsOn[r.channel] !== false);
    const spend = on.reduce((s, r) => s + r.spend, 0);
    const leads = on.reduce((s, r) => s + r.leads, 0);
    const budgetDelta = totalBudget - spend;
    return {
      spend,
      leads,
      cpl: leads ? spend / leads : 0,
      roas: activeScenario.roas + (isFlexible ? 0 : (weights.loyalty - 50) / 200),
      budgetDelta,
      atBudget: Math.abs(budgetDelta) < totalBudget * 0.02,
    };
  }, [rows, channelsOn, weights, activeScenario.roas, totalBudget, isFlexible]);

  const alloc = useMemo(() => {
    const on = rows.filter((r) => channelsOn[r.channel] !== false);
    const tot = on.reduce((s, r) => s + r.spend, 0) || 1;
    return on.map((r) => ({
      ch: r.channel,
      pct: (r.spend / tot) * 100,
      spend: r.spend,
      color: channelColor(r.channel),
    }));
  }, [rows, channelsOn]);

  const setChannelPct = useCallback(
    (channel: string, pct: number) => {
      const weights: Record<string, number> = {};
      for (const a of alloc) {
        weights[channelKeyFromDisplay(a.ch)] = a.ch === channel ? pct : a.pct;
      }
      void runFlexibleAllocate(weights);
    },
    [alloc, runFlexibleAllocate],
  );

  const handleBidOptimize = async () => {
    const topChannel = alloc[0]?.ch ?? "meta";
    try {
      const result = await bidOptimize.mutateAsync({
        keyword: "gymshark budget allocation",
        current_bid: totals.cpl,
        platform: topChannel.toLowerCase(),
      });
      adtecLog([
        {
          msg: result.success
            ? `Thompson bid optimizer applied to ${topChannel} · ${result.execution_time_ms}ms`
            : `Bid optimization failed: ${result.error ?? "unknown"}`,
          tone: result.success ? "ok" : "err",
        },
      ]);
    } catch {
      adtecLog([{ msg: "Bid optimization trigger failed — check API connection", tone: "err" }]);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex shrink-0 flex-wrap items-stretch gap-3 border-b border-[#1f1f1f] px-4 py-3.5">
        <div className="flex min-w-[280px] flex-1 flex-wrap gap-3">
          {(Object.entries(matrix) as [UiScenarioKey, UiScenario][]).map(([id, s]) => (
            <ScenarioTab
              key={id}
              id={id}
              s={s}
              active={scn === id}
              onClick={() => {
                setScn(id);
                adtecLog([
                  { msg: `Switching to the ${s.label.toLowerCase()} budget plan…`, tone: "work" },
                  {
                    msg: `Re-modelling spend and CPL from ${fromApi ? "terminal API" : "fallback"} models.`,
                    tone: "info",
                  },
                ]);
              }}
            />
          ))}
        </div>
        <div className="flex min-w-[240px] flex-col justify-center text-right">
          <div className="eyebrow">
            SCENARIO P&amp;L · {activeScenario.label}
            {fromApi && <span className="ml-2 text-[#00ff88]">· LIVE</span>}
            {isFlexible && allocating && (
              <span className="ml-2 text-[#00d4ff]">· ALLOCATING…</span>
            )}
          </div>
          <div className="mt-1 flex flex-wrap justify-end gap-x-4 gap-y-1">
            <PnL k="SPEND" v={fmt(totals.spend)} />
            <PnL k="LEADS" v={Math.round(totals.leads).toLocaleString()} c="#00D4FF" />
            <PnL k="BLENDED CPL" v={`£${totals.cpl.toFixed(2)}`} c="#00FF88" />
            <PnL k="ROAS" v={`${totals.roas.toFixed(1)}×`} c="#00FF88" />
            {isFlexible && (
              <PnL
                k="BUDGET Δ"
                v={totals.atBudget ? "ON TARGET" : fmt(totals.budgetDelta)}
                c={totals.atBudget ? "#00FF88" : "#FFB800"}
              />
            )}
          </div>
        </div>
      </div>

      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <div className="flex min-h-0 min-w-0 flex-1 flex-col border-b border-[#1f1f1f] lg:border-b-0 lg:border-r">
          <div className="min-h-0 flex-1 overflow-auto">
            <table className="w-full border-collapse font-mono text-xs">
              <thead>
                <tr className="sticky top-0 z-[2] bg-[#0a0a0a]">
                  {["CHANNEL", "AWARENESS %", "LOYALTY IDX", "EST. LEADS", "CPL", "SPEND"].map(
                    (h, i) => (
                      <th
                        key={h}
                        className="border-b border-[#1f1f1f] px-3 py-2 text-[9.5px] font-medium tracking-wide text-[#666]"
                        style={{ textAlign: i ? "right" : "left" }}
                      >
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {rows.map((r, ci) => (
                  <tr key={r.channel} style={{ opacity: channelsOn[r.channel] !== false ? 1 : 0.35 }}>
                    <td className="border-b border-[#141414] px-3 py-1.5">
                      <span className="inline-flex items-center gap-2">
                        <span
                          className="h-2 w-2 shrink-0"
                          style={{ background: channelColor(r.channel) }}
                        />
                        {r.channel}
                      </span>
                    </td>
                    <EditCell
                      value={r.awareness}
                      display={(v) => `${v}%`}
                      onChange={(v) => setCell(ci, "awareness", v)}
                    />
                    <EditCell
                      value={r.loyalty}
                      display={(v) => String(v)}
                      onChange={(v) => setCell(ci, "loyalty", v)}
                    />
                    <td className="tnum border-b border-[#141414] px-3 py-1.5 text-right text-[#00d4ff]">
                      {r.leads.toLocaleString()}
                    </td>
                    <EditCell
                      value={r.cpl}
                      display={(v) => `£${(+v).toFixed(2)}`}
                      onChange={(v) => setCell(ci, "cpl", v)}
                      color="#00FF88"
                    />
                    <EditCell value={r.spend} display={fmt} onChange={(v) => setCell(ci, "spend", v)} />
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="px-3 py-2 text-[9.5px] text-[#444]">
              {isFlexible ? (
                <>
                  ↳ <span className="text-[#00D4FF]">FLEXIBLE</span> — edit spend/CPL freely; other
                  channels rebalance to £{totalBudget.toLocaleString()} · POST{" "}
                  <span className="text-[#00FF88]">/terminal/budget-allocate</span>
                </>
              ) : (
                <>
                  ↳ Click any cell to edit · seeded from{" "}
                  <span className="text-[#00FF88]">/terminal/budget-scenarios</span>
                </>
              )}
            </div>
          </div>
          <div className="shrink-0 border-t border-[#1f1f1f] bg-[#0b0b0b] p-4">
            <div className="mb-2 flex items-center justify-between">
              <div className="eyebrow">
                PLATFORM ALLOCATION · {fmt(totals.spend)} / {fmt(totalBudget)}
              </div>
              {isFlexible && (
                <label className="flex items-center gap-1.5 text-[9px] text-[#888]">
                  TOTAL
                  <input
                    type="number"
                    value={totalBudget}
                    onChange={(e) => setTotalBudget(Math.max(1000, +e.target.value || 0))}
                    className="w-20 border border-[#333] bg-black px-1 py-0.5 text-right text-[10px] text-white"
                  />
                </label>
              )}
            </div>
            <div className="flex h-6 overflow-hidden rounded-sm border border-[#1a1a1a]">
              {alloc.map((a) => (
                <div
                  key={a.ch}
                  title={`${a.ch} ${a.pct.toFixed(0)}%`}
                  className="flex items-center justify-center overflow-hidden transition-[width] duration-300"
                  style={{ width: `${a.pct}%`, background: a.color }}
                >
                  {a.pct > 9 && (
                    <span className="text-[9px] font-medium text-white">{a.pct.toFixed(0)}%</span>
                  )}
                </div>
              ))}
            </div>
            <div className="mt-2 flex flex-wrap gap-x-3.5 gap-y-1">
              {alloc.map((a) => (
                <div key={a.ch} className="flex items-center gap-1.5">
                  <span className="h-2 w-2 shrink-0" style={{ background: a.color }} />
                  <span className="text-[9.5px] text-[#999]">{a.ch}</span>
                  {isFlexible ? (
                    <PctInput
                      pct={a.pct}
                      onCommit={(pct) => setChannelPct(a.ch, pct)}
                    />
                  ) : (
                    <span className="tnum text-[9.5px] text-[#666]">{a.pct.toFixed(0)}%</span>
                  )}
                  <span className="tnum text-[9.5px] text-[#666]">{fmt(a.spend)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex w-full shrink-0 flex-col overflow-y-auto bg-[#0d0d0d] p-4 lg:w-[280px]">
          <ModelInputsPanel
            scenario={activeScenario}
            algorithmScores={dashboard?.algorithm_scores ?? []}
            fromApi={fromApi}
          />

          <button
            type="button"
            onClick={handleBidOptimize}
            disabled={bidOptimize.isPending}
            className="mb-4 flex w-full items-center justify-center gap-2 rounded border border-[#00ff88] bg-[#00ff8815] px-3 py-2 text-[10px] font-medium uppercase tracking-wide text-[#00ff88] transition-colors hover:bg-[#00ff8825] disabled:opacity-50"
          >
            {bidOptimize.isPending ? "Optimizing…" : "Run Thompson Bid Optimize"}
          </button>

          <div className="eyebrow mb-3.5">
            {isFlexible ? "FLEXIBLE FUNNEL CONTROLS" : "FINE-TUNE CONTROLS"}
          </div>
          {isFlexible && pillarSplit && (
            <div className="mb-3 rounded border border-[#00d4ff33] bg-[#00d4ff08] px-2 py-1.5 text-[9px] text-[#aaa]">
              Pillars: {pillarSplit.awareness}% / {pillarSplit.consideration}% /{" "}
              {pillarSplit.performance}%
              {pillarSumWarning && (
                <span className="mt-1 block text-[#ffb800]">{pillarSumWarning}</span>
              )}
            </div>
          )}
          <Slider
            label="Brand Awareness Weight"
            v={weights.awareness}
            min={0}
            max={100}
            suffix="%"
            onChange={(v) => setWeights((w) => ({ ...w, awareness: v }))}
          />
          <Slider
            label="Loyalty ↔ Acquisition"
            v={weights.loyalty}
            min={0}
            max={100}
            left="LOYALTY"
            right="ACQUIRE"
            onChange={(v) => setWeights((w) => ({ ...w, loyalty: v }))}
          />
          <Slider
            label="Timeline Aggressiveness"
            v={weights.timeline}
            min={3}
            max={12}
            suffix="mo"
            onChange={(v) => setWeights((w) => ({ ...w, timeline: v }))}
          />
          <div className="eyebrow mb-2 mt-2">CHANNELS ACTIVE</div>
          {channelList.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setChannelsOn((o) => ({ ...o, [c]: !o[c] }))}
              className="flex w-full items-center gap-2.5 py-1.5"
            >
              <span
                className="h-2 w-2 shrink-0"
                style={{ background: channelColor(c), opacity: channelsOn[c] !== false ? 1 : 0.3 }}
              />
              <span
                className={`flex-1 text-left text-[11px] ${channelsOn[c] !== false ? "text-[#ddd]" : "text-[#555]"}`}
              >
                {c}
              </span>
              <Toggle on={channelsOn[c] !== false} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function PnL({ k, v, c }: { k: string; v: string; c?: string }) {
  return (
    <div className="shrink-0">
      <div className="text-[9px] text-[#666]">{k}</div>
      <div className="tnum font-display text-lg font-bold" style={{ color: c || "#fff" }}>
        {v}
      </div>
    </div>
  );
}

function Slider({
  label,
  v,
  min,
  max,
  suffix,
  left,
  right,
  onChange,
}: {
  label: string;
  v: number;
  min: number;
  max: number;
  suffix?: string;
  left?: string;
  right?: string;
  onChange: (v: number) => void;
}) {
  return (
    <div className="mb-4">
      <div className="mb-1.5 flex justify-between text-[10.5px]">
        <span className="text-[#aaa]">{label}</span>
        <span className="tnum text-[#00d4ff]">
          {v}
          {suffix || ""}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={v}
        onChange={(e) => onChange(+e.target.value)}
        className="h-1 w-full accent-[#00d4ff]"
      />
      {(left || right) && (
        <div className="mt-0.5 flex justify-between text-[8.5px] text-[#555]">
          <span>{left}</span>
          <span>{right}</span>
        </div>
      )}
    </div>
  );
}

function PctInput({ pct, onCommit }: { pct: number; onCommit: (pct: number) => void }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const commit = () => {
    setEditing(false);
    const n = parseFloat(draft.replace(/[^0-9.]/g, ""));
    if (!isNaN(n) && n >= 0) onCommit(n);
  };
  if (editing) {
    return (
      <input
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => e.key === "Enter" && commit()}
        className="w-10 border border-[#00d4ff] bg-black px-0.5 text-right text-[9px] text-white"
      />
    );
  }
  return (
    <button
      type="button"
      onClick={() => {
        setDraft(String(Math.round(pct)));
        setEditing(true);
      }}
      className="tnum text-[9.5px] text-[#00d4ff] hover:underline"
    >
      {pct.toFixed(0)}%
    </button>
  );
}

function Toggle({ on }: { on: boolean }) {
  return (
    <span
      className="relative h-4 w-[30px] shrink-0 rounded-full border transition-colors"
      style={{
        background: on ? "#00FF8833" : "#1A1A1A",
        borderColor: on ? "#00FF88" : "#333",
      }}
    >
      <span
        className="absolute top-px h-3 w-3 rounded-full transition-[left]"
        style={{ left: on ? 15 : 1, background: on ? "#00FF88" : "#555" }}
      />
    </span>
  );
}
