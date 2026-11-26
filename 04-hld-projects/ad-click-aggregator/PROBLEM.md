# Ad Click Aggregator

## Problem Statement

Design a click aggregation system with real-time counters, deduplication, and queryable advertiser metrics.

---

## Requirements and constraints

### Functional requirements
1. Accept click events from ad-serving clients with an event id, campaign/ad-group/ad ids, publisher id, event timestamp, and user/device attributes.
2. Deduplicate retries and accidental double fires before counters are used for billing, pacing, or advertiser dashboards.
3. Aggregate impressions/clicks by advertiser, campaign, ad group, publisher, placement, geography, and 1-minute/1-hour/day windows.
4. Serve near-real-time dashboard reads and a corrected historical view when late events or replay jobs change prior windows.
5. Expose operator visibility for ingest lag, duplicate rate, hot campaigns, late-event corrections, and replay/backfill jobs.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Availability | 99.95% |
| Ingest throughput | 2M click events/s peak, burstable by campaign |
| Ingest latency | p95 < 200 ms to durable log append |
| Dashboard freshness | < 60 seconds for hot windows |
| Correction latency | < 15 minutes for late events inside the accepted watermark |
| Durability | No acknowledged event loss; replay must be idempotent |

### Constraints
- The event id or idempotency key is required; unauthenticated clients and malformed events are rejected before log append.
- Dashboard counters may be eventually consistent, but billing-grade counters require dedupe and correction audit trails.
- Retain raw immutable events long enough for dispute resolution and replay; retain aggregate buckets much longer.
- Keep v1 fraud scoring as a side pipeline so the core answer stays focused on ingestion, aggregation, and correctness.

### Out of scope
- ML fraud model internals, attribution model experimentation, and advertiser billing invoice generation.
- Creative review, campaign management, and ad-serving auction decisions.
- Organization-specific compliance implementation details.

## API / system interface


```http
POST /api/v1/click-events
GET  /api/v1/advertisers/{advertiser_id}/metrics?from=...&to=...&granularity=1m
GET  /api/v1/campaigns/{campaign_id}/corrections?from=...&to=...
GET  /api/v1/operators/ingest-lag?partition=...
```

## Key design challenges

1. Preserving low-latency dashboards without letting duplicate events inflate billing counters.
2. Handling late/out-of-order events with event-time windows, watermarks, correction logs, and replay-safe aggregate updates.
3. Surviving hot campaigns or publishers whose traffic can overwhelm a naive partition key.
4. Explaining where the system is exact, where it is eventually corrected, and how advertisers can audit changes.

## Related links
- [HLD Design Template](../DESIGN-TEMPLATE.md)
- [Idempotency](../../03-hld-concepts/idempotency/THEORY.md)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
- [Write Scaling](../../03-hld-concepts/write-scaling/THEORY.md)
