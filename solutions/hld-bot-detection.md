# 🏆 Coach Answer: Bot Detection — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (6 min)

- Detect abusive automated accounts across major user surfaces.
- Minimize abuse impact with strict false-positive controls.
- Graduated actions: challenge, limit, suspend.

## Phase 2 — Capacity (6 min)

- Estimate behavioral event volume and peak rates.
- Quantify scarce investigator label throughput.

## Phase 3 — APIs (8 min)

```http
POST /api/v1/bot-detection/evaluate-account
POST /api/v1/bot-detection/appeals
POST /api/v1/bot-detection/investigator-labels
GET  /api/v1/bot-detection/account/{account_id}/status
```

## Phase 4 — Data Model (6 min)

- Account risk state, behavior signals, action events, trusted labels.
- Policy versioning and reason codes for auditability.

## Phase 5 — Architecture (12 min)

- Stream ingestion -> real-time features -> layered risk engine (rules + ML + anomaly).
- Policy engine applies confidence-banded remediation.
- Appeals/investigator outcomes feed retraining/calibration.

## Phase 6 — Deep Dives (5 min)

1. Adversarial drift handling.
2. Active labeling strategy.
3. Precision floors per action band.

## Phase 7 — Trade-Off Wrap (2 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Detection | layered stack | single model | better resiliency under attack shift |
| Enforcement | graduated | immediate bans | lower collateral damage |
| Labeling | active selection | random sampling only | higher label efficiency |
