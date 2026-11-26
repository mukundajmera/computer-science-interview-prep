# News Feed — System Comparison

## Social Feed vs Publisher News Feed

| Concern | Social Feed | Publisher News Feed |
|---|---|---|
| Source | Followed users/accounts | Publisher ingestion streams |
| Personalization | Strongly graph-driven | Region/topic-first, optional personalization |
| Freshness pressure | Continuous social updates | Spike-heavy around breaking events |
| Core write bottleneck | Fan-out to followers | Ingestion normalization and ranking |

## Feed vs Notification Service

| Concern | Feed | Notification Service |
|---|---|---|
| Delivery | Pull-first, optional push assist | Push-first, read-later inbox |
| Ordering | Relevance + recency ranking | Priority/severity order |
| Tolerance for delay | Seconds acceptable | Lower tolerance for critical alerts |

## Feed vs Search/Discovery

| Concern | Feed | Search/Discovery |
|---|---|---|
| Trigger | Passive consumption | Explicit query |
| Candidate generation | Precomputed + incremental merge | Query-time retrieval |
| Data structure emphasis | Per-user/per-topic feed cache | Inverted index + ranking engine |

## Feed vs Chat Messaging

| Concern | Feed | Chat |
|---|---|---|
| Consistency target | Eventual freshness | Ordered conversation delivery |
| Fan-out shape | One-to-many broadcast | One-to-one or small group |
| UX expectation | Browsing and scroll | Immediate conversational response |

---

## Practical Reuse Guidance

- Reuse fan-out and cache ideas between social and publisher feeds.
- Reuse ranking primitives between feed and discovery/search.
- Keep notification and chat systems decoupled from feed critical path.

---

## Instagram Feed Variant

| Concern | Generic News Feed | Instagram Variant |
|---|---|---|
| Primary content type | Text/link heavy | Media heavy (photo/video) |
| Delivery bottleneck | Feed query and ranking | Feed query + media delivery |
| Key infra addition | Cache/fanout | Cache/fanout + blob/CDN optimization |
