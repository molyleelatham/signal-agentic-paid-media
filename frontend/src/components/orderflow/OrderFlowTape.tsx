import type { OrderFlowTapeEntry } from "../../hooks/useLiveOrderFlow";

export function OrderFlowTape({ entries }: { entries: OrderFlowTapeEntry[] }) {
  return (
    <div className="shrink-0 border-t border-[#1f1f1f] bg-[#0a0a0a]">
      <div className="flex items-center justify-between px-2 py-1">
        <span className="text-[8px] tracking-[0.18em] text-[#555]">LIVE TAPE</span>
        <span className="text-[8px] text-[#444]">{entries.length} ticks</span>
      </div>
      <div className="orderflow-tape max-h-[88px] overflow-hidden px-1 pb-1.5">
        <ul className="flex flex-col gap-0.5">
          {entries.map((e, i) => (
            <li
              key={e.id}
              className={`orderflow-tape-row flex min-w-0 items-center gap-1.5 rounded px-1.5 py-0.5 text-[9px] ${
                e.side === "up" ? "orderflow-tick-up" : "orderflow-tick-down"
              }`}
              style={{ animationDelay: i === 0 ? "0ms" : undefined }}
            >
              <span className="tnum shrink-0 text-[#444]">{e.ts}</span>
              <span
                className={`shrink-0 font-bold ${e.side === "up" ? "text-[#00ff88]" : "text-[#ff4444]"}`}
              >
                {e.side === "up" ? "▲" : "▼"}
              </span>
              <span className="min-w-0 flex-1 truncate font-medium text-[#bbb]">{e.channel}</span>
              <span className="shrink-0 text-[#666]">{e.label}</span>
              <span className="tnum shrink-0 font-semibold text-white">{e.value}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
