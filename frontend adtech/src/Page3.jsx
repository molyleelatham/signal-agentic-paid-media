/* Page3.jsx — Budget Scenario Planner (exported to window.Page3) */
const { useState: useS3, useMemo: useM3, useRef: useR3 } = React;

const fmt = n => "£"+Math.round(n).toLocaleString();

function ScenarioTab({ s, id, active, onClick }) {
  return (
    <div onClick={onClick} style={{ width:200, height:74, padding:"12px 16px", cursor:"pointer",
      background:s.bg, border:"1px solid "+(active?"#fff":s.border), borderRadius:3,
      boxShadow: active?"0 0 0 1px #fff, 0 8px 22px rgba(0,0,0,.5)":"none", transition:"all .15s",
      display:"flex", flexDirection:"column", justifyContent:"center" }}>
      <div style={{ display:"flex", alignItems:"center", gap:7, marginBottom:4 }}>
        <span className="dot" style={{ width:7, height:7, background: id==="conservative"?"#888":id==="optimistic"?"#00FF88":"#FF4444" }}></span>
        <span style={{ fontFamily:"var(--disp)", fontWeight:700, fontSize:18, letterSpacing:".01em", color:active?"#fff":"#ccc" }}>{s.label}</span>
      </div>
      <div style={{ fontSize:10, color:"#888" }}>{s.desc}</div>
    </div>
  );
}

function EditCell({ value, fmt:fm, onChange, color }) {
  const [editing, setEditing] = useS3(false);
  const [flash, setFlash] = useS3(false);
  const [draft, setDraft] = useS3("");
  const commit = ()=>{
    setEditing(false);
    const n = parseFloat(draft.replace(/[^0-9.]/g,""));
    if (!isNaN(n)) { onChange(n); setFlash(true); setTimeout(()=>setFlash(false),500); }
  };
  return (
    <td onClick={()=>{ setDraft(String(value)); setEditing(true); }}
      style={{ padding:"7px 12px", textAlign:"right", cursor:"text", color:color||"#D6D6D6",
        animation: flash?"flash .5s":"none", borderBottom:"1px solid #141414", position:"relative" }}>
      {editing
        ? <input autoFocus value={draft} onChange={e=>setDraft(e.target.value)} onBlur={commit}
            onKeyDown={e=>e.key==="Enter"&&commit()} style={{ width:64, background:"#000", border:"1px solid #00D4FF",
            color:"#fff", fontFamily:"var(--mono)", fontSize:12, textAlign:"right", padding:"2px 4px" }}/>
        : (fm?fm(value):value)}
    </td>
  );
}

function Page3() {
  const D = window.ADTEC;
  const [scn, setScn] = useS3("optimistic");
  const [matrix, setMatrix] = useS3(()=>JSON.parse(JSON.stringify(D.scenarios)));
  const [weights, setWeights] = useS3({ awareness:60, loyalty:50, timeline:6 });
  const [channelsOn, setChannelsOn] = useS3(()=>Object.fromEntries(D.channels.map(c=>[c,true])));

  const rows = matrix[scn].matrix;
  const setCell = (ci, key, v) => {
    setMatrix(m=>{ const n=JSON.parse(JSON.stringify(m)); n[scn].matrix[ci][key]=v;
      const r=n[scn].matrix[ci]; if(key==="spend"||key==="cpl"){ r.leads = r.cpl>0?Math.round(r.spend/r.cpl):r.leads; } return n; });
  };
  const totals = useM3(()=>{
    const on = rows.filter(r=>channelsOn[r.channel]);
    const spend = on.reduce((s,r)=>s+r.spend,0);
    const leads = on.reduce((s,r)=>s+r.leads,0);
    return { spend, leads, cpl: leads?spend/leads:0, roas: 4.0 + (weights.loyalty-50)/120 };
  },[rows, channelsOn, weights]);

  const alloc = useM3(()=>{
    const on = rows.filter(r=>channelsOn[r.channel]);
    const tot = on.reduce((s,r)=>s+r.spend,0)||1;
    return on.map(r=>({ ch:r.channel, pct:r.spend/tot*100, spend:r.spend, color:D.platformColors[r.channel] }));
  },[rows, channelsOn]);

  return (
    <div style={{ height:"100%", display:"flex", flexDirection:"column" }}>
      {/* scenario tabs */}
      <div style={{ display:"flex", gap:12, padding:"14px 18px", flex:"none", borderBottom:"1px solid #1F1F1F" }}>
        {Object.entries(D.scenarios).map(([id,s])=>(
          <ScenarioTab key={id} id={id} s={s} active={scn===id} onClick={()=>{ setScn(id); window.adtecLog && window.adtecLog([{ msg:`Switching to the ${s.label.toLowerCase()} budget plan…`, tone:"work" }, { msg:`Re-modelling spend and cost-per-lead for ${s.label.toLowerCase()} reach.`, tone:"info" }]); }}/>
        ))}
        <div style={{ marginLeft:"auto", alignSelf:"center", textAlign:"right" }}>
          <div className="eyebrow">SCENARIO P&amp;L · {matrix[scn].label}</div>
          <div style={{ display:"flex", gap:18, marginTop:4 }}>
            <PnL k="SPEND" v={fmt(totals.spend)}/>
            <PnL k="LEADS" v={Math.round(totals.leads).toLocaleString()} c="#00D4FF"/>
            <PnL k="BLENDED CPL" v={"£"+totals.cpl.toFixed(2)} c="#00FF88"/>
            <PnL k="ROAS" v={totals.roas.toFixed(1)+"×"} c="#00FF88"/>
          </div>
        </div>
      </div>

      <div style={{ flex:1, display:"flex", minHeight:0 }}>
        {/* matrix + allocation */}
        <div style={{ flex:1, display:"flex", flexDirection:"column", minWidth:0, borderRight:"1px solid #1F1F1F" }}>
          <div style={{ flex:1, overflow:"auto", minHeight:0 }}>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12, fontFamily:"var(--mono)" }}>
              <thead>
                <tr style={{ position:"sticky", top:0, background:"#0A0A0A", zIndex:2 }}>
                  {["CHANNEL","AWARENESS %","LOYALTY IDX","EST. LEADS","CPL","SPEND"].map((h,i)=>(
                    <th key={h} style={{ padding:"9px 12px", textAlign:i?"right":"left", fontSize:9.5, letterSpacing:".08em",
                      color:"#666", borderBottom:"1px solid #1F1F1F", fontWeight:500 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r,ci)=>{
                  const off = !channelsOn[r.channel];
                  return (
                    <tr key={r.channel} style={{ opacity:off?0.35:1 }}>
                      <td style={{ padding:"7px 12px", borderBottom:"1px solid #141414" }}>
                        <span style={{ display:"inline-flex", alignItems:"center", gap:8 }}>
                          <span style={{ width:8, height:8, background:D.platformColors[r.channel] }}></span>
                          <span style={{ color:"#EAEAEA" }}>{r.channel}</span>
                        </span>
                      </td>
                      <EditCell value={r.awareness} fmt={v=>v+"%"} onChange={v=>setCell(ci,"awareness",v)}/>
                      <EditCell value={r.loyalty} onChange={v=>setCell(ci,"loyalty",v)}/>
                      <td className="tnum" style={{ padding:"7px 12px", textAlign:"right", color:"#00D4FF", borderBottom:"1px solid #141414" }}>{r.leads.toLocaleString()}</td>
                      <EditCell value={r.cpl} fmt={v=>"£"+(+v).toFixed(2)} onChange={v=>setCell(ci,"cpl",v)} color="#00FF88"/>
                      <EditCell value={r.spend} fmt={fmt} onChange={v=>setCell(ci,"spend",v)}/>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div style={{ fontSize:9.5, color:"#444", padding:"8px 12px" }}>↳ Click any cell to edit · row leads recalc live · writes to <span style={{color:"#00FF88"}}>supabase.budget_scenarios</span></div>
          </div>
          {/* allocation bar */}
          <div style={{ flex:"none", padding:"12px 16px", borderTop:"1px solid #1F1F1F", background:"#0B0B0B" }}>
            <div className="eyebrow" style={{ marginBottom:8 }}>PLATFORM ALLOCATION · {fmt(totals.spend)} TOTAL</div>
            <div style={{ display:"flex", height:24, borderRadius:2, overflow:"hidden", border:"1px solid #1A1A1A" }}>
              {alloc.map(a=>(
                <div key={a.ch} title={`${a.ch} ${a.pct.toFixed(0)}%`} style={{ width:a.pct+"%", background:a.color,
                  display:"flex", alignItems:"center", justifyContent:"center", overflow:"hidden", transition:"width .3s" }}>
                  {a.pct>9 && <span style={{ fontSize:9, color:"#fff", fontWeight:500 }}>{a.pct.toFixed(0)}%</span>}
                </div>
              ))}
            </div>
            <div style={{ display:"flex", gap:14, flexWrap:"wrap", marginTop:8 }}>
              {alloc.map(a=>(
                <div key={a.ch} style={{ display:"flex", alignItems:"center", gap:6 }}>
                  <span style={{ width:9, height:9, background:a.color }}></span>
                  <span style={{ fontSize:9.5, color:"#999" }}>{a.ch}</span>
                  <span className="tnum" style={{ fontSize:9.5, color:"#666" }}>{fmt(a.spend)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* fine-tune sidebar */}
        <div style={{ width:280, flex:"none", padding:"16px 16px", overflowY:"auto", background:"#0D0D0D" }}>
          <div className="eyebrow" style={{ marginBottom:14 }}>FINE-TUNE CONTROLS</div>
          <Slider label="Brand Awareness Weight" v={weights.awareness} min={0} max={100} suffix="%" onChange={v=>setWeights(w=>({...w,awareness:v}))}/>
          <Slider label="Loyalty ↔ Acquisition" v={weights.loyalty} min={0} max={100} left="LOYALTY" right="ACQUIRE" onChange={v=>setWeights(w=>({...w,loyalty:v}))}/>
          <Slider label="Timeline Aggressiveness" v={weights.timeline} min={3} max={12} suffix="mo" onChange={v=>setWeights(w=>({...w,timeline:v}))}/>
          <div className="eyebrow" style={{ margin:"18px 0 10px" }}>CHANNELS ACTIVE</div>
          {D.channels.map(c=>(
            <div key={c} onClick={()=>setChannelsOn(o=>({...o,[c]:!o[c]}))}
              style={{ display:"flex", alignItems:"center", gap:10, padding:"7px 0", cursor:"pointer" }}>
              <span style={{ width:9, height:9, background:D.platformColors[c], opacity:channelsOn[c]?1:.3 }}></span>
              <span style={{ flex:1, fontSize:11, color:channelsOn[c]?"#ddd":"#555" }}>{c}</span>
              <Toggle on={channelsOn[c]}/>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PnL({ k, v, c }) {
  return <div style={{ textAlign:"left" }}>
    <div style={{ fontSize:9, color:"#666", letterSpacing:".06em" }}>{k}</div>
    <div className="tnum" style={{ fontFamily:"var(--disp)", fontWeight:700, fontSize:18, color:c||"#fff" }}>{v}</div>
  </div>;
}
function Slider({ label, v, min, max, suffix, left, right, onChange }) {
  return (
    <div style={{ marginBottom:16 }}>
      <div style={{ display:"flex", justifyContent:"space-between", marginBottom:6 }}>
        <span style={{ fontSize:10.5, color:"#aaa" }}>{label}</span>
        <span className="tnum" style={{ fontSize:10.5, color:"#00D4FF" }}>{v}{suffix||""}</span>
      </div>
      <input type="range" min={min} max={max} value={v} onChange={e=>onChange(+e.target.value)}
        style={{ width:"100%", accentColor:"#00D4FF", height:4 }}/>
      {(left||right) && <div style={{ display:"flex", justifyContent:"space-between", marginTop:3 }}>
        <span style={{ fontSize:8.5, color:"#555" }}>{left}</span><span style={{ fontSize:8.5, color:"#555" }}>{right}</span>
      </div>}
    </div>
  );
}
function Toggle({ on }) {
  return <span style={{ width:30, height:16, borderRadius:8, background:on?"#00FF8833":"#1A1A1A",
    border:"1px solid "+(on?"#00FF88":"#333"), position:"relative", flex:"none", transition:"all .15s" }}>
    <span style={{ position:"absolute", top:1, left:on?15:1, width:12, height:12, borderRadius:6,
      background:on?"#00FF88":"#555", transition:"left .15s" }}></span>
  </span>;
}
window.Page3 = Page3;
