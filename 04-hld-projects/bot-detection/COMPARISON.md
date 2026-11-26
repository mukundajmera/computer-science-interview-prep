# Bot Detection — Comparison Notes

| System | Similarity | Key difference |
|---|---|---|
| [Content Moderation](../content-moderation/) | abuse reduction and policy actions | account-level behavior vs content-level semantics |
| [Rate Limiting](../../03-hld-concepts/rate-limiting/) | abuse throttling controls | coarse traffic control vs model-driven account risk |
| [Metrics Monitoring](../metrics-monitoring/) | streaming signals + alerting | operational metrics vs adversarial detection objective |

## Reuse guidance

- Reuse stream processing, risk-state storage, and alerting patterns.
- Keep campaign-level analysis async to protect online latency.
- Isolate enforcement policy from model implementation details.
