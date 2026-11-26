# Content Moderation Platform

## Problem Statement

Design a content moderation platform that classifies user-generated text and media, applies policy actions with strict precision guardrails, and escalates uncertain cases to human review.

---

## Requirements and Constraints

### Functional Requirements

1. Evaluate each content item and return risk/confidence scores.
2. Apply action ladder: `allow`, `demote`, `review`, `remove`.
3. Route low-confidence or high-impact items to reviewer queues.
4. Keep auditable decision history with policy/model versions.
5. Re-evaluate old content after policy/model updates.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| p95 decision latency | < 300 ms |
| Action propagation to feeds | < 2 sec |
| Availability | 99.9% |
| Auto-remove precision | >= 95% |
| Throughput | 1B items/day class |

### Out of Scope

- Model training pipeline internals
- Full appeals UX
- Legal policy authoring workflow

---

## Interview Focus

- Separate inference, calibration, and enforcement responsibilities.
- Show confidence-aware routing, not only binary classification.
- Explain reviewer capacity constraints and queue prioritization.
- Cover rollback and drift safeguards for policy changes.

## APIs (Illustrative)

```http
POST /api/v1/moderation/evaluate
POST /api/v1/moderation/enforce
POST /api/v1/moderation/review-tasks
POST /api/v1/moderation/review-tasks/{taskId}/resolve
GET  /api/v1/moderation/audit/{contentId}
```

## Cross-Links

- [DESIGN](./DESIGN.md)
- [RUBRIC](./RUBRIC.md)
- [PITFALLS](./PITFALLS.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [Safety & Governance](../../06-genai-systems/00-concepts/safety-governance/)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/)
