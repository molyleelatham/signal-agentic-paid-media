/* AppDesktop.jsx — shell: nav + GSAP snap-scroll stage + WebGL + terminal */
const { useState: useSA, useEffect: useEA, useRef: useRA } = React;

function Clock() {
  const [t, setT] = useSA("");
  useEA(() => {const f = () => {const d = new Date();const p = (n) => String(n).padStart(2, "0");setT(`${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())} GMT`);};f();const iv = setInterval(f, 1000);return () => clearInterval(iv);}, []);
  return <span className="tnum" style={{ fontSize: 11, color: "#888" }}>{t}</span>;
}

function Nav({ pages, active, onJump }) {
  return (
    <div style={{ flex: "none", height: 52, display: "flex", alignItems: "center", gap: 0, padding: "0 18px",
      borderBottom: "1px solid #1F1F1F", background: "#080808", zIndex: 40 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
        <span className="dot active" style={{ width: 8, height: 8 }}></span>
        <span style={{ fontFamily: "var(--disp)", fontWeight: 700, fontSize: 21, letterSpacing: "0.02em", color: "#fff" }}>SIGNAL</span>
        <span style={{ fontSize: 9, color: "#555", letterSpacing: ".14em", marginTop: 4 }}>AD TECH INTELLIGENCE</span>
      </div>
      <div style={{ display: "flex", marginLeft: 40 }}>
        {pages.map((p, i) =>
        <button key={p.id} onClick={() => onJump(i)} style={{ display: "flex", alignItems: "baseline", gap: 8, padding: "0 16px", height: 52,
          background: "transparent", border: "none", borderBottom: "2px solid " + (active === i ? "#00D4FF" : "transparent"), cursor: "pointer" }}>
            <span className="tnum" style={{ fontSize: 10, color: active === i ? "#00D4FF" : "#555" }}>{p.n}</span>
            <span style={{ fontFamily: "var(--mono)", fontSize: 11, letterSpacing: ".06em", textTransform: "uppercase",
            color: active === i ? "#fff" : "#777" }}>{p.title}</span>
          </button>
        )}
      </div>
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 16 }}>
        <span className="pill" style={{ color: "#00FF88", background: "rgba(0,255,136,.1)" }}><span className="dot active" style={{ width: 6, height: 6 }}></span>LIVE</span>
        <Clock />
      </div>
    </div>);

}

function PageHeader({ p }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "12px 20px 10px", flex: "none" }}>
      <div style={{ fontFamily: "var(--disp)", fontWeight: 800, fontSize: 40, lineHeight: 1, color: "transparent",
        WebkitTextStroke: "1px #2a2a2a" }}>{p.n}</div>
      <div style={{ width: 1, height: 34, background: "#222" }}></div>
      <div>
        <h2 style={{ fontSize: 26, textTransform: "uppercase", color: "#fff", lineHeight: 1, whiteSpace: "nowrap" }}>{p.title}</h2>
        <div style={{ fontSize: 10.5, color: "#666", marginTop: 3, letterSpacing: ".02em" }}>{p.sub}</div>
      </div>
    </div>);

}

function Placeholder({ name }) {
  return <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#333", fontSize: 13 }}>{name} — building…</div>;
}

function AppDesktop() {
  const { pages } = window.ADTEC;
  const [active, setActive] = useSA(0);
  const scrollerRef = useRA(null);
  const glRef = useRA(null);
  const jumpRef = useRA(() => {});
  const jump = (i) => jumpRef.current(i);

  useEA(() => {
    const gl = ADTECGL.init(glRef.current, { count: 90 });
    gl.pulse();
    const scroller = scrollerRef.current;
    const N = pages.length;
    let cur = 0,animating = false;
    const revealed = new Set();

    const revealSection = (i) => {
      const el = scroller.querySelectorAll(".reveal")[i];
      if (el && window.gsap && !revealed.has(i)) {revealed.add(i);
        gsap.fromTo(el, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: .6, ease: "power2.out" });}
    };
    revealSection(0);gl.setScroll(0);

    const goTo = (i) => {
      i = Math.max(0, Math.min(N - 1, i));
      if (i === cur && !animating) return;
      cur = i;animating = true;setActive(i);revealSection(i);
      gl.setScroll(N > 1 ? i / (N - 1) : 0);
      // fire a short plain-English trace for the page we just opened
      const pid = pages[i].id;window.__adtecActivePage = pid;
      window.adtecLog && window.adtecLog(window.ADTEC.traceScripts[pid]);
      const start = scroller.scrollTop,end = i * scroller.clientHeight,t0 = performance.now(),dur = 680;
      const ease = (t) => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      const step = (now) => {const p = Math.min(1, (now - t0) / dur);
        scroller.scrollTop = start + (end - start) * ease(p);
        if (p < 1) requestAnimationFrame(step);else animating = false;};
      requestAnimationFrame(step);
    };
    jumpRef.current = goTo;

    // does an inner scrollable region still have room to scroll in `dir`?
    const innerCanScroll = (node, dir) => {
      while (node && node !== scroller) {
        if (node.scrollHeight - node.clientHeight > 4) {
          const cs = getComputedStyle(node).overflowY;
          if (cs === "auto" || cs === "scroll") {
            if (dir > 0 && node.scrollTop + node.clientHeight < node.scrollHeight - 2) return true;
            if (dir < 0 && node.scrollTop > 2) return true;
          }
        }
        node = node.parentElement;
      }
      return false;
    };

    let wheelLock = false;
    const onWheel = (e) => {
      const dir = Math.sign(e.deltaY);
      if (innerCanScroll(e.target, dir)) return; // let inner lists scroll
      e.preventDefault();
      if (animating || wheelLock || Math.abs(e.deltaY) < 4) return;
      wheelLock = true;setTimeout(() => {wheelLock = false;}, 700);
      goTo(cur + dir);
    };
    scroller.addEventListener("wheel", onWheel, { passive: false });

    const onKey = (e) => {
      if (e.key === "ArrowDown" || e.key === "PageDown") {e.preventDefault();goTo(cur + 1);}
      if (e.key === "ArrowUp" || e.key === "PageUp") {e.preventDefault();goTo(cur - 1);}
    };
    window.addEventListener("keydown", onKey);

    // touch swipe
    let ty = 0;
    const onTS = (e) => {ty = e.touches[0].clientY;};
    const onTE = (e) => {const dy = ty - e.changedTouches[0].clientY;
      if (Math.abs(dy) > 40 && !innerCanScroll(e.target, Math.sign(dy))) goTo(cur + Math.sign(dy));};
    scroller.addEventListener("touchstart", onTS, { passive: true });
    scroller.addEventListener("touchend", onTE, { passive: true });

    return () => {scroller.removeEventListener("wheel", onWheel);window.removeEventListener("keydown", onKey);
      scroller.removeEventListener("touchstart", onTS);scroller.removeEventListener("touchend", onTE);gl.destroy();};
  }, []);


  const render = (id) => {
    if (id === "intel" && window.Page1) return <Page1 />;
    if (id === "strategy" && window.Page2) return <Page2 />;
    if (id === "budget" && window.Page3) return <Page3 />;
    if (id === "perf" && window.Page4) return <Page4 />;
    return <Placeholder name={id} />;
  };

  return (
    <div style={{ position: "fixed", inset: 0, display: "flex", flexDirection: "column", background: "#000" }}>
      <canvas ref={glRef} style={{ position: "fixed", inset: 0, zIndex: 0, opacity: .55 }}></canvas>
      <div style={{ position: "fixed", inset: 0, zIndex: 0, background: "radial-gradient(120% 80% at 50% -10%, rgba(0,212,255,.06), transparent 60%)" }}></div>
      <Nav pages={pages} active={active} onJump={jump} />
      <div ref={scrollerRef} className="scroller" style={{ position: "relative", zIndex: 10, flex: 1, overflow: "hidden", minHeight: 0 }}>
        {pages.map((p) =>
        <section key={p.id} className="snap-section" data-screen-label={p.title} style={{ height: "100%",
          display: "flex", flexDirection: "column", minHeight: 0 }}>
            <PageHeader p={p} />
            <div className="reveal" style={{ flex: 1, margin: "0 20px 18px", minHeight: 0, display: "flex", flexDirection: "column",
            background: "rgba(8,8,8,.94)", border: "1px solid #1F1F1F", overflow: "hidden" }}>
              {render(p.id)}
            </div>
          </section>
        )}
      </div>
      <Terminal mode="flow" defaultOpen={true} heightPct={20} />
    </div>);

}
window.AppDesktop = AppDesktop;