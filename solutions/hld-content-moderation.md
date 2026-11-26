# 🏆 Coach Answer: Content Moderation — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (6 min)

- Multi-modal post moderation (text + image).
- Objective: minimize harmful exposure under precision guardrails.
- Actions: remove, demote, review, allow.

## Phase 2 — Capacity (6 min)

- Model large daily post volume and low harmful prevalence.
- Quantify review queue budget and latency constraints.

## Phase 3 — APIs (8 min)

```http
POST /api/v1/moderation/evaluate
POST /api/v1/moderation/reports
POST /api/v1/moderation/appeals
GET  /api/v1/moderation/content/{content_id}/decision
```

## Phase 4 — Data Model (6 min)

- Content events, moderation decisions, review queue items, feedback events.
- Track policy/model version for auditability and rollback.

## Phase 5 — Architecture (12 min)

- Ingest stream -> feature extraction -> scoring -> policy engine -> action executor.
- Human-review and feedback loops integrated asynchronously.

## Phase 6 — Deep Dives (5 min)

1. Calibration by harm class and precision floors.
2. Class imbalance and selective labeling.
3. Drift/evasion response cadence.

## Phase 7 — Trade-Off Wrap (2 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Enforcement | confidence-banded actions | single threshold | balances precision and coverage |
| Pipeline | fast online + async enrichment | heavy model everywhere | meets latency/cost targets |
| Learning loop | continuous feedback | periodic audits only | faster adaptation |
