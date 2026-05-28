# SIGNAL Frontend

Bloomberg Terminal-style React dashboard for the SIGNAL adtech platform.

## Features

Ported from `frontend adtech/` (legacy HTML/Babel prototype):

| Page | Features |
|------|----------|
| **01 Market Intelligence** | Data source ribbon, trending topics, detail panel, audience AI queries |
| **02 Strategy Generator** | Quarterly funnel bars, line charts, KPI strip, Claude strategy drawer |
| **03 Budget Scenario Planner** | 3 scenarios, editable CPL matrix, allocation bar, fine-tune sliders |
| **04 Campaign Performance** | Advanced KPIs, before/after SIGNAL comparison, adstock decay |
| **05 SIGNAL Terminal** | Agent signals, P&L, market data, execution log (live API) |

**Order Flow** (right column, all pages) — Channels tab with ▲/▼ flow; Campaigns tab with BUY/HOLD/STOP SIGNAL badges.

**Overmind Trace** (bottom) — Plain-English agent log; updates on navigation and interactions.

**Live API** — Polls `GET /terminal/full-dashboard` every 30s (falls back to demo data if API is down).

## Run

```bash
# Terminal 1 — API
cd .. && uv run uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Build

```bash
npm run build
npm run preview
```

## Stack

- React 18 + TypeScript + Vite
- Tailwind CSS (Bloomberg dark theme from `FRONTEND_DESIGN_SPECIFICATION.md`)
- TanStack Query for server state
