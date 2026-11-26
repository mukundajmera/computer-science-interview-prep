# Interview Questions: CAP Theorem

## Basic Questions

### 1. What does CAP theorem actually say?
**Q**: Give a practical explanation.

**A**: During a network partition, you cannot guarantee both strong consistency and full availability for every request. In distributed systems, partition tolerance is assumed, so the decision is usually consistency vs availability per operation.

### 2. Is CAP a whole-system choice?
**Q**: Do you pick CP or AP once?

**A**: No. Strong designs choose behavior per endpoint. Critical writes can be consistency-first while read-heavy browsing endpoints can be availability-first.

### 3. CAP consistency vs ACID consistency?
**Q**: Why do people confuse these?

**A**: CAP consistency is distributed-read visibility under partition. ACID consistency is transactional integrity within database rules/constraints.

### 4. Give examples of consistency-first operations.
**Q**: Which user actions usually need it?

**A**: Payment capture, inventory claim, final booking confirmation, and account balance mutations.

### 5. Give examples of availability-first operations.
**Q**: Which actions can accept staleness?

**A**: Feed reads, profile views, recommendation widgets, and most analytics dashboards.

## Intermediate Questions

### 1. How do you answer CP vs AP in interviews?
**Q**: What structure should you use?

**A**:
1. Identify operation.
2. State business risk of stale data.
3. Choose failure mode (stale response vs error/timeout).
4. Add mitigation and recovery behavior.

### 2. What is a degraded mode strategy?
**Q**: How do you avoid total outage during partition?

**A**: Keep non-critical reads available with freshness labels, queue/retry non-critical writes, and reserve strict quorum requirements for critical writes.

### 3. How do you reconcile after partition heals?
**Q**: What is your post-partition plan?

**A**: Use deterministic conflict policies (domain-specific merge, timestamps where safe, or stronger semantic rules) and run idempotent reconciliation jobs.

### 4. What consistency level is enough for social products?
**Q**: Do they need strong consistency everywhere?

**A**: Usually no. Read-your-writes for self-facing UX plus eventual consistency for global fan-out is commonly acceptable.

### 5. How do quorums relate to CAP?
**Q**: Why mention `R/W/N` in interviews?

**A**: Quorums tune consistency and availability behavior. Higher quorum improves recency guarantees but can reduce availability under partition.

## Scenario Questions

### 1. Ticket booking system
**Q**: Partition occurs between two regions. What now?

**A**: Enforce consistency-first for seat allocation (reject/defer if quorum unavailable), keep browse endpoints availability-first with explicit staleness tolerance.

### 2. Social profile updates
**Q**: A user updates profile photo; another region is partitioned.

**A**: Keep reads available with temporary staleness. Guarantee read-your-writes for the updater if possible. Reconcile asynchronously after partition heals.

### 3. Mixed-mode commerce flow
**Q**: Checkout has cart, payment, and recommendation calls. How do you split CAP behavior?

**A**: Payment/inventory writes are consistency-first. Cart display and recommendations can stay availability-first with bounded staleness.

## Advanced Questions

### 1. How do you express CAP policy in APIs?
**Q**: How do clients know what to expect?

**A**: Define endpoint-level freshness and failure contracts in API docs (for example, strict write ack vs stale-allowed reads), and expose traceable response metadata when degraded mode is active.

### 2. PACELC relevance
**Q**: What beyond CAP should senior candidates mention?

**A**: Even without partitions, systems trade latency vs consistency (PACELC framing). This helps explain day-to-day design choices, not only partition incidents.

### 3. Observability for CAP decisions
**Q**: Which metrics matter?

**A**: Stale-read rate, write rejection rate, quorum failure rate, replication lag, reconciliation backlog, and user-visible error percentages.

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Generic CAP definition only |
| 3 | Correct operation-level CP/AP examples |
| 5 | Endpoint contracts, mitigations, and reconciliation strategy |

## Common follow-ups

1. Which user journeys cannot tolerate stale reads?
2. How long can stale data be tolerated for each endpoint?
3. What fallback does client UI show during partition?
4. How do you test partition behavior before production incidents?
5. How do you track and drain reconciliation debt?

## Red flags to avoid

- "Pick two of three" with no practical mapping
- Ignoring partition handling details
- No difference between browse path and transaction path
- No reconciliation or degraded-mode communication plan

## Strong verbal answers

### 45-second version
"In distributed systems partition tolerance is mandatory, so CAP choices happen per operation. I keep correctness-critical writes consistency-first, even if that means temporary write unavailability under partition. For read-heavy user experiences I keep availability-first with explicit staleness tolerance and then reconcile after partition heal."

### 2-minute version
"I do not label the whole system CP or AP. I choose by endpoint and business risk. For booking, payment, or inventory claims, stale reads can cause irreversible errors, so I require stronger consistency and accept limited availability during partition. For profile views, feeds, and recommendations, stale data is usually acceptable for a bounded window, so I preserve availability. I document this as endpoint contracts, add observability on stale-read and reject rates, and run deterministic reconciliation when links heal. That shows the design is operationally complete, not just theoretically correct."

## Related concepts

- [CAP Theory](./THEORY.md)
- [Database Replication](../database-replication/)
- [Database Sharding](../database-sharding/)
- [CAP in Theory Section](../../00-theory/system-design-fundamentals/cap-theorem.md)
