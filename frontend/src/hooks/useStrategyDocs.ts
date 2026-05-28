import { useQuery } from "@tanstack/react-query";
import { fetchStrategyDocs } from "../api/terminal";

export function useStrategyDocs() {
  return useQuery({
    queryKey: ["terminal", "strategy-docs"],
    queryFn: fetchStrategyDocs,
    staleTime: 30_000,
  });
}
