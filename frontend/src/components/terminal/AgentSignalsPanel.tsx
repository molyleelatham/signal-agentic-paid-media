import type { CampaignSignal } from "../../types/terminal";
import { SignalBadge } from "./SignalBadge";
import { useTriggerBidOptimize, useTriggerMarketAnalyze, useTriggerCreativeOptimize } from "../../hooks/useAgentTriggers";
import { useState } from 'react';

export function AgentSignalsPanel({ signals }: { signals: CampaignSignal[] }) {
  const bidOptimize = useTriggerBidOptimize();
  const marketAnalyze = useTriggerMarketAnalyze();
  const creativeOptimize = useTriggerCreativeOptimize();
  
  const [triggering, setTriggering] = useState<{ [key: string]: boolean }>({});
  const [triggerResults, setTriggerResults] = useState<{ [key: string]: any }>({});

  const handleTriggerBid = async (signal: CampaignSignal) => {
    const key = signal.name;
    setTriggering(prev => ({ ...prev, [key]: true }));
    
    try {
      const result = await bidOptimize.mutateAsync({
        keyword: signal.name.toLowerCase().replace(/\s+/g, '_'),
        current_bid: signal.spend / 100, // Convert from spend to approximate bid
        platform: 'google',
      });
      
      setTriggerResults(prev => ({ ...prev, [key]: result }));
    } catch (error) {
      console.error('Trigger failed:', error);
      alert('Failed to trigger bid optimization');
    } finally {
      setTriggering(prev => ({ ...prev, [key]: false }));
    }
  };

  const handleTriggerMarket = async (signal: CampaignSignal) => {
    const key = `${signal.name}-market`;
    setTriggering(prev => ({ ...prev, [key]: true }));
    
    try {
      const result = await marketAnalyze.mutateAsync({
        query: signal.name,
        time_range: 'week',
      });
      
      setTriggerResults(prev => ({ ...prev, [key]: result }));
    } catch (error) {
      console.error('Trigger failed:', error);
      alert('Failed to trigger market analysis');
    } finally {
      setTriggering(prev => ({ ...prev, [key]: false }));
    }
  };

  const handleTriggerCreative = async (signal: CampaignSignal) => {
    const key = `${signal.name}-creative`;
    setTriggering(prev => ({ ...prev, [key]: true }));
    
    try {
      const result = await creativeOptimize.mutateAsync({
        creative_id: signal.name.toLowerCase().replace(/\s+/g, '_'),
        creative_type: 'image',
        platform: 'meta',
      });
      
      setTriggerResults(prev => ({ ...prev, [key]: result }));
    } catch (error) {
      console.error('Trigger failed:', error);
      alert('Failed to trigger creative optimization');
    } finally {
      setTriggering(prev => ({ ...prev, [key]: false }));
    }
  };

  return (
    <section className="flex min-h-0 flex-col overflow-hidden rounded border border-[#1f1f1f] bg-[#1a1a1a]">
      <div className="panel-header">
        <h2 className="panel-title">Agent Signals</h2>
        <span className="text-[10px] text-[#555]">{signals.length} active</span>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-3">
        {signals.map((s) => {
          const triggerKeyBid = s.name;
          const triggerKeyMarket = `${s.name}-market`;
          const triggerKeyCreative = `${s.name}-creative`;
          const result = triggerResults[triggerKeyBid];
          
          return (
            <article
              key={s.name}
              className={`rounded border transition-all ${
                result?.success 
                  ? 'border-green-500/50 bg-green-500/10' 
                  : 'border-[#2a2a2a] bg-[#2a2a2a]/60'
              } hover:border-[#444]`}
            >
              <div className="mb-2 flex items-center justify-between">
                <SignalBadge signal={s.signal} />
                <span className="tnum text-[10px] text-[#888]">
                  {s.confidence}%
                </span>
              </div>
              
              <h3 className="truncate font-display text-sm font-medium text-white">
                {s.name}
              </h3>
              
              <p className="tnum mt-1 text-xs text-[#ccc]">
                £{s.spend.toLocaleString()} · ROAS {s.roas}×
              </p>
              
              {/* Trigger Buttons */}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => handleTriggerBid(s)}
                  disabled={triggering[triggerKeyBid]}
                  className="flex-1 px-2 py-1 text-xs rounded border border-[#444] bg-[#2a2a2a] hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {triggering[triggerKeyBid] ? (
                    <span className="animate-pulse">⏳</span>
                  ) : (
                    <>
                      <span className="text-green-400">⚡</span> Optimize Bid
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => handleTriggerMarket(s)}
                  disabled={triggering[triggerKeyMarket]}
                  className="flex-1 px-2 py-1 text-xs rounded border border-[#444] bg-[#2a2a2a] hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {triggering[triggerKeyMarket] ? (
                    <span className="animate-pulse">⏳</span>
                  ) : (
                    <>
                      <span className="text-blue-400">📊</span> Analyze
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => handleTriggerCreative(s)}
                  disabled={triggering[triggerKeyCreative]}
                  className="flex-1 px-2 py-1 text-xs rounded border border-[#444] bg-[#2a2a2a] hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {triggering[triggerKeyCreative] ? (
                    <span className="animate-pulse">⏳</span>
                  ) : (
                    <>
                      <span className="text-purple-400">🎨</span> Creative
                    </>
                  )}
                </button>
              </div>
              
              {/* Trigger Result */}
              {result && (
                <div className={`mt-2 p-2 rounded text-xs ${
                  result.success 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}>
                  {result.success ? (
                    <>
                      <div className="font-medium">✅ Trigger Successful</div>
                      <div className="mt-1 text-[#888]">
                        {result.output?.recommended_bid && (
                          <div>New Bid: £{result.output.recommended_bid.toFixed(2)}</div>
                        )}
                        <div>Time: {result.execution_time_ms}ms · Tokens: {result.tokens_used}</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="font-medium">❌ Trigger Failed</div>
                      <div className="mt-1 text-[#888]">{result.error}</div>
                    </>
                  )}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
