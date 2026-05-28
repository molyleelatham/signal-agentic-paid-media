import { useCallback, useEffect, useRef, useState } from "react";
import type { PageId } from "../../data/adtec";
import type { TraceLine, TraceTone } from "../../data/adtec";
import { agentLogsToTrace, fetchAgentLogs } from "../../api/agentLogs";
import { getSectionThreadLogs, randomStreamLog } from "../../lib/mockAgentLogs";

const TONE: Record<TraceTone, string> = {
  work: "#00D4FF",
  ok: "#00FF88",
  info: "#CFCFCF",
  warn: "#FFB800",
  err: "#FF4444",
};

const SECTION_LABEL: Record<PageId, string> = {
  intel: "§01 Market Intel",
  strategy: "§02 Strategy",
  budget: "§03 Budget",
  perf: "§04 Performance",
  terminal: "§05 SIGNAL",
};

function ts() {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

interface LogLine extends TraceLine {
  id: number;
  ts: string;
  isNew?: boolean;
}

export function OvermindTerminal({
  activePage,
  defaultOpen = true,
  heightPct = 18,
}: {
  activePage: PageId;
  defaultOpen?: boolean;
  heightPct?: number;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const [lines, setLines] = useState<LogLine[]>([]);
  const [loading, setLoading] = useState(true);
  const bodyRef = useRef<HTMLDivElement>(null);
  const idRef = useRef(0);

  const push = useCallback((batch: TraceLine[], markNew = false) => {
    if (!batch.length) return;
    setLines((prev) => {
      const add = batch.map((l) => ({
        ...l,
        id: idRef.current++,
        ts: ts(),
        isNew: markNew,
      }));
      return [...prev, ...add].slice(-80);
    });
  }, []);

  const refreshFromApi = useCallback(async () => {
    setLoading(true);
    try {
      const logs = await fetchAgentLogs(40);
      const sectionLogs = getSectionThreadLogs(activePage).slice(0, 4);
      const merged = [...sectionLogs, ...logs].slice(0, 40);
      const traced = agentLogsToTrace(merged).map((l) => ({
        ...l,
        id: idRef.current++,
        ts: ts(),
      }));
      setLines([
        {
          id: idRef.current++,
          ts: ts(),
          msg: `Thread context → ${SECTION_LABEL[activePage]}`,
          tone: "work" as const,
        },
        ...traced,
      ]);
    } catch (e) {
      push([
        {
          msg: e instanceof Error ? e.message : "Failed to load agent logs",
          tone: "err",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [activePage, push]);

  useEffect(() => {
    void refreshFromApi();
  }, [refreshFromApi]);

  useEffect(() => {
    const interval = setInterval(() => {
      const entry = randomStreamLog(activePage);
      push(agentLogsToTrace([entry]), true);
    }, 4500 + Math.random() * 2500);
    return () => clearInterval(interval);
  }, [activePage, push]);

  useEffect(() => {
    const onLog = (e: Event) => push((e as CustomEvent<TraceLine[]>).detail || [], true);
    window.addEventListener("adtec:log", onLog);
    return () => window.removeEventListener("adtec:log", onLog);
  }, [push]);

  useEffect(() => {
    if (open && bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [lines, open]);

  useEffect(() => {
    if (!lines.some((l) => l.isNew)) return;
    const t = setTimeout(() => {
      setLines((prev) => prev.map((l) => ({ ...l, isNew: false })));
    }, 800);
    return () => clearTimeout(t);
  }, [lines]);

  const copy = useCallback(() => {
    const txt = lines.map((l) => `[${l.ts}]  ${l.msg}`).join("\n");
    void navigator.clipboard?.writeText(txt);
  }, [lines]);

  return (
    <div
      className="relative z-[60] flex w-full shrink-0 flex-col border-t border-[#1f1f1f] bg-[#0a0a0a] font-mono transition-[height] duration-200"
      style={{ height: open ? `${heightPct}vh` : 34 }}
    >
      <div
        className={`flex h-[34px] shrink-0 select-none items-center justify-between px-3.5 ${open ? "border-b border-[#1f1f1f]" : ""}`}
      >
        <div className="flex min-w-0 items-center gap-2">
          <span className="orderflow-live-dot h-1.5 w-1.5 rounded-full bg-[#00ff88]" />
          <span className="text-[11px] tracking-[0.16em] text-[#888]">OVERMIND TRACE</span>
          <span className="truncate text-[10px] text-[#444]">
            · {SECTION_LABEL[activePage]} · {lines.length} events
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          {open && (
            <>
              <TermBtn onClick={() => void refreshFromApi()} className="text-[#00d4ff] border-[#0c4a52]">
                {loading ? "…" : "↻ REFRESH"}
              </TermBtn>
              <TermBtn onClick={() => setLines([])}>CLEAR</TermBtn>
              <TermBtn onClick={copy}>COPY</TermBtn>
            </>
          )}
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="h-6 w-6 rounded-full border border-[#444] bg-[#1a1a1a] text-[10px] text-[#888]"
            aria-label="toggle terminal"
          >
            {open ? "▼" : "▲"}
          </button>
        </div>
      </div>
      {open && (
        <div ref={bodyRef} className="flex-1 overflow-y-auto px-3.5 py-2 text-[12px] leading-relaxed">
          {loading && lines.length === 0 && (
            <div className="text-[11px] text-[#555]">Loading agent thread from /terminal/agent-logs…</div>
          )}
          {lines.map((l) => (
            <div
              key={l.id}
              className={`mb-0.5 flex items-baseline gap-2.5 ${l.isNew ? "trace-line-new" : ""}`}
            >
              <span className="tnum shrink-0 text-[#4a4a4a]">{l.ts}</span>
              <span className="shrink-0 text-[9px]" style={{ color: TONE[l.tone] }}>
                {l.tone === "work" ? "›" : "•"}
              </span>
              <span className={l.tone === "work" ? "text-[#9a9a9a]" : "text-[#e2e2e2]"}>
                {l.msg}
              </span>
            </div>
          ))}
          {!loading && lines.length === 0 && (
            <div className="text-[11px] text-[#444]">
              No events. Trigger Tavily Research or an agent — logs stream here.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TermBtn({
  children,
  onClick,
  className = "",
}: {
  children: React.ReactNode;
  onClick: () => void;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-sm border border-[#2a2a2a] bg-transparent px-2 py-1 text-[9px] tracking-widest text-[#777] hover:text-white ${className}`}
    >
      {children}
    </button>
  );
}
