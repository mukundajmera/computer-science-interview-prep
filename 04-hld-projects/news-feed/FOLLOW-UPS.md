# News Feed - Follow-Up Questions

Common follow-up variants interviewers ask after the base News Feed design.

> Related docs: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [STRONG-ANSWER](./STRONG-ANSWER.md)

## 1. How do you add ML ranking safely?

- Split feed generation into candidate retrieval and scoring stages.
- Keep a deterministic fallback ranker (recency + engagement) behind a feature flag.
- Enforce strict latency budgets so model calls do not violate feed p95.

## 2. How do you handle ultra-high-follower publishers?

- Use hybrid fan-out: fan-out-on-write for normal users, fan-out-on-read for celebrity users.
- Store celebrity posts in a separate cache namespace and merge during feed read.
- Tune threshold by write queue pressure and cache write latency.

## 3. How do you improve pagination consistency?

- Use cursor pagination with stable sort keys.
- Include tie-breakers to prevent duplicates/holes across pages.
- Accept bounded staleness instead of offset pagination correctness illusions.

## 4. How do you keep feeds fresh without overloading compute?

- Precompute for active users only and apply short TTLs.
- Trigger targeted refresh on follow/unfollow, major location changes, or interest updates.
- Use background refresh workers with backpressure controls.

## 5. How do you avoid showing already-seen/swiped content in a Tinder-like variant?

- Maintain per-user interaction state (`liked`, `passed`, `blocked`, `already_seen`).
- Filter candidate sets using a fast exclusion index before ranking.
- Add a replay policy window only for explicit product intents (for example, re-discovery modes).

## 6. How do you guarantee mutual-match correctness in a swipe workflow?

- Persist current swipe, then atomically check reverse swipe in the same consistency boundary.
- Use idempotency keys to avoid duplicate match notifications.
- Add repair jobs for rare race windows and emit audit metrics on missed matches.

## 7. How do you handle stale candidate profiles in recommendation feeds?

- Define staleness reasons: moved location, changed preferences, deactivated profile.
- Apply cache invalidation triggers plus periodic background recomputation.
- Keep recommendation TTL short for geo-sensitive surfaces.

## 8. How do you add realtime feed updates?

- Use WebSocket/SSE for active sessions and polling fallback for restrictive networks.
- Assign monotonic event IDs and support replay from last seen event.
- Keep transport choice aligned with [real-time-updates](../../03-hld-concepts/real-time-updates/).

## 9. How do you control contention on hot users/items?

- Start optimistic and escalate only for hot partitions.
- Use selective locks/serialized lanes for high-conflict keys.
- Tie mitigation to [contention-control](../../03-hld-concepts/contention-control/) and measured conflict rates.

## 10. How do you run long feed maintenance jobs safely?

- Treat cache warming, score rebuilds, and recommendation backfills as tracked workflows.
- Add heartbeat, retries, DLQ, and replay semantics.
- Follow [long-running-tasks](../../03-hld-concepts/long-running-tasks/) patterns.

---

## Instagram-Specific Follow-Ups

1. How do you optimize media prefetch without over-fetching?
2. How do you handle massive creator spikes during live events?
3. How do you evolve from chronological feed to ML-ranked feed safely?
4. How do you isolate story/reel pipelines from home-feed stability?
