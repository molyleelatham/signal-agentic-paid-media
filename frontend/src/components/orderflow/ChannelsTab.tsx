import type { LiveChannelMetric } from "../../hooks/useLiveOrderFlow";
import { TrendIndicator } from "./TrendIndicator";

const CHANNEL_COLORS: Record<string, string> = {
  META: "#1877F2",
  GOOGLE: "#4285F4",
  TIKTOK: "#FF0050",
  MICROSOFT: "#00A4EF",
  INSTAGRAM: "#E1306C",
  REDDIT: "#FF4500",
  OOH: "#00FF88",
};

export function ChannelsTab({ channels }: { channels: LiveChannelMetric[] }) {
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <div className="grid shrink-0 grid-cols-[minmax(0,1fr)_auto] gap-x-2 gap-y-0.5 border-b border-[#1f1f1f] px-2 py-1.5 text-[8px] tracking-widest text-[#555]">
        <span>CHANNEL</span>
        <span className="text-right">METRICS</span>
      </div>
      <ul className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden">
        {channels.map((ch) => (
          <li
            key={`${ch.name}-${ch.tickKey}`}
            className={`min-w-0 border-b border-[#1f1f1f]/80 px-2 py-2 transition-colors hover:bg-[#222] ${
              ch.tick === "up"
                ? "orderflow-row-up"
                : ch.tick === "down"
                  ? "orderflow-row-down"
                  : ""
            }`}
          >
            <div className="flex min-w-0 items-center gap-1.5">
              <span
                className="h-2 w-2 shrink-0 rounded-sm"
                style={{ background: CHANNEL_COLORS[ch.name] ?? "#888" }}
              />
              <span className="min-w-0 flex-1 truncate font-display text-[11px] font-semibold text-white">
                {ch.name}
              </span>
              <TrendIndicator trend={ch.trend} tick={ch.tick} compact />
            </div>
            <div className="mt-1 flex min-w-0 items-center justify-between gap-2 pl-3.5 text-[10px]">
              <span className="tnum shrink-0 text-[#ccc]">
                £{(ch.spend / 1000).toFixed(1)}K
              </span>
              <span className="tnum shrink-0 text-[#888]">CPA £{ch.cpa.toFixed(2)}</span>
            </div>
          </li>
        ))}
      </ul>
      <div className="shrink-0 truncate border-t border-[#1f1f1f] px-2 py-1.5 text-[9px] text-[#555]">
        <span className="text-[#00ff88]">{channels.filter((c) => c.trend === "up").length} ▲</span>
        {" · "}
        <span className="text-[#ff4444]">{channels.filter((c) => c.trend === "down").length} ▼</span>
        {" · live"}
      </div>
    </div>
  );
}
