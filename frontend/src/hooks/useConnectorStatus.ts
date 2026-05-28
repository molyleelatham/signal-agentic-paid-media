import { useQuery } from "@tanstack/react-query";
import { mergeDataConnectors } from "../config/connectors";
import { apiFetch } from "../api/client";

export interface ConnectorItem {
  id: string;
  label: string;
  status: "active" | "degraded" | "inactive";
  sync: string;
  note: string;
  type?: string;
  endpoint?: string;
}

export interface ConnectorHealth {
  api: string;
  connectors: ConnectorItem[];
  tavily: "active" | "degraded" | "inactive";
  tavilySync: string;
  tavilyNote: string;
}

async function fetchConnectorHealth(): Promise<ConnectorHealth> {
  let apiConnectors: ConnectorItem[] = [];
  let apiStatus = "online";

  try {
    const res = await apiFetch("/api/v1/connectors/status?probe=true");
    if (res.ok) {
      const data = await res.json();
      apiStatus = data.api ?? "online";
      apiConnectors = (data.connectors ?? []).map(
        (c: {
          id: string;
          label: string;
          status: string;
          sync: string;
          note: string;
          type?: string;
          endpoint?: string;
        }) => ({
          id: c.id,
          label: c.label,
          status: c.status as ConnectorItem["status"],
          sync: c.sync,
          note: c.note,
          type: c.type,
          endpoint: c.endpoint,
        }),
      );
    }
  } catch {
    /* fall through */
  }

  if (apiConnectors.length === 0) {
    try {
      const healthRes = await apiFetch("/health");
      if (!healthRes.ok) {
        throw new Error(
          "API unreachable — start: uv run uvicorn api.main:app --reload --port 8000",
        );
      }
      const health = await healthRes.json();
      apiStatus = health.status ?? "unknown";
      const configured = health.services?.tavily === "configured";
      const thradOk = health.services?.thrad === "configured";
      const metaOk = health.services?.meta_mcp === "configured";
      const gadsOk = health.services?.google_ads === "configured";
      const redditOk = health.services?.reddit === "configured";

      apiConnectors = [
        {
          id: "tavily",
          label: "TAVILY WEB CRAWL",
          status: configured ? "degraded" : "inactive",
          sync: configured ? "key configured" : "no API key",
          note: configured ? "API up" : "Set TAVILY_API_KEY",
          type: "Web crawl + extract",
          endpoint: "api.tavily.com/search",
        },
        {
          id: "meta_mcp",
          label: "META MCP",
          status: metaOk ? "active" : "degraded",
          sync: metaOk ? "connected" : "demo mode",
          note: metaOk ? "MCP + Marketing API" : "Demo MCP",
          type: "Creative placement · MCP",
          endpoint: "mcp://meta/ads",
        },
        {
          id: "google_ads",
          label: "GOOGLE ADS API",
          status: gadsOk ? "active" : "degraded",
          sync: gadsOk ? "configured" : "demo",
          note: gadsOk ? "OAuth configured" : "Demo mode",
          type: "Search + PMax campaigns",
          endpoint: "googleads.googleapis.com",
        },
        {
          id: "ads_manager",
          label: "ADS MANAGER API",
          status: metaOk ? "degraded" : "inactive",
          sync: metaOk ? "configured" : "not connected",
          note: "Meta Business API",
          type: "Meta Business · campaign mgmt",
          endpoint: "graph.facebook.com/v19.0",
        },
        {
          id: "reddit",
          label: "REDDIT",
          status: redditOk ? "degraded" : "inactive",
          sync: redditOk ? "via Tavily" : "inactive",
          note: "Tavily Reddit scrape",
          type: "Community signals · scrape",
          endpoint: "reddit.com · Tavily proxy",
        },
        {
          id: "thrad",
          label: "THRAD",
          status: thradOk ? "active" : "degraded",
          sync: thradOk ? "connected" : "demo",
          note: thradOk ? "Thrad API + DisBERT" : "Demo inference",
          type: "DistilBERT · intent classify",
          endpoint: "thrad.ai · DisBERT bridge",
        },
      ];
    } catch (e) {
      throw e;
    }
  }

  const connectors = mergeDataConnectors(apiConnectors);
  const tavily = connectors.find((c) => c.id === "tavily");

  return {
    api: apiStatus,
    connectors,
    tavily: (tavily?.status ?? "inactive") as ConnectorHealth["tavily"],
    tavilySync: tavily?.sync ?? "—",
    tavilyNote: tavily?.note ?? "",
  };
}

export function useConnectorStatus() {
  return useQuery({
    queryKey: ["connectors", "status"],
    queryFn: fetchConnectorHealth,
    refetchInterval: 45_000,
    retry: 2,
    staleTime: 15_000,
  });
}
