/* ============================================================
   adtec — WebGL background (Three.js)
   A drifting node network ("data mesh"): points + proximity edges
   in GS terminal-green / cyan. Reacts to scroll progress, mouse
   parallax, and a one-shot "hero coalesce" pulse on load.
   API:  const gl = ADTECGL.init(canvas);
         gl.setScroll(0..1);  gl.pulse();  gl.destroy();
   ============================================================ */
window.ADTECGL = (function () {
  function init(canvas, opts) {
    opts = opts || {};
    if (!window.THREE) { console.warn("THREE not loaded"); return stub(); }
    const THREE = window.THREE;
    const COUNT = opts.count || 150;
    const RANGE = 60;          // node cloud half-extent
    const LINK = 11;           // link distance
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setClearColor(0x000000, 0);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 400);
    camera.position.z = 78;

    // node positions + velocities
    const pos = new Float32Array(COUNT * 3);
    const home = new Float32Array(COUNT * 3);
    const vel = new Float32Array(COUNT * 3);
    for (let i = 0; i < COUNT; i++) {
      const x = (Math.random() - 0.5) * RANGE * 2;
      const y = (Math.random() - 0.5) * RANGE * 1.3;
      const z = (Math.random() - 0.5) * RANGE * 0.9;
      pos[i*3]=x; pos[i*3+1]=y; pos[i*3+2]=z;
      home[i*3]=x; home[i*3+1]=y; home[i*3+2]=z;
      vel[i*3]=(Math.random()-0.5)*0.06; vel[i*3+1]=(Math.random()-0.5)*0.06; vel[i*3+2]=(Math.random()-0.5)*0.04;
    }

    // points
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const sprite = makeDot();
    const pMat = new THREE.PointsMaterial({ size: 1.5, map: sprite, transparent: true, color: 0x00ff88, opacity: 0.9, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true });
    const points = new THREE.Points(pGeo, pMat);
    scene.add(points);

    // a few brighter cyan "hub" nodes
    const hubGeo = new THREE.BufferGeometry();
    const hubPos = new Float32Array(18 * 3);
    hubGeo.setAttribute("position", new THREE.BufferAttribute(hubPos, 3));
    const hubMat = new THREE.PointsMaterial({ size: 3.4, map: sprite, transparent: true, color: 0x00d4ff, opacity: 0.95, depthWrite: false, blending: THREE.AdditiveBlending });
    const hubs = new THREE.Points(hubGeo, hubMat);
    scene.add(hubs);

    // lines
    const maxLines = COUNT * 6;
    const linePos = new Float32Array(maxLines * 2 * 3);
    const lineCol = new Float32Array(maxLines * 2 * 3);
    const lGeo = new THREE.BufferGeometry();
    lGeo.setAttribute("position", new THREE.BufferAttribute(linePos, 3));
    lGeo.setAttribute("color", new THREE.BufferAttribute(lineCol, 3));
    const lMat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false });
    const lines = new THREE.LineSegments(lGeo, lMat);
    scene.add(lines);

    let W = 1, H = 1, dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    function resize() {
      const r = canvas.getBoundingClientRect();
      W = r.width || canvas.clientWidth || 800; H = r.height || canvas.clientHeight || 600;
      renderer.setPixelRatio(dpr);
      renderer.setSize(W, H, false);
      camera.aspect = W / H; camera.updateProjectionMatrix();
    }
    resize();
    const ro = new ResizeObserver(resize); ro.observe(canvas);

    // interaction state
    let scroll = 0, scrollT = 0;
    let mx = 0, my = 0, mxT = 0, myT = 0;
    let pulse = 0; // 1 -> 0 coalesce energy
    function onMove(e) {
      const r = canvas.getBoundingClientRect();
      mxT = ((e.clientX - r.left) / r.width - 0.5) * 2;
      myT = ((e.clientY - r.top) / r.height - 0.5) * 2;
    }
    window.addEventListener("pointermove", onMove);

    let raf, t0 = performance.now(), alive = true, fcount = 0;
    function frame(now) {
      if (!alive) return;
      fcount++;
      const dt = Math.min(33, now - t0); t0 = now;
      scrollT += (scroll - scrollT) * 0.06;
      mxT && 0; mx += (mxT - mx) * 0.05; my += (myT - my) * 0.05;
      pulse *= 0.972;

      const tt = now * 0.0002;
      // update nodes
      for (let i = 0; i < COUNT; i++) {
        const ix = i*3, iy = ix+1, iz = ix+2;
        pos[ix] += vel[ix]; pos[iy] += vel[iy]; pos[iz] += vel[iz];
        // gentle pull home + pulse pull toward center
        pos[ix] += (home[ix]-pos[ix])*0.002 - pos[ix]*pulse*0.012;
        pos[iy] += (home[iy]-pos[iy])*0.002 - pos[iy]*pulse*0.012;
        pos[iz] += (home[iz]-pos[iz])*0.002;
        // bounds
        if (Math.abs(pos[ix])>RANGE) vel[ix]*=-1;
        if (Math.abs(pos[iy])>RANGE*0.7) vel[iy]*=-1;
        if (Math.abs(pos[iz])>RANGE*0.5) vel[iz]*=-1;
      }
      pGeo.attributes.position.needsUpdate = true;
      for (let h = 0; h < 18; h++) { hubPos[h*3]=pos[h*9]; hubPos[h*3+1]=pos[h*9+1]; hubPos[h*3+2]=pos[h*9+2]; }
      hubGeo.attributes.position.needsUpdate = true;

      // rebuild links every other frame (O(n^2) but n is small) — halves CPU cost
      if (fcount % 2 === 0) {
        let li = 0; const link2 = LINK*LINK;
        for (let i = 0; i < COUNT && li < maxLines; i++) {
          for (let j = i+1; j < COUNT && li < maxLines; j++) {
            const dx=pos[i*3]-pos[j*3], dy=pos[i*3+1]-pos[j*3+1], dz=pos[i*3+2]-pos[j*3+2];
            const d2 = dx*dx+dy*dy+dz*dz;
            if (d2 < link2) {
              const a = (1 - Math.sqrt(d2)/LINK);
              const o = li*6;
              linePos[o]=pos[i*3]; linePos[o+1]=pos[i*3+1]; linePos[o+2]=pos[i*3+2];
              linePos[o+3]=pos[j*3]; linePos[o+4]=pos[j*3+1]; linePos[o+5]=pos[j*3+2];
              // color: green base, cyan when high pulse / near hubs
              const cyan = Math.min(1, pulse*1.4 + (i<18?0.5:0));
              const g = 1, b = 0.45 + cyan*0.55, rr = 0.0 + cyan*0.0;
              for (let k=0;k<2;k++){ lineCol[o+k*3]=rr; lineCol[o+k*3+1]=g*a; lineCol[o+k*3+2]=b*a; }
              li++;
            }
          }
        }
        lGeo.setDrawRange(0, li*2);
        lGeo.attributes.position.needsUpdate = true;
        lGeo.attributes.color.needsUpdate = true;
      }
      lMat.opacity = 0.4 + pulse*0.4;
      pMat.opacity = 0.7 + pulse*0.3;

      // camera: parallax + scroll drift
      camera.position.x += (mx*9 - camera.position.x) * 0.04;
      camera.position.y += (-my*6 + scrollT*-10 - camera.position.y) * 0.04;
      camera.position.z = 78 - pulse*10 + scrollT*8;
      scene.rotation.y = Math.sin(tt)*0.08 + mx*0.05;
      scene.rotation.x = scrollT*0.12;
      camera.lookAt(0,0,0);

      renderer.render(scene, camera);
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);

    function makeDot() {
      const c = document.createElement("canvas"); c.width = c.height = 64;
      const x = c.getContext("2d");
      const g = x.createRadialGradient(32,32,0,32,32,32);
      g.addColorStop(0,"rgba(255,255,255,1)"); g.addColorStop(0.25,"rgba(255,255,255,0.8)");
      g.addColorStop(0.5,"rgba(255,255,255,0.25)"); g.addColorStop(1,"rgba(255,255,255,0)");
      x.fillStyle=g; x.beginPath(); x.arc(32,32,32,0,7); x.fill();
      const tex = new THREE.Texture(c); tex.needsUpdate = true; return tex;
    }

    return {
      setScroll(v){ scroll = Math.max(0, Math.min(1, v)); },
      pulse(){ pulse = 1; },
      destroy(){ alive = false; cancelAnimationFrame(raf); ro.disconnect(); window.removeEventListener("pointermove", onMove); renderer.dispose(); pGeo.dispose(); lGeo.dispose(); hubGeo.dispose(); },
    };
  }
  function stub(){ return { setScroll(){}, pulse(){}, destroy(){} }; }
  return { init };
})();
