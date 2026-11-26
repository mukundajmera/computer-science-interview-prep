
# Live Comments System - Design

## 1. Requirements and Constraints

Design a live comment stream for large broadcasts where viewers can post, receive, and replay recent comments with low latency.

| Requirement | Target |
|---|---|
| Fanout latency | p99 < 250 ms from accepted write to connected viewers in same region |
| Post latency | p95 < 100 ms for validation + durable append |
| Availability | 99.99% for reads/fanout, 99.95% for writes |
| Ordering | Stable per `stream_id` partition; no global total order |
| Replay | Last 5-10 minutes or last 2,000 comments per active stream |
| Safety | Moderation before broad fanout; audit retained for abuse review |

Out of scope: full video delivery, recommendation ranking, creator monetization, and long-term analytics dashboards.

## 2. Capacity and Latency Assumptions

| Metric | Assumption | Design Impact |
|---|---:|---|
| Concurrent viewers | 5M peak globally, 1M on one marquee stream | WebSocket tier must shard by `stream_id` and region |
| Comment writes | 150K/sec peak globally, 20K/sec on one stream | Append log partitions and slow-mode controls are required |
| Fanout deliveries | 5M/sec peak for visible comments | Push only sampled/ranked comments for very hot streams |
| Comment size | 300 B text + 500 B metadata | Hot retention fits in Redis/Scylla; cold archive in object storage |
| Storage | ~65 GB/day raw at 150K/sec peak for 1 hour + normal traffic | TTL hot store, compacted audit/archive path |

The design optimizes for low-latency regional delivery while preserving a durable append before fanout.

## 3. API and WebSocket Contracts

### REST APIs

```http
POST /api/v1/live/{streamId}/comments
Idempotency-Key: <client-generated-uuid>
Authorization: Bearer <token>

{
  "clientCommentId": "cmt_tmp_123",
  "body": "Great point!",
  "replyToCommentId": "optional",
  "deviceTsMs": 1730000000000
}
```

Response:

```json
{
  "commentId": "01JABCD...",
  "streamId": "live_42",
  "status": "accepted",
  "serverTsMs": 1730000000123,
  "cursor": "p07:000000918273"
}
```

```http
GET /api/v1/live/{streamId}/comments?cursor=p07:000000918273&limit=100
GET /api/v1/live/{streamId}/replay?sinceMs=1730000000000&limit=200
POST /api/v1/live/{streamId}/moderation/actions
POST /api/v1/live/{streamId}/acks
```

Error model: `400` invalid body, `401/403` auth or banned user, `409` duplicate idempotency key conflict, `429` slow-mode/rate limit, `503` write path unavailable.

### WebSocket Contract

```text
wss://comments.example.com/v1/live/{streamId}?resumeCursor=p07:000000918273
```

Server events:

```json
{"type":"comment","commentId":"01JABCD...","cursor":"p07:000000918274","body":"...","authorBadge":"member","serverTsMs":1730000000456}
{"type":"moderation_redact","commentId":"01JABCD...","reason":"policy"}
{"type":"slow_mode","intervalSec":10,"untilTsMs":1730000060000}
{"type":"replay_gap","fromCursor":"p07:000000918100","toCursor":"p07:000000918274"}
```

Client events: `ack_cursor`, `heartbeat`, `resume`, and optional `hide_comment` feedback for moderation signals.

## 4. Data Model and Storage

| Store | Schema / Key | Indexes and Partitioning | Retention |
|---|---|---|---|
| Comment log (Scylla/Cassandra) | `comments_by_stream_bucket(stream_id, bucket_minute, shard_id, seq) -> comment_id, user_id, body, status, server_ts` | Partition by `(stream_id, bucket_minute, shard_id)`, clustering by `seq`; `shard_id = hash(comment_id) % N` for hot streams | 7-30 days, TTL by product tier |
| Idempotency store (Redis/DynamoDB) | `idem:{stream_id}:{user_id}:{key} -> comment_id, body_hash, expires_at` | Key-value lookup on write retry | 24 hours |
| Hot replay buffer (Redis Streams) | `replay:{stream_id}:{shard_id}` entries keyed by cursor | Trim by max length and age; per-region replicas | 10 minutes or 2,000 comments |
| Connection registry (Redis) | `conn:{stream_id}:{edge_shard} -> ws_server_ids` and `user_conn:{user_id}` | Sharded by stream and edge shard | Heartbeat TTL 60 seconds |
| Moderation/audit (PostgreSQL + object storage) | `moderation_events(comment_id, action, actor, reason, ts)` | Index on `(stream_id, ts)` and `(user_id, ts)` | 1 year audit, redacted text per policy |
| Stream controls (PostgreSQL) | `stream_controls(stream_id, slow_mode_sec, banned_terms_version, fanout_policy)` | Primary key `stream_id` | Until stream ends + 30 days |

Cursor format: `<partition>:<monotonic_seq>`, for example `p07:000000918274`. It is opaque to clients but lets servers resume from the right log partition without scanning all shards.

## 5. High-Level Architecture

[Architecture Diagram](./diagrams/architecture.mmd)


## 6. Read, Write, Failure, and Recovery Paths

### Write Path

1. API Gateway authenticates the user, checks stream membership, and enforces per-user and per-stream rate limits (e.g., using Redis).
2. Comment API validates payload size, deduplicates by idempotency key, and loads stream controls.
3. Moderation precheck applies banned terms, user trust tier, and spam heuristics. Clear comments continue; suspicious comments are held or shadowed.
4. Comment API appends to the durable comment log with a generated sortable `comment_id` and cursor.
5. The append emits a comment event to Kafka/Pulsar partitioned by `(stream_id, shard_id)`.
6. Fanout workers push to WebSocket edge servers; replay writers update the hot replay buffer.

### Live Read Path

1. Client opens WebSocket with an optional `resumeCursor`.
2. WebSocket Edge registers the connection under `(stream_id, edge_shard)` and sends missed replay entries when the cursor is still in the hot buffer.
3. New comment events are pushed over the socket with cursor and server timestamp.
4. If a cursor gap is detected, the client receives `replay_gap` and calls the Replay API.

### Replay and History Path

1. Replay API first reads Redis Streams for recent comments.
2. If the requested cursor is older than hot retention, it scans the durable log by `(stream_id, bucket_minute, shard_id, seq)`.
3. Results are merged by cursor, filtered for moderation status, and returned with `nextCursor`.

### Failure and Recovery Path

- WebSocket server failure: connection registry entries expire by heartbeat; clients reconnect with last acknowledged cursor and replay from hot buffer.
- Fanout worker lag: preserve durable log first, expose lag metrics, and degrade hot streams to sampled comments until lag clears.
- Kafka/Pulsar partition outage: write path can continue only if durable append succeeds and event publish is confirmed; otherwise return `503` so clients retry with the same idempotency key.
- Replay buffer loss: rebuild recent windows from the durable log for active streams; clients may see higher replay latency but no accepted comments are lost.
- Poison moderation/fanout events: route to DLQ with comment ID, stream ID, and policy version; recovery replays by cursor range after fixing the consumer.
- Regional outage: DNS shifts viewers to another region; active streams recover from replicated durable log with relaxed latency until local buffers warm.

## 7. Deep Dives

### Fanout Cursors and Hot Streams

For normal streams, every accepted comment is pushed to all connected viewers. For celebrity-scale streams, pushing every comment to every viewer can exceed socket and client rendering limits, so the service separates durable acceptance from visible fanout.

- Partition each stream into `N` comment shards and assign monotonic sequence numbers per shard.
- Build an opaque cursor that identifies shard and sequence; clients acknowledge the highest rendered cursor per shard.
- Fanout workers maintain per-edge cursors and send batches capped by bytes/sec and comments/sec.
- Hot streams can switch from `all_comments` to `ranked_sample` fanout while preserving the full durable log for replay, moderation, and creator tools.
- Backpressure is explicit: if edge send queues exceed limits, drop low-priority visible comments and send a `replay_gap` marker instead of blocking durable writes.

### Moderation, Slow-Mode, and Replay

Moderation must be fast enough for live chat but strong enough to avoid broadcasting abusive content.

- Pre-fanout checks reject banned users, blocked terms, duplicate spam, and oversized payloads synchronously.
- Risky comments are written with `status=held` and excluded from fanout until async moderation clears them.
- Moderator actions emit `moderation_redact` events so clients remove already-rendered comments.
- Slow-mode is stored in `stream_controls` and enforced before append with per-user token buckets; creators can raise the interval during spikes.
- Replay always filters by latest moderation status, so late joiners do not see comments that were later removed.

## 8. Observability, Rollout, and Rollback

Key metrics: write p95/p99, fanout p99, WebSocket connected count, per-stream publish lag, replay gap rate, moderation hold rate, DLQ depth, slow-mode throttles, and reconnect success rate.

Logs and traces carry `stream_id`, `comment_id`, `cursor`, `user_id_hash`, `policy_version`, and `edge_server_id`. Alerts page on fanout p99 > 250 ms for 5 minutes, replay gap rate > 1%, or durable append error rate > 0.1%.

Rollout plan:

1. Shadow-write comments to the new log while old path serves traffic.
2. Enable replay reads for internal streams.
3. Route 1% of low-risk streams to new fanout, then 10%, then marquee streams.
4. Enable ranked-sample fanout only behind a per-stream feature flag.

Rollback: disable the fanout flag, drain workers, keep durable log writes for reconciliation if healthy, or switch writes back to the previous append path. Cursor versions are prefixed so clients can reconnect through either path during rollback.

## 9. Trade-offs and Decisions

| Decision | Choice | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Ordering | Per stream shard ordering | Global ordering | Lower latency and avoids a single hot sequencer | Product requires exact total order |
| Delivery | WebSocket push + replay gap repair | Polling only | Lower live latency and better mobile experience | Socket costs exceed budget |
| Hot stream fanout | Adaptive all-comments or ranked sample | Always fanout every comment | Protects clients and edge queues during spikes | Creator requires unfiltered firehose |
| Storage | Durable log + hot replay buffer | Redis-only chat buffer | Accepted comments survive process/cache loss | Retention requirements shrink materially |
| Moderation | Fast precheck + async hold/redact | Fully manual review before send | Keeps latency low while limiting abuse blast radius | Regulated content requires stricter review |

## 10. Follow-up Questions and Strong Answer

- At 10x scale, increase stream shard count, regionalize fanout, and move marquee streams to ranked-sample by default.
- Under regional outage, accepted comments recover from the replicated durable log, but live fanout latency temporarily degrades.
- To reduce cost, lower hot replay retention, compress cold comments, and sample fanout for anonymous viewers.
- For the time-boxed interview narrative, use [STRONG-ANSWER.md](./STRONG-ANSWER.md) as the 45-minute section plan.
