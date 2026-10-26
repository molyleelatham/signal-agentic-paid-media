# LLM architecture: Cursor agents vs OpenAI generative

SIGNAL uses **two LLM backends** on purpose. They are not interchangeable.

## Cursor SDK + Composer 2.5 (agent runtime)

**Use for:** Running and optimizing the registered SIGNAL agents under test.

| Component | Backend |
|-----------|---------|
| `BaseAgent.think()` | Cursor Composer 2.5 when `CURSOR_API_KEY` is set |
| Overmind entrypoint harnesses (`services/agents/overmind/*`) | Same — invokes agents that call Composer |
| `overmind agent validate` / baseline / eval | Agent subprocess uses Composer via harness |

**Configure in** `.env.local` (app) and `.overmind/.env` (Overmind runner loads this for agent subprocesses):

```bash
CURSOR_API_KEY=cursor_...
CURSOR_MODEL=composer-2.5
```

Get keys at [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations).

Composer is **not** exposed as a standard LiteLLM chat-completion provider. Overmind’s internal analyzer cannot call `cursor/composer-2.5` via `litellm.completion` today.

## OpenAI (Overmind generative / analyzer)

**Use for:** Everything Overmind does with LiteLLM — setup, diagnosis, synthetic datasets, optimization analyzer.

| Component | Backend |
|-----------|---------|
| `overmind setup` | `ANALYZER_MODEL` + `SYNTHETIC_DATAGEN_MODEL` (OpenAI) |
| `overmind optimize` / `optimize-step diagnose` | `ANALYZER_MODEL` (OpenAI) |
| Fallback when Cursor is unavailable in app | `OPENAI_API_KEY` via `BaseAgent` |

**Configure in** `.overmind/.env`:

```bash
OPENAI_API_KEY=sk-...
ANALYZER_MODEL=gpt-4o-mini
SYNTHETIC_DATAGEN_MODEL=gpt-4o-mini
OVERMIND_API_KEY=ovr_...
```

## Quick reference

| Task | Key | Model |
|------|-----|-------|
| Agent chat / trading / briefs | `CURSOR_API_KEY` | `composer-2.5` |
| Overmind setup & optimize loop | `OPENAI_API_KEY` | `gpt-4o-mini` (or stronger OpenAI model) |
| Overmind tracing | `OVERMIND_API_KEY` | — |

## Bootstrap

`scripts/bootstrap_overmind_env.py` is not in this repository. Put the keys in `.env` (the app reads `.env` and `.env.local`) and copy the same values into `.overmind/.env` for the Overmind CLI.

Overmind setup fails if `OPENAI_API_KEY` is still a placeholder.

## Optimization path

- **Agent evals** exercise Composer (what you are improving).
- **Overmind analyzer** proposes code changes using OpenAI (how you decide what to change).

That matches “Cursor SDK + Composer for the agent; OpenAI for generative Overmind tooling.”
