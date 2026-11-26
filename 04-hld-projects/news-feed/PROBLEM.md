# News Feed / Timeline System

## Problem Statement

Design a feed system that serves a personalized timeline of posts from followed accounts, with support for high read throughput and near-real-time freshness.

---

## Requirements and Constraints

### Functional Requirements

1. Users can create posts.
2. Users can follow and unfollow accounts.
3. Users can fetch home feed with cursor pagination.
4. New posts appear in feed with bounded delay.
5. Feed supports ranking by recency and engagement signals.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Feed read latency | < 200 ms P99 |
| Post write latency | < 500 ms P99 |
| Availability | 99.9% |
| Consistency | Eventual for feed freshness |
| Scale | 100K+ read QPS class |

### Capacity Assumptions

- 200M DAU.
- 400M posts/day.
- Billions of feed reads/day.
- Heavy skew for celebrity publishers.

### Out of Scope

- Comments/reactions subsystem internals.
- Direct messaging and notifications internals.
- Ads auction internals.

### Scaling Pattern Constraints

- **Read scaling trigger:** Once feed fetches cross ~100K QPS or celebrity fanout backlogs grow, switch most traffic to the aggregated read path described in [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/) so we can cache and merge feeds without writing to billions of timelines per post.
- **Write scaling trigger:** Sustained bursts while processing 400M posts/day require batching and rate-limiting on the fan-out service along with adaptive partitioning (see [03-hld-concepts/write-scaling](../../03-hld-concepts/write-scaling/)). This avoids write-coordinator hot spots when celebrities post or breaking news arrives.
- **Large content handling:** For rich media attachments that resemble blobs, defer heavy uploads to a dedicated blob service and publish lightweight references (see [03-hld-concepts/large-blob-handling](../../03-hld-concepts/large-blob-handling/)) so writer fan-out work stays predictable.
- **Long-running tasks:** Feed aggregation jobs (offline ranking, cache warming, publisher ingestion) must be resilient to failures and support retries plus dead-lettering (see [03-hld-concepts/long-running-tasks](../../03-hld-concepts/long-running-tasks/)). Track their progress separately from synchronous APIs to keep feed creation latency under 500 ms.

---

## News Aggregator Variant (Mapped from Source)

In addition to social-follow feed, this project now explicitly supports a **publisher-aggregated news feed** variant:

- Content source is publisher ingestion rather than user-generated social posts.
- Feed can be region/category based with optional personalization.
- Infinite scroll, freshness, and ranking constraints still apply.

This keeps one shared feed architecture while allowing interviewers to pivot between social and news contexts.

---

## High-Level Design Outline

### Core Services

- Post/Content Ingestion Service
- Graph or Subscription Service
- Feed Fanout Service
- Feed Read Service
- Ranking Service
- Cache + Async event pipeline

### API Surface (Illustrative)

```http
POST /api/v1/posts
POST /api/v1/follows
GET /api/v1/feed?cursor=...&limit=...
GET /api/v1/feed/news?region=...&cursor=...
```

---

## Scoring Rubric

Strong answers cover:

1. Fan-out-on-write vs fan-out-on-read trade-off and hybrid threshold.
2. Celebrity/high-follower strategy.
3. Cache, pagination, and freshness controls.
4. Variant adaptation for publisher-aggregated feeds.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Pure fan-out-on-write for all users.
- No staleness target or propagation budget.
- Cursor model not defined clearly.
- Missing fallback for high-skew read patterns.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How to add ML ranking?
- How to support trending/explore feed?
- How to guarantee pagination consistency during rapid writes?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Social following feed.
- Publisher-aggregated news feed.
- Topic/trending discovery feed.

---

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
- [03-hld-concepts/message-queues](../../03-hld-concepts/message-queues/)
- [03-hld-concepts/kafka](../../03-hld-concepts/kafka/)
- [case-studies/linkedin-feed](../../case-studies/linkedin-feed/)
- [case-studies/twitter-timeline](../../case-studies/twitter-timeline/)

---

## Instagram Variant Addendum

This project now explicitly includes an Instagram-style media feed variant:

- Mixed photo/video payloads with object-storage-backed media metadata.
- Follow-graph timeline generation with bounded staleness.
- Hybrid fan-out preserving low-latency reads while containing celebrity amplification.
- Separate media-delivery optimization track (CDN + blob lifecycle) from feed ranking path.
