/* Port of frontend adtech/src/data.js — mock layer + page config */

export type TraceTone = "work" | "ok" | "info" | "warn" | "err";

export interface TraceLine {
  msg: string;
  tone: TraceTone;
}

const rnd = ((seed: number) => () => {
  seed = (seed * 9301 + 49297) % 233280;
  return seed / 233280;
})(42);

const series = (n: number, base: number, vol: number) =>
  Array.from({ length: n }, (_, i) =>
    +(base + Math.sin(i * 0.7) * vol + (rnd() - 0.5) * vol * 1.4).toFixed(1),
  );

export const sources = [
  { id: "tavily", label: "TAVILY WEB CRAWL", status: "active" as const, sync: "0:04s ago", type: "Web crawl + extract", endpoint: "tvly.crawl(uk.gymshark.com)", note: "1,284 paths indexed · depth 2" },
  { id: "meta", label: "META ADS", status: "active" as const, sync: "0:12s ago", type: "Ad spend + reach (mock)", endpoint: "graph.facebook.com/v19", note: "4 campaigns live" },
  { id: "google", label: "GOOGLE ADS", status: "active" as const, sync: "0:31s ago", type: "Search + PMax (mock)", endpoint: "googleads.googleapis.com", note: "spend syncing" },
  { id: "tiktok", label: "TIKTOK ADS", status: "degraded" as const, sync: "4:02m ago", type: "Spark Ads (mock)", endpoint: "business-api.tiktok.com", note: "rate-limited · retry 0/3" },
  { id: "msft", label: "MICROSOFT ADS", status: "inactive" as const, sync: "—", type: "Search (mock)", endpoint: "not connected", note: "auth token expired" },
  { id: "mcp", label: "GYMSHARK MCP", status: "active" as const, sync: "0:08s ago", type: "Brand .md files + MCP", endpoint: "mcp://gymshark/brand", note: "12 brand docs read" },
];

export interface Trend {
  id: string;
  kw: string;
  growth: number;
  vol: string;
  intensity: "hot" | "warm" | "cool";
  src: string[];
  spark: number[];
  detail?: {
    vol12: number[];
    relevance: number;
    bidders: string[];
    attribution: { src: string; w: number }[];
    tavily_url?: string;
    tavily_snippet?: string;
  };
}

export const trends: Trend[] = [
  { id: "t1", kw: "scrunch leggings", growth: 34, vol: "182K", intensity: "hot", src: ["T", "TT", "G"], spark: series(7, 40, 18) },
  { id: "t2", kw: "vital seamless 2.0", growth: 28, vol: "147K", intensity: "hot", src: ["T", "G"], spark: series(7, 35, 14) },
  { id: "t3", kw: "pump cover oversized", growth: 41, vol: "121K", intensity: "hot", src: ["T", "TT"], spark: series(7, 30, 20) },
  { id: "t4", kw: "gymshark vs alphalete", growth: 19, vol: "98K", intensity: "warm", src: ["T", "G"], spark: series(7, 44, 9) },
  { id: "t5", kw: "adapt camo seamless", growth: 12, vol: "76K", intensity: "warm", src: ["T", "G"], spark: series(7, 50, 6) },
  { id: "t6", kw: "blackout drop restock", growth: 67, vol: "64K", intensity: "hot", src: ["T", "TT", "MS"], spark: series(7, 20, 24) },
  { id: "t7", kw: "lifting straps", growth: -8, vol: "52K", intensity: "cool", src: ["G", "MS"], spark: series(7, 60, 7) },
  { id: "t8", kw: "everyday seamless set", growth: 6, vol: "47K", intensity: "warm", src: ["T", "TT"], spark: series(7, 41, 5) },
  { id: "t9", kw: "gymshark womens shorts", growth: -12, vol: "39K", intensity: "cool", src: ["G"], spark: series(7, 55, 8) },
  { id: "t10", kw: "speed running shoe", growth: 23, vol: "31K", intensity: "warm", src: ["T", "TT"], spark: series(7, 28, 11) },
];

trends.forEach((t) => {
  t.detail = {
    vol12: series(12, 50, 22),
    relevance: Math.min(99, 40 + Math.round(Math.abs(t.growth) * 1.3 + rnd() * 20)),
    bidders: ["google", "tiktok", "msft"].filter(() => rnd() > 0.35),
    attribution: [
      { src: "Tavily /search", w: 0.42 },
      { src: "uk.gymshark.com crawl", w: 0.31 },
      { src: "reddit.com r/Gymshark", w: 0.16 },
      { src: "tiktok.com", w: 0.11 },
    ],
  };
});

export const aiQueries = [
  { q: "What's the best Gymshark legging for HIIT?", intent: "COMPARISON", vol: 8.4, trend: "up" as const },
  { q: "Are Vital Seamless leggings squat proof?", intent: "PURCHASE", vol: 7.1, trend: "up" as const },
  { q: "Gymshark vs Lululemon for lifting", intent: "COMPARISON", vol: 6.8, trend: "up" as const },
  { q: "When does the next Gymshark drop release?", intent: "DISCOVERY", vol: 6.2, trend: "up" as const },
  { q: "How do Gymshark sizes run?", intent: "PURCHASE", vol: 5.5, trend: "flat" as const },
  { q: "Best pump cover for the gym", intent: "DISCOVERY", vol: 4.9, trend: "up" as const },
  { q: "Is Gymshark worth the price?", intent: "COMPARISON", vol: 4.1, trend: "flat" as const },
  { q: "Gymshark student discount code", intent: "PURCHASE", vol: 3.7, trend: "down" as const },
  { q: "How to style oversized gym tops", intent: "LOYALTY", vol: 3.2, trend: "up" as const },
].map((a) => ({
  ...a,
  adRank: +(rnd() * 9 + 1).toFixed(1),
  ctxScore: Math.round(rnd() * 40 + 55),
}));

export const funnelStages = [
  { id: "awareness", label: "AWARENESS", color: "#00D4FF" },
  { id: "interest", label: "INTEREST", color: "#8B5CF6" },
  { id: "consideration", label: "CONSIDERATION", color: "#F59E0B" },
  { id: "intent", label: "INTENT", color: "#EF4444" },
  { id: "evaluation", label: "EVALUATION", color: "#10B981" },
];

export const quarters = ["Q1", "Q2", "Q3", "Q4"].map((q, qi) => ({
  q,
  stages: {
    awareness: [120, 145, 168, 152][qi],
    interest: [88, 102, 124, 110][qi],
    consideration: [64, 71, 92, 80][qi],
    intent: [42, 49, 68, 58][qi],
    evaluation: [28, 33, 44, 38][qi],
  },
  leads: [9200, 11400, 14230, 12800][qi],
  spend: [48200, 55600, 62400, 59100][qi],
  cpl: [5.24, 4.88, 4.2, 4.62][qi],
}));

export const kpiRows = [
  { k: "Leads Generated", v: "14,230", b: "+18% vs. industry", tone: "good" as const },
  { k: "CPL (Cost per Lead)", v: "£4.20", b: "↓ 12% MoM", tone: "good" as const },
  { k: "Spend", v: "£62,400", b: "On-budget", tone: "neutral" as const },
  { k: "ROAS", v: "4.2×", b: "↑ above target", tone: "good" as const },
  { k: "Funnel Drop-off", v: "34%", b: "⚠ Interest→Consideration", tone: "warn" as const },
];

export const channels = ["Meta", "Google", "TikTok", "Microsoft", "Organic", "Influencer"];
export const platformColors: Record<string, string> = {
  Meta: "#1877F2",
  Google: "#4285F4",
  TikTok: "#FF0050",
  Microsoft: "#00A4EF",
  Organic: "#00FF88",
  Influencer: "#8B5CF6",
};

const mkMatrix = (mult: number, cplBase: number) =>
  channels.map((c, i) => {
    const spend = Math.round([18000, 14000, 11000, 6000, 0, 9000][i] * mult);
    const cpl = +(cplBase + i * 0.4).toFixed(2);
    return {
      channel: c,
      awareness: [62, 41, 78, 33, 88, 71][i],
      loyalty: [54, 67, 38, 49, 82, 61][i],
      leads: cpl > 0 ? Math.round(spend / cpl) : Math.round([1200, 800, 600, 0, 2400, 500][i] * mult),
      cpl,
      spend,
    };
  });

export const scenarios = {
  conservative: { label: "CONSERVATIVE", desc: "Lower spend, protect margins", bg: "#1A1A1A", border: "#3A3A3A", matrix: mkMatrix(0.78, 4.1) },
  optimistic: { label: "OPTIMISTIC", desc: "Balanced growth target", bg: "#0D1F0D", border: "#1F6B3A", matrix: mkMatrix(1.0, 4.2) },
  aggressive: { label: "AGGRESSIVE", desc: "Maximum reach, high spend", bg: "#1F0D0D", border: "#6B1F1F", matrix: mkMatrix(1.42, 4.85) },
};

export const advKpis = [
  { id: "ltvcac", title: "LTV : CAC", value: "3.8×", cat: "#00D4FF", spark: series(6, 3.2, 0.5), sub: "LTV £142 · CAC £37" },
  { id: "ret", title: "Retention Rate", value: "68%", cat: "#10B981", heat: Array.from({ length: 18 }, () => Math.round(rnd() * 100)), sub: "6-mo cohort" },
  { id: "cart", title: "Cart Abandonment", value: "24.3%", cat: "#F59E0B", before: 31.2, after: 24.3, sub: "−6.9pt via retargeting" },
  { id: "cpld", title: "CPL Delta", value: "−20%", cat: "#00FF88", delta: "+40% leads", sub: "vs. prior period" },
];

export const beforeAfter = [
  { k: "CPL", before: "£6.20", after: "£4.96", delta: "−20%", tone: "good" as const },
  { k: "Leads", before: "8,200", after: "11,480", delta: "+40%", tone: "good" as const },
  { k: "ROAS", before: "3.1×", after: "4.2×", delta: "+35%", tone: "good" as const },
  { k: "Brand Search Vol.", before: "—", after: "+18% lift", delta: "↑", tone: "good" as const },
];

export const adstock = [
  { name: "Scrunch Drop — Spark", plat: "TikTok", platColor: "#FF0050", signal: "BUY" as const, curve: series(14, 40, 28).map((_, i) => Math.max(4, 90 - i * 5 + (rnd() - 0.5) * 8)) },
  { name: "Vital Seamless — PMax", plat: "Google", platColor: "#4285F4", signal: "HOLD" as const, curve: Array.from({ length: 14 }, (_, i) => Math.max(12, 80 - i * 2.4)) },
  { name: "Blackout Restock — Advantage+", plat: "Meta", platColor: "#1877F2", signal: "BUY" as const, curve: Array.from({ length: 14 }, (_, i) => Math.max(6, 95 - i * 6)) },
  { name: "Pump Cover — Spark", plat: "TikTok", platColor: "#FF0050", signal: "SELL" as const, curve: Array.from({ length: 14 }, (_, i) => Math.max(2, 50 - i * 3.6)) },
  { name: "Adapt Camo — Search", plat: "Microsoft", platColor: "#00A4EF", signal: "HOLD" as const, curve: Array.from({ length: 14 }, (_, i) => Math.max(10, 70 - i * 3)) },
];

export const traceScripts: Record<string, TraceLine[]> = {
  boot: [
    { msg: "Connected to Overmind — agent is ready.", tone: "ok" },
    { msg: "6 data sources online. TikTok is rate-limited right now.", tone: "warn" },
  ],
  intel: [
    { msg: "Market Intelligence ready — run Tavily Research to populate Section A & B.", tone: "info" },
    { msg: "Use the search box: e.g. gymshark leggings trends 2026", tone: "work" },
  ],
  strategy: [
    { msg: "Building this quarter's funnel from 48 campaign records.", tone: "work" },
    { msg: "Claude drafted a Q3 strategy summary.", tone: "ok" },
    { msg: "Biggest leak: 34% of people drop from Interest to Consideration.", tone: "warn" },
  ],
  budget: [
    { msg: "Recalculating cost-per-lead across all 6 channels.", tone: "work" },
    { msg: "The Optimistic plan returns 14,230 leads at £4.20 each.", tone: "ok" },
    { msg: "TikTok is giving the cheapest awareness at the moment.", tone: "info" },
  ],
  perf: [
    { msg: "Pulling campaign performance for the last 14 days.", tone: "work" },
    { msg: "Retargeting cut cart abandonment by 6.9 points.", tone: "ok" },
    { msg: "LTV-to-CAC is healthy at 3.8×.", tone: "info" },
  ],
  terminal: [
    { msg: "SIGNAL terminal online — polling agent signals.", tone: "ok" },
    { msg: "Thompson allocator issued BUY on Summer Training.", tone: "info" },
  ],
};

export function trendTrace(t: Trend): TraceLine[] {
  return [
    { msg: `Looking up "${t.kw}" in more detail…`, tone: "work" },
    t.growth >= 0
      ? { msg: `Mentions are up ${t.growth}% over the past 7 days.`, tone: "ok" }
      : { msg: `Mentions are down ${Math.abs(t.growth)}% over the past 7 days.`, tone: "warn" },
    { msg: `${t.detail?.bidders.length ?? 0} competitors are currently bidding on it.`, tone: "info" },
  ];
}

export const intentColors: Record<string, string> = {
  DISCOVERY: "#00D4FF",
  COMPARISON: "#8B5CF6",
  PURCHASE: "#00FF88",
  LOYALTY: "#FFB800",
};

export const intensityColors: Record<string, string> = {
  hot: "#FF4444",
  warm: "#FFB800",
  cool: "#00D4FF",
};

export const pages = [
  { id: "intel", n: "01", title: "Market Intelligence", sub: "Live brand & market signal aggregation for GymShark" },
  { id: "strategy", n: "02", title: "Strategy Generator", sub: "Quarterly funnel planning & KPIs" },
  { id: "budget", n: "03", title: "Budget Scenario Planner", sub: "CPL matrix across 3 scenarios" },
  { id: "perf", n: "04", title: "Campaign Performance", sub: "Advanced signals · adstock · LTV:CAC" },
  { id: "terminal", n: "05", title: "SIGNAL Terminal", sub: "Agent signals · P&L · execution log" },
] as const;

export type PageId = (typeof pages)[number]["id"];
