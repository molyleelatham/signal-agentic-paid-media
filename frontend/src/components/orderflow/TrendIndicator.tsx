import type { Trend } from "../../types/terminal";

export function TrendIndicator({
  trend,
  compact = false,
}: {
  trend: Trend;
  compact?: boolean;
}) {
  const up = trend === "up";
  return (
    <span
      className={`inline-flex shrink-0 items-center rounded px-1 py-0.5 font-semibold tnum ${
        compact ? "text-[9px]" : "gap-0.5 text-[10px]"
      } ${
        up
          ? "bg-[rgba(0,255,0,0.12)] text-[#00ff00]"
          : "bg-[rgba(255,0,0,0.12)] text-[#ff0000]"
      }`}
      title={up ? "Flow up" : "Flow down"}
    >
      {up ? "▲" : "▼"}
      {!compact && (up ? " UP" : " DN")}
    </span>
  );
}
