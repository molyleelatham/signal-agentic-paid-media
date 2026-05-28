# adtec — AI Marketing Intelligence

A Bloomberg/trading-terminal-style marketing intelligence dashboard.
Single-page web app: GSAP snap-scroll between four pages, a WebGL "data-mesh"
ambient background (Three.js), and an Overmind agent trace log that runs on
interaction.

## Run it

It's a static site — no build step required. Serve the folder over HTTP:

```bash
npx serve .
# or
python3 -m http.server 8000
```

Then open `adtec.html`.

> Open over `http://` (not `file://`) so the browser will load the `.jsx`
> module files.

## Stack

- **React 18** (UMD) + **Babel Standalone** — JSX is transpiled in the browser
- **Three.js** (r128) — `src/webgl.js` node-network background
- **GSAP** + ScrollTrigger — snap-scroll paging (`src/AppDesktop.jsx`)
- Plain CSS design tokens — `src/theme.css`
  - Headings: **Space Grotesk** · Body / UI / captions: **IBM Plex Sans**

## Structure

```
adtec.html          entry — loads libs + all modules, mounts <AppDesktop/>
src/
  theme.css         design tokens (colors, type, components)
  data.js           mock data layer (window.ADTEC) + trace scripts
  webgl.js          Three.js ambient data-mesh (window.ADTECGL)
  shared.jsx        chart/UI atoms (Spark, LineChart, badges…)
  Terminal.jsx      Overmind trace log — updates on interaction, not a timer
  Page1.jsx         Market Intelligence
  Page2.jsx         Strategy Generator
  Page3.jsx         Budget Scenario Planner
  Page4.jsx         Campaign Performance
  AppDesktop.jsx    shell: nav + snap-scroll + WebGL + terminal
```

## Notes

- All API data (Tavily / Supabase / Thrads / Meta / Google …) is **mocked** in
  `src/data.js`. Shapes mirror the real endpoints so it's wireable later.
- The terminal log appends plain-English sentences when you navigate a page,
  click a trend, switch a budget scenario, generate a strategy, or press **RUN**.

## Porting to Vite

The browser-Babel setup is great for a zero-build prototype. To move to Vite:

1. `npm create vite@latest adtec -- --template react`
2. Move `src/*.jsx` in, replace the `window.X = …` globals with ES
   `import`/`export`, and convert the CDN `<script>` tags to npm deps
   (`react`, `react-dom`, `three`, `gsap`).
3. Keep `theme.css` as-is and import it in your root.
