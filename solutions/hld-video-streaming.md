# 🏆 Coach Answer: Video Streaming — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (6 min)

### Functional

1. Resumable video uploads.
2. Async transcode + manifest generation.
3. CDN-first adaptive playback.
4. Personalized recommendation endpoint for home/watch-next.

### Non-Functional

| Metric | Target |
|---|---|
| Playback start | < 2s |
| Rebuffer ratio | < 1% |
| Availability | 99.99% |
| Rec request p95 | < 200 ms |

---

## Phase 2 — Capacity (5 min)

- Upload and transcode throughput drive ingest architecture.
- Global read skew and egress dominate delivery cost.
- Recommendation compute must fit read-path latency budget.

---

## Phase 3 — APIs + Data Model (8 min)

```http
POST /api/v1/uploads/sessions
PUT  /api/v1/uploads/sessions/{sessionId}/parts/{partNumber}
POST /api/v1/uploads/sessions/{sessionId}/complete
GET  /api/v1/videos/{videoId}/manifest
GET  /api/v1/recommendations?userId={userId}&contextVideoId={videoId}&limit={k}
```

Core entities: `UploadSession`, `VideoAsset`, `Manifest`, `CandidateSet`, `RankedRecommendation`.

---

## Phase 4 — Architecture (12 min)

- Upload coordinator + object store.
- Async processing workers for transcode/package.
- CDN-first playback with origin shielding.
- Recommendation subsystem:
  - candidate generation
  - light ranker
  - heavy ranker
  - reranker (policy/diversity/explore).

### Recommendation Latency Budget (p95)

| Stage | Budget |
|---|---|
| Candidate generation | <= 50 ms |
| Light ranker | <= 30 ms |
| Heavy ranker | <= 80 ms |
| Reranker | <= 20 ms |
| Network/headroom | <= 20 ms |
| **Total** | **<= 200 ms** |

---

## Phase 5 — Deep Dives (10 min)

1. Multipart upload idempotency and recovery.
2. Ranking latency split across multi-stage pipeline, with fallback to light-ranker output if heavy stage times out.
3. Cold start handling (new users/videos) plus feedback-loop controls (exploration + freshness + drift monitors).

---

## Phase 6 — Trade-Off Wrap (4 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Media processing | Async | Inline | protects ingest latency |
| Delivery | CDN + segments | Origin direct | startup and cost efficiency |
| Ranking | Multi-stage | Single heavy model | latency-quality balance |
| Freshness | Nearline feature updates | batch-only | faster adaptation |
