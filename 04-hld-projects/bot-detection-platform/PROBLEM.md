# Bot Detection Platform

## Problem Statement

Design a platform that detects automated malicious account behavior, combines known-pattern and anomaly detection, and applies confidence-aware remediation with investigator escalation.

---

## Requirements and Constraints

### Functional Requirements

1. Ingest behavioral, graph, and device/network signals.
2. Compute account risk and confidence continuously.
3. Apply action ladder: `allow`, `limit`, `challenge`, `suspend`.
4. Route uncertain/high-impact cases to investigators.
5. Keep explainable reason codes and risk timelines.
6. Re-score accounts when new evidence arrives.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Online risk-gate p95 | < 200 ms |
| Availability | 99.9% |
| Critical review SLA | < 10 min |
| Throughput | 500M DAU class |
| False-positive tolerance | strict for trusted users |

### Out of Scope

- End-user appeal product flow
- Full identity/KYC systems
- Cross-company anti-abuse consortium

---

## Interview Focus

- Frame the problem as adversarial and dynamic, not static classification.
- Show supervised + anomaly dual-path design.
- Explain remediation ladder trade-offs.
- Cover adaptation loop and campaign-level observability.

## APIs (Illustrative)

```http
POST /api/v1/bot-risk/evaluate
POST /api/v1/bot-risk/remediate
POST /api/v1/bot-risk/investigations
POST /api/v1/bot-risk/investigations/{id}/resolve
GET  /api/v1/bot-risk/accounts/{accountId}
```

## Cross-Links

- [DESIGN](./DESIGN.md)
- [RUBRIC](./RUBRIC.md)
- [PITFALLS](./PITFALLS.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [Rate Limiting](../../03-hld-concepts/rate-limiting/)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/)
