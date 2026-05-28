import { useMemo, useState } from "react";
import { sources as staticSources } from "../../data/adtec";
import { useConnectorStatus } from "../../hooks/useConnectorStatus";

type SourceStatus = "active" | "degraded" | "inactive";

interface ConnectorSource {
  id: string;
  label: string;
  status: SourceStatus;
  sync: string;
  type: string;
  endpoint: string;
  note: string;
}

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

/** Data source connectors — global status ribbon in app header */
export function ConnectorsBar() {
  const [hover, setHover] = useState<number | null>(null);
  const { data: health, isError, isLoading } = useConnectorStatus();

  const sources = useMemo((): ConnectorSource[] => {
    const tavilyOk = health?.tavily === "configured";
    return staticSources.map((s) => {
      if (s.id !== "tavily") return s;
      return {
        ...s,
        status: isError
          ? ("inactive" as const)
          : isLoading
            ? ("degraded" as const)
            : tavilyOk
              ? ("active" as const)
              : ("inactive" as const),
        sync: isLoading
          ? "checking…"
          : isError
            ? "API offline"
            : tavilyOk
              ? "connected"
              : "no API key",
        endpoint: "api.tavily.com/search",
        note: tavilyOk
          ? "Live Tavily search · include_answer"
          : "Set TAVILY_API_KEY in .env.local",
      };
    });
  }, [health, isError, isLoading]);

  return (
    <div className="relative flex h-10 shrink-0 items-stretch border-t border-[#1a1a1a] bg-[#111]">
      <div className="flex shrink-0 items-center border-r border-[#1a1a1a] px-3">
        <span className="text-[8px] tracking-[0.2em] text-[#555]">CONNECTORS</span>
      </div>
      <div className="flex min-w-0 flex-1 overflow-x-auto">
        {sources.map((s, i) => (
          <div
            key={s.id}
            onMouseEnter={() => setHover(i)}
            onMouseLeave={() => setHover(null)}
            className={`relative flex min-w-[120px] flex-1 cursor-default items-center gap-2 px-3 ${
              s.id === "tavily" && s.status === "active" ? "bg-[#00d4ff08]" : ""
            }`}
            style={{
              borderRight: i < sources.length - 1 ? "1px solid #1A1A1A" : undefined,
              background: hover === i ? "#161616" : undefined,
            }}
          >
            <span className={`dot ${s.status} h-2 w-2 shrink-0`} />
            <div className="min-w-0">
              <div className="truncate text-[10px] tracking-wide text-[#ddd]">{s.label}</div>
              <div className="truncate text-[9px] text-[#555]">{s.sync}</div>
            </div>
            {hover === i && (
              <div className="absolute left-1/2 top-full z-[60] mt-1 w-[260px] -translate-x-1/2 border border-[#2a2a2a] bg-[#0a0a0a] p-3 shadow-xl">
                <div className="eyebrow mb-1.5">{s.label}</div>
                <MetaRow k="TYPE" v={s.type} />
                <MetaRow k="ENDPOINT" v={s.endpoint} />
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
        ))}
      </div>
    </div>
  );
}
