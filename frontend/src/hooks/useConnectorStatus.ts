import { useQuery } from "@tanstack/react-query";

export interface ConnectorHealth {
  tavily: "configured" | "not_configured";
  status: string;
}

async function fetchHealth(): Promise<ConnectorHealth> {
  const res = await fetch("/health");
  if (!res.ok) throw new Error("API unreachable");
  const data = await res.json();
  return {
    tavily: data.services?.tavily === "configured" ? "configured" : "not_configured",
    status: data.status ?? "unknown",
  };
}

export function useConnectorStatus() {
  return useQuery({
    queryKey: ["health", "connectors"],
    queryFn: fetchHealth,
    refetchInterval: 60_000,
    retry: 1,
  });
}
