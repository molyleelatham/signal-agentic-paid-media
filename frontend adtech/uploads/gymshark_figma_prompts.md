# Figma Design Prompts — Gymshark AI Marketing Intelligence Dashboard
> Cursor-ready. All pages share the Global Terminal component and Gymshark brand system.

---

## Tavily API Reference (4 endpoints — use the right one per job)

Tavily is not a single "web search" call. It exposes four distinct endpoints, each used differently across the four pages:

| Endpoint | Method | What it does | Used on |
|----------|--------|-------------|---------|
| `POST /search` | `tvly.search(query, { include_domains, search_depth })` | Keyword/topic search across the web; returns ranked results with snippets | Page 1 — Trending topics feed |
| `POST /extract` | `tvly.extract(url)` | Pulls structured content from a specific URL | Page 1 — Deep Gymshark product/blog page ingestion |
| `POST /crawl` | `tvly.crawl(url, { instructions, max_depth, max_breadth })` | Recursive site crawl following internal links | Page 1 — Full `uk.gymshark.com` brand crawl on init |
| `POST /map` | `tvly.map(url)` | Returns the full URL sitemap of a domain without content extraction | Page 1 — Status ribbon: confirms Gymshark site is reachable and indexes all crawlable paths |
| `POST /research` | `tvly.research(input, { output_schema })` | Agentic multi-step research with structured JSON output | Page 2 — Strategy Generator context enrichment |

**Install:** `npm i @tavily/core`
**Auth:** `Authorization: Bearer tvly-YOUR_API_KEY`

---

## Brand System Reference
**Crawl target:** `https://uk.gymshark.com/` — extract and apply:
- **Colour palette:** Primary `#000000` (GS Black), `#FFFFFF`, accent `#00D4FF` (data-viz highlight), functional red/amber/green for status
- **Typography:** Bold compressed display type (Gymshark uses a custom condensed sans); pair with `DM Mono` for data/terminal layers
- **Tone:** High-performance, direct, confident. No decorative fluff.
- **Logo:** Use Gymshark wordmark (text-only black/white version as seen on `uk.gymshark.com`)
- **UI density:** Dense data-forward layout; information-rich without feeling cluttered

---

## Global Component — Persistent Terminal Panel (applies to ALL pages)

### What it is
A collapsible dark-theme terminal drawer fixed to the **bottom** of every page. It occupies **20% of the vertical viewport height** when open, and collapses to a **32px handle bar** when closed.

### Layout & Structure
- **Width:** 100% horizontal
- **Background:** `#0A0A0A` with a 1px top border in `#1F1F1F`
- **Font:** `DM Mono` 11px, `#00FF88` (terminal green) for output text, `#666` for timestamps
- **Header bar (always visible):**
  - Left: `● OVERMIND TRACE` label with a slow-pulsing green dot (CSS animation: `pulse 2s infinite`)
  - Right: Toggle button — a `▲` (open) / `▼` (close) chevron arrow inside a `24×24px` pill button (`#1A1A1A` bg, `#444` border). On click, the terminal slides open/closed with a `200ms ease` transition.

### Terminal Content — What to Display
The terminal uses the **Overmind Tracing SDK** (`https://docs.overmindlab.ai/guides/how-to-use-tracing`) to capture and stream every LLM call, tool invocation, and API fetch in real time. Display lines in this format:

```
[HH:MM:SS]  →  FETCH     Tavily /search  {"query": "gymshark leggings trending UK"}
[HH:MM:SS]  ←  RESPONSE  Tavily          200 OK  |  14 results  |  312ms
[HH:MM:SS]  →  LLM CALL  claude-sonnet   "Analyse trend signals for Gymshark Q3..."
[HH:MM:SS]  ←  LLM OUT   claude-sonnet   "Top signal: scrunch leggings +34% YoY..."
[HH:MM:SS]  →  FETCH     Supabase        SELECT * FROM campaign_kpis WHERE brand='gymshark'
[HH:MM:SS]  ←  RESPONSE  Supabase        200 OK  |  48 rows  |  89ms
[HH:MM:SS]  ⚙  OVERMIND  Optimizer       Scoring trace #1042 against eval policy...
```

- Auto-scroll to latest line
- Lines fade in with a `150ms` stagger
- Scrollable with a custom minimal scrollbar (`#1F1F1F` track, `#444` thumb)
- Include a `CLEAR` button (top-right of terminal body) and a `COPY` button

### Cursor/API Notes
- Wire terminal output to `overmind.trace()` events via the JS SDK: `import { init } from '@overmind/sdk'`
- Each API fetch (Tavily, Supabase, Thrads, Meta mock, etc.) should emit a trace event that updates the terminal stream
- Terminal content is read-only in the UI; it reflects real async events

---

## Page 1 — Market Intelligence Panel

### Purpose
Real-time brand and market signal aggregation for Gymshark, pulling live data from crawled web sources, ad platform mocks, and brand documents. Answers the question: *"What is happening in the market right now, and what are people asking AI about our brand?"*

### Data Source Status Bar (top of page, full width)

Design a **horizontal status ribbon** — `48px` tall, `#111` background, subtle bottom border.

Inside, display **6 data source pills**, each containing:
- An animated status dot (`12px` circle):
  - `#00FF88` slowly pulsing → **Active**
  - `#FF4444` static → **Inactive**
  - `#FFB800` fast blinking → **Degraded / Broken**
- Source name label (DM Mono, 11px, uppercase)
- Last-synced timestamp in muted grey

**The 6 sources:**
1. `TAVILY WEB CRAWL` — crawls `https://uk.gymshark.com/` and broader web
2. `META ADS` — mocked; shows as active/inactive toggle
3. `GOOGLE ADS` — mocked
4. `TIKTOK ADS` — mocked
5. `MICROSOFT ADS` — mocked
6. `GYMSHARK MCP` — reads brand `.md` files and MCPs from Gymshark's brand assets

On **hover**, each pill expands to show a tooltip:
- Data type being pulled
- API endpoint or source path
- Error message if status is broken (amber/red state)

### Section A — Trending Topics Feed

**Layout:** 2-column grid. Left: live feed list. Right: detail panel that populates on row click.

**Left — Feed List:**
Each row is a **trend card** (`64px` tall, `#111` bg, `1px #1F1F1F` border, `4px` left accent bar coloured by growth intensity):
- Trend keyword / topic (bold, white)
- Growth percentage badge: `+34%` in green pill, `-12%` in red pill
- Source icon(s): small `T` for Tavily, `M` `G` `TT` `MS` for ad platforms
- Sparkline thumbnail (7-day trend, 60px wide)

Sort options at top: `TRENDING ↑` | `VOLUME` | `RECENCY`

**Right — Detail Panel:**
On row click, expand to show:
- Full topic breakdown with source attribution
- Volume over time (small line chart, `recharts` / `Chart.js`)
- Competitive signal: which ad platforms are bidding on this keyword
- Gymshark relevance score (0–100, derived from brand MCP match)

**Cursor/API notes:**
- **Brand site crawl (on init):** `tvly.crawl("https://uk.gymshark.com", { instructions: "Find all product categories, trending collections, and blog content", max_depth: 2, max_breadth: 30 })` — runs once on app load, seeds the `market_signals` Supabase table
- **Specific page extraction:** `tvly.extract("https://uk.gymshark.com/collections/new-releases/womens")` — pulls structured content from key Gymshark pages (new drops, best sellers, blog articles)
- **Live trend search:** `tvly.search("gymshark activewear trends UK 2025", { include_domains: ["uk.gymshark.com", "reddit.com", "tiktok.com"], search_depth: "advanced" })` — runs on a timed interval (e.g. every 15 mins) to refresh the trending feed
- **Site mapping (status ribbon):** `tvly.map("https://uk.gymshark.com")` — called on load to verify domain is reachable; result count used to confirm GYMSHARK MCP source dot is green
- Results stored and cached in **Supabase** table `market_signals`
- Each API call emits an Overmind trace event visible in the terminal

---

### Section B — "What Your Audience is Asking AI Assistants"

**Layout:** Full-width card below the trending feed, `#0D0D0D` bg, accent top border.

**Header:** `AUDIENCE AI QUERIES` — what people are typing into ChatGPT, Gemini, Perplexity about Gymshark and activewear.

**Content:** A grid of **question cards** (3 columns), each showing:
- The question in quotes (e.g., *"What's the best Gymshark legging for HIIT?"*)
- Volume indicator: dot-size or number
- Intent tag: `DISCOVERY` / `COMPARISON` / `PURCHASE` / `LOYALTY` coloured pill
- Trend arrow: `↑` `→` `↓`

**Below the grid:** A **Thrads API integration note** (visible in Cursor/dev mode only):
> *Wire to `POST https://api.thrads.ai/v1/bid-request` — Thrads enables real-time prompt analysis across LLM applications. Each question card can trigger a contextual bid request to understand which ad contexts are firing against these audience queries.*

**Cursor/API notes:**
- Derive questions from Tavily crawl + Supabase synthesis
- Thrads `bid-request` endpoint: pass each question as `prompt` context; surface `ad_rank` and `context_score` as a data overlay on each card
- Overmind trace: log each Thrads API call with inputs and bid response to terminal

---

## Page 2 — Strategy Generator

### Purpose
Interactive campaign planning tool with a time-series chart broken into quarterly periods, segmented by marketing funnel stage. Selecting chart elements surfaces KPIs and budget performance.

### Chart Area (top 60% of page)

**Dual-chart layout — side by side:**

**Left: Stacked Bar Chart (quarterly campaign view)**
- X-axis: `Q1 | Q2 | Q3 | Q4`
- Y-axis: campaign volume / spend index
- Each bar is **segmented by funnel stage** with distinct colours:
  - `AWARENESS` → `#00D4FF` (bright cyan)
  - `INTEREST` → `#8B5CF6` (purple)
  - `CONSIDERATION` → `#F59E0B` (amber)
  - `INTENT` → `#EF4444` (red)
  - `EVALUATION` → `#10B981` (emerald)
- Bars are **clickable** — single click selects one bar; `Shift+click` or drag-select for multi-bar selection
- Selected bars highlight with a `2px` white outline and raise with a subtle `translateY(-2px)` animation
- Deselected bars dim to `40%` opacity

**Right: Complementary Line Chart**
- Mirrors the quarterly time axis
- Plots: `Leads`, `Spend`, `CPL` as separate lines
- Lines update dynamically to reflect only the **selected bars** from the bar chart
- Animated path draw on selection change (`stroke-dashoffset` animation, `400ms`)

**Chart interaction rules:**
- When 0 bars selected: show aggregate full-year view
- When 1+ bars selected: filter KPI panel to that period + funnel stage(s)
- Clicking a funnel-stage legend item filters to only that stage across all quarters

### KPI Panel (below charts, appears on selection)

When bars are selected, a **KPI strip** slides up from below the chart:

| KPI | Value | vs. Benchmark |
|-----|-------|---------------|
| Leads Generated | 14,230 | `+18% vs. industry` |
| CPL (Cost per Lead) | £4.20 | `↓ 12% MoM` |
| Spend | £62,400 | On-budget |
| ROAS | 4.2× | `↑ above target` |
| Funnel Drop-off | 34% (Interest→Consideration) | ⚠ Flag |

Use **industry-standard marketing benchmarks** for activewear/DTC e-commerce as comparison values.

### "Suggest New Strategy" Button

- Positioned top-right of the page
- Style: `#000` fill, `#FFF` border, bold uppercase label `GENERATE STRATEGY ↗`
- On click: triggers a Claude API call (via Anthropic `/v1/messages`) with a prompt constructed from the currently selected chart segments + current KPIs
- Response streams into a **slide-over panel** on the right (400px wide, dark bg)
- Panel shows the strategy recommendation with: Campaign theme, Channel mix, Budget reallocation suggestion, Risk flags
- Each suggestion is linked back to the supporting data with inline citations

**Cursor/API notes:**
- Strategy context enrichment: before calling Claude, pre-fetch with `tvly.research("Gymshark Q3 campaign performance activewear UK market", { output_schema: { trends: [], competitor_signals: [], audience_intents: [] } })` — structured JSON output feeds directly into the Claude system prompt as grounding context
- System prompt: *"You are a performance marketing strategist for Gymshark UK. Based on the provided quarterly campaign data and funnel metrics, generate a specific, data-backed campaign strategy..."*
- Overmind traces: log the full LLM input/output to terminal

---

## Page 3 — Budget Scenario Planner

### Purpose
An interactive CPL matrix showing three budget scenarios, with platform-level allocation driven by market intelligence results and fine-tunable by the user.

### Scenario Selector (top of page)

Three **scenario tabs** rendered as large toggle cards (`200px × 80px` each):

| Scenario | Style | Description |
|----------|-------|-------------|
| `CONSERVATIVE` | `#1A1A1A` bg, grey border | Lower spend, protect margins |
| `OPTIMISTIC` | `#0D1F0D` bg, green border | Balanced growth target |
| `AGGRESSIVE` | `#1F0D0D` bg, red border | Maximum reach, high spend |

Active scenario card: raised shadow, white border glow.

### CPL Matrix Table

A dense data table (`#0A0A0A` bg, `DM Mono` font):

**Rows:** Channels (Meta, Google, TikTok, Microsoft, Organic, Influencer)
**Columns:** Timeline (Month 1 → Month 6), Brand Awareness %, Loyalty Index, Estimated Leads, CPL, Spend

Each cell is **editable** (click to focus, type to update). On change:
- Row totals recalculate in real time
- Affected scenario P&L summary (bottom of table) updates instantly
- Changed cells pulse briefly with a `#FFB800` background flash to confirm edit

**Platform Allocation Breakdown (below table):**
- Horizontal stacked bar: shows `%` split of total budget across platforms
- Updates live as the table is edited or a new scenario is selected
- Labelled with `£` values and `%` share
- Colour-coded per platform: Meta `#1877F2`, Google `#4285F4`, TikTok `#FF0050`, Microsoft `#00A4EF`

**Fine-tune Controls (right sidebar, 280px):**
Sliders and toggles for:
- `Brand Awareness Weight` — range 0–100%
- `Loyalty vs. Acquisition` — left/right slider
- `Timeline Aggressiveness` — compressed (3mo) to extended (12mo)
- `Channels Active` — toggle per platform (linked to the status bar from Page 1)

Each control change triggers a **Supabase write** to persist the scenario state and a **re-query** to recalculate the matrix via API.

**Cursor/API notes:**
- Scenario data read/write: Supabase table `budget_scenarios` — CRUD via `@supabase/supabase-js`
- Matrix recalculation: triggered as a Supabase Edge Function `recalculate_cpl_matrix(scenario_id)`
- Market intelligence feed from Page 1 informs default channel weights (passed as context to the Edge Function)
- All API calls emit Overmind trace events to terminal

---

## Page 4 — Campaign Performance

### Purpose
Advanced signal dashboard tracking post-campaign performance metrics beyond standard ROAS — including LTV:CAC, retention, adstock decay, and before/after SIGNAL comparisons powered by Overmind and Thrads.

### Section A — Advanced KPI Cards (top row, 4 cards)

Each card: `#111` bg, `1px #1F1F1F` border, left accent bar by metric category.

| Card | Metric | Supporting data |
|------|--------|-----------------|
| 1 | **LTV : CAC** `3.8×` | LTV trend line (6-month sparkline), CAC breakdown by channel |
| 2 | **Retention Rate** `68%` | Cohort retention curve (mini heatmap, 3×6 grid of cells) |
| 3 | **Cart Abandonment** `24.3%` | Before/after comparison, recovery rate from retargeting |
| 4 | **CPL Delta** `−20%` | vs. prior period; leads delta `+40%` in green badge |

Cards are expandable (click to open detail drawer beneath).

### Section B — Before/After SIGNAL Comparison

A **split-panel view** showing two time windows side by side:

```
[ BEFORE PERIOD ]              [ AFTER PERIOD ]
  CPL: £6.20         →           CPL: £4.96  (−20%)
  Leads: 8,200       →           Leads: 11,480  (+40%)
  ROAS: 3.1×         →           ROAS: 4.2×
  Brand Search Vol.  →           +18% lift
```

Visual treatment: left panel in muted tones, right panel in brighter Gymshark-palette tones with a vertical divider. Delta values animate counting up on page load.

Source attribution shown below: *"Signal comparison powered by Overmind trace analysis — comparing campaign trace #1031–1042"*

### Section C — Adstock Decay Indicator

**Layout:** One row per active ad/campaign, with a decay curve visualisation.

Each row contains:
- Campaign name + platform icon
- **Adstock decay curve** (small SVG line chart, `120px wide`): shows signal strength decaying over time from the last impression
- **Signal badge** (3 states):
  - `HOLD` — `#FFB800` amber pill: signal still active, do not cut spend
  - `BUY` — `#00FF88` green pill: adstock depleted, re-invest now
  - `SELL` — `#FF4444` red pill: diminishing returns, pause or redirect

**Decision logic is driven by Overmind + Thrads:**
- Overmind Optimizer analyses LLM traces from ad copy testing to determine prompt-level performance
- Thrads `bid-request` endpoint is called per campaign: if `bid: null` (no winning contextual bid), flag as `SELL`
- If Thrads returns a high `ad_rank`, flag as `BUY`

Each signal badge has a tooltip: *"Determined by Overmind trace score + Thrads contextual bid signal at [timestamp]"*

**Cursor/API notes:**
- Overmind: `import { init, trace } from '@overmind/sdk'` — wrap each ad evaluation in a trace span
- Thrads: `POST https://api.thrads.ai/v1/bid-request` — pass campaign context as `prompt`; map `bid` value to HOLD/BUY/SELL threshold logic
- Supabase: write each signal determination to `adstock_signals` table with timestamp
- All determinations logged to the persistent terminal at bottom of page

---

## Implementation Notes for Cursor

### File Structure (suggested)
```
/src
  /components
    Terminal.tsx          ← Global persistent terminal (Overmind SDK)
    StatusRibbon.tsx      ← Data source status bar (Page 1)
    TrendCard.tsx         ← Market intelligence feed item
    FunnelChart.tsx       ← Interactive bar + line chart (Page 2)
    ScenarioPlanner.tsx   ← CPL matrix + sliders (Page 3)
    AdstockRow.tsx        ← Decay indicator + signal badge (Page 4)
  /lib
    overmind.ts           ← Overmind SDK init + trace wrapper
    thrads.ts             ← Thrads bid-request helper
    supabase.ts           ← Supabase client
    tavily.ts             ← Tavily search wrapper
    anthropic.ts          ← Claude API strategy generator
```

### Key API Integrations
| Integration | Endpoint | Use |
|-------------|----------|-----|
| Overmind JS SDK | `init()` + `trace()` | Terminal stream, agent tracing |
| Thrads API | `POST /v1/bid-request` | Adstock signals, audience query context |
| Tavily `/search` | `tvly.search(query, opts)` | Live trend keyword search |
| Tavily `/extract` | `tvly.extract(url)` | Gymshark page content extraction |
| Tavily `/crawl` | `tvly.crawl(url, opts)` | Full `uk.gymshark.com` brand crawl |
| Tavily `/map` | `tvly.map(url)` | Site reachability + URL inventory (status dot) |
| Tavily `/research` | `tvly.research(input, { output_schema })` | Structured agentic research for strategy context |
| Supabase | REST + Edge Functions | Data persistence, scenario state |
| Anthropic | `POST /v1/messages` | Strategy generation (Page 2) |
| Ad Platforms | Mocked JSON fixtures | Meta, Google, TikTok, Microsoft data |

### Supabase Tables Needed
- `market_signals` — Tavily crawl results, timestamps, source tags
- `campaign_kpis` — quarterly funnel metrics per campaign
- `budget_scenarios` — CPL matrix rows, scenario configs
- `adstock_signals` — decay curves, HOLD/BUY/SELL determinations, timestamps

---
*Prepared for Figma → Cursor handoff. All pages share the terminal component. Brand colours verified against `uk.gymshark.com` live crawl.*
