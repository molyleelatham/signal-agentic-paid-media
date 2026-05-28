import { useQuery } from "@tanstack/react-query";
import { agentLogsToTrace, fetchAgentLogs } from "../api/agentLogs";

export function useAgentLogs(limit = 40) {
  return useQuery({
    queryKey: ["agent-logs", limit],
    queryFn: () => fetchAgentLogs(limit),
    refetchInterval: 20_000,
    staleTime: 8_000,
  });
}

export function useAgentLogsAsTrace(limit = 40) {
  const q = useAgentLogs(limit);
  return {
    ...q,
    traceLines: agentLogsToTrace(q.data ?? []),
  };
}
