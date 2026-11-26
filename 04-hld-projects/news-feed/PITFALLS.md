# News Feed - Common Interview Pitfalls

Frequent mistakes in News Feed interviews and what interviewers expect instead.

> Related docs: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [STRONG-ANSWER](./STRONG-ANSWER.md)

## 1. Using only fan-out-on-write

### The mistake
Ignoring celebrity/high-fanout users and pushing every post to every follower timeline.

### Expected signal
Show hybrid fan-out and explain the threshold, migration trigger, and read-path merge strategy.

## 2. Not discussing push vs pull trade-offs

### The mistake
Presenting one model as universally correct.

### Expected signal
Compare write amplification vs read latency and justify a mixed strategy.

## 3. Treating chronological order as final ranking

### The mistake
Skipping relevance signals and personalization.

### Expected signal
Use a two-stage rank pipeline (candidate generation + lightweight rerank).

## 4. Ignoring hot partitions and hot keys

### The mistake
Assuming uniform traffic distribution.

### Expected signal
Call out mitigation: bucketing, cache replication, throttling, and queue isolation.

## 5. Missing unfollow/invalidation behavior

### The mistake
Designing follow path only, leaving stale content in feed.

### Expected signal
Describe invalidation policy and fallback filter-at-read strategy.

## 6. Not handling feed freshness vs latency explicitly

### The mistake
Claiming both perfect freshness and sub-200ms latency without trade-offs.

### Expected signal
State bounded staleness targets and user-visible guarantees.

## 7. Missing cold-start strategy

### The mistake
No plan for users with sparse graph/history.

### Expected signal
Seed with interest/trending candidates and transition to personalized ranking.

## 8. Re-showing previously swiped or seen candidates in Tinder-like variants

### The mistake
Recommendation loop returns candidates the user already passed or liked.

### Expected signal
Maintain exclusion state and enforce it before ranking to preserve trust.

## 9. Race conditions in mutual-like match detection

### The mistake
Two users swipe around the same time and no match notification is emitted.

### Expected signal
Use atomic check-and-write semantics or durable repair jobs with idempotent notifications.

## 10. Not defining stale-profile invalidation in geo filters

### The mistake
Serving profile cards that no longer satisfy location/preference constraints.

### Expected signal
Define invalidation triggers and short-lived recommendation caches for geo-sensitive feeds.

## Quick scoring impact

| Pitfall | Typical impact |
|---|---|
| No hybrid fan-out | Architecture and deep-dive score drops heavily |
| No ranking strategy | Product sense and trade-off depth drops |
| Swipe/match correctness gaps | Consistency and reliability judgment drops |
| No stale candidate handling | User experience and operational rigor drops |

---

## Instagram Variant Pitfalls

- Treating media blobs as inline feed payloads.
- Missing creator-spike mitigation for media fanout.
- Ignoring media lifecycle and storage-cost controls.
