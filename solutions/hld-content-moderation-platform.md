# 🏆 Coach Answer: Content Moderation Platform — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (6 min)

### Functional

1. Score text/media risk and confidence.
2. Apply staged actions: allow, demote, review, remove.
3. Escalate low-confidence/high-impact items to human review.
4. Persist decision timeline for audits.

### Non-Functional

| Metric | Target |
|---|---|
| Decision p95 | < 300 ms |
| Action propagation | < 2 sec |
| Availability | 99.9% |
| Auto-remove precision | >= 95% |

---

## Phase 2 — Estimation (5 min)

- 1B items/day implies high online decision throughput.
- Reviewer capacity is a hard bottleneck under drift or policy changes.

---

## Phase 3 — API + Data Model (8 min)

Define a clear contract with score, confidence, action, reasons, and policy version.

Core entities: `ModelScore`, `PolicyDecision`, `ReviewTask`, `AuditRecord`.

---

## Phase 4 — Architecture (12 min)

- Inference service computes risk/confidence.
- Calibrator maps scores to staged actions.
- Enforcement service updates serving systems asynchronously.
- Review queue and console handle uncertain/high-risk cases.
- Audit + eval pipeline monitors drift and regressions.

---

## Phase 5 — Deep Dives (10 min)

1. Precision guardrails by action category.
2. Queue prioritization by exposure impact.
3. Canary rollout and rollback triggers for policy updates.

---

## Phase 6 — Trade-Off Wrap (4 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Decisioning | score + confidence calibration | binary label only | safer action control |
| Escalation | explicit review lane | full automation | lowers catastrophic false positives |
| Enforcement path | async updates | inline heavy updates | preserves post-path latency |
