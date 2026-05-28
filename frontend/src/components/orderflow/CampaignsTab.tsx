import type { CampaignSignal } from "../../types/terminal";
import { SignalBadge } from "../terminal/SignalBadge";

export function CampaignsTab({ campaigns }: { campaigns: CampaignSignal[] }) {
  const sorted = [...campaigns].sort((a, b) => {
    const order = { BUY: 0, HOLD: 1, STOP: 2 };
    return order[a.signal] - order[b.signal];
  });

  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <div className="shrink-0 truncate px-2 py-1.5 text-[8px] tracking-widest text-[#555]">
        SIGNAL · live allocation
      </div>
      <ul className="min-h-0 min-w-0 flex-1 space-y-1.5 overflow-y-auto overflow-x-hidden px-1.5 pb-2">
        {sorted.map((c) => (
          <li
            key={c.name}
            className="min-w-0 overflow-hidden rounded border border-[#2a2a2a] bg-[#1a1a1a] p-2"
          >
            <div className="mb-1.5 flex min-w-0 items-start justify-between gap-1">
              <SignalBadge signal={c.signal} compact />
              <span className="shrink-0 rounded bg-[#333] px-1 py-0.5 text-[8px] text-[#00bfff]">
                SIG
              </span>
            </div>
            <h4
              className="line-clamp-2 break-words font-display text-[11px] font-medium leading-snug text-white"
              title={c.name}
            >
              {c.name}
            </h4>
            <div className="mt-1.5 grid min-w-0 grid-cols-3 gap-0.5 text-center">
              <MiniStat label="Conf" value={`${c.confidence}%`} />
              <MiniStat label="Spend" value={`£${(c.spend / 1000).toFixed(1)}K`} />
              <MiniStat label="ROAS" value={`${c.roas}×`} highlight />
            </div>
            <div className="mt-1.5 h-1 overflow-hidden rounded bg-[#333]">
              <div
                className={`h-full max-w-full ${
                  c.signal === "BUY"
                    ? "bg-[#00ff00]"
                    : c.signal === "HOLD"
                      ? "bg-[#ffff00]"
                      : "bg-[#ff0000]"
                }`}
                style={{ width: `${Math.min(100, c.confidence)}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function MiniStat({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="min-w-0 overflow-hidden">
      <div className="truncate text-[7px] tracking-wider text-[#555]">{label}</div>
      <div
        className={`tnum truncate text-[10px] font-medium ${highlight ? "text-[#00bfff]" : "text-[#ccc]"}`}
      >
        {value}
      </div>
    </div>
  );
}
