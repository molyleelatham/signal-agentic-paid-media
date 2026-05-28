import { useMemo, useState } from "react";
import {
  aiQueries,
  intentColors,
  intensityColors,
  trendTrace,
  trends,
  type Trend,
} from "../data/adtec";
import { adtecLog } from "../lib/trace";
import { GrowthBadge, LineChart, Spark, TrendArrow } from "../components/shared/charts";
import { useTriggerKeywordClassify, useTriggerTavilyResearch } from "../hooks/useAgentTriggers";
import type { Trend as TrendType } from "../data/adtec";

const SRC_GLYPH: Record<string, string> = {
  T: "#00D4FF",
  G: "#4285F4",
  TT: "#FF0050",
  MS: "#00A4EF",
};

const BID_PLATFORMS = ["google", "tiktok", "msft"] as const;
const BID_COLORS: Record<string, string> = {
  google: "#4285F4",
  tiktok: "#FF0050",
  msft: "#00A4EF",
};

function TrendCard({
  t,
  active,
  onClick,
}: {
  t: Trend;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="flex h-[62px] cursor-pointer items-center gap-2.5 border-b border-[#1a1a1a] pr-3 transition-colors"
      style={{
        background: active ? "#161616" : "#111",
        borderLeft: `4px solid ${intensityColors[t.intensity] ?? intensityColors.warm}`,
      }}
    >
      <div className="min-w-0 flex-1 pl-3">
        <div className="truncate font-display text-base font-bold uppercase tracking-tight text-white">
          {t.kw}
        </div>
        <div className="mt-0.5 flex gap-1">
          {t.src.map((s) => (
            <span
              key={s}
              className="inline-block h-[13px] w-[15px] rounded-sm border text-center text-[8px] leading-[13px]"
              style={{ color: SRC_GLYPH[s], borderColor: `${SRC_GLYPH[s]}55` }}
            >
              {s}
            </span>
          ))}
          <span className="ml-1 text-[10px] text-[#555]">{t.vol}</span>
        </div>
      </div>
      <Spark data={t.spark} color={intensityColors[t.intensity] ?? intensityColors.warm} w={56} h={24} />
      <GrowthBadge v={t.growth} />
    </div>
  );
}

function DetailPanel({ t }: { t: Trend | undefined }) {
  const keywordClassify = useTriggerKeywordClassify();
  const [isClassifying, setIsClassifying] = useState(false);
  const [classificationResult, setClassificationResult] = useState<any>(null);
  
  if (!t?.detail) {
    return <div className="p-6 text-xs text-[#555]">Select a trend to inspect →</div>;
  }
  const d = t.detail!;
  
  const handleClassifyKeyword = async () => {
    setIsClassifying(true);
    try {
      const result = await keywordClassify.mutateAsync({
        query: t.kw,
        use_disbert: true,
      });
      setClassificationResult(result);
    } catch (error) {
      console.error('Classification failed:', error);
      alert('Failed to classify keyword');
    } finally {
      setIsClassifying(false);
    }
  };
  
  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="eyebrow">TREND DETAIL · SUPABASE market_signals</div>
      <h3 className="mt-1 font-display text-2xl uppercase text-white">{t.kw}</h3>
      <div className="mb-3.5 mt-2 flex items-center gap-2.5">
        <GrowthBadge v={t.growth} />
        <span className="text-[11px] text-[#666]">{t.vol} mentions · 7d</span>
        <span className="ml-auto text-[11px] text-[#00d4ff]">
          RELEVANCE {d.relevance}/100
        </span>
      </div>
      <div className="mb-4 h-1 bg-[#1a1a1a]">
        <div
          className="h-full bg-gradient-to-r from-[#00ff88] to-[#00d4ff]"
          style={{ width: `${d.relevance}%` }}
        />
      </div>
      
      {/* DisBERT Classification Trigger */}
      <div className="mb-4 rounded border border-[#2a2a2a] bg-[#1a1a1a] p-3">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs font-medium text-white">DisBERT Classification</span>
          <button
            onClick={handleClassifyKeyword}
            disabled={isClassifying}
            className="px-3 py-1 text-xs rounded border border-[#444] bg-[#2a2a2a] hover:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isClassifying ? (
              <span className="animate-pulse">⏳ Classifying...</span>
            ) : (
              <>
                <span className="text-green-400">✨</span> Classify with DisBERT
              </>
            )}
          </button>
        </div>
        
        {classificationResult && (
          <div className={`mt-2 p-2 rounded text-xs ${
            classificationResult.success 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-red-500/20 text-red-400 border border-red-500/30'
          }`}>
            {classificationResult.success ? (
              <>
                <div className="font-medium">✅ Classification Complete</div>
                <div className="mt-1 text-[#888]">
                  <div>Category: <span className="text-white">{classificationResult.output?.category}</span></div>
                  <div>Model: {classificationResult.output?.model_used || 'thrad_disbert'}</div>
                  <div>Time: {classificationResult.execution_time_ms}ms</div>
                </div>
              </>
            ) : (
              <>
                <div className="font-medium">❌ Classification Failed</div>
                <div className="mt-1 text-[#888]">{classificationResult.error}</div>
              </>
            )}
          </div>
        )}
      </div>
      
      <div className="eyebrow mb-1.5">VOLUME OVER TIME · 12W</div>
      <LineChart
        series={[{ name: "vol", color: "#00D4FF", data: d.vol12 }]}
        labels={Array(12).fill("")}
        w={300}
        h={120}
        animateKey={t.id}
      />
      {(d.tavily_snippet || d.tavily_url) && (
        <div className="mb-4 rounded border border-[#00d4ff33] bg-[#00d4ff08] p-2.5">
          <div className="eyebrow mb-1 text-[#00d4ff]">TAVILY INTELLIGENCE</div>
          {d.tavily_snippet && (
            <p className="line-clamp-4 text-[11px] leading-relaxed text-[#bbb]">{d.tavily_snippet}</p>
          )}
          {d.tavily_url && (
            <a
              href={d.tavily_url}
              target="_blank"
              rel="noreferrer"
              className="mt-1 block truncate text-[10px] text-[#00d4ff] hover:underline"
            >
              {d.tavily_url}
            </a>
          )}
        </div>
      )}
      <div className="eyebrow mb-2 mt-4">COMPETITIVE BID SIGNAL</div>
      <div className="flex flex-wrap gap-1.5">
        {BID_PLATFORMS.map((p) => {
          const on = d.bidders.includes(p);
          const c = BID_COLORS[p];
          return (
            <span
              key={p}
              className="pill text-[10px]"
              style={{
                color: on ? c : "#555",
                background: on ? `${c}1A` : "#141414",
                border: `1px solid ${on ? `${c}44` : "#222"}`,
              }}
            >
              {p.toUpperCase()} {on ? "BIDDING" : "—"}
            </span>
          );
        })}
      </div>
      <div className="eyebrow mb-2 mt-4">SOURCE ATTRIBUTION</div>
      {d.attribution.map((a, i) => (
        <div key={i} className="mb-1 flex items-center gap-2">
          <span className="w-[150px] shrink-0 text-[10px] text-[#999]">{a.src}</span>
          <div className="h-1 flex-1 bg-[#1a1a1a]">
            <div className="h-full bg-[#00ff88]/80" style={{ width: `${a.w * 100}%` }} />
          </div>
          <span className="tnum w-8 text-right text-[10px] text-[#666]">
            {Math.round(a.w * 100)}%
          </span>
        </div>
      ))}
    </div>
  );
}

function AIQueries() {
  return (
    <div className="flex h-full flex-col border-l border-t-2 border-[#1f1f1f] border-t-[#00d4ff] bg-[#0d0d0d]">
      <div className="shrink-0 px-3.5 pb-2 pt-3">
        <div className="eyebrow">SECTION B</div>
        <h4 className="font-display text-lg uppercase text-white">Audience AI Queries</h4>
        <div className="mt-0.5 text-[10px] text-[#555]">
          What people ask ChatGPT · Gemini · Perplexity
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-2 overflow-y-auto px-3.5 pb-3.5">
        {aiQueries.map((a, i) => (
          <div key={i} className="border border-[#1a1a1a] bg-[#111] p-2.5">
            <div className="mb-1.5 text-xs leading-snug text-[#e6e6e6]">"{a.q}"</div>
            <div className="flex items-center gap-1.5">
              <span
                className="pill text-[9px]"
                style={{
                  color: intentColors[a.intent],
                  background: `${intentColors[a.intent]}18`,
                }}
              >
                {a.intent}
              </span>
              <span className="text-[9px] text-[#555]">vol {a.vol}K</span>
              <TrendArrow t={a.trend} />
              <span className="ml-auto text-[9px] text-[#666]">
                rank <span className="text-[#8b5cf6]">{a.adRank}</span> · ctx{" "}
                <span className="text-[#00d4ff]">{a.ctxScore}</span>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MarketIntelligencePage() {
  const [sortBy, setSortBy] = useState<"trending" | "volume" | "recency">("trending");
  const [sel, setSel] = useState(trends[0].id);
  const [tavilyQuery, setTavilyQuery] = useState("");
  const [isResearching, setIsResearching] = useState(false);
  const [customTrends, setCustomTrends] = useState<TrendType[]>([]);
  const [disbertSegments, setDisbertSegments] = useState<any>(null);
  const [showSegments, setShowSegments] = useState(false);
  const [tavilyError, setTavilyError] = useState<string | null>(null);
  const [tavilyAnswer, setTavilyAnswer] = useState<string | null>(null);
  
  const tavilyResearch = useTriggerTavilyResearch();
  
  const sorted = useMemo(() => {
    const allTrends = [...customTrends, ...trends];
    const a = [...allTrends];
    if (sortBy === "trending") a.sort((x, y) => y.growth - x.growth);
    if (sortBy === "volume") a.sort((x, y) => parseFloat(y.vol) - parseFloat(x.vol));
    return a;
  }, [sortBy, customTrends]);
  const selT = sorted.find((t) => t.id === sel);
  
  const handleTavilyResearch = async () => {
    if (!tavilyQuery.trim() || isResearching) return;
    
    setIsResearching(true);
    setShowSegments(false);
    setTavilyError(null);
    try {
      const result = await tavilyResearch.mutateAsync({
        query: tavilyQuery,
        max_results: 10,
        extract_keywords: true,
      });
      
      if (!result.success) {
        setTavilyError(result.error || "Tavily research failed");
        return;
      }

      setTavilyAnswer(result.output?.answer ?? null);

      const topics = (result.output?.trending_topics ?? []).map((t: TrendType) => ({
        ...t,
        intensity:
          t.intensity === "hot" || t.intensity === "warm" || t.intensity === "cool"
            ? t.intensity
            : ("warm" as const),
      }));

      if (topics.length > 0) {
        setCustomTrends((prev) => [...topics, ...prev]);
        setSel(topics[0].id);
        adtecLog([
          { msg: `Tavily returned ${topics.length} topics for "${tavilyQuery}".`, tone: "ok" },
          { msg: result.output?.answer?.slice(0, 120) ?? "Research complete.", tone: "info" },
        ]);
      } else {
        setTavilyError("Tavily connected but returned no topics — try a different query.");
      }

      if (result.output?.disbert_segments) {
        setDisbertSegments(result.output.disbert_segments);
        setShowSegments(true);
      }
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Tavily research failed";
      console.error("Tavily research failed:", error);
      setTavilyError(msg);
      adtecLog([{ msg: `Tavily error: ${msg.slice(0, 100)}`, tone: "err" }]);
    } finally {
      setIsResearching(false);
    }
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[minmax(280px,1fr)_1.2fr_minmax(240px,0.9fr)]">
        <div className="flex min-h-0 flex-col border-r border-[#1f1f1f]">
          <div className="flex shrink-0 flex-col gap-2 border-b border-[#1f1f1f] px-3.5 py-2.5">
            <div className="flex items-center gap-3">
              <span className="eyebrow">SECTION A · TRENDING TOPICS</span>
              <div className="ml-auto flex gap-1">
                {(
                  [
                    ["trending", "TRENDING ↑"],
                    ["volume", "VOLUME"],
                    ["recency", "RECENCY"],
                  ] as const
                ).map(([k, l]) => (
                  <button
                    key={k}
                    type="button"
                    onClick={() => setSortBy(k)}
                    className="rounded-sm border px-1.5 py-1 text-[9px] tracking-wide"
                    style={{
                      borderColor: sortBy === k ? "#00D4FF" : "#222",
                      color: sortBy === k ? "#00D4FF" : "#666",
                      background: sortBy === k ? "#00d4ff14" : "transparent",
                    }}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>
            
            {tavilyError && (
              <div className="rounded border border-[#ff444433] bg-[#ff444410] px-2 py-1.5 text-[10px] text-[#ff8888]">
                {tavilyError}
              </div>
            )}
            {tavilyAnswer && !tavilyError && (
              <div className="line-clamp-2 rounded border border-[#00d4ff22] bg-[#00d4ff08] px-2 py-1 text-[10px] text-[#aaa]">
                <span className="text-[#00d4ff]">Tavily · </span>
                {tavilyAnswer}
              </div>
            )}

            {/* Tavily Research Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={tavilyQuery}
                onChange={(e) => setTavilyQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleTavilyResearch()}
                placeholder="Research trending topics with Tavily..."
                className="flex-1 rounded border border-[#2a2a2a] bg-[#1a1a1a] px-2 py-1 text-xs text-white placeholder-[#555] focus:border-[#00D4FF] focus:outline-none"
                disabled={isResearching}
              />
              <button
                onClick={handleTavilyResearch}
                disabled={isResearching || !tavilyQuery.trim()}
                className="px-3 py-1 text-xs rounded border border-[#00D4FF] bg-[#00d4ff14] text-[#00D4FF] hover:bg-[#00d4ff24] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isResearching ? (
                  <span className="animate-pulse">⏳</span>
                ) : (
                  <>
                    <span>🔍</span> Research
                  </>
                )}
              </button>
              {showSegments && (
                <button
                  onClick={() => setShowSegments(false)}
                  className="px-2 py-1 text-xs rounded border border-[#444] bg-[#2a2a2a] text-white hover:bg-[#333] transition-colors"
                  title="Hide segments"
                >
                  ✕
                </button>
              )}
            </div>
            
            {/* DisBERT Segments Panel */}
            {showSegments && disbertSegments && (
              <div className="mt-2 rounded border border-[#2a2a2a] bg-[#1a1a1a] p-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-white">DisBERT Segments</span>
                  <span className="text-[10px] text-[#888]">{disbertSegments.total_segments} segments</span>
                </div>
                
                {/* High-Value Segments */}
                {disbertSegments.high_value_segments && disbertSegments.high_value_segments.length > 0 && (
                  <div className="mb-2">
                    <div className="text-[10px] text-[#00ff88] mb-1">HIGH VALUE (H, J, E)</div>
                    {disbertSegments.high_value_segments.map((segment: any, idx: number) => (
                      <div key={idx} className="mb-1 rounded bg-green-500/10 border border-green-500/30 p-1.5">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-medium text-green-400">
                            {segment.classification} - {segment.tavily_fields.join(', ')}
                          </span>
                          <span className="text-[9px] text-[#888]">{(segment.commercial_intent * 100).toFixed(0)}% intent</span>
                        </div>
                        <div className="text-[9px] text-[#666] mt-0.5 truncate">
                          {Object.values(segment.mapped_data || {}).join(' · ')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Segments by Classification */}
                <div className="text-[10px] text-[#888] mb-1">ALL SEGMENTS BY CLASSIFICATION</div>
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {Object.entries(disbertSegments.segments_by_classification || {}).map(([classification, segments]: [string, any]) => (
                    <div key={classification} className="rounded border border-[#2a2a2a] bg-[#0a0a0a] p-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-medium text-white">
                          {classification} ({Array.isArray(segments) ? segments.length : 0})
                        </span>
                        <span className={`text-[9px] ${
                          classification === 'H' ? 'text-green-400' :
                          classification === 'J' ? 'text-purple-400' :
                          classification === 'E' ? 'text-blue-400' :
                          'text-[#666]'
                        }`}>
                          {classification === 'H' ? 'HIGH VALUE' :
                           classification === 'J' ? 'HIGHEST PRIORITY' :
                           classification === 'E' ? 'HIGH PRIORITY' : ''}
                        </span>
                      </div>
                      {Array.isArray(segments) && segments.length > 0 && (
                        <div className="text-[9px] text-[#666] mt-0.5 truncate">
                          {segments[0].tavily_fields.join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            {sorted.map((t) => (
              <TrendCard
                key={t.id}
                t={t}
                active={t.id === sel}
                onClick={() => {
                  setSel(t.id);
                  adtecLog(trendTrace(t));
                }}
              />
            ))}
          </div>
        </div>
        <div className="min-h-0 border-r border-[#1f1f1f] bg-[#0b0b0b]">
          <DetailPanel t={selT} />
        </div>
        <AIQueries />
      </div>
    </div>
  );
}
