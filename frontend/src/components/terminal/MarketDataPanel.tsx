import type { AlgorithmScore } from "../../types/terminal";

export function MarketDataPanel({ scores }: { scores: AlgorithmScore[] }) {
  const avg =
    scores.length > 0
      ? scores.reduce((a, s) => a + s.score, 0) / scores.length
      : 0;
  const sentiment = avg >= 90 ? "Bullish" : avg >= 80 ? "Neutral" : "Cautious";

  return (
    <section className="flex min-h-0 flex-col overflow-hidden rounded border border-[#1f1f1f] bg-[#1a1a1a]">
      <div className="panel-header">
        <h2 className="panel-title">Market Data</h2>
      </div>
      <div className="flex-1 space-y-3 p-3">
        <Row label="Volume" value="+12%" positive />
        <Row label="Trend" value="↑ Momentum" positive />
        <Row label="Sentiment" value={sentiment} positive={sentiment === "Bullish"} />
        <div className="border-t border-[#2a2a2a] pt-2">
          <div className="mb-2 text-[9px] tracking-widest text-[#666]">
            Algorithm Health
          </div>
          {scores.map((s) => (
            <div key={s.name} className="mb-2 flex items-center gap-2">
              <span className="w-24 truncate text-[11px] text-[#aaa]">
                {s.name}
              </span>
              <div className="h-1.5 flex-1 overflow-hidden rounded bg-[#333]">
                <div
                  className="h-full rounded bg-[#00bfff]"
                  style={{ width: `${s.score}%` }}
                />
              </div>
              <span className="tnum w-8 text-right text-[10px] text-[#888]">
                {s.score}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Row({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-[10px] tracking-wider text-[#666]">{label}</span>
      <span
        className={`tnum font-display text-sm font-medium ${
          positive ? "text-[#00ff00]" : "text-[#ccc]"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
