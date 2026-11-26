# Online Auction System - Design

## 1. Requirements and constraints

### Functional
- Sellers create auctions with reserve/start price, bid increment, start time, close time, and optional anti-sniping extension.
- Buyers place bids that must be strictly higher than the current winning bid for the same auction.
- Readers see live auction state, bid history, and final winner after close.
- System sends bidder/seller notifications without blocking bid acceptance.

### Non-functional
| Requirement | Target |
|---|---|
| Bid correctness | Linearizable per auction; no two accepted bids at the same sequence |
| Bid latency | p99 < 200 ms for hot auctions in the primary region |
| Read latency | p95 < 80 ms for auction detail reads |
| Availability | 99.95% overall; bid writes fail closed on quorum/lock loss |
| Durability | No acknowledged bid loss; accepted bids are replayable from the event log |

## 2. Back-of-envelope estimation

Assume 20M DAU, 2M active auctions/day, and celebrity drops that concentrate traffic.

| Metric | Value | Design impact |
|---|---|---|
| Average reads | 60K RPS | Cache auction detail and leaderboards |
| Peak reads | 600K RPS | CDN/edge cache only for non-critical metadata; live price cache with short TTL |
| Average bids | 8K TPS | Append bid events and update auction head atomically |
| Peak bids | 120K TPS, with 20K TPS on one auction | Per-auction serialization and hot-auction sharding by queue, not by mutable winner row |
| Storage | ~700M bid events/day at 500 bytes | Tier event log after 90 days; keep audit archive for disputes |

## 3. APIs

```http
POST /api/v1/auctions
GET  /api/v1/auctions?status=live&category=collectibles&cursor=...
GET  /api/v1/auctions/{auctionId}
GET  /api/v1/auctions/{auctionId}/bids?cursor=...
POST /api/v1/auctions/{auctionId}/bids
POST /api/v1/auctions/{auctionId}/close
```

### Bid contract

```http
POST /api/v1/auctions/auc_123/bids
Idempotency-Key: user_42:auc_123:bid:1700000123

{
  "bidder_id": "user_42",
  "amount_cents": 125000,
  "client_seen_version": 18
}
```

```json
{
  "auction_id": "auc_123",
  "accepted": true,
  "bid_id": "bid_999",
  "winning_amount_cents": 125000,
  "auction_version": 19,
  "extended_until": "2026-06-14T12:05:00Z"
}
```

| Error | Retry? | Handling |
|---|---|---|
| `bid_too_low` | no | Return current winning amount and minimum next bid. |
| `auction_closed` | no | Return final state and winner if finalized. |
| `stale_client_version` | yes | Client refreshes auction detail and retries with a higher amount. |
| `duplicate_idempotency_key` | no | Replay stored result when payload hash matches; reject mismatched payload. |
| `write_quorum_unavailable` | yes | Fail closed; do not accept bids that cannot be durably committed. |

## 4. Data model and storage

| Store/table | Key fields | Keys, indexes, and partitioning | Retention |
|---|---|---|---|
| `auction` | `auction_id`, `seller_id`, `status`, `start_at`, `close_at`, `reserve_cents`, `min_increment_cents`, `version`, `winning_bid_id`, `winning_amount_cents`, `winner_id` | PK `auction_id`; index `(status, close_at)` for close scanner; index `(seller_id, created_at)`; partition by hashed `auction_id` | Active plus 7 years metadata/audit |
| `auction_head` | `auction_id`, `version`, `winning_bid_id`, `winning_amount_cents`, `winner_id`, `close_at` | PK `auction_id`; conditional update where `version` and current amount match; hot rows pinned to primary region | Active auctions plus 30 days |
| `bid_event` | `auction_id`, `bid_seq`, `bid_id`, `bidder_id`, `amount_cents`, `accepted_at`, `request_id` | PK `(auction_id, bid_seq)`; unique `bid_id`; index `(bidder_id, accepted_at)`; partition by `auction_id`, with hot-auction event stream lane | 90 days hot, 7 years cold audit |
| `bid_idempotency` | `auction_id`, `bidder_id`, `idem_key`, `payload_hash`, `bid_id`, `response_body`, `expires_at` | Unique `(auction_id, bidder_id, idem_key)`; TTL index `expires_at` | 24 hours for client retries, longer for disputes when accepted |
| `auction_projection` | `auction_id`, `status`, `current_price`, `bid_count`, `watcher_count`, `updated_at` | KV/cache by `auction_id`; rebuilt from `bid_event`; versioned by `auction.version` | Rebuildable; TTL minutes to hours |
| `notification_outbox` | `event_id`, `auction_id`, `recipient_id`, `event_type`, `status`, `next_attempt_at` | PK `event_id`; index `(status, next_attempt_at)`; partition by recipient hash | Until delivered plus 30 days |

Primary bid correctness lives in `auction_head` plus append-only `bid_event`. Search/listing projections, notifications, and analytics are derived and can lag or be rebuilt.

## 5. High-level architecture

[Architecture Diagram](./diagrams/architecture.mmd)

### Read path
1. Auction detail read hits cache/projection by `auction_id`.
2. If projection version is stale or missing, read `auction_head` and recent `bid_event` rows, then refresh cache.
3. Bid history paginates from `bid_event` by `(auction_id, bid_seq)`; list/search reads use derived indexes.

### Bid write path
1. Gateway authenticates bidder and forwards `Idempotency-Key`.
2. Bid coordinator validates auction status, close time, amount, reserve/min increment, bidder eligibility, and payload hash.
3. Insert/fetch `bid_idempotency`; replay prior response for exact duplicate.
4. Execute one per-auction conditional transaction: update `auction_head` from version N to N+1 and append `bid_event(auction_id, bid_seq=N+1)`.
5. Publish outbox/event-log message for projections, websocket updates, notifications, and fraud/risk analytics.

### Close/finalization path
1. Close scanner reads `auction(status=live, close_at <= now)` by index.
2. Finalizer conditionally transitions auction to `closing`, verifies latest `auction_head`, applies anti-sniping extension if needed, then sets `closed`.
3. Winner and seller notifications are emitted from the same finalization event; payment/escrow is a downstream integration, not part of bid correctness.

## 6. Online-auction deep dives

### Deep dive A: hot-auction bid correctness
- Route all bids for a hot `auction_id` to one coordinator lane using consistent hashing so the mutable winner decision is serialized.
- Use conditional writes on `(auction_id, version, winning_amount_cents)` to reject races even if two coordinators briefly receive the same auction.
- Keep the accepted bid event append and head update in one atomic commit; if the event cannot be written, the bid is not acknowledged.
- For extreme celebrity auctions, require bid reservations in an in-memory sequencer backed by synchronous event-log flush; fail over by replaying the last committed sequence before reopening writes.

### Deep dive B: anti-sniping and close-time races
- A bid accepted inside the final extension window updates both `winning_amount_cents` and `close_at` in the same conditional transaction.
- The close worker only finalizes when `now >= close_at` and the `auction_head.version` has not changed since it read the row.
- If a bid and close race, the loser retries against the newer version: bid may extend the auction, or close may observe no eligible late bid and finalize.
- Clients treat displayed countdown as advisory; server time and committed `close_at` are authoritative.

### Deep dive C: projection rebuild and recovery
- Rebuild auction detail, bid history summaries, and search/list projections from `bid_event` with checkpointed consumers.
- Poison projection events go to DLQ, but bid acceptance remains available because projections are not source of truth.
- If cache/index corruption is detected, disable affected projection reads, serve direct head/event-log reads for hot auctions, and backfill by `auction_id` ranges.

## 7. Failure handling

| Failure | User-visible behavior | Recovery |
|---|---|---|
| Bid coordinator crash after commit before response | Client retry with same idempotency key returns stored accepted result. | Idempotency table and event log preserve the response. |
| Cache/projection outage | Auction detail may be slower; bid writes continue. | Read through primary head/event log; rebuild projections from checkpoints. |
| Event worker lag | Notifications and live fanout lag; accepted bid state remains correct. | Alert on consumer lag, scale workers, replay from event log. |
| Primary store quorum loss | New bids fail closed with retryable error. | Promote healthy primary only after latest committed bid sequence is known. |
| Finalizer crash mid-close | Auction may remain `closing` briefly. | Lease-based finalizer retries; version checks prevent double winner emission. |

## 8. Observability, rollout, and rollback

### Observability
- Metrics: bid accept/reject rate, p50/p95/p99 bid latency, conditional-write conflict rate, hot-auction queue depth, close-finalization lag, projection lag, websocket fanout lag, DLQ count.
- Logs/traces: propagate `request_id`, `auction_id`, `bid_id`, `bid_seq`, `idempotency_key_hash`, and `auction_version`.
- Alerts: accepted-bid event missing, duplicate bid sequence, close lag over SLA, projection lag over freshness target, write quorum unavailable, or high `bid_too_low` spikes suggesting stale clients.

### Rollout
- Start with single-region writes and read-only shadow projections.
- Enable bidding by category/seller cohort, then by traffic percentage.
- Shadow close/finalization decisions before allowing automated winner notifications.
- Run synthetic hot-auction load tests before promoting large planned drops.

### Rollback
- Disable new auction creation or route new auctions to the previous bid path behind a feature flag.
- Keep event consumers and finalizers running for already-started auctions until they close.
- Do not mutate bid history during rollback; append compensating audit events and rebuild projections from `bid_event`.
- If a coordinator release corrupts projections only, roll back readers first and replay projections without stopping bid writes.

## 9. Trade-offs

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Consistency boundary | Linearizable per auction | Globally serial bidding | Preserves correctness where needed without killing throughput |
| Source of truth | Head row + append-only bid events | Cache-first current price | Durable replay and dispute audit |
| Hot auctions | Serialized lane per auction | Blind multi-writer sharding | Avoids split-brain winners |
| Notifications | Async outbox/fanout | Synchronous notify on bid | Keeps bid p99 under target |
| Multi-region writes | Single writable primary per auction | Active-active same-auction writes | Simpler correctness; can shard auctions across regions |

## 10. Strong-answer reference

Use [STRONG-ANSWER.md](./STRONG-ANSWER.md) for the 45-minute interview flow. Lead with per-auction bid correctness, then add hot-auction handling, close-time races, and replayable recovery.

---
**Real-world reference**: See how Amazon solved this in the [Amazon case study](../../case-studies/amazon-orders/)
