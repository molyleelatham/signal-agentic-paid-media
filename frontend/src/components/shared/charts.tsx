import { useEffect, useRef, useState } from "react";

export function Spark({
  data,
  w = 60,
  h = 22,
  color = "#00FF88",
  fill = true,
}: {
  data: number[];
  w?: number;
  h?: number;
  color?: string;
  fill?: boolean;
}) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const rng = max - min || 1;
  const pts = data.map((v, i) => [
    (i / (data.length - 1)) * w,
    h - ((v - min) / rng) * (h - 3) - 1.5,
  ]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const area = `${d} L ${w} ${h} L 0 ${h} Z`;
  return (
    <svg width={w} height={h} className="block overflow-visible">
      {fill && <path d={area} fill={color} opacity={0.1} />}
      <path d={d} fill="none" stroke={color} strokeWidth={1.2} />
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r={1.8} fill={color} />
    </svg>
  );
}

export function LineChart({
  series,
  labels,
  w = 360,
  h = 200,
  pad = 28,
  animateKey,
  highlight,
}: {
  series: { name: string; color: string; data: number[] }[];
  labels?: string[];
  w?: number;
  h?: number;
  pad?: number;
  animateKey?: string;
  highlight?: number[];
}) {
  const ref = useRef<SVGSVGElement>(null);
  const all = series.flatMap((s) => s.data);
  const min = Math.min(...all);
  const max = Math.max(...all);
  const rng = max - min || 1;
  const n = series[0]?.data.length || 1;
  const X = (i: number) =>
    n <= 1 ? pad + (w - pad * 1.4) / 2 : pad + (i / (n - 1)) * (w - pad * 1.4);
  const Y = (v: number) => h - pad - ((v - min) / rng) * (h - pad * 1.6);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.querySelectorAll("path.ln").forEach((p) => {
      const path = p as SVGPathElement;
      const len = path.getTotalLength();
      path.style.transition = "none";
      path.style.strokeDasharray = String(len);
      path.style.strokeDashoffset = String(len);
      void path.getBoundingClientRect();
      path.style.transition = "stroke-dashoffset .55s ease";
      path.style.strokeDashoffset = "0";
    });
  }, [animateKey]);

  return (
    <svg ref={ref} width={w} height={h} className="block">
      {highlight?.map((hi) => {
        const bw = (w - pad * 1.4) / (n - 1);
        return (
          <rect
            key={hi}
            x={X(hi) - bw * 0.4}
            y={pad * 0.4}
            width={bw * 0.8}
            height={h - pad * 1.6}
            fill="#00D4FF"
            opacity={0.07}
          />
        );
      })}
      {[0, 0.5, 1].map((g, i) => (
        <line
          key={i}
          x1={pad}
          x2={w - pad * 0.4}
          y1={pad * 0.6 + (h - pad * 2.2) * g}
          y2={pad * 0.6 + (h - pad * 2.2) * g}
          stroke="#1F1F1F"
          strokeWidth={1}
        />
      ))}
      {labels?.map((l, i) => (
        <text key={i} x={X(i)} y={h - 8} fontSize={9} fill="#666" textAnchor="middle">
          {l}
        </text>
      ))}
      {series.map((s, si) => (
        <path
          key={si}
          className="ln"
          d={s.data.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ")}
          fill="none"
          stroke={s.color}
          strokeWidth={1.6}
        />
      ))}
      {series.flatMap((s, si) =>
        s.data.map((v, i) => (
          <circle key={`${si}-${i}`} cx={X(i)} cy={Y(v)} r={2} fill={s.color} />
        )),
      )}
    </svg>
  );
}

export function DecayCurve({
  data,
  w = 120,
  h = 30,
  color = "#00FF88",
}: {
  data: number[];
  w?: number;
  h?: number;
  color?: string;
}) {
  const max = Math.max(...data) || 1;
  const pts = data.map((v, i) => [(i / (data.length - 1)) * w, h - (v / max) * (h - 2) - 1]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  return (
    <svg width={w} height={h} className="block">
      <path d={`${d} L ${w} ${h} L 0 ${h} Z`} fill={color} opacity={0.08} />
      <path d={d} fill="none" stroke={color} strokeWidth={1.3} />
    </svg>
  );
}

export function TrendArrow({ t }: { t: "up" | "down" | "flat" }) {
  const m: Record<string, [string, string]> = {
    up: ["↑", "#00FF88"],
    down: ["↓", "#FF4444"],
    flat: ["→", "#A0A0A0"],
  };
  const [glyph, color] = m[t] || ["→", "#A0A0A0"];
  return <span style={{ color, fontWeight: 600 }}>{glyph}</span>;
}

export function GrowthBadge({ v }: { v: number }) {
  const up = v >= 0;
  return (
    <span className={`pill text-[10px] ${up ? "badge-up" : "badge-down"}`}>
      {up ? "+" : ""}
      {v}%
    </span>
  );
}

export function useCountUp(target: number, dur = 900, run = true) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!run) {
      setVal(target);
      return;
    }
    let raf: number;
    let start: number;
    const tick = (t: number) => {
      if (!start) start = t;
      const p = Math.min(1, (t - start) / dur);
      setVal(target * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, run, dur]);
  return val;
}
