import { useEffect, useRef, useState } from "react";
import type { CampaignSignal, ChannelMetric, Trend } from "../types/terminal";
import { nowTimestamp } from "../lib/mockAgentLogs";

export type TickDirection = "up" | "down";

export interface LiveChannelMetric extends ChannelMetric {
  tick?: TickDirection;
  tickKey: number;
}

export interface LiveCampaignSignal extends CampaignSignal {
  tick?: TickDirection;
  tickKey: number;
}

export interface OrderFlowTapeEntry {
  id: number;
  ts: string;
  channel: string;
  side: TickDirection;
  label: string;
  value: string;
}

function ts() {
  return nowTimestamp();
}

function jitterChannel(ch: ChannelMetric): { next: LiveChannelMetric; tape?: OrderFlowTapeEntry } {
  const cpaDelta = (Math.random() - 0.48) * 0.35;
  const spendDelta = Math.round((Math.random() - 0.42) * 280);
  const leadsDelta = Math.round((Math.random() - 0.45) * 18);

  const nextCpa = Math.max(8, +(ch.cpa + cpaDelta).toFixed(2));
  const nextSpend = Math.max(500, ch.spend + spendDelta);
  const nextLeads = Math.max(10, ch.leads + leadsDelta);

  const improved = nextCpa < ch.cpa;
  const trend: Trend = improved ? "up" : "down";
  const side: TickDirection = improved ? "up" : "down";

  return {
    next: {
      ...ch,
      cpa: nextCpa,
      spend: nextSpend,
      leads: nextLeads,
      trend,
      tick: side,
      tickKey: Date.now(),
    },
    tape: {
      id: 0,
      ts: ts(),
      channel: ch.name,
      side,
      label: side === "up" ? "CPA ↓" : "CPA ↑",
      value: `£${nextCpa.toFixed(2)}`,
    },
  };
}

function jitterCampaign(c: CampaignSignal): { next: LiveCampaignSignal; tape?: OrderFlowTapeEntry } {
  const roasDelta = (Math.random() - 0.48) * 0.18;
  const confDelta = Math.round((Math.random() - 0.45) * 6);
  const nextRoas = Math.max(1.2, +(c.roas + roasDelta).toFixed(2));
  const nextConf = Math.min(99, Math.max(35, c.confidence + confDelta));
  const improved = nextRoas >= c.roas;
  const side: TickDirection = improved ? "up" : "down";

  return {
    next: {
      ...c,
      roas: nextRoas,
      confidence: nextConf,
      tick: side,
      tickKey: Date.now(),
    },
    tape: {
      id: 0,
      ts: ts(),
      channel: c.name.split(" ").slice(0, 2).join(" "),
      side,
      label: `${c.signal} ROAS`,
      value: `${nextRoas.toFixed(1)}×`,
    },
  };
}

const SEED_TAPE: OrderFlowTapeEntry[] = [
  { id: 1, ts: "14:02:55", channel: "META", side: "up", label: "CPA ↓", value: "£14.52" },
  { id: 2, ts: "14:02:52", channel: "TIKTOK", side: "down", label: "CPA ↑", value: "£15.71" },
  { id: 3, ts: "14:02:49", channel: "Summer Training", side: "up", label: "BUY ROAS", value: "4.3×" },
  { id: 4, ts: "14:02:46", channel: "GOOGLE", side: "up", label: "CPA ↓", value: "£14.98" },
  { id: 5, ts: "14:02:43", channel: "TikTok Fitness", side: "up", label: "BUY ROAS", value: "3.9×" },
  { id: 6, ts: "14:02:40", channel: "MICROSOFT", side: "down", label: "CPA ↑", value: "£15.34" },
];

export function useLiveOrderFlow(
  channels: ChannelMetric[],
  campaigns: CampaignSignal[],
  enabled = true,
) {
  const [liveChannels, setLiveChannels] = useState<LiveChannelMetric[]>([]);
  const [liveCampaigns, setLiveCampaigns] = useState<LiveCampaignSignal[]>([]);
  const [tape, setTape] = useState<OrderFlowTapeEntry[]>(SEED_TAPE);
  const tapeId = useRef(SEED_TAPE.length + 1);
  const initialized = useRef(false);

  useEffect(() => {
    if (!channels.length && !campaigns.length) return;
    setLiveChannels(channels.map((c) => ({ ...c, tickKey: 0 })));
    setLiveCampaigns(campaigns.map((c) => ({ ...c, tickKey: 0 })));
    initialized.current = true;
  }, [channels, campaigns]);

  useEffect(() => {
    if (!enabled || !initialized.current) return;
    if (!liveChannels.length && !liveCampaigns.length) return;

    const tick = () => {
      const roll = Math.random();

      if (roll < 0.55 && liveChannels.length) {
        const idx = Math.floor(Math.random() * liveChannels.length);
        setLiveChannels((prev) => {
          if (!prev.length) return prev;
          const { next, tape: entry } = jitterChannel(prev[idx]);
          const copy = [...prev];
          copy[idx] = next;
          if (entry) {
            setTape((t) => [{ ...entry, id: tapeId.current++ }, ...t].slice(0, 24));
          }
          return copy;
        });
      } else if (liveCampaigns.length) {
        const idx = Math.floor(Math.random() * liveCampaigns.length);
        setLiveCampaigns((prev) => {
          if (!prev.length) return prev;
          const { next, tape: entry } = jitterCampaign(prev[idx]);
          const copy = [...prev];
          copy[idx] = next;
          if (entry) {
            setTape((t) => [{ ...entry, id: tapeId.current++ }, ...t].slice(0, 24));
          }
          return copy;
        });
      }
    };

    const interval = setInterval(tick, 1800 + Math.random() * 1200);
    return () => clearInterval(interval);
  }, [enabled, liveChannels.length, liveCampaigns.length]);

  return {
    channels: liveChannels.length ? liveChannels : channels.map((c) => ({ ...c, tickKey: 0 })),
    campaigns: liveCampaigns.length ? liveCampaigns : campaigns.map((c) => ({ ...c, tickKey: 0 })),
    tape,
  };
}
