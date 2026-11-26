
# Online Auction System

## Problem Statement

Design a high-contention auction platform where sellers create auctions and buyers place monotonic bids until close time.

---

## Requirements and Constraints

### Functional Requirements

1. Create auctions with start price and close time
2. Place bids with strict monotonic increase
3. Read live highest bid and winner after close

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Bid correctness | Strong for same auction item |
| Availability | 99.95% |
| Bid API latency | < 200 ms P99 |
| Durability | No accepted bid loss |

### Out of Scope

- Full recommendation/ads internals.
- Back-office analytics tooling.
- Third-party billing and compliance details.

---

## High-Level Design Outline

- API Gateway + stateless app tier
- Domain service layer
- Cache + durable primary store
- Async pipeline for fanout/indexing/notifications
- Monitoring, alerting, and replay controls

### Sample APIs

```http
POST /api/v1/auctions
POST /api/v1/auctions/{auctionId}/bids
GET /api/v1/auctions/{auctionId}
POST /api/v1/auctions/{auctionId}/close
```

---

## Scoring Rubric

- Requirement framing and boundary definition
- Capacity assumptions tied to architecture
- Correct consistency model on critical operations
- Clear failure handling and degraded mode

See [RUBRIC](./RUBRIC.md).

## Common Pitfalls

See [PITFALLS](./PITFALLS.md).

## Follow-Up Questions

See [FOLLOW-UPS](./FOLLOW-UPS.md).

## Variants and Extensions

- Global multi-region rollout.
- Cost-optimized variant with relaxed freshness.
- Compliance-first variant with stricter audit rules.

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/contention-control](../../03-hld-concepts/contention-control/)
- [03-hld-concepts/message-queues](../../03-hld-concepts/message-queues/)
- [03-hld-concepts/workflow-orchestration](../../03-hld-concepts/workflow-orchestration/)
- [solutions/hld-online-auction.md](../../solutions/hld-online-auction.md)
