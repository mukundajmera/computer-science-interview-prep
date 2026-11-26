# 🏆 Coach Answer: Video Recommendations — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (6 min)

- Up-next recommendations for active sessions.
- Objective: maximize quality-adjusted long-term engagement.
- Latency SLA: < 250 ms P95.

## Phase 2 — Capacity (6 min)

- Estimate recommendation request QPS and catalog scale.
- Prove full online scoring is infeasible.

## Phase 3 — APIs (7 min)

```http
POST /api/v1/recommendations/up-next
POST /api/v1/recommendations/feedback
GET  /api/v1/recommendations/model-metadata
```

## Phase 4 — Data Model (6 min)

- Session context, candidate pool, rank scores, feedback events.
- Model/version tagging for experiment reproducibility.

## Phase 5 — Architecture (13 min)

- Parallel candidate generation -> lightweight ranker -> heavy ranker -> top-k response.
- Feedback stream updates feature store and evaluation dashboards.

## Phase 6 — Deep Dives (5 min)

1. Explore/exploit budget.
2. Cold start strategies.
3. Long-horizon metric evaluation.

## Phase 7 — Trade-Off Wrap (2 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Ranking path | multi-stage cascade | single heavy model | meets scale + latency |
| Objective | long-term value model | CTR-only | avoids clickbait bias |
| Exploration | bounded | none | prevents model lock-in |
