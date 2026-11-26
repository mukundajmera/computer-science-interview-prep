# Content Moderation Platform — High-Level Design

## 1) Requirements and Constraints

- Low-latency moderation decisions on UGC.
- High precision for irreversible actions (`remove`).
- Human-in-the-loop for uncertainty and policy-sensitive cases.
- Full auditability and rollback controls.

## 2) Back-of-Envelope Estimates

- 1B items/day -> ~11.6K eval/s average.
- 3x peak -> ~35K eval/s.
- If 1% needs follow-up, downstream capacity planning becomes the bottleneck.

## 3) API / Interface

```http
POST /api/v1/moderation/evaluate
{
  "content_id": "c123",
  "text": "...",
  "media_refs": ["m1"],
  "surface": "feed"
}
```

Response:

```json
{
  "risk_score": 0.91,
  "confidence": 0.96,
  "action": "remove",
  "reasons": ["violence_policy_v4"],
  "policy_version": "p2026.04"
}
```

## 4) Core Data Model

- `ModerationEvent(content_id, actor_id, created_at, surface)`
- `ModelScore(content_id, model_version, risk_score, confidence, features_ref)`
- `PolicyDecision(content_id, action, reasons, policy_version, decided_at)`
- `ReviewTask(task_id, content_id, priority, status, assigned_to)`
- `AuditRecord(content_id, timeline, final_action)`

## 5) Architecture

[Architecture Diagram](diagrams/architecture.mmd)

### Read/Write Paths

1. New content enters moderation gateway.
2. Inference computes risk and confidence.
3. Calibrator maps score to action using policy thresholds.
4. Enforcement updates serving state asynchronously.
5. Decisions and human outcomes feed audit and evaluation loops.

### Failure-aware Path
- Degraded mode: If the ML engine fails completely, default to routing everything to human review or enforce a strict lockdown based on business policy.
**Named Failure Histories:**
1. **Sync Path Timeout / Failure:** 
   - *State owner:* The Moderation Gateway holds the source of truth.
   - *After timeout/replay:* If the Inference Service fails to respond, the timeout triggers. The item is routed to human review or retried based on policy.
2. **Async Enforcement Outage:**
   - *Retained guarantee:* The enforcement happens asynchronously via the Review Queue. The content remains blocked/unblocked based on last known state until enforcement catches up.

## 6) Deep Dives

### A. Calibration for Precision Guardrails

- Category-specific thresholds.
- Higher confidence requirement for `remove` than for `demote`.
- Near-threshold traffic routed to review.

### B. Reviewer Queue Prioritization

- Rank by expected exposure and severity.
- Keep SLA classes for highest-risk categories.
- Use queue backpressure to temporarily tighten auto-demote policy.

### C. Drift and Rollback Controls

- Track precision@action, disagreement rate, and policy breach rate.
- Canary threshold updates.
- Keep last-known-good policy profiles for fast rollback.

## 7) Trade-Offs

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Decisioning | score + confidence calibration | binary label only | better risk control |
| Escalation path | explicit review lane | full auto moderation | safer for edge cases |
| Enforcement updates | async side effects | inline blocking everywhere | protects post-path latency |

## 8) Variants and Extensions

- Real-time chat moderation with tighter p99.
- Region-specific policy overlays.
- Trust-tier based thresholds for repeat actors.
