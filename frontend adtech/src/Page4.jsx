/* Page4.jsx — Campaign Performance (exported to window.Page4) */
const { useState: useS4, useEffect: useE4 } = React;

const SIGNAL = {
  BUY:  { c:"#00FF88", bg:"rgba(0,255,136,.12)", note:"Adstock depleted — re-invest now" },
  HOLD: { c:"#FFB800", bg:"rgba(255,184,0,.12)", note:"Signal still active — do not cut spend" },
  SELL: { c:"#FF4444", bg:"rgba(255,68,68,.12)", note:"Diminishing returns — pause or redirect" },
};

function KpiCard({ k, expanded, onToggle, run }) {
  return (
    <div onClick={onToggle} style={{ flex:1, background:"#111", border:"1px solid #1F1F1F",
      borderLeft:`3px solid ${k.cat}`, padding:"12px 14px", cursor:"pointer", minWidth:0 }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
        <div>
          <div style={{ fontSize:9.5, letterSpacing:".08em", color:"#777", textTransform:"uppercase" }}>{k.title}</div>
          <div className="tnum" style={{ fontFamily:"var(--disp)", fontWeight:800, fontSize:30, color:"#fff", lineHeight:1.05 }}>{k.value}</div>
        </div>
        {k.spark && <Spark data={k.spark} color={k.cat} w={56} h={26}/>}
        {k.delta && <span className="pill badge-up">{k.delta}</span>}
      </div>
      <div style={{ fontSize:10, color:"#666", marginTop:6 }}>{k.sub}</div>
      {/* retention heatmap */}
      {k.heat && <div style={{ display:"grid", gridTemplateColumns:"repeat(6,1fr)", gap:2, marginTop:8 }}>
        {k.heat.map((v,i)=><div key={i} title={v+"%"} style={{ aspectRatio:"1.6", background:`rgba(16,185,129,${0.15+v/130})` }}></div>)}
      </div>}
      {k.before!=null && <div style={{ display:"flex", alignItems:"center", gap:8, marginTop:8 }}>
        <span style={{ fontSize:11, color:"#666" }} className="tnum">{k.before}%</span>
        <span style={{ color:"#444" }}>→</span>
        <span style={{ fontSize:11, color:"#00FF88" }} className="tnum">{k.after}%</span>
      </div>}
      {expanded && <div style={{ marginTop:10, paddingTop:10, borderTop:"1px solid #1F1F1F", fontSize:10, color:"#888", lineHeight:1.5 }}>
        Detail drawer · channel breakdown synced from <span style={{color:"#00FF88"}}>supabase.campaign_kpis</span>. Trace span captured by Overmind Optimizer.
      </div>}
    </div>
  );
}

function BeforeAfter({ run }) {
  const { beforeAfter } = window.ADTEC;
  return (
    <div style={{ display:"flex", flexDirection:"column", height:"100%", borderRight:"1px solid #1F1F1F" }}>
      <div style={{ padding:"12px 16px 8px", flex:"none" }}>
        <div className="eyebrow">SECTION B · SIGNAL COMPARISON</div>
        <div style={{ fontSize:10, color:"#555", marginTop:2 }}>Overmind trace analysis · #1031 → #1042</div>
      </div>
      <div style={{ flex:1, display:"flex", minHeight:0 }}>
        <div style={{ flex:1, padding:"6px 16px", display:"flex", flexDirection:"column", justifyContent:"center", gap:14, opacity:.6 }}>
          <div className="eyebrow" style={{ color:"#555" }}>BEFORE</div>
          {beforeAfter.map(b=><div key={b.k}>
            <div style={{ fontSize:9.5, color:"#666" }}>{b.k}</div>
            <div className="tnum" style={{ fontFamily:"var(--disp)", fontWeight:700, fontSize:22, color:"#999" }}>{b.before}</div>
          </div>)}
        </div>
        <div style={{ width:1, background:"linear-gradient(#1F1F1F,#333,#1F1F1F)" }}></div>
        <div style={{ flex:1, padding:"6px 16px", display:"flex", flexDirection:"column", justifyContent:"center", gap:14 }}>
          <div className="eyebrow" style={{ color:"#00D4FF" }}>AFTER ▸</div>
          {beforeAfter.map(b=><div key={b.k}>
            <div style={{ fontSize:9.5, color:"#666" }}>{b.k}</div>
            <div style={{ display:"flex", alignItems:"baseline", gap:8 }}>
              <div className="tnum" style={{ fontFamily:"var(--disp)", fontWeight:800, fontSize:22, color:"#fff" }}>{b.after}</div>
              <span className="pill badge-up">{b.delta}</span>
            </div>
          </div>)}
        </div>
      </div>
    </div>
  );
}

function AdstockRow({ a }) {
  const s = SIGNAL[a.signal];
  return (
    <div style={{ display:"flex", alignItems:"center", gap:14, padding:"10px 16px", borderBottom:"1px solid #141414" }}>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:7 }}>
          <span style={{ width:8, height:8, background:a.platColor, flex:"none" }}></span>
          <span style={{ fontSize:12, color:"#E2E2E2", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>{a.name}</span>
        </div>
        <div style={{ fontSize:9.5, color:"#555", marginTop:2, paddingLeft:15 }}>{a.plat}</div>
      </div>
      <DecayCurve data={a.curve} color={s.c} w={120} h={30}/>
      <span title={"Overmind trace score + Thrads contextual bid · "+new Date().toLocaleTimeString()}
        className="pill" style={{ color:s.c, background:s.bg, border:`1px solid ${s.c}44`, fontWeight:500,
        minWidth:54, justifyContent:"center" }}>{a.signal}</span>
    </div>
  );
}

function Page4() {
  const { advKpis, adstock } = window.ADTEC;
  const [exp, setExp] = useS4(null);
  return (
    <div style={{ height:"100%", display:"flex", flexDirection:"column" }}>
      {/* KPI cards */}
      <div style={{ display:"flex", gap:0, padding:"14px 16px", flex:"none", gap:12 }}>
        {advKpis.map((k,i)=><KpiCard key={k.id} k={k} expanded={exp===i} onToggle={()=>setExp(e=>e===i?null:i)}/>)}
      </div>
      <div style={{ flex:1, display:"grid", gridTemplateColumns:"1fr 1.15fr", minHeight:0, borderTop:"1px solid #1F1F1F" }}>
        <BeforeAfter/>
        {/* adstock */}
        <div style={{ display:"flex", flexDirection:"column", minHeight:0 }}>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"12px 16px 8px", flex:"none" }}>
            <div>
              <div className="eyebrow">SECTION C · ADSTOCK DECAY</div>
              <div style={{ fontSize:10, color:"#555", marginTop:2 }}>Overmind Optimizer + Thrads bid signal</div>
            </div>
            <div style={{ display:"flex", gap:10 }}>
              {Object.entries(SIGNAL).map(([k,v])=>(
                <span key={k} style={{ display:"flex", alignItems:"center", gap:5, fontSize:9 }}>
                  <span style={{ width:8, height:8, borderRadius:4, background:v.c }}></span><span style={{color:"#888"}}>{k}</span>
                </span>
              ))}
            </div>
          </div>
          <div style={{ flex:1, overflowY:"auto", minHeight:0 }}>
            {adstock.map((a,i)=><AdstockRow key={i} a={a}/>)}
            <div style={{ fontSize:9.5, color:"#444", padding:"10px 16px", lineHeight:1.5 }}>
              ↳ HOLD/BUY/SELL = Overmind trace score × Thrads <span style={{color:"#8B5CF6"}}>/v1/bid-request</span>. bid:null → SELL · high ad_rank → BUY. Written to <span style={{color:"#00FF88"}}>supabase.adstock_signals</span>.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
window.Page4 = Page4;
