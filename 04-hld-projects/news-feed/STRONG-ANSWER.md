# News Feed - Strong Answer Outline (Time-Boxed)

Say: "I will choose fanout strategy based on follower distribution: precompute for normal users, handle celebrities differently, and keep ranking/freshness as explicit trade-offs."

A compact model answer for a 40-45 minute News Feed interview.

> Related docs: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

## Time allocation

| Phase | Time | Outcome |
|---|---|---|
| Requirements and scope | 5 min | Clear in/out boundaries |
| Back-of-envelope | 5 min | Numbers that drive design |
| API + data model + HLD | 12 min | End-to-end architecture |
| Deep dives | 15 min | Scalability and correctness |
| Trade-offs + wrap | 5 min | Decision-quality summary |

## 1) Requirements and constraints

- Confirm home feed vs explore feed.
- Confirm ranking expectations, freshness target, and celebrity distribution.
- Set latency/availability targets and explicit out-of-scope boundaries.

## 2) Capacity estimates that change design

- Estimate post write QPS, feed read QPS, and fan-out cost distribution.
- Use celebrity fan-out explosion to justify hybrid feed strategy.
- Use cache sizing to justify Redis namespace layout and TTL strategy.

## 3) Interfaces and data model

- APIs: create post, follow/unfollow, fetch feed with cursor.
- Stores: write-optimized post store, graph store, feed cache, ranking features.
- Access patterns: write path async fan-out, read path merge + rerank.

## 4) Architecture

- Post ingest -> queue -> fan-out workers -> feed cache.
- Feed read -> cache candidate retrieval -> rerank -> response.
- Event-driven invalidation for graph changes and stale cache windows.

## 5) Deep dives to secure a strong score

- Hybrid fan-out thresholds and migration strategy.
- Hot key/partition handling and queue backpressure.
- Freshness guarantees and replay behavior for realtime updates.

## 6) Tinder-like recommendation variant (source integration)

If interviewer pivots from timeline feed to swipe feed (Tinder-style):

- Replace follow-graph candidates with recommendation candidates filtered by preferences and distance.
- Add strict exclusion state to avoid resurfacing already-swiped profiles.
- Match creation requires strong consistency around reverse-swipe check and idempotent notification.
- Keep feed-latency SLO (for card stack retrieval) while accepting bounded staleness in recommendation recompute.

Cross-links:
- [chat-service](../chat-service/)
- [contention-control](../../03-hld-concepts/contention-control/)
- [real-time-updates](../../03-hld-concepts/real-time-updates/)

## 7) Wrap-up statement

- Restate chosen architecture and one intentional trade-off.
- Call out first bottleneck at 10x and mitigation path.
- End with a clear evolution plan (v1 basic -> v2 scaled -> v3 distributed).
