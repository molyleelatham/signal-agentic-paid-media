/* Terminal.jsx — global Overmind trace log (exported to window)
   Plain-English sentences. Updates ON DEMAND: listens for the
   `adtec:log` window event (fired by nav + page interactions) and a
   manual RUN button. No background timer — nothing streams on its own. */
const { useState: useStateT, useEffect: useEffectT, useRef: useRefT, useCallback } = React;

const TONE = {
  work: "#00D4FF", ok: "#00FF88", info: "#CFCFCF", warn: "#FFB800", err: "#FF4444",
};
function ts(){ const d=new Date(); const p=n=>String(n).padStart(2,"0"); return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`; }

function Terminal({ defaultOpen = true, heightPct = 20, mode = "flow" }) {
  const boot = window.ADTEC.traceScripts.boot;
  const [open, setOpen] = useStateT(defaultOpen);
  const [lines, setLines] = useStateT(() => {
    let i = 0; return boot.map(l => ({ ...l, id: i++, ts: ts() }));
  });
  const bodyRef = useRefT(null);
  const idRef = useRefT(100);

  // append a batch of sentences (capped to the last 80)
  const push = useCallback((batch) => {
    setLines(prev => {
      const add = batch.map(l => ({ ...l, id: idRef.current++, ts: ts() }));
      return [...prev, ...add].slice(-80);
    });
  }, []);

  // listen for log events fired anywhere in the app
  useEffectT(() => {
    const onLog = (e) => push(e.detail || []);
    window.addEventListener("adtec:log", onLog);
    return () => window.removeEventListener("adtec:log", onLog);
  }, [push]);

  useEffectT(() => {
    if (open && bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
  }, [lines, open]);

  const run = useCallback(() => {
    const id = window.__adtecActivePage || "intel";
    push(window.ADTEC.traceScripts[id] || []);
  }, [push]);

  const copy = useCallback(() => {
    const txt = lines.map(l => `[${l.ts}]  ${l.msg}`).join("\n");
    navigator.clipboard && navigator.clipboard.writeText(txt);
  }, [lines]);

  return (
    <div style={{ position:"relative", flex:"none", width:"100%", zIndex:60,
      background:"#0A0A0A", borderTop:"1px solid #1F1F1F",
      height: open ? `${heightPct}vh` : 34, transition:"height .2s ease",
      display:"flex", flexDirection:"column", fontFamily:"var(--mono)" }}>
      {/* header */}
      <div style={{ height:34, flex:"none", display:"flex", alignItems:"center", justifyContent:"space-between",
        padding:"0 14px", borderBottom: open?"1px solid #1F1F1F":"none", userSelect:"none" }}>
        <div style={{ display:"flex", alignItems:"center", gap:9 }}>
          <span className="dot active" style={{ width:7, height:7 }}></span>
          <span style={{ fontSize:11, letterSpacing:".16em", color:"#888" }}>OVERMIND TRACE</span>
          <span style={{ fontSize:10, color:"#444", marginLeft:4 }}>· {lines.length} events · runs on interaction</span>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:6 }}>
          {open && (
            <>
              <button onClick={run} title="Re-run the current page's agent" style={{ ...termBtn, color:"#00D4FF", borderColor:"#0c4a52" }}>▶ RUN</button>
              <button onClick={()=>setLines([])} title="Clear" style={termBtn}>CLEAR</button>
              <button onClick={copy} title="Copy" style={termBtn}>COPY</button>
            </>
          )}
          <button onClick={()=>setOpen(o=>!o)} aria-label="toggle terminal"
            style={{ width:24, height:24, borderRadius:12, background:"#1A1A1A", border:"1px solid #444",
              color:"#888", cursor:"pointer", fontSize:10, lineHeight:"22px", padding:0 }}>
            {open ? "▼" : "▲"}
          </button>
        </div>
      </div>
      {/* body */}
      {open && (
        <div ref={bodyRef} style={{ flex:1, overflowY:"auto", padding:"8px 14px 12px", fontSize:12, lineHeight:1.7 }}>
          {lines.map((l, idx) => (
            <div key={l.id} style={{ display:"flex", alignItems:"baseline", gap:10,
              animation:"fadeIn .18s ease both",
              animationDelay: idx >= lines.length-4 ? `${(idx-(lines.length-4))*0.05}s` : "0s" }}>
              <span style={{ color:"#4a4a4a", flex:"none" }}>{l.ts}</span>
              <span style={{ color: TONE[l.tone]||"#888", flex:"none", fontSize:9, lineHeight:"18px" }}>{l.tone==="work"?"›":"•"}</span>
              <span style={{ color: l.tone==="work" ? "#9a9a9a" : "#E2E2E2" }}>{l.msg}</span>
            </div>
          ))}
          {lines.length===0 && <div style={{ color:"#444", fontSize:11 }}>Cleared. Click around the dashboard, or press RUN.</div>}
        </div>
      )}
      <style>{`@keyframes fadeIn{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}`}</style>
    </div>
  );
}
const termBtn = { fontFamily:"var(--mono)", fontSize:9, letterSpacing:".1em", padding:"4px 9px",
  background:"transparent", border:"1px solid #2A2A2A", color:"#777", cursor:"pointer", borderRadius:2 };

window.Terminal = Terminal;
