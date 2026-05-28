import { useMemo, useState } from "react";
import { channels, platformColors, scenarios } from "../data/adtec";
import { adtecLog } from "../lib/trace";

const fmt = (n: number) => "£" + Math.round(n).toLocaleString();

type MatrixRow = {
  channel: string;
  awareness: number;
  loyalty: number;
  leads: number;
  cpl: number;
  spend: number;
};

type ScenarioState = typeof scenarios;

function ScenarioTab({
  s,
  id,
  active,
  onClick,
}: {
  s: (typeof scenarios)[keyof typeof scenarios];
  id: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex h-[74px] w-[200px] flex-col justify-center rounded-sm px-4 text-left transition-all"
      style={{
        background: s.bg,
        border: `1px solid ${active ? "#fff" : s.border}`,
        boxShadow: active ? "0 0 0 1px #fff, 0 8px 22px rgba(0,0,0,.5)" : undefined,
      }}
    >
      <div className="mb-1 flex items-center gap-1.5">
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{
            background:
              id === "conservative" ? "#888" : id === "optimistic" ? "#00FF88" : "#FF4444",
          }}
        />
        <span
          className={`font-display text-lg font-bold ${active ? "text-white" : "text-[#ccc]"}`}
        >
          {s.label}
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

export function BudgetScenarioPage() {
  const [scn, setScn] = useState<keyof ScenarioState>("optimistic");
  const [matrix, setMatrix] = useState(() =>
    JSON.parse(JSON.stringify(scenarios)) as ScenarioState,
  );
  const [weights, setWeights] = useState({ awareness: 60, loyalty: 50, timeline: 6 });
  const [channelsOn, setChannelsOn] = useState(() =>
    Object.fromEntries(channels.map((c) => [c, true])),
  );

  const rows = matrix[scn].matrix as MatrixRow[];
  const setCell = (ci: number, key: keyof MatrixRow, v: number) => {
    setMatrix((m) => {
      const n = JSON.parse(JSON.stringify(m)) as ScenarioState;
      (n[scn].matrix[ci] as MatrixRow)[key] = v as never;
      const r = n[scn].matrix[ci] as MatrixRow;
      if (key === "spend" || key === "cpl") {
        r.leads = r.cpl > 0 ? Math.round(r.spend / r.cpl) : r.leads;
      }
      return n;
    });
  };

  const totals = useMemo(() => {
    const on = rows.filter((r) => channelsOn[r.channel]);
    const spend = on.reduce((s, r) => s + r.spend, 0);
    const leads = on.reduce((s, r) => s + r.leads, 0);
    return {
      spend,
      leads,
      cpl: leads ? spend / leads : 0,
      roas: 4.0 + (weights.loyalty - 50) / 120,
    };
  }, [rows, channelsOn, weights]);

  const alloc = useMemo(() => {
    const on = rows.filter((r) => channelsOn[r.channel]);
    const tot = on.reduce((s, r) => s + r.spend, 0) || 1;
    return on.map((r) => ({
      ch: r.channel,
      pct: (r.spend / tot) * 100,
      spend: r.spend,
      color: platformColors[r.channel],
    }));
  }, [rows, channelsOn]);

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex shrink-0 flex-wrap items-center gap-3 border-b border-[#1f1f1f] px-4 py-3.5">
        {(Object.entries(scenarios) as [keyof ScenarioState, (typeof scenarios)[keyof typeof scenarios]][]).map(
          ([id, s]) => (
            <ScenarioTab
              key={id}
              id={id}
              s={s}
              active={scn === id}
              onClick={() => {
                setScn(id);
                adtecLog([
                  { msg: `Switching to the ${s.label.toLowerCase()} budget plan…`, tone: "work" },
                  { msg: `Re-modelling spend and CPL for ${s.label.toLowerCase()} reach.`, tone: "info" },
                ]);
              }}
            />
          ),
        )}
        <div className="ml-auto text-right">
          <div className="eyebrow">SCENARIO P&amp;L · {matrix[scn].label}</div>
          <div className="mt-1 flex gap-4">
            <PnL k="SPEND" v={fmt(totals.spend)} />
            <PnL k="LEADS" v={Math.round(totals.leads).toLocaleString()} c="#00D4FF" />
            <PnL k="BLENDED CPL" v={`£${totals.cpl.toFixed(2)}`} c="#00FF88" />
            <PnL k="ROAS" v={`${totals.roas.toFixed(1)}×`} c="#00FF88" />
          </div>
        </div>
      </div>

      <div className="flex min-h-0 flex-1">
        <div className="flex min-w-0 flex-1 flex-col border-r border-[#1f1f1f]">
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
                  <tr key={r.channel} style={{ opacity: channelsOn[r.channel] ? 1 : 0.35 }}>
                    <td className="border-b border-[#141414] px-3 py-1.5">
                      <span className="inline-flex items-center gap-2">
                        <span
                          className="h-2 w-2"
                          style={{ background: platformColors[r.channel] }}
                        />
                        {r.channel}
                      </span>
                    </td>
                    <EditCell
                      value={r.awareness}
                      display={(v) => `${v}%`}
                      onChange={(v) => setCell(ci, "awareness", v)}
                    />
                    <EditCell value={r.loyalty} display={(v) => String(v)} onChange={(v) => setCell(ci, "loyalty", v)} />
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
          </div>
          <div className="shrink-0 border-t border-[#1f1f1f] bg-[#0b0b0b] p-4">
            <div className="eyebrow mb-2">PLATFORM ALLOCATION · {fmt(totals.spend)} TOTAL</div>
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
          </div>
        </div>

        <div className="w-[260px] shrink-0 overflow-y-auto bg-[#0d0d0d] p-4">
          <div className="eyebrow mb-3.5">FINE-TUNE CONTROLS</div>
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
          <div className="eyebrow mb-2 mt-4">CHANNELS ACTIVE</div>
          {channels.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setChannelsOn((o) => ({ ...o, [c]: !o[c] }))}
              className="flex w-full items-center gap-2.5 py-1.5"
            >
              <span
                className="h-2 w-2"
                style={{ background: platformColors[c], opacity: channelsOn[c] ? 1 : 0.3 }}
              />
              <span className={`flex-1 text-left text-[11px] ${channelsOn[c] ? "text-[#ddd]" : "text-[#555]"}`}>
                {c}
              </span>
              <Toggle on={channelsOn[c]} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function PnL({ k, v, c }: { k: string; v: string; c?: string }) {
  return (
    <div>
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
