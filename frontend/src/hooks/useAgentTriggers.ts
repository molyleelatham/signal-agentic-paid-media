/**
 * Hook for Agent Triggers
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  triggerBidOptimize,
  triggerContentGenerate,
  triggerCreativeOptimize,
  triggerMarketAnalyze,
  triggerKeywordClassify,
  triggerTavilyResearch,
  triggerOrchestrate,
  getTriggerHistory,
  getTriggerStats,
} from '../api/agentTriggers';

/**
 * Hook for triggering bid optimization
 */
export function useTriggerBidOptimize() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerBidOptimize,
    onSuccess: (data) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
    },
  });
}

/**
 * Hook for triggering content generation
 */
export function useTriggerContentGenerate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerContentGenerate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
    },
  });
}

/**
 * Hook for triggering creative optimization
 */
export function useTriggerCreativeOptimize() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerCreativeOptimize,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
    },
  });
}

/**
 * Hook for triggering market analysis
 */
export function useTriggerMarketAnalyze() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerMarketAnalyze,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
    },
  });
}

/**
 * Hook for triggering keyword classification
 */
export function useTriggerKeywordClassify() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerKeywordClassify,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
    },
  });
}

/**
 * Hook for triggering Tavily research
 */
export function useTriggerTavilyResearch() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerTavilyResearch,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
      queryClient.invalidateQueries({ queryKey: ['market-intelligence'] });
    },
  });
}

/**
 * Hook for triggering orchestration
 */
export function useTriggerOrchestrate() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: triggerOrchestrate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['terminal'] });
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] });
      queryClient.invalidateQueries({ queryKey: ['trigger-history'] });
    },
  });
}

/**
 * Hook for getting trigger history
 */
export function useTriggerHistory(limit: number = 50) {
  return useQuery({
    queryKey: ['trigger-history', limit],
    queryFn: () => getTriggerHistory(limit),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

/**
 * Hook for getting trigger stats
 */
export function useTriggerStats(days: number = 30) {
  return useQuery({
    queryKey: ['trigger-stats', days],
    queryFn: () => getTriggerStats(days),
    refetchInterval: 60000, // Refetch every minute
  });
}