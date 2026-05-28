import { useState } from "react";
import { DATA_CONNECTOR_IDS } from "../../config/connectors";
import { useConnectorStatus } from "../../hooks/useConnectorStatus";

type SourceStatus = "active" | "degraded" | "inactive";

const ACCENT: Record<string, string> = {
  tavily: "#00D4FF",
  meta_mcp: "#1877F2",
  google_ads: "#4285F4",
  ads_manager: "#1877F2",
  reddit: "#FF4500",
  thrad: "#8B5CF6",
};

function MetaRow({ k, v, c }: { k: string; v: string; c?: string }) {
  return (
    <div className="mb-0.5 flex gap-2 text-[10px]">
      <span className="w-16 shrink-0 text-[#555]">{k}</span>
      <span style={{ color: c || "#bbb" }} className="break-all">
        {v}
      </span>
    </div>
  );
}

/**
 * CONNECTORS ribbon — directly under the main header nav.
 * Shows Tavily, Meta MCP, Google Ads, Ads Manager, Reddit, Thrad.
 */
export function ConnectorsBar() {
  const [hover, setHover] = useState<string | null>(null);
  const { data: health, isError, isLoading, error, refetch, isFetching } = useConnectorStatus();

  const sources = health?.connectors ?? [];

  return (
    <div className="relative flex shrink-0 flex-col border-t border-[#1a1a1a] bg-[#111]">
      {isError && (
        <div className="flex items-center justify-between gap-2 border-b border-[#ff444422] bg-[#ff444410] px-3 py-0.5 text-[9px] text-[#ff8888]">
          <span className="truncate">
            {error instanceof Error ? error.message : "Backend connection failed"}
          </span>
          <button
            type="button"
            onClick={() => refetch()}
            className="shrink-0 text-[#00d4ff] hover:underline"
          >
            Retry
          </button>
        </div>
      )}
      <div className="flex h-11 items-stretch">
        <div className="flex shrink-0 flex-col justify-center border-r border-[#1a1a1a] px-3 py-1">
          <span className="text-[8px] tracking-[0.2em] text-[#555]">CONNECTORS</span>
          <span className="text-[8px] text-[#444]">{DATA_CONNECTOR_IDS.length} sources</span>
          {isFetching && !isLoading && (
            <span className="text-[8px] text-[#00d4ff]">↻</span>
          )}
        </div>
        <div className="flex min-w-0 flex-1 overflow-x-auto">
          {isLoading && sources.length === 0 && (
            <div className="flex items-center px-3 text-[10px] text-[#555]">
              Loading connectors…
            </div>
          )}
          {sources.map((s, i) => {
            const accent = ACCENT[s.id] ?? "#666";
            const isActive = s.status === "active";
            return (
              <div
                key={s.id}
                onMouseEnter={() => setHover(s.id)}
                onMouseLeave={() => setHover(null)}
                className="relative flex min-w-[128px] shrink-0 cursor-default items-center gap-2 px-3"
                style={{
                  borderRight: i < sources.length - 1 ? "1px solid #1A1A1A" : undefined,
                  background:
                    hover === s.id
                      ? "#161616"
                      : isActive
                        ? `${accent}12`
                        : undefined,
                }}
              >
                <span
                  className={`dot ${s.status as SourceStatus} h-2 w-2 shrink-0`}
                  style={isActive ? { boxShadow: `0 0 6px ${accent}` } : undefined}
                />
                <div className="min-w-0">
                  <div
                    className="truncate text-[10px] font-medium tracking-wide"
                    style={{ color: isActive ? accent : "#ddd" }}
                  >
                    {s.label}
                  </div>
                  <div className="truncate text-[9px] text-[#555]">{s.sync}</div>
                </div>
                {hover === s.id && (
                  <div className="absolute left-0 top-full z-[60] mt-0 w-[280px] border border-[#2a2a2a] bg-[#0a0a0a] p-3 shadow-xl">
                    <div className="eyebrow mb-1.5" style={{ color: accent }}>
                      {s.label}
                    </div>
                    {s.type && <MetaRow k="TYPE" v={s.type} />}
                    {s.endpoint && <MetaRow k="ENDPOINT" v={s.endpoint} />}
                    <MetaRow
                      k="STATUS"
                      v={s.note}
                      c={
                        s.status === "active"
                          ? "#00FF88"
                          : s.status === "degraded"
                            ? "#FFB800"
                            : "#FF4444"
                      }
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
