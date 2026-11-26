
# Online Auction System - Strong Answer

## 0-5 min: Requirements

Say: "I will optimize for a fair auction: once a bid is accepted, it is durable, ordered within that auction, and cannot lose to a lower or later bid."

- Scope marketplace auctions with authenticated bidders, reserve price, bid history, live price updates, close/finalize flow, and seller-visible audit trail.
- Non-goals: payment capture, fraud scoring, catalog search, and shipment workflows unless the interviewer asks.
- Correctness boundary: bid acceptance and auction close are linearizable per `auction_id`.

## 5-10 min: Scale and Constraints

Say: "The shape is read-heavy overall, but the dangerous path is a hot auction where many bidders race on one item."

- Target p99 bid latency under 200 ms and p95 auction-detail reads under 80 ms.
- Separate normal auctions from hot auctions; normal traffic uses conditional writes, hot auctions use a serialized per-auction lane.
- Fail closed when the write quorum, lock, or sequencer is unavailable.

## 10-20 min: API and Data Model

Say: "The bid API must be idempotent and reject stale clients rather than accepting ambiguous writes."

- `POST /auctions/{id}/bids` with `bidder_id`, `amount_cents`, `client_seen_version`, and `idempotency_key`.
- `GET /auctions/{id}` returns head state, current winner alias, close time, version, and projection freshness.
- Core records: `auction`, `auction_head`, `bid_event`, `auction_close_task`, and `bid_idempotency`.
- Use `(auction_id, bid_seq)` for ordered history and `(auction_id, version, winning_amount_cents)` for conditional updates.

## 20-35 min: Architecture

Say: "Writes go through a correctness path first; caches, websocket fanout, and search indexes are derived from the committed event log."

- API Gateway handles auth/rate limits and sends bid writes to Auction API.
- Auction API checks idempotency, validates amount, applies conditional update or hot-auction sequencer, and appends `BidAccepted`.
- Projection workers update auction-detail cache, bid history views, websocket fanout, and seller analytics.
- Close workers finalize only when `now >= close_at` and the head version has not changed since the close read.

## 35-42 min: Deep Dives

Say: "The two failure cases I would defend hardest are split-brain winners and stale projections misleading bidders."

- Race control: per-auction sequence, monotonic `bid_seq`, and conditional write checks reject duplicate winners.
- Hot partitions: move celebrity auctions to a dedicated sequencer backed by synchronous log flush; reopen after replaying the last committed sequence.
- Projection failure: serve direct head/event-log reads for hot auctions and rebuild projections by `auction_id` range.
- Close correctness: soft close extends if bids arrive in the final window; finalization emits one immutable `AuctionClosed`.

## 42-45 min: Wrap-up

Say: "I chose single-writer correctness per auction, derived read models, and explicit fail-closed behavior because fairness matters more than accepting every bid during a partial outage."

- Trade-off: single writable primary per auction simplifies fairness but limits active-active writes for the same item.
- Next evolution: shard auctions across regions by seller or item category, then add read-only replicas for global browse traffic.
