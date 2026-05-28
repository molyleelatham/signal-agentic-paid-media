import { useCallback, useEffect, useRef, useState } from "react";
import { traceScripts, type PageId } from "../../data/adtec";
import type { TraceLine, TraceTone } from "../../data/adtec";

const TONE: Record<TraceTone, string> = {
  work: "#00D4FF",
  ok: "#00FF88",
  info: "#CFCFCF",
  warn: "#FFB800",
  err: "#FF4444",
};

function ts() {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

interface LogLine extends TraceLine {
  id: number;
  ts: string;
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
  const [lines, setLines] = useState<LogLine[]>(() => {
    let i = 0;
    return traceScripts.boot.map((l) => ({ ...l, id: i++, ts: ts() }));
  });
  const bodyRef = useRef<HTMLDivElement>(null);
  const idRef = useRef(100);

  const push = useCallback((batch: TraceLine[]) => {
    setLines((prev) => {
      const add = batch.map((l) => ({ ...l, id: idRef.current++, ts: ts() }));
      return [...prev, ...add].slice(-80);
    });
  }, []);

  useEffect(() => {
    const onLog = (e: Event) => push((e as CustomEvent<TraceLine[]>).detail || []);
    window.addEventListener("adtec:log", onLog);
    return () => window.removeEventListener("adtec:log", onLog);
  }, [push]);

  useEffect(() => {
    if (open && bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [lines, open]);

  const run = useCallback(() => {
    push(traceScripts[activePage] || []);
  }, [activePage, push]);

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
        <div className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-[#00ff88]" />
          <span className="text-[11px] tracking-[0.16em] text-[#888]">OVERMIND TRACE</span>
          <span className="ml-1 text-[10px] text-[#444]">· {lines.length} events</span>
        </div>
        <div className="flex items-center gap-1.5">
          {open && (
            <>
              <TermBtn onClick={run} className="text-[#00d4ff] border-[#0c4a52]">
                ▶ RUN
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
          {lines.map((l) => (
            <div key={l.id} className="mb-0.5 flex items-baseline gap-2.5">
              <span className="tnum shrink-0 text-[#4a4a4a]">{l.ts}</span>
              <span className="shrink-0 text-[9px]" style={{ color: TONE[l.tone] }}>
                {l.tone === "work" ? "›" : "•"}
              </span>
              <span className={l.tone === "work" ? "text-[#9a9a9a]" : "text-[#e2e2e2]"}>
                {l.msg}
              </span>
            </div>
          ))}
          {lines.length === 0 && (
            <div className="text-[11px] text-[#444]">
              Cleared. Navigate pages or press RUN.
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
