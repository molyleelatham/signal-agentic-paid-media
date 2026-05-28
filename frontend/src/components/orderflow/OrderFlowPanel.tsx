import { useState } from "react";
import type { CampaignSignal, ChannelMetric } from "../../types/terminal";
import { CampaignsTab } from "./CampaignsTab";
import { ChannelsTab } from "./ChannelsTab";

type Tab = "channels" | "campaigns";

interface OrderFlowPanelProps {
  channels: ChannelMetric[];
  campaigns: CampaignSignal[];
  className?: string;
}

export function OrderFlowPanel({ channels, campaigns, className = "" }: OrderFlowPanelProps) {
  const [tab, setTab] = useState<Tab>("channels");
  const [collapsed, setCollapsed] = useState(false);

  if (collapsed) {
    return (
      <aside
        className={`flex min-h-0 w-9 shrink-0 flex-col items-center border-l border-[#1f1f1f] bg-[#0d0d0d] ${className}`}
      >
        <button
          type="button"
          onClick={() => setCollapsed(false)}
          title="Expand Order Flow"
          className="mt-3 flex h-8 w-8 items-center justify-center rounded border border-[#2a2a2a] text-[10px] text-[#888] hover:border-[#555] hover:text-white"
          aria-label="Expand order flow"
        >
          ◀
        </button>
        <span
          className="mt-4 text-[9px] font-medium tracking-[0.2em] text-[#555]"
          style={{ writingMode: "vertical-rl", textOrientation: "mixed" }}
        >
          ORDER FLOW
        </span>
        <span className="mt-auto mb-3 h-2 w-2 animate-pulse rounded-full bg-[#00ff88]" />
      </aside>
    );
  }

  return (
    <aside
      className={[
        "flex min-h-0 min-w-0 flex-col overflow-hidden border-l border-[#1f1f1f] bg-[#0d0d0d]",
        "w-[clamp(11rem,26vw,18.75rem)] max-w-[45%] shrink",
        className,
      ].join(" ")}
    >
      <div className="panel-header min-w-0 shrink-0 gap-2 border-[#1f1f1f] bg-[#111]">
        <div className="min-w-0 flex-1">
          <h2 className="truncate font-display text-sm font-semibold tracking-wide text-white">
            Order Flow
          </h2>
          <p className="truncate text-[9px] text-[#666]">Channel tape · campaign signals</p>
        </div>
        <div className="flex shrink-0 items-center gap-1.5">
          <span className="h-2 w-2 animate-pulse rounded-full bg-[#00ff88]" />
          <button
            type="button"
            onClick={() => setCollapsed(true)}
            title="Collapse Order Flow"
            className="flex h-6 w-6 items-center justify-center rounded border border-[#2a2a2a] text-[10px] text-[#666] hover:text-white"
            aria-label="Collapse order flow"
          >
            ▶
          </button>
        </div>
      </div>

      <div className="flex min-w-0 shrink-0 border-b border-[#1f1f1f]">
        <TabButton
          active={tab === "channels"}
          onClick={() => setTab("channels")}
          label="Channels"
          count={channels.length}
        />
        <TabButton
          active={tab === "campaigns"}
          onClick={() => setTab("campaigns")}
          label="Campaigns"
          count={campaigns.length}
        />
      </div>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        {tab === "channels" ? (
          <ChannelsTab channels={channels} />
        ) : (
          <CampaignsTab campaigns={campaigns} />
        )}
      </div>
    </aside>
  );
}

function TabButton({
  active,
  onClick,
  label,
  count,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  count: number;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex min-w-0 flex-1 items-center justify-center gap-1 border-b-2 px-1 py-2 text-[10px] tracking-wide transition-colors ${
        active
          ? "border-[#00bfff] bg-[#1a1a1a] text-white"
          : "border-transparent text-[#777] hover:text-[#aaa]"
      }`}
    >
      <span className="truncate">{label}</span>
      <span
        className={`tnum shrink-0 rounded px-1 py-0.5 text-[9px] ${
          active ? "bg-[#00bfff]/20 text-[#00bfff]" : "bg-[#222] text-[#666]"
        }`}
      >
        {count}
      </span>
    </button>
  );
}
