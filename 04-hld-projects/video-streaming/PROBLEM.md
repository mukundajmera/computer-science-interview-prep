# Video Streaming Platform

## Problem Statement

Design a VOD platform that supports large uploads, asynchronous transcoding, and low-latency global playback. Extend the design with a scoped recommendation subsystem for personalized "Up Next" and home ranking.

---

## Requirements and Constraints

### Functional Requirements

1. Upload videos with resumable multipart sessions.
2. Process uploads into adaptive bitrate variants and manifests.
3. Serve playback through CDN with low startup delay.
4. Return metadata and playback manifests for clients.
5. Generate personalized recommendation candidates.
6. Rank candidates with a multi-stage pipeline (`candidate -> light ranker -> heavy ranker -> reranker`).
7. Handle cold start for new users and new videos.
8. Add exploration controls to avoid feedback-loop lock-in.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Playback start latency | < 2 sec |
| Rebuffer ratio | < 1% session time |
| Upload durability | strong |
| Availability | 99.99% |
| Recommendation request p95 | < 200 ms |
| Recommendation staleness window | < 5 min for fresh events |
| Candidate generation p95 | < 50 ms |
| Light ranker p95 | < 30 ms |
| Heavy ranker p95 | < 80 ms |
| Reranker p95 | < 20 ms |

### Scale Assumptions

- ~1M uploads/day.
- ~100M watches/day.
- Recommendations requested on home, watch-next, and search surfaces.

### Out of Scope

- Ads stack and monetization auctions.
- Creator payouts.
- Full model training infrastructure internals.

---

## High-Level Design Outline

- Upload session service + object storage.
- Async media processing pipeline.
- CDN-first playback delivery.
- Recommendation control plane:
  - candidate retrieval
  - lightweight ranker
  - heavy ranker
  - reranker/policy layer
  - exploration and cold-start fallbacks

## Cross-Links

- [DESIGN](./DESIGN.md)
- [RUBRIC](./RUBRIC.md)
- [PITFALLS](./PITFALLS.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [CDN](../../03-hld-concepts/cdn/)
- [Read Scaling](../../03-hld-concepts/read-scaling/)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/)
