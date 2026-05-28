import { useQuery } from "@tanstack/react-query";
import { fetchFullDashboard } from "../api/terminal";

export function useTerminalData() {
  return useQuery({
    queryKey: ["terminal", "full-dashboard"],
    queryFn: fetchFullDashboard,
    refetchInterval: 30_000,
    staleTime: 10_000,
  });
}
