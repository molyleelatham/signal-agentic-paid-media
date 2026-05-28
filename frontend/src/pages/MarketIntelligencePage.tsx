import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { intentColors, intensityColors, type Trend } from "../data/adtec";
import { adtecLog } from "../lib/trace";
import { mapTavilyResearchResult } from "../lib/mapTavilyResearch";
import { trendTraceFromApi, type AudienceQuery } from "../lib/tavilyMappers";
import { fetchAgentLogs, agentLogsToTrace } from "../api/agentLogs";
import { useConnectorStatus } from "../hooks/useConnectorStatus";
import { GrowthBadge, LineChart, Spark, TrendArrow } from "../components/shared/charts";
import { useTriggerKeywordClassify, useTriggerTavilyResearch } from "../hooks/useAgentTriggers";

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

const DEFAULT_QUERY = "gymshark leggings trends 2026";

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
        <div className="flex items-center gap-1.5">
          <span className="rounded bg-[#00d4ff22] px-1 text-[8px] text-[#00d4ff]">TAVILY</span>
          <div className="truncate font-display text-base font-bold uppercase tracking-tight text-white">
            {t.kw}
          </div>
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
  const [classificationResult, setClassificationResult] = useState<{
    success: boolean;
    error?: string;
    output?: { category?: string; model_used?: string };
    execution_time_ms?: number;
  } | null>(null);

  if (!t?.detail) {
    return (
      <div className="p-6 text-xs text-[#555]">
        Run Tavily Research to load trend detail from the API.
      </div>
    );
  }
  const d = t.detail;

  const handleClassifyKeyword = async () => {
    setIsClassifying(true);
    try {
      const result = await keywordClassify.mutateAsync({
        query: t.kw,
        use_disbert: true,
      });
      setClassificationResult(result);
      adtecLog([
        {
          msg: result.success
            ? `DisBERT classified "${t.kw}" as ${result.output?.category}`
            : `DisBERT failed for "${t.kw}"`,
          tone: result.success ? "ok" : "err",
        },
      ]);
    } catch {
      adtecLog([{ msg: `DisBERT classification failed for "${t.kw}"`, tone: "err" }]);
    } finally {
      setIsClassifying(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="eyebrow">TREND DETAIL · TAVILY LIVE</div>
      <h3 className="mt-1 font-display text-2xl uppercase text-white">{t.kw}</h3>
      <div className="mb-3.5 mt-2 flex items-center gap-2.5">
        <GrowthBadge v={t.growth} />
        <span className="text-[11px] text-[#666]">{t.vol} · Tavily score</span>
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

      <div className="mb-4 rounded border border-[#2a2a2a] bg-[#1a1a1a] p-3">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs font-medium text-white">DisBERT Classification</span>
          <button
            type="button"
            onClick={handleClassifyKeyword}
            disabled={isClassifying}
            className="rounded border border-[#444] bg-[#2a2a2a] px-3 py-1 text-xs hover:bg-[#333] disabled:opacity-50"
          >
            {isClassifying ? "⏳ Classifying…" : "✨ Classify"}
          </button>
        </div>
        {classificationResult && (
          <div
            className={`mt-2 rounded p-2 text-xs ${
              classificationResult.success
                ? "border border-green-500/30 bg-green-500/20 text-green-400"
                : "border border-red-500/30 bg-red-500/20 text-red-400"
            }`}
          >
            {classificationResult.success ? (
              <>
                Category: {classificationResult.output?.category} ·{" "}
                {classificationResult.execution_time_ms}ms
              </>
            ) : (
              classificationResult.error
            )}
          </div>
        )}
      </div>

      {(d.tavily_snippet || d.tavily_url) && (
        <div className="mb-4 rounded border border-[#00d4ff33] bg-[#00d4ff08] p-2.5">
          <div className="eyebrow mb-1 text-[#00d4ff]">TAVILY INTELLIGENCE</div>
          {d.tavily_snippet && (
            <p className="text-[11px] leading-relaxed text-[#bbb]">{d.tavily_snippet}</p>
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

      {d.vol12.length > 0 && (
        <>
          <div className="eyebrow mb-1.5">VOLUME OVER TIME · 12W</div>
          <LineChart
            series={[{ name: "vol", color: "#00D4FF", data: d.vol12 }]}
            labels={Array(12).fill("")}
            w={300}
            h={120}
            animateKey={t.id}
          />
        </>
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

      {d.attribution.length > 0 && (
        <>
          <div className="eyebrow mb-2 mt-4">SOURCE ATTRIBUTION</div>
          {d.attribution.map((a, i) => (
            <div key={i} className="mb-1 flex items-center gap-2">
              <span className="w-[150px] shrink-0 truncate text-[10px] text-[#999]">{a.src}</span>
              <div className="h-1 flex-1 bg-[#1a1a1a]">
                <div className="h-full bg-[#00ff88]/80" style={{ width: `${a.w * 100}%` }} />
              </div>
              <span className="tnum w-8 text-right text-[10px] text-[#666]">
                {Math.round(a.w * 100)}%
              </span>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

function AIQueries({
  queries,
  loading,
}: {
  queries: AudienceQuery[];
  loading?: boolean;
}) {
  return (
    <aside className="flex h-full min-h-0 w-[280px] shrink-0 flex-col border-l-2 border-[#00d4ff] bg-[#0d0d0d]">
      <div className="shrink-0 px-3.5 pb-2 pt-3">
        <div className="flex items-center gap-2">
          <span className="eyebrow">SECTION B</span>
          {queries.length > 0 && (
            <span className="rounded bg-[#8b5cf618] px-1.5 text-[8px] text-[#8b5cf6]">
              THRAD · {queries.length}
            </span>
          )}
        </div>
        <h4 className="font-display text-lg uppercase text-white">Audience AI Queries</h4>
        <div className="mt-0.5 text-[10px] text-[#555]">
          Filled from Thrad, Reddit, SEO, Google & Tavily · DisBERT per row
        </div>
      </div>
      <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto px-3.5 pb-3.5">
        {loading && (
          <div className="text-[11px] text-[#8b5cf6]">Loading audience queries…</div>
        )}
        {!loading && queries.length === 0 ? (
          <div className="text-[11px] text-[#555]">
            Run Tavily Research to populate Section B.
          </div>
        ) : (
          queries.map((a, i) => (
            <div key={`${a.q}-${i}`} className="border border-[#1a1a1a] bg-[#111] p-2.5">
              <div className="mb-1 flex flex-wrap items-center gap-1">
                <span className="rounded bg-[#8b5cf622] px-1 text-[8px] text-[#8b5cf6]">
                  THRAD
                </span>
                {a.thrad_category && (
                  <span className="text-[8px] text-[#666]">cat {a.thrad_category}</span>
                )}
                {a.source && (
                  <span className="text-[8px] text-[#555]">{a.source}</span>
                )}
              </div>
              <div className="mb-1.5 text-xs leading-snug text-[#e6e6e6]">"{a.q}"</div>
              {a.disbert_classification && (
                <div className="mb-1 truncate text-[9px] text-[#00d4ff]">
                  DisBERT · {a.disbert_classification.replace(/_/g, " ")}
                </div>
              )}
              <div className="flex items-center gap-1.5">
                <span
                  className="pill text-[9px]"
                  style={{
                    color: intentColors[a.intent] ?? "#888",
                    background: `${intentColors[a.intent] ?? "#888"}18`,
                  }}
                >
                  {a.intent}
                </span>
                <span className="text-[9px] text-[#555]">conf {a.vol}K</span>
                <TrendArrow t={a.trend} />
                <span className="ml-auto text-[9px] text-[#666]">
                  rank <span className="text-[#8b5cf6]">{a.adRank}</span> · ctx{" "}
                  <span className="text-[#00d4ff]">{a.ctxScore}</span>
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export function MarketIntelligencePage() {
  const [sortBy, setSortBy] = useState<"trending" | "volume" | "recency">("trending");
  const [sel, setSel] = useState<string | null>(null);
  const [tavilyQuery, setTavilyQuery] = useState(DEFAULT_QUERY);
  const [isResearching, setIsResearching] = useState(false);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [audienceQueries, setAudienceQueries] = useState<AudienceQuery[]>([]);
  const [disbertSegments, setDisbertSegments] = useState<{
    total_segments: number;
    high_value_segments?: { classification: string; tavily_fields: string[] }[];
  } | null>(null);
  const [showSegments, setShowSegments] = useState(false);
  const [tavilyError, setTavilyError] = useState<string | null>(null);
  const [tavilyAnswer, setTavilyAnswer] = useState<string | null>(null);
  const autoRan = useRef(false);

  const { data: connectorHealth } = useConnectorStatus();
  const tavilyResearch = useTriggerTavilyResearch();

  const sorted = useMemo(() => {
    const a = [...trends];
    if (sortBy === "trending") a.sort((x, y) => y.growth - x.growth);
    if (sortBy === "volume") a.sort((x, y) => parseFloat(y.vol) - parseFloat(x.vol));
    if (sortBy === "recency") a.reverse();
    return a;
  }, [sortBy, trends]);

  const selT = sorted.find((t) => t.id === sel) ?? sorted[0];

  const applyResearchResult = useCallback((result: Awaited<ReturnType<typeof tavilyResearch.mutateAsync>>) => {
    if (!result.success) {
      setTavilyError(result.error || "Tavily research failed");
      adtecLog([{ msg: result.error || "Tavily research failed", tone: "err" }]);
      return;
    }

    const bundle = mapTavilyResearchResult(result);
    setTrends(bundle.trends);
    setAudienceQueries(bundle.audienceQueries);
    setTavilyAnswer(bundle.answer);
    setTavilyError(null);

    if (bundle.trends.length > 0) {
      setSel(bundle.trends[0].id);
    }

    if (result.output?.disbert_segments) {
      setDisbertSegments(result.output.disbert_segments);
      setShowSegments(true);
    }

    adtecLog(bundle.traceLines);
  }, []);

  const handleTavilyResearch = useCallback(async () => {
    if (!tavilyQuery.trim() || isResearching) return;

    setIsResearching(true);
    setShowSegments(false);
    setTavilyError(null);
    adtecLog([{ msg: `Querying Tavily + Gymshark research pipeline: "${tavilyQuery}"…`, tone: "work" }]);

    try {
      const result = await tavilyResearch.mutateAsync({
        query: tavilyQuery,
        max_results: 10,
        extract_keywords: true,
      });

      applyResearchResult(result);

      const liveLogs = await fetchAgentLogs(30);
      if (liveLogs.length) {
        adtecLog(agentLogsToTrace(liveLogs));
      }
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Tavily research failed";
      setTavilyError(msg);
      adtecLog([{ msg: `Tavily error: ${msg.slice(0, 140)}`, tone: "err" }]);
    } finally {
      setIsResearching(false);
    }
  }, [tavilyQuery, isResearching, tavilyResearch, applyResearchResult]);

  useEffect(() => {
    if (autoRan.current || !connectorHealth) return;
    if (connectorHealth.tavily === "inactive") return;
    autoRan.current = true;
    void handleTavilyResearch();
  }, [connectorHealth, handleTavilyResearch]);

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden">
      <div className="min-h-0 flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex h-full min-h-[280px] w-full min-w-[920px]">
        <section className="flex w-[min(32%,300px)] min-w-[240px] shrink-0 flex-col border-r border-[#1f1f1f]">
          <div className="flex shrink-0 flex-col gap-2 border-b border-[#1f1f1f] px-3.5 py-2.5">
            <div className="flex items-center gap-3">
              <span className="eyebrow">SECTION A · TRENDING TOPICS</span>
              {trends.length > 0 && (
                <span className="rounded bg-[#00d4ff14] px-1.5 text-[9px] text-[#00d4ff]">
                  {trends.length} LIVE
                </span>
              )}
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
                    disabled={trends.length === 0}
                    className="rounded-sm border px-1.5 py-1 text-[9px] tracking-wide disabled:opacity-40"
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

            <div className="flex gap-2">
              <input
                type="text"
                value={tavilyQuery}
                onChange={(e) => setTavilyQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleTavilyResearch()}
                placeholder="Research query for Tavily + agents"
                className="flex-1 rounded border border-[#2a2a2a] bg-[#1a1a1a] px-2 py-1 text-xs text-white placeholder-[#555] focus:border-[#00D4FF] focus:outline-none"
                disabled={isResearching}
              />
              <button
                type="button"
                onClick={() => void handleTavilyResearch()}
                disabled={isResearching || !tavilyQuery.trim()}
                className="shrink-0 rounded border border-[#00D4FF] bg-[#00d4ff14] px-3 py-1 text-xs text-[#00D4FF] hover:bg-[#00d4ff24] disabled:opacity-50"
              >
                {isResearching ? "⏳ Researching…" : "🔍 Research"}
              </button>
            </div>

            {tavilyAnswer && !tavilyError && (
              <div className="max-h-20 overflow-y-auto rounded border border-[#00d4ff22] bg-[#00d4ff08] px-2 py-1.5 text-[11px] leading-relaxed text-[#ccc]">
                <span className="font-medium text-[#00d4ff]">Tavily answer · </span>
                {tavilyAnswer}
              </div>
            )}

            {showSegments && disbertSegments && (
              <div className="rounded border border-[#2a2a2a] bg-[#1a1a1a] p-2">
                <div className="mb-1 flex justify-between text-xs text-white">
                  <span>DisBERT segments (agent mapper)</span>
                  <span className="text-[#888]">{disbertSegments.total_segments} total</span>
                </div>
                <div className="max-h-24 space-y-1 overflow-y-auto">
                  {(disbertSegments.high_value_segments ?? []).map((seg, idx) => (
                    <div
                      key={idx}
                      className="rounded border border-green-500/30 bg-green-500/10 p-1 text-[9px] text-green-400"
                    >
                      {seg.classification} · {seg.tavily_fields?.join(", ")}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {connectorHealth?.tavily !== "active" && !isResearching && trends.length === 0 && (
              <p className="text-[9px] text-[#555]">
                Configure TAVILY_API_KEY and ensure the API is online, then run Research.
              </p>
            )}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto">
            {isResearching && trends.length === 0 && (
              <div className="p-4 text-[11px] text-[#00d4ff]">
                Running Tavily search + GymsharkTavilyResearch agents…
              </div>
            )}
            {!isResearching && trends.length === 0 && (
              <div className="p-4 text-[11px] text-[#555]">
                No trends loaded. Submit a query to pull live Tavily results.
              </div>
            )}
            {sorted.map((t) => (
              <TrendCard
                key={t.id}
                t={t}
                active={t.id === (selT?.id ?? sel)}
                onClick={() => {
                  setSel(t.id);
                  adtecLog(trendTraceFromApi(t));
                }}
              />
            ))}
          </div>
        </section>

        <section className="flex min-h-0 min-w-[280px] flex-1 flex-col border-r border-[#1f1f1f] bg-[#0b0b0b]">
          <DetailPanel t={selT} />
        </section>

        <AIQueries queries={audienceQueries} loading={isResearching} />
        </div>
      </div>
    </div>
  );
}
