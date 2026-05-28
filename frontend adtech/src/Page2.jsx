/* Page2.jsx — Strategy Generator (exported to window.Page2) */
const { useState: useS2, useMemo: useM2, useRef: useR2, useEffect: useE2 } = React;

/* stacked, clickable quarterly bar chart */
function FunnelBars({ sel, setSel, stageFilter, setStageFilter }) {
  const { quarters, funnelStages } = window.ADTEC;
  const maxTotal = Math.max(...quarters.map(q => funnelStages.reduce((s,st)=>s+q.stages[st.id],0)));
  const onBar = (i, e) => {
    setSel(prev => {
      if (e.shiftKey) return prev.includes(i) ? prev.filter(x=>x!==i) : [...prev, i];
      return prev.length===1 && prev[0]===i ? [] : [i];
    });
  };
  return (
    <div style={{ flex:1, display:"flex", flexDirection:"column", minWidth:0 }}>
      <div className="eyebrow" style={{ padding:"0 0 8px" }}>QUARTERLY CAMPAIGN VOLUME · CLICK BAR · SHIFT+CLICK MULTI</div>
      <div style={{ flex:1, display:"flex", alignItems:"flex-end", gap:18, padding:"0 8px", minHeight:0 }}>
        {quarters.map((q,i)=>{
          const total = funnelStages.reduce((s,st)=>s+q.stages[st.id],0);
          const dim = sel.length>0 && !sel.includes(i);
          const on = sel.includes(i);
          return (
            <div key={q.q} onClick={(e)=>onBar(i,e)} style={{ flex:1, display:"flex", flexDirection:"column",
              alignItems:"center", gap:8, cursor:"pointer", height:"100%", justifyContent:"flex-end" }}>
              <div style={{ width:"100%", maxWidth:88, display:"flex", flexDirection:"column-reverse",
                height: (total/maxTotal*100)+"%", outline: on?"2px solid #fff":"none", outlineOffset:2,
                transform: on?"translateY(-3px)":"none", opacity: dim?0.4:1, transition:"all .2s" }}>
                {funnelStages.map(st=>{
                  const v = q.stages[st.id];
                  const faded = stageFilter && stageFilter!==st.id;
                  return <div key={st.id} title={`${st.label} ${v}`} style={{ height:(v/total*100)+"%",
                    background:st.color, opacity:faded?0.15:1, transition:"opacity .2s" }}></div>;
                })}
              </div>
              <span className="tnum" style={{ fontSize:13, fontFamily:"var(--disp)", fontWeight:700, color:on?"#fff":"#888" }}>{q.q}</span>
            </div>
          );
        })}
      </div>
      {/* legend */}
      <div style={{ display:"flex", gap:12, flexWrap:"wrap", padding:"12px 4px 0" }}>
        {funnelStages.map(st=>(
          <button key={st.id} onClick={()=>setStageFilter(f=>f===st.id?null:st.id)}
            style={{ display:"flex", alignItems:"center", gap:6, background:"none", border:"none", cursor:"pointer",
              opacity: stageFilter && stageFilter!==st.id?0.4:1 }}>
            <span style={{ width:10, height:10, background:st.color }}></span>
            <span style={{ fontSize:9.5, letterSpacing:".06em", color:"#999" }}>{st.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function StrategyPanel({ open, onClose, sel }) {
  const { quarters } = window.ADTEC;
  const [text, setText] = useS2("");
  const [loading, setLoading] = useS2(false);
  const canned = useM2(()=>{
    const qs = (sel.length?sel:[0,1,2,3]).map(i=>quarters[i].q).join(", ");
    return [
      { h:"CAMPAIGN THEME", b:`"Squat-Proof Season" — lead with the scrunch leggings +34% signal across ${qs}. Anchor creative on the Vital Seamless 2.0 squat-proof proof-point that audiences are actively asking AI about.` },
      { h:"CHANNEL MIX", b:"Shift 18% of Meta Advantage+ budget into TikTok Spark Ads to ride the scrunch + blackout-restock momentum. Hold Google PMax as the demand-capture floor; pause Microsoft until auth is restored." },
      { h:"BUDGET REALLOCATION", b:"£62.4K → reweight: TikTok 32% (+8pt), Meta 28% (−6pt), Google 24%, Influencer 16%. Projected CPL £4.20 → £3.90, ROAS 4.2× → 4.6×." },
      { h:"RISK FLAGS", b:"⚠ Interest→Consideration drop-off at 34% — add a mid-funnel retargeting layer. TikTok source is rate-limited; cap daily spend until sync stabilises." },
    ];
  },[sel]);

  useE2(()=>{
    if(!open) return;
    setLoading(true); setText("");
    let cancelled = false;
    const run = async ()=>{
      let full = "";
      if (window.claude && window.claude.complete) {
        try {
          const ctx = `Selected quarters: ${(sel.length?sel:[0,1,2,3]).map(i=>quarters[i].q).join(", ")}. KPIs: leads 14230, CPL £4.20, ROAS 4.2x, drop-off 34%.`;
          full = await window.claude.complete(`You are a performance marketing strategist for Gymshark UK. Based on this quarterly campaign data, write a concise strategy with sections CAMPAIGN THEME, CHANNEL MIX, BUDGET REALLOCATION, RISK FLAGS. ${ctx}`);
        } catch(e){ full = ""; }
      }
      if (!full) full = canned.map(s=>`§ ${s.h}\n${s.b}`).join("\n\n");
      // stream it
      for (let i=0;i<=full.length;i+=3){ if(cancelled) return; setText(full.slice(0,i)); await new Promise(r=>setTimeout(r,8)); }
      if(!cancelled){ setText(full); setLoading(false); }
    };
    run();
    return ()=>{ cancelled = true; };
  },[open]);

  return (
    <div style={{ position:"absolute", top:0, right:0, bottom:0, width:380, zIndex:70, background:"#0A0A0A",
      borderLeft:"1px solid #2A2A2A", transform: open?"translateX(0)":"translateX(105%)", transition:"transform .35s cubic-bezier(.4,0,.1,1)",
      display:"flex", flexDirection:"column", boxShadow:"-20px 0 40px rgba(0,0,0,.5)" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"12px 14px", borderBottom:"1px solid #1F1F1F" }}>
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <span className="dot active" style={{width:7,height:7}}></span>
          <span style={{ fontSize:11, letterSpacing:".12em", color:"#ccc" }}>STRATEGY · claude-sonnet</span>
        </div>
        <button onClick={onClose} style={{ background:"none", border:"1px solid #2A2A2A", color:"#888", cursor:"pointer", width:22, height:22, borderRadius:2, fontSize:11 }}>✕</button>
      </div>
      <div style={{ flex:1, overflowY:"auto", padding:"14px 16px", fontSize:12, lineHeight:1.6, color:"#D6D6D6", whiteSpace:"pre-wrap" }}>
        {text.split("\n\n").map((blk,i)=>{
          const isH = blk.startsWith("§ ");
          const lines = blk.split("\n");
          return <div key={i} style={{ marginBottom:14 }}>
            {lines[0].startsWith("§ ")
              ? <><div style={{ fontFamily:"var(--mono)", fontSize:10, letterSpacing:".14em", color:"#00D4FF", marginBottom:4 }}>{lines[0].slice(2)}</div>
                  <div>{lines.slice(1).join("\n")}</div></>
              : <div>{blk}</div>}
          </div>;
        })}
        {loading && <span style={{ display:"inline-block", width:7, height:13, background:"#00FF88", animation:"blink .8s infinite", verticalAlign:"middle" }}></span>}
      </div>
      <div style={{ padding:"10px 14px", borderTop:"1px solid #1F1F1F", fontSize:9, color:"#555" }}>
        ⓘ Grounded via <span style={{color:"#00D4FF"}}>tvly.research()</span> · streamed from Anthropic <span style={{color:"#8B5CF6"}}>/v1/messages</span> · trace #1042
      </div>
    </div>
  );
}

function Page2() {
  const { quarters, kpiRows } = window.ADTEC;
  const [sel, setSel] = useS2([2]);          // selected bar indices
  const [stageFilter, setStageFilter] = useS2(null);
  const [panel, setPanel] = useS2(false);
  const useQ = sel.length ? sel : [0,1,2,3];
  const lineSeries = useM2(()=>{
    // always plot the full quarterly trajectory; selection is conveyed by the bars + KPI strip
    return [
      { name:"Leads (k)", color:"#00D4FF", data:quarters.map(q=>q.leads/1000) },
      { name:"Spend (£k)", color:"#8B5CF6", data:quarters.map(q=>q.spend/1000) },
      { name:"CPL (×10)", color:"#FFB800", data:quarters.map(q=>q.cpl*10) },
    ];
  },[sel.join(",")]);
  const labels = quarters.map(q=>q.q);

  return (
    <div style={{ position:"relative", height:"100%", display:"flex", flexDirection:"column" }}>
      {/* generate button */}
      <div style={{ position:"absolute", top:12, right:16, zIndex:30 }}>
        <button className="btn btn-primary" onClick={()=>{ setPanel(true); window.adtecLog && window.adtecLog(window.ADTEC.traceScripts.strategy); }}>GENERATE STRATEGY ↗</button>
      </div>
      {/* charts */}
      <div style={{ flex:1, display:"grid", gridTemplateColumns:"1fr 1fr", gap:0, minHeight:0 }}>
        <div style={{ padding:"16px 18px", borderRight:"1px solid #1F1F1F", display:"flex", flexDirection:"column" }}>
          <FunnelBars sel={sel} setSel={setSel} stageFilter={stageFilter} setStageFilter={setStageFilter}/>
        </div>
        <div style={{ padding:"16px 18px", display:"flex", flexDirection:"column" }}>
          <div className="eyebrow" style={{ marginBottom:8 }}>
            LEADS · SPEND · CPL {sel.length?`· ${sel.length} period(s) selected`:"· FULL YEAR"}
          </div>
          <div style={{ flex:1, display:"flex", alignItems:"center", minHeight:0 }}>
            <LineChart series={lineSeries} labels={labels} w={420} h={210} animateKey={sel.join(",")} highlight={sel}/>
          </div>
          <div style={{ display:"flex", gap:14, paddingTop:4 }}>
            {lineSeries.map(s=>(
              <div key={s.name} style={{ display:"flex", alignItems:"center", gap:6 }}>
                <span style={{ width:14, height:2, background:s.color }}></span>
                <span style={{ fontSize:9.5, color:"#999" }}>{s.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      {/* KPI strip */}
      <div style={{ flex:"none", height: sel.length?92:0, overflow:"hidden", transition:"height .3s ease",
        borderTop:"1px solid #1F1F1F", background:"#0B0B0B", display:"flex" }}>
        {kpiRows.map((k,i)=>(
          <div key={i} style={{ flex:1, padding:"12px 16px", borderRight:i<kpiRows.length-1?"1px solid #1A1A1A":"none" }}>
            <div style={{ fontSize:9.5, letterSpacing:".08em", color:"#666", textTransform:"uppercase", marginBottom:5 }}>{k.k}</div>
            <div className="tnum" style={{ fontFamily:"var(--disp)", fontWeight:700, fontSize:24, color:"#fff", lineHeight:1 }}>{k.v}</div>
            <div className="pill" style={{ marginTop:5, padding:"1px 0",
              color: k.tone==="good"?"#00FF88":k.tone==="warn"?"#FFB800":"#999", background:"none" }}>{k.b}</div>
          </div>
        ))}
      </div>
      <StrategyPanel open={panel} onClose={()=>setPanel(false)} sel={sel}/>
    </div>
  );
}
window.Page2 = Page2;
