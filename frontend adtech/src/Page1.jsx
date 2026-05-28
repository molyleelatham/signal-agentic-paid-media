/* Page1.jsx — Market Intelligence Panel (exported to window.Page1) */
const { useState: useS1, useMemo: useM1 } = React;

/* ---- status ribbon ---- */
function StatusRibbon() {
  const { sources } = window.ADTEC;
  const [hover, setHover] = useS1(null);
  return (
    <div style={{ position:"relative", height:48, flex:"none", background:"#111", borderBottom:"1px solid #1F1F1F",
      display:"flex", alignItems:"stretch" }}>
      {sources.map((s, i) => (
        <div key={s.id} onMouseEnter={()=>setHover(i)} onMouseLeave={()=>setHover(null)}
          style={{ flex:1, display:"flex", alignItems:"center", gap:8, padding:"0 14px",
            borderRight: i<sources.length-1?"1px solid #1A1A1A":"none", cursor:"default",
            background: hover===i?"#161616":"transparent" }}>
          <span className={"dot "+s.status} style={{ width:9, height:9 }}></span>
          <div style={{ minWidth:0 }}>
            <div style={{ fontSize:10, letterSpacing:".08em", color: s.status==="inactive"?"#666":"#DDD", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{s.label}</div>
            <div style={{ fontSize:9, color:"#555" }}>{s.sync}</div>
          </div>
          {hover===i && (
            <div style={{ position:"absolute", top:52, left: `calc(${(i+0.5)*(100/sources.length)}% - 130px)`, width:260, zIndex:50,
              background:"#0A0A0A", border:"1px solid #2A2A2A", padding:"10px 12px", boxShadow:"0 8px 24px rgba(0,0,0,.6)" }}>
              <div style={{ fontSize:10, letterSpacing:".1em", color:"#888", marginBottom:6 }}>{s.label}</div>
              <Row k="TYPE" v={s.type}/>
              <Row k="ENDPOINT" v={s.endpoint}/>
              <Row k="STATUS" v={s.note} c={s.status==="active"?"#00FF88":s.status==="degraded"?"#FFB800":"#FF4444"}/>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
function Row({ k, v, c }) {
  return (
    <div style={{ display:"flex", gap:8, fontSize:10, marginBottom:3 }}>
      <span style={{ color:"#555", width:64, flex:"none" }}>{k}</span>
      <span style={{ color:c||"#BBB", wordBreak:"break-all" }}>{v}</span>
    </div>
  );
}

const SRC_GLYPH = { T:"#00D4FF", M:"#1877F2", G:"#4285F4", TT:"#FF0050", MS:"#00A4EF" };

/* ---- trend card ---- */
function TrendCard({ t, active, onClick }) {
  const { intensityColors } = window.ADTEC;
  return (
    <div onClick={onClick} style={{ display:"flex", alignItems:"center", gap:10, height:62, padding:"0 12px 0 0",
      background: active?"#161616":"#111", borderBottom:"1px solid #1A1A1A", cursor:"pointer",
      borderLeft:`4px solid ${intensityColors[t.intensity]}`, transition:"background .12s" }}>
      <div style={{ flex:1, minWidth:0, paddingLeft:12 }}>
        <div style={{ fontFamily:"var(--disp)", fontWeight:700, fontSize:16, color: active?"#fff":"#EAEAEA",
          textTransform:"uppercase", letterSpacing:"-0.01em", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{t.kw}</div>
        <div style={{ display:"flex", gap:4, marginTop:2 }}>
          {t.src.map(s=>(
            <span key={s} style={{ fontSize:8, width:15, height:13, lineHeight:"13px", textAlign:"center",
              borderRadius:2, color:SRC_GLYPH[s], border:`1px solid ${SRC_GLYPH[s]}55` }}>{s}</span>
          ))}
          <span style={{ fontSize:10, color:"#555", marginLeft:4 }}>{t.vol}</span>
        </div>
      </div>
      <Spark data={t.spark} color={intensityColors[t.intensity]} w={56} h={24}/>
      <GrowthBadge v={t.growth}/>
    </div>
  );
}

/* ---- detail panel ---- */
function DetailPanel({ t }) {
  const { platformColors } = window.ADTEC;
  if (!t) return <div style={{ padding:24, color:"#555", fontSize:12 }}>Select a trend to inspect →</div>;
  return (
    <div style={{ padding:"16px 18px", overflowY:"auto", height:"100%" }}>
      <div className="eyebrow">TREND DETAIL · SUPABASE market_signals</div>
      <h3 style={{ fontSize:26, textTransform:"uppercase", color:"#fff", margin:"4px 0 2px" }}>{t.kw}</h3>
      <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:14 }}>
        <GrowthBadge v={t.growth}/>
        <span style={{ fontSize:11, color:"#666" }}>{t.vol} mentions · 7d</span>
        <span style={{ marginLeft:"auto", fontSize:11, color:"#00D4FF" }}>RELEVANCE {t.detail.relevance}/100</span>
      </div>
      {/* relevance bar */}
      <div style={{ height:4, background:"#1A1A1A", marginBottom:18 }}>
        <div style={{ height:"100%", width:t.detail.relevance+"%", background:"linear-gradient(90deg,#00FF88,#00D4FF)" }}></div>
      </div>
      <div className="eyebrow" style={{ marginBottom:6 }}>VOLUME OVER TIME · 12W</div>
      <LineChart series={[{ name:"vol", color:"#00D4FF", data:t.detail.vol12 }]}
        labels={["","","","","","","","","","","",""]} w={300} h={120} animateKey={t.id}/>
      <div className="eyebrow" style={{ margin:"16px 0 8px" }}>COMPETITIVE BID SIGNAL</div>
      <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
        {["meta","google","tiktok","msft"].map(p=>{
          const on = t.detail.bidders.includes(p);
          const c = { meta:"#1877F2",google:"#4285F4",tiktok:"#FF0050",msft:"#00A4EF" }[p];
          return <span key={p} className="pill" style={{ color:on?c:"#555", background:on?c+"1A":"#141414", border:`1px solid ${on?c+"44":"#222"}` }}>
            {p.toUpperCase()} {on?"BIDDING":"—"}</span>;
        })}
      </div>
      <div className="eyebrow" style={{ margin:"16px 0 8px" }}>SOURCE ATTRIBUTION</div>
      {t.detail.attribution.map((a,i)=>(
        <div key={i} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:5 }}>
          <span style={{ fontSize:10, color:"#999", width:150, flex:"none" }}>{a.src}</span>
          <div style={{ flex:1, height:5, background:"#1A1A1A" }}>
            <div style={{ height:"100%", width:(a.w*100)+"%", background:"#00FF88", opacity:.8 }}></div>
          </div>
          <span className="tnum" style={{ fontSize:10, color:"#666", width:32, textAlign:"right" }}>{Math.round(a.w*100)}%</span>
        </div>
      ))}
    </div>
  );
}

/* ---- audience AI queries column ---- */
function AIQueries() {
  const { aiQueries, intentColors } = window.ADTEC;
  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", background:"#0D0D0D", borderLeft:"1px solid #1F1F1F", borderTop:"2px solid #00D4FF" }}>
      <div style={{ padding:"12px 14px 8px", flex:"none" }}>
        <div className="eyebrow">SECTION B</div>
        <h4 style={{ fontSize:17, color:"#fff", textTransform:"uppercase" }}>Audience AI Queries</h4>
        <div style={{ fontSize:10, color:"#555", marginTop:2 }}>What people ask ChatGPT · Gemini · Perplexity</div>
      </div>
      <div style={{ flex:1, overflowY:"auto", padding:"0 14px 14px", display:"flex", flexDirection:"column", gap:8 }}>
        {aiQueries.map((a,i)=>(
          <div key={i} style={{ background:"#111", border:"1px solid #1A1A1A", padding:"9px 11px" }}>
            <div style={{ fontSize:12, color:"#E6E6E6", lineHeight:1.35, marginBottom:7 }}>“{a.q}”</div>
            <div style={{ display:"flex", alignItems:"center", gap:7 }}>
              <span className="pill" style={{ color:intentColors[a.intent], background:intentColors[a.intent]+"18" }}>{a.intent}</span>
              <span style={{ fontSize:9, color:"#555" }}>vol {a.vol}K</span>
              <TrendArrow t={a.trend}/>
              <span title="Thrads contextual bid" style={{ marginLeft:"auto", fontSize:9, color:"#666" }}>
                rank <span style={{color:"#8B5CF6"}}>{a.adRank}</span> · ctx <span style={{color:"#00D4FF"}}>{a.ctxScore}</span>
              </span>
            </div>
          </div>
        ))}
        <div style={{ fontSize:9, color:"#444", lineHeight:1.5, marginTop:2, borderTop:"1px dashed #222", paddingTop:8 }}>
          ⓘ Wired to <span style={{color:"#8B5CF6"}}>POST api.thrads.ai/v1/bid-request</span> — each query fires a contextual bid; ad_rank + context_score overlaid above.
        </div>
      </div>
    </div>
  );
}

function Page1() {
  const { trends } = window.ADTEC;
  const [sortBy, setSortBy] = useS1("trending");
  const [sel, setSel] = useS1(trends[0].id);
  const sorted = useM1(()=>{
    const a = [...trends];
    if (sortBy==="trending") a.sort((x,y)=>y.growth-x.growth);
    if (sortBy==="volume") a.sort((x,y)=>parseFloat(y.vol)-parseFloat(x.vol));
    return a;
  },[sortBy]);
  const selT = trends.find(t=>t.id===sel);
  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%" }}>
      <StatusRibbon/>
      <div style={{ flex:1, display:"grid", gridTemplateColumns:"minmax(340px,1.05fr) 1.2fr minmax(280px,0.95fr)", minHeight:0 }}>
        {/* feed list */}
        <div style={{ display:"flex", flexDirection:"column", borderRight:"1px solid #1F1F1F", minHeight:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:12, padding:"10px 14px", borderBottom:"1px solid #1F1F1F", flex:"none" }}>
            <span className="eyebrow">SECTION A · TRENDING TOPICS</span>
            <div style={{ marginLeft:"auto", display:"flex", gap:4 }}>
              {[["trending","TRENDING ↑"],["volume","VOLUME"],["recency","RECENCY"]].map(([k,l])=>(
                <button key={k} onClick={()=>setSortBy(k)} style={{ fontFamily:"var(--mono)", fontSize:9, letterSpacing:".06em",
                  padding:"4px 7px", border:"1px solid "+(sortBy===k?"#00D4FF":"#222"), color:sortBy===k?"#00D4FF":"#666",
                  background:sortBy===k?"#00d4ff14":"transparent", cursor:"pointer", borderRadius:2 }}>{l}</button>
              ))}
            </div>
          </div>
          <div style={{ flex:1, overflowY:"auto", minHeight:0 }}>
            {sorted.map(t=><TrendCard key={t.id} t={t} active={t.id===sel} onClick={()=>{ setSel(t.id); window.adtecLog && window.adtecLog(window.ADTEC.trendTrace(t)); }}/>)}
          </div>
        </div>
        {/* detail */}
        <div style={{ borderRight:"1px solid #1F1F1F", minHeight:0, background:"#0B0B0B" }}>
          <DetailPanel t={selT}/>
        </div>
        {/* AI queries */}
        <AIQueries/>
      </div>
    </div>
  );
}
window.Page1 = Page1;
