# SIGNAL — Technical Algorithm & Science Specification
**For engineering handoff**
**Product:** Autonomous Media Trading Platform
**Stack sponsors:** Overmind · Tavily · Thrad AI

---

## Philosophy

The system is **human-in-the-loop autonomous**. The trading engine executes media buying without requiring constant marketer input — but at every significant decision point it surfaces the intelligence that drove that decision, so a marketer can understand, question, and override it. AI handles price discovery, position sizing, decay detection, and execution. The marketer retains creative agency: what angles to run, which audiences feel right, whether the gap the system found actually matches their brand.

Tavily's search agent is the intelligence layer — it is always running, always feeding context. Thrad's BERT intent signal is not just a bidding input, it is a **context surface** — shown to the marketer as "here is what your audience is actually asking AI assistants about, here is where you are absent." The marketer uses that to make creative decisions. The trading engine uses it to price inventory.

---

## Module 1 — Intelligence Ingestion (Tavily)

### 1.1 Tavily search agent — always-on market scanner

The Tavily search agent runs continuously, not just on a schedule. It uses `search_and_answer` with sub-query decomposition to maintain a live picture of the market the system is trading in.

**What it runs:**

```
search_and_answer:
  query: "what are people asking about [category] right now"
  max_number_of_subqueries: 4
  topic: "general"
  time_range: "week"
  model_config: anthropic:claude-sonnet-4-6
  fallback: groq:llama-3.3-70b-versatile

search_dedup:
  queries: [
    "[category] trends this week",
    "[competitor A] recent campaigns",
    "[competitor B] recent campaigns",
    "[category] common complaints reviews",
    "[category] first time buyer questions",
  ]
  search_depth: "advanced"
  max_results: 10
  chunks_per_source: 5
  time_range: "week"

social_media_search:
  platform: "combined"   # Reddit, X, LinkedIn, TikTok, Instagram, Facebook
  time_range: "week"
  max_results: 50
  include_raw_content: True

crawl_and_summarize:
  competitor URLs: weekly
  select_paths: ["/blog/.*", "/guides/.*", "/resources/.*"]
  max_depth: 2
  output_schema: CompetitorContent (Pydantic)
```

**Output:** unified document corpus, tagged by source type:
- `source: "competitor"` — competitor content
- `source: "market"` — general market content
- `source: "social"` — organic social posts
- `source: "brand"` — the marketer's own content

**What the marketer sees from this:**
A weekly intelligence digest — not a data dump. Three sections:

1. **What your audience is talking about** — top 5 conversation themes on social this week, with example posts
2. **What competitors published** — topics they went after, angles they used
3. **Where you were mentioned** — brand citations in AI answers, sentiment, context

This is the creative intelligence layer. The marketer reads this and decides what content angles to prioritise. The trading engine reads the same data and prices inventory accordingly.

---

### 1.2 Thrad BERT intent signal — demand context surface

Thrad's BERT classifier reads LLM user prompts from its corpus and outputs intent classifications. This is used in two distinct ways:

**Way 1 — Trading signal (automated):** Intent volume by topic cluster informs bid weights. High purchase-intent volume on a topic cluster = bid up on that inventory.

**Way 2 — Marketer context (surfaced to UI):** The raw intent data is shown to the marketer as a demand map. "48,000 people asked an AI assistant about first-time buyer home insurance this month. Your brand was mentioned in 0 of those conversations." That is a creative decision prompt, not just a bidding input.

**How BERT intent classification works (for dev context):**

BERT (Bidirectional Encoder Representations from Transformers) is a transformer encoder. Thrad fine-tunes it on their labelled LLM prompt corpus.

Architecture:
```
Input prompt → WordPiece tokeniser → [CLS] t1 t2 ... [SEP]
  → 12 transformer encoder layers
    (each layer: multi-head self-attention across all token pairs, bidirectional)
  → [CLS] token final hidden state (768-dim vector)
  → Linear classification head: Linear(768, num_classes)
  → Softmax → intent probability distribution
```

Output per prompt:
```json
{
  "purchase_intent": 0.71,
  "research_intent": 0.22,
  "awareness_intent": 0.05,
  "brand_specific_intent": 0.02
}
```

**Thrad API call for gap analysis:**
```python
thrad_signal = thrad_client.get_intent_volume(
    topic_cluster="home insurance first time buyer",
    intent_types=["purchase_intent", "research_intent"],
    brand_filter="exclude:your_brand",
    time_range="30d"
)
# Returns: { purchase_intent: 48200, research_intent: 112000, brand_mentions: 0 }
```

**What this surfaces to the marketer:**
A demand map UI component — topic clusters ranked by intent volume, with your brand's presence score overlaid. The marketer sees exactly where they are absent in high-demand conversations. They decide whether to act on it. The trading engine uses the same signal to weight bids.

---

## Module 2 — BERTopic Gap Matrix

### 2.1 What it is

A topic model that clusters all intelligence inputs into coherent semantic groups, scores each group on three axes, and classifies each into a strategic zone. This is the shared intelligence layer — marketer and trading engine both read from it.

### 2.2 Pipeline

**Step 1 — Embedding**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")
embeddings = model.encode(all_documents, batch_size=32, show_progress_bar=True)
```

**Step 2 — Dimensionality reduction**
```python
from umap import UMAP

umap_model = UMAP(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric="cosine",
    random_state=42
)
reduced_embeddings = umap_model.fit_transform(embeddings)
```

**Step 3 — Clustering**
```python
from hdbscan import HDBSCAN

hdbscan_model = HDBSCAN(
    min_cluster_size=15,
    min_samples=10,
    metric="euclidean",
    cluster_selection_method="eom",
    prediction_data=True
)
```

**Step 4 — BERTopic fit**
```python
from bertopic import BERTopic

topic_model = BERTopic(
    embedding_model=model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    nr_topics="auto",
    verbose=True
)
topics, probs = topic_model.fit_transform(all_documents, embeddings)
```

**Step 5 — Temporal slicing (topic velocity)**
```python
topics_over_time = topic_model.topics_over_time(
    docs=all_documents,
    timestamps=doc_timestamps,
    nr_bins=6,              # monthly bins, last 6 months
    evolution_tuning=True,
    global_tuning=True
)
```
Topic velocity = rate of change in document frequency per cluster per month. Rising velocity = emerging demand. Falling velocity = fading topic (competitor may be abandoning it — gap opening).

### 2.3 Three-axis scoring

For each topic cluster:

| Axis | Signal | Computation |
|---|---|---|
| Competitor coverage | Count of `source:competitor` docs in cluster | `competitor_score = n_competitor_docs / total_cluster_docs` |
| Thrad intent volume | Purchase + research intent prompts from Thrad API | `intent_score = log1p(purchase_intent + research_intent) / log1p(max_intent_across_clusters)` |
| Brand presence | Count of `source:brand` docs + LLM citation mentions | `brand_score = n_brand_docs / total_cluster_docs` |

Log-normalise intent volume to prevent one dominant cluster from compressing all others.

### 2.4 Zone classification

```python
def classify_zone(competitor_score, intent_score, brand_score,
                  thresholds={"high": 0.6, "low": 0.3}):
    H, L = thresholds["high"], thresholds["low"]

    if competitor_score > H and intent_score > H and brand_score < L:
        return "gap"        # attack — high demand, competitors there, you're not
    elif competitor_score > H and intent_score > H and brand_score >= L:
        return "contested"  # differentiate — you're present but so are they
    elif competitor_score < L and intent_score > H and brand_score > H:
        return "owned"      # defend — you own this, competitors haven't found it
    elif intent_score < L:
        return "ignore"     # no demand, not worth attacking regardless of competition
    else:
        return "monitor"    # ambiguous — watch for movement
```

### 2.5 What the marketer sees

Gap matrix UI: a scatter plot with competitor coverage on X, intent volume on Y, bubble size = your brand presence, colour = zone. Marketer clicks a bubble to see: what people are actually saying in this cluster (example social posts from Tavily), which competitors are active here (from crawl), what the Thrad intent volume is (demand size). They decide whether this is a topic they want to pursue creatively. The trading engine uses the same zones to weight bid strategy.

---

## Module 3 — LOESS / DMR Bid Discovery

### 3.1 What it solves

Media auctions have non-linear supply curves — the relationship between bid price and conversion rate is not linear. Below a threshold bid, you win too little inventory to matter. Above the DMR inflection point, incremental bid increases produce rapidly diminishing conversion returns. Most media buyers operate in the saturation zone, systematically overpaying. This module finds the inflection point empirically.

### 3.2 LOESS fit

LOESS (Locally Weighted Scatterplot Smoothing) — non-parametric regression. No assumption about curve shape. Each point on the curve is estimated using only nearby observations, weighted by distance.

```python
from statsmodels.nonparametric.smoothers_lowess import lowess
import numpy as np

def fit_loess_curve(bid_prices: np.ndarray, conversion_rates: np.ndarray,
                    frac: float = 0.3, it: int = 3):
    """
    frac: bandwidth — fraction of data used in each local regression.
          Lower = more local, captures fine structure but noisier.
          Higher = smoother, more stable, less responsive to local variation.
          0.3 is a reasonable default for media auction data.
    it: robustness iterations — downweights outliers. 3 is standard.
    """
    smoothed = lowess(
        endog=conversion_rates,
        exog=bid_prices,
        frac=frac,
        it=it,
        return_sorted=True
    )
    return smoothed[:, 0], smoothed[:, 1]   # bid_grid, smoothed_conv_rate
```

### 3.3 DMR inflection point detection

Fit a spline to the LOESS output. Take first and second derivatives. Inflection point = where second derivative crosses zero — the boundary between increasing and decreasing marginal returns.

```python
from scipy.interpolate import UnivariateSpline
from scipy.optimize import brentq

def find_dmr_optimal(bid_grid: np.ndarray, conv_grid: np.ndarray,
                     buffer: float = 0.92):
    """
    buffer: bid at 92% of inflection point — stay on the efficient
            part of the curve, don't push to the exact boundary.
    """
    spline = UnivariateSpline(bid_grid, conv_grid, s=0.01, k=4)
    d1 = spline.derivative(n=1)
    d2 = spline.derivative(n=2)

    try:
        inflection = brentq(d2, bid_grid.min(), bid_grid.max())
    except ValueError:
        # No sign change — curve is monotonic (very sparse data)
        # Fall back to point of maximum first derivative
        inflection = bid_grid[np.argmax(d1(bid_grid))]

    optimal_bid = inflection * buffer

    return {
        "optimal_bid": float(optimal_bid),
        "inflection_point": float(inflection),
        "expected_conv_rate": float(spline(optimal_bid)),
        "marginal_return": float(d1(optimal_bid)),
        "curve_confidence": "high" if len(bid_grid) >= 50 else "low"
    }
```

### 3.4 Temporal surface — non-stationarity handling

Auction dynamics shift over time. A curve fitted on last quarter's data may be stale. Fit LOESS per weekly cohort, then LOESS again across the time series of optimal bids to produce a smoothed forward signal.

```python
def build_temporal_surface(historical_data: pd.DataFrame) -> pd.DataFrame:
    """
    For each week cohort: fit LOESS, extract DMR optimal bid.
    Then fit LOESS across the time series of optimal bids.
    Output: smoothed optimal bid trajectory with forward extrapolation.
    """
    weekly_optima = []

    for week, cohort in historical_data.groupby("week_cohort"):
        if len(cohort) < 20:
            continue  # too sparse for stable fit
        bid_grid, conv_grid = fit_loess_curve(
            cohort["bid_price"].values,
            cohort["conversion_rate"].values
        )
        result = find_dmr_optimal(bid_grid, conv_grid)
        weekly_optima.append({"week": week, "optimal_bid": result["optimal_bid"]})

    df = pd.DataFrame(weekly_optima).sort_values("week")

    # LOESS on the time series of optimal bids
    smoothed_trajectory = lowess(
        endog=df["optimal_bid"].values,
        exog=np.arange(len(df)),
        frac=0.4,
        it=2
    )

    return smoothed_trajectory  # forward-extrapolate for next week's bid
```

**What the marketer sees from this:**
A bid curve chart per topic cluster — the empirical supply curve with the DMR point marked. Marketer can see: "the system is bidding £1.40 CPM because that's where marginal returns start collapsing on this audience." They can override the bid if they have domain knowledge the model doesn't (e.g. "this is a launch week, I want to be more aggressive").

---

## Module 4 — Bayesian Cold Start (Empirical Bayes)

### 4.1 The problem

LOESS requires at least 50 observations per (topic cluster, platform) pair for a stable fit. New campaigns, new topic clusters, and new platforms start with zero data. Without a principled cold start, the system either refuses to bid (too conservative) or bids arbitrarily (dangerous).

### 4.2 James-Stein shrinkage — shrink toward global prior

```python
def bayesian_bid(topic_cluster: str, platform: str,
                 cluster_data: pd.DataFrame,
                 global_prior: dict) -> dict:
    """
    Shrink cluster-specific LOESS estimate toward global category prior.
    Shrinkage weight proportional to data richness.

    James-Stein shrinkage: individual estimate pulled toward grand mean,
    with weight inversely proportional to uncertainty (sample size).

    global_prior = {
        "mean_optimal_bid": float,   # average DMR optimal across all clusters
        "pseudo_count": int,         # e.g. 30 — effective prior sample size
        "std": float                 # prior variance
    }
    """
    n = len(cluster_data)
    shrinkage_weight = n / (n + global_prior["pseudo_count"])

    if n >= 50:
        bid_grid, conv_grid = fit_loess_curve(
            cluster_data["bid_price"].values,
            cluster_data["conversion_rate"].values
        )
        cluster_optimal = find_dmr_optimal(bid_grid, conv_grid)["optimal_bid"]
    else:
        cluster_optimal = global_prior["mean_optimal_bid"]

    # Posterior estimate: weighted combination
    posterior_bid = (
        shrinkage_weight * cluster_optimal +
        (1 - shrinkage_weight) * global_prior["mean_optimal_bid"]
    )

    return {
        "bid": posterior_bid,
        "confidence": shrinkage_weight,   # 0 = pure prior, 1 = cluster-specific
        "n_observations": n,
        "mode": "cold_start" if n < 50 else "fitted"
    }
```

### 4.3 Epsilon-greedy exploration during cold start

During cold start, the system deliberately samples different bid points to build the dataset needed for LOESS fitting. This is intentional, not a failure mode. The marketer is told about it.

```python
def cold_start_bid(n_obs: int, posterior_bid: float,
                   explore_range: float = 0.25) -> float:
    """
    Epsilon decreases linearly as observations accumulate.
    At n=0: fully exploratory (epsilon=1.0)
    At n=50: fully exploitative (epsilon=0.0)

    Exploration samples uniformly from ±explore_range around posterior bid.
    This deliberately maps different points on the supply curve.
    """
    epsilon = max(0.0, 1.0 - (n_obs / 50))

    if np.random.random() < epsilon:
        bid = posterior_bid * np.random.uniform(
            1 - explore_range, 1 + explore_range
        )
        mode = "exploring"
    else:
        bid = posterior_bid
        mode = "exploiting"

    return {"bid": bid, "mode": mode, "epsilon": epsilon}
```

---

## Module 5 — Thompson Sampling Budget Allocator

### 5.1 What it solves

Given a fixed budget across N platforms (Meta, Google, Thrad), how much goes to each? Not a static split. A dynamic allocation that tracks which platforms are actually delivering efficiently and shifts capital toward them — while still exploring underperforming platforms in case conditions have changed.

### 5.2 Beta-Bernoulli bandit

Model each platform as an arm. Each auction event is a Bernoulli trial: did spend convert (success) or not (failure)?

```python
import numpy as np
from dataclasses import dataclass

@dataclass
class PlatformPosterior:
    platform: str
    alpha: float = 2.0   # successes + prior
    beta:  float = 2.0   # failures + prior
    # Beta(2,2) prior: weakly informative, symmetric, neither arm starts dominant

def update_posterior(posterior: PlatformPosterior,
                     conversions: int, non_converting_spend: int):
    posterior.alpha += conversions
    posterior.beta  += non_converting_spend
    return posterior

def thompson_allocate(posteriors: list[PlatformPosterior],
                      total_budget: float,
                      floors: dict,      # minimum budget per platform
                      caps: dict) -> dict:
    """
    Sample from each platform's posterior.
    Allocate budget proportional to samples.
    Enforce floor and cap hard constraints after sampling.
    """
    samples = {
        p.platform: np.random.beta(p.alpha, p.beta)
        for p in posteriors
    }

    total_sample = sum(samples.values())
    raw_allocation = {
        platform: (sample / total_sample) * total_budget
        for platform, sample in samples.items()
    }

    # Enforce floors
    allocation = {}
    remaining = total_budget
    for platform, amount in raw_allocation.items():
        floored = max(amount, floors.get(platform, 0))
        capped  = min(floored, caps.get(platform, float("inf")))
        allocation[platform] = capped
        remaining -= capped

    # Redistribute any remaining proportionally to uncapped platforms
    # (standard constraint enforcement, implementation detail)
    return allocation
```

**What the marketer sees:**
"Meta is receiving 62% of budget this week — it's converting at the highest rate. Google is at 28% — still building data. Thrad is at 10% — exploratory." With an override slider if they want to force a different split.

---

## Module 6 — Thrad Contextual Bid

### 6.1 What it does

Each Thrad auction comes with an intent classification of the specific LLM prompt that triggered it. The bid scales by how well that intent aligns with the campaign goal.

### 6.2 Intent-goal alignment matrix

```python
INTENT_GOAL_ALIGNMENT = {
    "lead_generation": {
        "purchase_intent":   1.4,   # ready to act — bid up
        "research_intent":   0.9,   # gathering info — near-normal bid
        "awareness_intent":  0.4,   # discovery — discount
        "brand_specific":    1.6    # asking about you — bid up hard
    },
    "customer_acquisition": {
        "purchase_intent":   1.6,
        "research_intent":   1.0,
        "awareness_intent":  0.5,
        "brand_specific":    1.8
    },
    "brand_awareness": {
        "purchase_intent":   0.6,
        "research_intent":   1.1,
        "awareness_intent":  1.5,   # discovery — this is who you want
        "brand_specific":    0.8
    },
    "retargeting": {
        "purchase_intent":   1.8,   # already warm — bid aggressively
        "research_intent":   0.5,
        "awareness_intent":  0.2,
        "brand_specific":    2.0    # they're asking about you — maximum bid
    }
}

def thrad_contextual_bid(loess_optimal: float,
                          prompt_intent: dict,
                          goal_type: str) -> float:
    alignment = INTENT_GOAL_ALIGNMENT[goal_type]

    # Weighted sum of intent scores × alignment weights
    intent_weight = sum(
        prompt_intent.get(bucket, 0) * alignment[bucket]
        for bucket in alignment
    )
    # intent_weight > 1.0 → bid above LOESS optimal
    # intent_weight < 1.0 → bid below
    return loess_optimal * intent_weight
```

**What the marketer sees from Thrad intent data:**
A topic-level demand map. "Research intent volume on 'first time buyer home insurance': 112,000 prompts/month. Your brand cited: 0 times." This is context for the marketer's creative decisions — not just an automated bidding input. They decide whether to brief content around this topic. The system handles the bidding either way.

---

## Module 7 — Adstock Theta Decay Monitor

### 7.1 The problem

Creative effectiveness decays over time. Audiences see the same ad, novelty disappears, CTR drops, CPL rises. Holding a position past the point of alpha exhaustion is equivalent to holding a losing trade — the loss compounds daily. Most buyers wait until performance visibly collapses before rotating. By then they've already overpaid for depleted inventory.

### 7.2 Adstock model

Classical adstock: `A_t = x_t + λ · A_{t-1}`

Where:
- `x_t` = raw effect at time t (daily conversions)
- `λ` = retention rate (0–1) — the decay parameter
- `A_t` = cumulative adstock effect at time t

λ close to 1 → slow decay, strong residual effect, creative still working
λ close to 0 → fast decay, creative exhausted

### 7.3 Fitting λ from position data

```python
from scipy.optimize import curve_fit
import numpy as np

def fit_adstock_lambda(daily_conversions: np.ndarray) -> dict:
    """
    Fit adstock decay model to observed daily conversion time series.
    Recover λ (retention rate) and initial_effect.
    """
    t = np.arange(len(daily_conversions))

    def adstock_curve(t, lambda_decay, initial_effect):
        return initial_effect * (lambda_decay ** t)

    try:
        params, covariance = curve_fit(
            adstock_curve,
            xdata=t,
            ydata=daily_conversions,
            p0=[0.5, daily_conversions[0]],
            bounds=([0, 0], [1, np.inf]),
            maxfev=5000
        )
        lambda_decay, initial_effect = params
        std_error = np.sqrt(np.diag(covariance))[0]  # uncertainty in λ

    except RuntimeError:
        # Fit failed — insufficient data or flat signal
        lambda_decay, std_error = 0.5, 0.5  # conservative unknown

    return {
        "lambda": float(lambda_decay),
        "std_error": float(std_error),
        "confidence": "high" if std_error < 0.1 else "low",
        "signal": classify_decay_signal(lambda_decay)
    }

def classify_decay_signal(lambda_val: float) -> str:
    if lambda_val > 0.7:  return "hold"     # strong residual, keep running
    if lambda_val > 0.4:  return "reduce"   # fading, reduce budget on this position
    return "exit"                            # alpha exhausted, rotate creative
```

### 7.4 What the marketer sees

Per active creative: a decay indicator. "This ad has a retention rate of λ=0.38 — effectiveness is fading fast. Recommend rotating." With the LOESS bid curve for the same cluster showing what a fresh creative could recapture. The marketer decides whether to act on the rotation recommendation and what angle to take next.

---

## Module 8 — Asymmetric P&L Scorer

### 8.1 The principle

Impressions and clicks without conversion are not neutral. They are evidence of mismatch between what the ad promised and what the audience wanted — and they cost money. Treating them as positive or zero signals produces systems that optimise for vanity metrics. Treating them as negative signals with a loss-aversion multiplier produces systems that optimise for actual P&L.

This is grounded in Prospect Theory (Kahneman & Tversky): losses loom larger than equivalent gains. Setting λ_penalty = 2.0 reflects empirical loss aversion ratios from behavioural economics.

### 8.2 Formula

```python
def position_pnl(
    conversions: int,
    avg_order_value: float,
    total_impressions: int,
    converting_impressions: int,    # impressions that led to conversion
    total_clicks: int,
    converting_clicks: int,         # clicks that led to conversion
    cpm: float,
    cpc: float,
    lambda_penalty: float = 2.0
) -> dict:
    """
    Gross revenue: conversion value
    Wasted attention cost: spend on impressions + clicks that didn't convert
    Net P&L: asymmetric — wasted attention penalised at 2× rate
    """
    gross_revenue = conversions * avg_order_value

    wasted_impressions = total_impressions - converting_impressions
    wasted_clicks = total_clicks - converting_clicks

    attention_waste_cost = (
        (wasted_impressions * cpm / 1000) +
        (wasted_clicks * cpc)
    )

    net_pnl = gross_revenue - (lambda_penalty * attention_waste_cost)

    return {
        "gross_revenue": gross_revenue,
        "attention_waste_cost": attention_waste_cost,
        "net_pnl": net_pnl,
        "efficiency_ratio": gross_revenue / max(attention_waste_cost, 0.01),
        "lambda_applied": lambda_penalty
    }
```

### 8.3 How this feeds Overmind

Every Overmind trace for a bid decision or brief is evaluated against its downstream P&L score. The LLM judge uses net_pnl as ground truth — not "did the brief get clicks" but "did the attention it attracted convert, and how efficiently." This is the reward signal that drives the self-improvement loop.

---

## Module 9 — Goal-Adjusted Concentration Risk (CAI)

### 9.1 What CAI measures

Creative Attention Index — a Herfindahl-Hirschman style concentration measure. Measures how evenly impressions are distributed across topic clusters and creatives.

```python
def compute_cai(impression_shares: dict) -> float:
    """
    impression_shares: { cluster_id: fraction_of_total_impressions }
    Returns: CAI in [0, 1]
    0 = perfectly distributed (one cluster per impression)
    1 = all impressions on one cluster
    """
    return sum(share ** 2 for share in impression_shares.values())
```

### 9.2 Goal-conditional targets

CAI is not universally good or bad. The risk is deviation from the optimal concentration level for the campaign goal.

```python
GOAL_CONCENTRATION_TARGETS = {
    "lead_generation":       {"target_cai": 0.55, "tolerance": 0.15},
    "customer_acquisition":  {"target_cai": 0.40, "tolerance": 0.15},
    "brand_awareness":       {"target_cai": 0.20, "tolerance": 0.10},
    "retargeting":           {"target_cai": 0.80, "tolerance": 0.10},
    # Retargeting SHOULD be concentrated — high CAI is correct here
}

def goal_adjusted_risk(actual_cai: float, goal_type: str) -> dict:
    target = GOAL_CONCENTRATION_TARGETS[goal_type]
    deviation = abs(actual_cai - target["target_cai"])
    risk_score = max(0.0, deviation - target["tolerance"])

    return {
        "actual_cai": actual_cai,
        "target_cai": target["target_cai"],
        "deviation": deviation,
        "risk_score": risk_score,
        "flag": risk_score > 0.1,
        "direction": "too_concentrated" if actual_cai > target["target_cai"] else "too_dispersed"
    }
```

**What the marketer sees:**
Not "your CAI is 0.82" — that's meaningless. Instead: "You're running a brand awareness campaign but 82% of impressions are going to one audience segment. That's atypical for awareness goals — is this intentional?" The marketer decides. For a retargeting campaign the same CAI would show no flag at all.

---

## Module 10 — Overmind Agent Tracing

### 10.1 What Overmind does

Every LLM call and tool call in the system is intercepted by the Overmind SDK. Overmind:
1. Records full trace: input, tool calls, output, latency, cost
2. Evaluates each trace against auto-generated quality criteria using an LLM judge
3. Generates candidate prompt variations based on underperforming traces
4. A/B tests candidates on holdout traces
5. Surfaces recommendations: model swaps, prompt rewrites, control flow changes

### 10.2 Integration pattern

```python
from overmind import OvmClient

ovm = OvmClient(api_key=OVERMIND_API_KEY)

@ovm.trace(
    name="content_brief_generator",
    tags=["gap_zone", "purchase_intent"],
    quality_criteria=[
        "Strategic angle is differentiated from all identified competitor angles",
        "Hook type is appropriate for the specified target platform and format",
        "Proof point is specific and verifiable — not a generic claim",
        "CTA matches the intent stage of the target audience",
        "Brief contains enough specificity that a creative could execute without clarifying questions"
    ]
)
async def generate_brief(gap_topic: dict, platform: str, goal_type: str) -> dict:
    ...

@ovm.trace(
    name="bid_calculator",
    tags=["loess", "dmr"],
    quality_criteria=[
        "Bid is at or below the DMR inflection point",
        "Cold start mode is correctly identified and communicated",
        "Bid reflects current posterior shrinkage weight"
    ]
)
async def calculate_bid(cluster_id: str, platform: str) -> dict:
    ...
```

### 10.3 P&L score as Overmind ground truth

The asymmetric P&L score (Module 8) is passed back to Overmind as the downstream outcome label for every brief and bid decision. This makes the judge's evaluation grounded in real-world outcome, not just prompt quality heuristics.

```python
# After campaign data is available (T+7 days):
ovm.log_outcome(
    trace_id="trace_7f3a2b91",
    outcome_label="net_pnl",
    outcome_value=position_pnl_result["net_pnl"]
)
# Overmind uses this to update judge criteria weights
# and prioritise which prompt experiments to run next
```

---

## Module 11 — Open-Source Creative Scoring

No black-box vendor models. Every creative scoring decision is auditable and reproducible.

### 11.1 Visual intent fit — CLIP

```python
import clip
import torch
from PIL import Image

model, preprocess = clip.load("ViT-B/32", device="cuda")

def score_creative_intent_fit(image_path: str, intent_labels: list[str]) -> dict:
    """
    Map image and text labels into shared CLIP embedding space.
    Cosine similarity = how well the creative visual matches each intent.
    """
    image = preprocess(Image.open(image_path)).unsqueeze(0).to("cuda")
    text  = clip.tokenize(intent_labels).to("cuda")

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features  = model.encode_text(text)
        similarity = (image_features @ text_features.T).softmax(dim=-1)

    return dict(zip(intent_labels, similarity[0].cpu().tolist()))

# Example output:
# { "first time buyer anxiety": 0.61, "price comparison": 0.24, "trust signals": 0.15 }
```

### 11.2 Creative diversity — pairwise similarity

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def creative_diversity_score(creative_embeddings: list[np.ndarray]) -> dict:
    """
    Pairwise cosine similarity across all active creatives.
    Mean similarity > 0.7 → homogeneity risk (algorithm may suppress duplicates).
    """
    matrix = cosine_similarity(creative_embeddings)
    np.fill_diagonal(matrix, 0)   # exclude self-similarity

    mean_similarity = matrix.mean()
    max_similarity  = matrix.max()

    return {
        "mean_similarity": float(mean_similarity),
        "max_similarity": float(max_similarity),
        "diversity_flag": mean_similarity > 0.7,
        "recommendation": "rotate_creative" if mean_similarity > 0.7 else "ok"
    }
```

### 11.3 Hook taxonomy — sentence transformers

```python
from sentence_transformers import SentenceTransformer, util

sbert = SentenceTransformer("all-mpnet-base-v2")

HOOK_ARCHETYPES = {
    "problem_empathy":  "You're struggling with X and you're not alone in this",
    "social_proof":     "Thousands of people like you have already solved X with us",
    "curiosity_gap":    "The one thing most people never find out about X",
    "direct_offer":     "Get X for Y — simple, fast, no hidden terms",
    "authority_data":   "New research shows X is now Y — here's what it means for you",
    "transformation":   "How people go from X problem to Y outcome using Z approach",
}

def classify_hook(copy: str) -> dict:
    copy_emb      = sbert.encode(copy)
    archetype_emb = sbert.encode(list(HOOK_ARCHETYPES.values()))
    scores        = util.cos_sim(copy_emb, archetype_emb)[0]
    best_idx      = int(scores.argmax())

    return {
        "hook_type": list(HOOK_ARCHETYPES.keys())[best_idx],
        "confidence": float(scores[best_idx]),
        "all_scores": dict(zip(HOOK_ARCHETYPES.keys(), scores.tolist()))
    }
```

---

## Module 12 — Full Bid Decision Pipeline

How all modules compose into a single bid decision per auction event.

```
Auction event received (topic_cluster, platform, prompt_intent)
    │
    ├── LOESS/DMR → loess_optimal_bid
    │     └── Bayesian shrinkage if n < 50 → posterior_bid
    │           └── Epsilon-greedy if cold start → explore or exploit
    │
    ├── Thrad contextual bid → loess_optimal × intent_weight (if Thrad platform)
    │
    ├── Adstock monitor → hold / reduce / exit signal
    │     └── If exit: pause bid, trigger creative rotation recommendation
    │
    ├── CAI risk check → flag if concentration deviates from goal target
    │     └── Does not block bid — surfaces to marketer for decision
    │
    ├── Thompson allocation → is this platform within its current budget allocation?
    │     └── If over-allocated: reduce bid proportionally
    │
    └── Final bid = min(true_value, loess_optimal) × intent_weight
          Where true_value = shapley_corrected AOV / avg_impressions_to_convert
```

```python
def compute_final_bid(
    cluster_id: str,
    platform: str,
    prompt_intent: dict,
    goal_type: str,
    position: MediaPosition,
    portfolio: PortfolioState
) -> BidDecision:

    # 1. Price discovery
    loess_result = bayesian_bid(cluster_id, platform, cluster_data, global_prior)
    base_bid = cold_start_bid(loess_result["n_obs"], loess_result["bid"])["bid"]

    # 2. Intent scaling (Thrad only)
    if platform == "thrad":
        base_bid = thrad_contextual_bid(base_bid, prompt_intent, goal_type)

    # 3. Decay check
    decay = fit_adstock_lambda(position.daily_conversions)
    if decay["signal"] == "exit":
        return BidDecision(bid=0.0, action="pause", reason="alpha_exhausted")

    # 4. Portfolio budget check
    platform_remaining = portfolio.remaining_budget(platform)
    if platform_remaining <= 0:
        return BidDecision(bid=0.0, action="skip", reason="budget_exhausted")

    # 5. CAI risk (does not block — surfaces as context)
    cai_risk = goal_adjusted_risk(portfolio.current_cai, goal_type)

    return BidDecision(
        bid=base_bid,
        action="bid",
        cai_flag=cai_risk["flag"],
        decay_signal=decay["signal"],
        confidence=loess_result["confidence"],
        mode=loess_result["mode"]
    )
```

---

## Data Flow Summary

```
Tavily (daily/weekly)
  search_and_answer → market intelligence
  social_media_search → social corpus
  search_dedup → competitive intelligence
  crawl_and_summarize → competitor content
          │
          ▼
BERTopic gap matrix (weekly re-run)
  → topic clusters + zone labels + velocity
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
Marketer UI   Trading engine
(context,     (LOESS/DMR,
 creative      Thompson,
 decisions)    Thrad bid,
               adstock)
          │
          ▼
Thrad BERT intent signal
  → bid weights (automated)
  → demand map (marketer context)
          │
          ▼
Platform execution (Meta MCP / Google MCP / Thrad API)
          │
          ▼
Performance data → P&L scorer → Overmind traces
          │
          └── weekly feedback → LOESS re-fit, posterior updates, gap matrix re-score
```

---

## What the Marketer Sees (Context Surfaces)

The marketer is not a passive recipient of automated decisions. Every module surfaces its reasoning:

| Module | What marketer sees | Decision they make |
|---|---|---|
| Tavily search agent | Weekly intelligence digest: audience conversations, competitor moves, LLM citations | Which content angles to prioritise |
| Thrad BERT intent map | Topic demand heatmap — where intent is high, where brand is absent | Whether to brief content for this topic |
| BERTopic gap matrix | Scatter plot: competitor coverage vs intent volume, coloured by zone | Which gaps are worth pursuing creatively |
| LOESS bid curve | Empirical supply curve with DMR point marked per topic cluster | Whether to override the system bid |
| Adstock decay | Per-creative decay signal with recommended action | Whether to approve creative rotation |
| CAI risk flag | Plain-English concentration alert (goal-conditional) | Whether the concentration is intentional |
| Thompson allocation | Platform efficiency ranking with budget share | Whether to override the platform split |
| P&L scorecard | Net P&L per position: gross revenue minus penalised waste | Which positions to investigate or close |

The AI executes. The marketer decides creatively and strategically. Neither replaces the other.

---

## Libraries and Dependencies

| Purpose | Library | Notes |
|---|---|---|
| Social + web intelligence | `tavily-agent-toolkit` | `search_and_answer`, `search_dedup`, `social_media_search`, `crawl_and_summarize` |
| Intent classification | Thrad API | BERT-based, via API key |
| Agent tracing | `overmind` SDK | Wraps all LLM + tool calls |
| Topic modelling | `bertopic` | Requires `umap-learn`, `hdbscan` |
| Sentence embeddings | `sentence-transformers` | `all-mpnet-base-v2` |
| Visual scoring | `clip` (OpenAI) | ViT-B/32, runs on GPU via Modal |
| LOESS fitting | `statsmodels` | `lowess` from `nonparametric` |
| Spline + optimisation | `scipy` | `UnivariateSpline`, `curve_fit`, `brentq`, `minimize` |
| Creative similarity | `scikit-learn` | `cosine_similarity` |
| Numerical | `numpy`, `pandas` | Standard |
| Platform MCPs | Meta Marketing API, Google Ads API, Thrad DSP API | Via MCP servers |
| Backend | `fastapi`, `celery`, `redis` | Async ETL + scheduling |
| Database | Supabase (PostgreSQL) | |
| Frontend | Next.js + React | Trading terminal UI |
| GPU inference | Modal | CLIP + BERTopic on serverless GPU |
