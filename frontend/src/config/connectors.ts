import type { ConnectorItem } from "../hooks/useConnectorStatus";

/** Canonical data connectors shown in the CONNECTORS ribbon (not SIGNAL API). */
export const DATA_CONNECTOR_IDS = [
  "tavily",
  "meta_mcp",
  "google_ads",
  "ads_manager",
  "reddit",
  "thrad",
] as const;

export type DataConnectorId = (typeof DATA_CONNECTOR_IDS)[number];

const DEFAULTS: Record<DataConnectorId, ConnectorItem> = {
  tavily: {
    id: "tavily",
    label: "TAVILY WEB CRAWL",
    status: "inactive",
    sync: "—",
    note: "Set TAVILY_API_KEY in .env.local",
    type: "Web crawl + extract",
    endpoint: "api.tavily.com/search",
  },
  meta_mcp: {
    id: "meta_mcp",
    label: "META MCP",
    status: "degraded",
    sync: "demo mode",
    note: "Creative placement · set META_ADS_ACCESS_TOKEN",
    type: "Creative placement · MCP",
    endpoint: "mcp://meta/ads",
  },
  google_ads: {
    id: "google_ads",
    label: "GOOGLE ADS API",
    status: "degraded",
    sync: "demo",
    note: "Search + PMax · set GOOGLE_ADS_* OAuth",
    type: "Search + PMax campaigns",
    endpoint: "googleads.googleapis.com",
  },
  ads_manager: {
    id: "ads_manager",
    label: "ADS MANAGER API",
    status: "inactive",
    sync: "not connected",
    note: "Meta Business · graph.facebook.com/v19.0",
    type: "Meta Business · campaign mgmt",
    endpoint: "graph.facebook.com/v19.0",
  },
  reddit: {
    id: "reddit",
    label: "REDDIT",
    status: "inactive",
    sync: "inactive",
    note: "Community scrape via Tavily pipeline",
    type: "Community signals · scrape",
    endpoint: "reddit.com · Tavily proxy",
  },
  thrad: {
    id: "thrad",
    label: "THRAD",
    status: "degraded",
    sync: "demo",
    note: "DisBERT classify · THRAD_API_KEY optional",
    type: "DistilBERT · intent classify",
    endpoint: "thrad.ai · DisBERT bridge",
  },
};

/** Merge API payload into canonical connector list for the CONNECTORS bar. */
export function mergeDataConnectors(apiConnectors: ConnectorItem[]): ConnectorItem[] {
  const fromApi = new Map(
    apiConnectors
      .filter((c) => DATA_CONNECTOR_IDS.includes(c.id as DataConnectorId))
      .map((c) => [c.id, c]),
  );
  return DATA_CONNECTOR_IDS.map((id) => {
    const api = fromApi.get(id);
    const base = DEFAULTS[id];
    return api ? { ...base, ...api } : base;
  });
}
