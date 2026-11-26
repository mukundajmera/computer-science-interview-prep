
# Live Comments System - Strong Answer

## 0-5 min: Requirements

Say: "I will design a low-latency live comment stream where accepted comments are durable before fanout, and clients can recover gaps through replay."

- Support posting, live websocket delivery, replay of recent comments, moderation redaction, slow mode, and per-stream controls.
- Non-goals: long-form discussion threads, recommendation ranking, and full content-review workflows.
- Correctness boundary: per-stream ordering and no acknowledged comment loss.

## 5-10 min: Scale and Constraints

Say: "The main bottleneck is not storage alone; it is fanout pressure on a few massive streams."

- Plan for roughly 150K comment writes/sec globally and 20K/sec on one stream.
- Target p95 post latency under 100 ms and p99 same-region fanout under 250 ms.
- Keep durable append independent from websocket delivery so slow clients cannot block writes.

## 10-20 min: API and Data Model

Say: "Every write carries an idempotency key because mobile clients will retry during reconnects."

- `POST /streams/{stream_id}/comments` with body, client timestamp, and idempotency key.
- `GET /streams/{stream_id}/comments?cursor=...` for replay and gap repair.
- WebSocket subscribes with `stream_id`, last cursor, auth claims, and client capabilities.
- Store `comment_log`, `comment_projection`, `replay_buffer`, `stream_controls`, and `idempotency` records.

## 20-35 min: Architecture

Say: "The architecture is append first, fanout second, replay always available."

- API Gateway authenticates users, rate limits, and applies stream membership checks.
- Comment API validates payload, deduplicates retries, and appends to Kafka/Pulsar by `stream_id`.
- Moderation precheck can hold or redact; accepted comments fan out through regional websocket edge servers.
- Replay writers maintain Redis Streams or a similar recent-window store, backed by the durable log.

## 35-42 min: Deep Dives

Say: "When a client sees a cursor gap, the system should repair from replay instead of pretending delivery was perfect."

- Ordering: partition by stream and generate sortable cursors within the accepted log.
- Backpressure: drop low-priority visible delivery for overloaded clients, emit `replay_gap`, and keep durable writes moving.
- Moderation: publish `moderation_redact` events so clients remove already-rendered comments.
- Regional outage: shift viewers through DNS and rebuild hot replay buffers from the replicated log.

## 42-45 min: Wrap-up

Say: "I chose websocket push for experience, a durable log for recovery, and explicit replay gaps because live systems fail in partial ways."

- Trade-off: per-stream ordering is simpler and faster than global ordering.
- Next evolution: adaptive slow mode, per-stream shard splitting, and ML-assisted moderation with safe fallback to hold queues.
