import { useEffect, useState } from "react";
import { pages as PAGE_LIST, type PageId } from "../../data/adtec";
import type { HeaderStats } from "../../types/terminal";
import { ConnectorsBar } from "./ConnectorsBar";

function Clock() {
  const [t, setT] = useState("");
  useEffect(() => {
    const tick = () => {
      const d = new Date();
      const p = (n: number) => String(n).padStart(2, "0");
      setT(`${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())} GMT`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="tnum text-[11px] text-[#888]">{t}</span>;
}

interface HeaderProps {
  stats?: HeaderStats;
  pages: typeof PAGE_LIST;
  active: PageId;
  onNavigate: (id: PageId) => void;
}

export function Header({ stats, pages: navPages, active, onNavigate }: HeaderProps) {
  return (
    <header className="relative z-40 shrink-0 border-b border-[#1f1f1f] bg-[#080808]">
      <div className="flex h-[52px] items-center px-4">
        <div className="flex shrink-0 items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-[#00ff88] shadow-[0_0_8px_rgba(0,255,136,0.7)]" />
          <span className="font-display text-xl font-bold tracking-wide text-white">SIGNAL</span>
          <span className="mt-0.5 hidden text-[9px] tracking-[0.14em] text-[#555] sm:inline">
            AD TECH INTELLIGENCE
          </span>
        </div>

        <nav className="ml-4 flex min-w-0 flex-1 overflow-x-auto">
          {navPages.map((p) => {
            const on = active === p.id;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => onNavigate(p.id)}
                className="flex h-[52px] shrink-0 items-baseline gap-1.5 border-0 border-b-2 bg-transparent px-2 sm:gap-2 sm:px-3"
                style={{ borderBottomColor: on ? "#00D4FF" : "transparent" }}
              >
                <span
                  className="tnum text-[10px]"
                  style={{ color: on ? "#00D4FF" : "#555" }}
                >
                  {p.n}
                </span>
                <span
                  className="hidden text-[11px] uppercase tracking-wide sm:inline"
                  style={{ color: on ? "#fff" : "#777" }}
                >
                  {p.title}
                </span>
              </button>
            );
          })}
        </nav>

        {stats && (
          <div className="ml-4 hidden items-center gap-4 lg:flex">
            <MiniStat label="ROAS" value={stats.roas.toFixed(2)} accent />
            <MiniStat label="Leads" value={stats.leads.toLocaleString()} />
          </div>
        )}

        <div className="ml-auto flex shrink-0 items-center gap-3">
          <span className="hidden items-center gap-1.5 rounded border border-[#2a2a2a] bg-[#111] px-2 py-0.5 md:flex">
            <span className="text-[9px] tracking-widest text-[#666]">CLIENT</span>
            <span className="font-display text-xs font-semibold text-white">GYMSHARK</span>
          </span>
          <span className="inline-flex items-center gap-1.5 rounded bg-[rgba(0,255,136,0.1)] px-2 py-0.5 text-[10px] text-[#00ff88]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#00ff88]" />
            LIVE
          </span>
          <Clock />
        </div>
      </div>

      <ConnectorsBar />
    </header>
  );
}

function MiniStat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div>
      <div className="text-[8px] tracking-widest text-[#555]">{label}</div>
      <div
        className={`tnum font-display text-xs font-semibold ${accent ? "text-[#00bfff]" : "text-white"}`}
      >
        {value}
      </div>
    </div>
  );
}
