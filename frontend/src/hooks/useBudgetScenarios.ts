import { useQuery } from "@tanstack/react-query";
import { fetchBudgetScenarios } from "../api/terminal";

export function useBudgetScenarios() {
  return useQuery({
    queryKey: ["terminal", "budget-scenarios"],
    queryFn: fetchBudgetScenarios,
    refetchInterval: 30_000,
    staleTime: 10_000,
  });
}
