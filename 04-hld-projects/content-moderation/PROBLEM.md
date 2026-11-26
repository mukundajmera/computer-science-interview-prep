# Content Moderation

## Problem Statement

Design a multi-modal content moderation system for a social platform that classifies posts (text + image), applies policy actions, and minimizes harmful exposure while preserving precision guardrails.

---

## Requirements and Constraints

### Functional Requirements

1. Classify new/updated posts as harmful or benign.
2. Support policy actions: delete, down-rank, queue for human review.
3. Enforce precision guardrails before auto-removal.
4. Ingest user reports and moderator feedback for continual improvement.
5. Provide per-policy metrics and operator dashboards.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Inference latency (online path) | < 200 ms P95 |
| Precision for auto-delete | >= 95% |
| Availability | 99.9% |
| Daily volume | up to 1B posts/day |
| Harmful prevalence | typically < 1% |

### Capacity Assumptions

- 1B posts/day, multi-region traffic.
- Majority of events resolved by automated path; human review is scarce.
- Labeling budget is constrained and must be prioritized.

### Out of Scope

- Full legal/regulatory policy authoring workflow.
- LLM governance platform internals.
- Ad ranking and recommendation internals.

### Scope Guardrail

This project focuses on applied ML moderation architecture (classification + action policy), not a full GenAI safety governance platform.

---

## API / System Interface

```http
POST /api/v1/moderation/evaluate
POST /api/v1/moderation/reports
POST /api/v1/moderation/appeals
GET  /api/v1/moderation/content/{content_id}/decision
GET  /api/v1/moderation/metrics?window=24h
```

---

## Key Design Challenges

1. High precision requirements with rare positive class.
2. Multi-modal signal fusion under tight latency budget.
3. Balancing automated enforcement with human-review capacity.
4. Feedback loops, drift, and policy versioning.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [RUBRIC](./RUBRIC.md)
- [PITFALLS](./PITFALLS.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [COMPARISON](./COMPARISON.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/)
- [Rate Limiting](../../03-hld-concepts/rate-limiting/)
- [Message Queues](../../03-hld-concepts/message-queues/)
- [LLM Evaluation](../../06-genai-systems/00-concepts/llm-evaluation/)
