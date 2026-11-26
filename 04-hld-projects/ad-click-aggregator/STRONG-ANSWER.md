# Ad Click Aggregator — Strong Answer Outline (Time-Boxed)

## 0-5 min: Requirements
- Clarify whether counters drive only dashboards or also billing; say billing-grade counters need dedupe, replay, and correction audit trails.
- Confirm event shape: event id, campaign/ad-group/ad ids, publisher id, event timestamp, user/device attributes, and idempotency key.
- State the accepted trade-off: dashboards are near-real-time and may be corrected; raw accepted events are durable and replayable.

Say: "I will optimize for durable accepted events and corrected aggregates. The dashboard can be fresh and eventually corrected, but billing-facing counters need dedupe and an auditable correction path."

## 5-10 min: Estimation
- Use a concrete peak such as 2M click events/s and 2% duplicate retries to justify a durable log, horizontal stream aggregation, and a TTL dedupe index.
- Estimate raw daily volume and explain why aggregate retention and raw-event retention need different storage tiers.

## 10-20 min: API + data model
- Present `POST /api/v1/click-events`, advertiser metric queries, and correction queries.
- Model `click_event`, `dedup_index`, `aggregate_bucket`, and `correction_log`.
- Call out partitioning by event date plus campaign/event hash, and aggregate keys by tenant/window/granularity/dimensions.

## 20-35 min: Architecture
- Walk the write path: gateway validation, idempotency check, immutable event log, stream aggregator, aggregate store, and correction log.
- Walk the read path: dashboard queries hit precomputed buckets and optionally surface a "corrected through" watermark.
- Explain backfill and replay as first-class flows rather than emergency scripts.

## 35-42 min: Deep dives
- Deep dive event-time windows, watermark closure, and late-event correction.
- Discuss hot campaign mitigation with salted subkeys and query-time merge.
- Cover replay idempotency using deterministic mutation ids for aggregate updates.

## 42-45 min: Wrap-up
- Restate the core decisions: durable append-only log, early dedupe, event-time aggregation, correction ledger, and adaptive partitioning.
- Mention next-scale extensions: fraud scoring side stream, attribution model changes, and multi-region read replicas.

Say: "The system stays fast by serving precomputed buckets, and it stays correct by making replay and correction part of the normal design instead of an afterthought."
