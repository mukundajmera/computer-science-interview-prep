# Bot Detection

## Problem Statement

Design a bot-detection system for a large social platform that identifies malicious automated accounts, applies graduated remediation, and minimizes abuse impact without unacceptable harm to legitimate users.

---

## Requirements and Constraints

### Functional Requirements

1. Detect likely bot accounts from behavioral, graph, and content-derived signals.
2. Support remediation actions: limit, challenge, demote, suspend.
3. Route uncertain cases to investigator review.
4. Ingest outcomes from appeals/investigations as high-quality labels.
5. Continuously monitor attack shifts and model degradation.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Decision latency (critical path) | < 150 ms P95 |
| Availability | 99.9% |
| DAU scale | 500M+ |
| Abuse prevalence after heuristics | < 1% |
| False-positive tolerance | strictly bounded |

### Capacity Assumptions

- High-volume event streams from login, messaging, posting, and follow actions.
- Ground-truth labels from investigators are scarce and expensive.
- Attackers adapt rapidly, so model drift is expected.

### Out of Scope

- Full fraud/financial risk stack.
- Generic content moderation for post payloads.
- End-to-end legal enforcement workflow.

### Scope Guardrail

This project targets account-level adversarial detection, not a generic content moderation redesign.

---

## API / System Interface

```http
POST /api/v1/bot-detection/evaluate-account
POST /api/v1/bot-detection/appeals
POST /api/v1/bot-detection/investigator-labels
GET  /api/v1/bot-detection/account/{account_id}/status
GET  /api/v1/bot-detection/metrics?window=24h
```

---

## Key Design Challenges

1. Sparse gold labels under adversarial dynamics.
2. Precision/recall trade-off where false positives are expensive.
3. Combining rules, supervised models, and anomaly detectors.
4. Fast remediation without destabilizing user trust.

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
- [Pattern Selection](../../03-hld-concepts/pattern-selection/)
- [Rate Limiting](../../03-hld-concepts/rate-limiting/)
- [Message Queues](../../03-hld-concepts/message-queues/)
