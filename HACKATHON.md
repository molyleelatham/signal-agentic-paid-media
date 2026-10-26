# SIGNAL at the Cursor AdTech hackathon

**Result: 1st place.**

This is the hackathon write-up. For a guide to the code as it stands, see [README.md](README.md).

## The event

The repository does not record the venue or the official dates. The commits from the build are 27 and 28 May 2026, UK time.

The old README lists Overmind, Tavily and Thrad as stack sponsors, and the submission is built around those three: Overmind for agent registration and tracing, Tavily for web research, and Thrad for intent.

## What was submitted

SIGNAL was shown as an assistant for paid-media optimisation. A person still approves the creative and strategic calls. The trading maths proposes the bid and the budget split.

**Agents.** Five agents are registered in `.overmind/agents.toml`: bid strategy, content brief, creative optimisation, market analysis and orchestration. Entry points are under `services/agents/overmind/`. The trigger service (`services/common/agent_trigger_service.py`) also defines keyword classification, Tavily research and campaign allocation. The HTTP routes mount bid optimisation, content generation, creative optimisation, market analysis, keyword classification, Tavily research, orchestration and a bulk call. Each result can carry tokens used, a cost and an execution time.

**Research and segments.** A Tavily query is mapped onto 13 DisBERT segments, A to M, in `services/intelligence/tavily_to_disbert_mapper.py`. Commercial-intent scores are a fixed table in `services/intelligence/disbert_thrad_classification.py`. They run from 0 (segment M, which the table blocks) to 0.95 (segment H, purchasable products). Assigning a segment to a query is keyword matching. The function notes that a live model would replace that in production. `ThradBERTClient` defaults to demo mode.

**Trading.** Bid discovery, cold start, Thompson sampling, adstock decay and asymmetric P&L are described in the README. They were already in the first commit.

**Front end.** The React app uses TanStack Query. The terminal page has trigger buttons with a loading state and the execution time. The market-intelligence page can show the DisBERT segments returned for a research query. Charts are drawn as SVG in `frontend/src/components/shared/charts.tsx`. The demo data is the Gymshark sample set loaded by `scripts/demo_data.py`, not a live ad account.

**Attention tokens.** The scoring lives in `services/analytics/asymmetric_pnl.py`. Wasted attention is penalised at λ = 2 by default, and that score can be turned into a token reward or burn. There is no `services/token` package. The tables are `shared/models/token.py`.

## Commit history

Times are UK time.

| When | What |
|---|---|
| 27 May, 01:10 | First commit. The platform arrives in one go: 65 files, 17,075 lines, including the trading engine. History before this commit is not in the repo, so the log cannot show what was written before the event. |
| 28 May, 02:11 | Planning and media-buying flows split into separate services. |
| 28 May, 20:00–20:45 | Terminal API wired to the Gymshark data, Makefile and local database setup, Overmind configuration. |
| 28 May, 22:21 | Agent triggers and DisBERT mapping, wired into the front end. In this commit the demo, planning, media-buying, Cursor and chat routers are commented out. |
| 28 May, 22:53–23:16 | Hackathon overview, project docs and front-end polish. |
| 31 May | Tidied for a public view: longer docs moved under `docs/`, then sample data and setup scripts restored. |
| 1 June | Product summary added. |

## What was true at submission, and what has changed since

At submission there was no automated test suite. The `scripts/test_*.py` files are manual smoke scripts against live services. No Alembic revision was committed (`.gitignore` ignored `alembic/versions/*.py`). The schema was created only if something imported the models and called `create_all`. The demo, planning and media-buying routers were already unmounted by the evening of 28 May.

The README describes the repository now, including the offline pytest suite and the initial migration.
