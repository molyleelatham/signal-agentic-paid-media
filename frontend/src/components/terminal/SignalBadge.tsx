import type { Signal } from "../../types/terminal";

const CONFIG: Record<
  Signal,
  { icon: string; className: string; label: string }
> = {
  BUY: { icon: "⚡", className: "signal-buy", label: "BUY" },
  HOLD: { icon: "⏸", className: "signal-hold", label: "HOLD" },
  STOP: { icon: "🛑", className: "signal-stop", label: "STOP" },
};

export function SignalBadge({
  signal,
  compact = false,
}: {
  signal: Signal;
  compact?: boolean;
}) {
  const c = CONFIG[signal];
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-0.5 font-semibold tracking-wider ${compact ? "text-[10px]" : "gap-1 text-xs"} ${c.className}`}
    >
      <span>{c.icon}</span>
      {c.label}
    </span>
  );
}
