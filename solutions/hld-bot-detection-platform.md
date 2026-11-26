# 🏆 Coach Answer: Bot Detection Platform — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (6 min)

### Functional

1. Ingest behavioral and graph signals.
2. Detect known and novel bot behaviors.
3. Apply remediation ladder: allow, limit, challenge, suspend.
4. Escalate uncertain/high-impact accounts to investigators.

### Non-Functional

| Metric | Target |
|---|---|
| Online risk gate p95 | < 200 ms |
| Availability | 99.9% |
| Critical investigator SLA | < 10 min |
| Throughput | 500M DAU class |

---

## Phase 2 — Estimation (5 min)

- Multi-billion action events/day.
- Sparse labels require careful feedback and calibration loops.
- Investigator capacity must be prioritized by risk impact.

---

## Phase 3 — API + Data Model (8 min)

Decision contract should include risk score, confidence, action, and reason codes.

Core entities: `AccountRiskSnapshot`, `RemediationAction`, `InvestigationTask`, `AccountRiskTimeline`.

---

## Phase 4 — Architecture (12 min)

- Signal ingest + feature store.
- Dual-path scoring: supervised model + anomaly detector.
- Decision calibrator chooses action by risk/confidence.
- Orchestrator applies remediation and writes audit trail.
- Investigator queue for borderline and high-value cases.

---

## Phase 5 — Deep Dives (10 min)

1. Confidence-aware remediation ladder.
2. Campaign adaptation loop for adversarial shifts.
3. Investigator queue prioritization and SLA policy.

---

## Phase 6 — Trade-Off Wrap (4 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Detection path | supervised + anomaly | supervised-only | better unknown attack coverage |
| Remediation | staged ladder | immediate hard suspend | lower collateral damage |
| Queue strategy | risk-priority | FIFO | aligns scarce capacity with impact |
