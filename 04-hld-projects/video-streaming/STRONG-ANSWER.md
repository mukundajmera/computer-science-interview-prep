# Video Streaming — Strong Interview Answer (45 Minutes)

Say: "I will keep upload/transcoding, CDN delivery, playback manifests, and analytics as separate paths so viewer playback stays reliable even when processing jobs lag."

## Suggested Flow

1. **Requirements (0-6 min):** VOD upload + playback, then scoped recommendation extension.
2. **Estimates (6-11 min):** upload, watch, egress, and recommendation QPS envelopes.
3. **API/Data (11-19 min):** upload lifecycle + manifest + recommendation endpoint and entities.
4. **Architecture (19-32 min):** ingest/process/delivery plus `candidate -> light -> heavy -> reranker` path.
5. **Deep dives (32-41 min):** multipart reliability, stage latency budgets, cold start, and feedback-loop mitigation.
6. **Wrap (41-45 min):** trade-offs and first 10x bottleneck.

## Strong Closing

- Media path is availability-first and cost-aware.
- Recommendation path is quality-aware but latency-bounded (explicit p95 split by stage).
- Evolution path: better features and policies without collapsing read-path SLOs.
