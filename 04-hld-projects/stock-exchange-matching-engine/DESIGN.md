# Stock Exchange Matching Engine - High Level Design

---

## 1. 📝 Requirements and Constraints

Please refer to [PROBLEM.md](./PROBLEM.md) for detailed requirements and constraints.

---

## 2. 📊 Back-of-Envelope Estimation

### Traffic

| Metric | Value | Formula |
|---|---|---|
| Daily Orders | $1\text{ Billion}$ | Input |
| Trading Hours | $6.5\text{ hours}$ | Exchange standard |
| Avg QPS | $43,000$ | $1\text{B} / (6.5 \times 3600)$ |
| Peak QPS | $215,000$ | $5 \times \text{Avg QPS}$ (market open/close burst) |

### Memory / Storage

- 100 active symbols.
- Size per symbol is $< 10\text{ MB}$, resulting in $< 1\text{ GB}$ total for the order book.
- The 1 GB order book state resides entirely in locked physical RAM (using `mlock` to prevent page swapping).
- The top 100 bid/ask price levels per symbol (~100 KB) fit neatly within CPU L2/L3 caches.
- Ring buffer entries use the LMAX Disruptor lock-free off-heap pattern.
- Order structs are pre-allocated with cache-line alignment ($64\text{ bytes}$) to prevent Garbage Collection pauses and false sharing.

---

## 3. 🔌 API / System Interface

### Protocol Choice and Justification
- **Chosen Order-Entry Protocol (FIX / Binary Session over Persistent TCP):** Institutional order entry uses a binary-framed FIX-like protocol (such as SBE or OUCH/FIX 4.4 tag-value over persistent TCP sessions) rather than REST/JSON. Text-based HTTP/JSON parsing allocates short-lived heap objects, triggers GC pauses, and adds hundreds of microseconds of serialization overhead—violating the $< 100\text{ }\mu\text{s}$ matching-core latency budget. A fixed-width binary or session-sequenced FIX framing allows zero-copy deserialization directly into pre-allocated ring-buffer slots.
- **Market Data Protocol (UDP Multicast + TCP Replay):** Real-time L2 book deltas are broadcast over UDP multicast for deterministic, low-jitter fan-out to colocated subscribers, paired with a TCP/HTTP snapshot and gap-replay API for recovery.
- **Auth & Rate Limiting:** Mutual TLS + session-level logon keys at the FIX/API Gateway; per-session token-bucket rate limits (orders/sec and cancel-to-fill ratios) prevent any single participant from starving the single-threaded matching core.

### Order Entry, Cancel, and Replace Contracts

All prices are encoded as **fixed-point integers** (cents or ticks, e.g., `18550` = `$185.50`) to eliminate floating-point rounding drift. Every mutating command carries a participant-unique `clientOrderId` for idempotency and receives a strictly monotonic per-symbol `sequenceId` from the Sequencer.

#### 1. New Limit Order (`NewOrderSingle` / `MsgType=D`, REST equivalent `POST /api/v1/orders`)
```text
# FIX-like logical frame (SOH-delimited in wire format)
35=D | 49=MM_07 | 11=cli-20261128-00042 | 55=AAPL | 54=1(BUY) | 40=2(LIMIT) | 44=18550 | 38=100 | 59=1(GTC)
```
**Outbound `ExecutionReport` (`MsgType=8`):**
```json
{
  "msgType": "EXECUTION_REPORT",
  "sequenceId": 481205,
  "orderId": "ord-9901842",
  "clientOrderId": "cli-20261128-00042",
  "symbol": "AAPL",
  "status": "PARTIALLY_FILLED",
  "filledQuantity": 40,
  "leavesQuantity": 60,
  "fills": [
    { "fillId": "fil-77101", "matchPrice": 18545, "matchedQuantity": 40 }
  ]
}
```

#### 2. Cancel Order (`OrderCancelRequest` / `MsgType=F`, REST equivalent `DELETE /api/v1/orders/{orderId}`)
```text
35=F | 49=MM_07 | 11=cxl-20261128-00043 | 41=cli-20261128-00042 | 37=ord-9901842 | 55=AAPL
```
**Outbound `ExecutionReport` (`MsgType=8`):**
```json
{
  "msgType": "EXECUTION_REPORT",
  "sequenceId": 481219,
  "orderId": "ord-9901842",
  "origClientOrderId": "cli-20261128-00042",
  "clientOrderId": "cxl-20261128-00043",
  "symbol": "AAPL",
  "status": "CANCELLED",
  "filledQuantity": 40,
  "leavesQuantity": 0
}
```

### Market Data Feed & Sequence-Number Gap Recovery

- **L2 Snapshot (`GET /api/v1/market-data/{symbol}/snapshot?depth=20`):** Returns aggregated bid/ask levels anchored at an exact `lastSequenceId`.
  ```json
  {
    "symbol": "AAPL",
    "lastSequenceId": 481219,
    "bids": [[18540, 500], [18535, 1200]],
    "asks": [[18550, 300], [18555, 800]]
  }
  ```
- **Incremental Delta (`MarketDataUpdate` over UDP Multicast / WebSocket):**
  ```json
  {
    "symbol": "AAPL",
    "sequenceId": 481220,
    "side": "BUY",
    "priceLevel": 18550,
    "quantityChange": 100,
    "newTotalQuantity": 100
  }
  ```
- **Deterministic Sequencing & Gap Recovery:** The Sequencer stamps every validated inbound command with a strictly contiguous `sequenceId` per symbol partition (`1, 2, 3, ...`). Subscribers buffer live deltas while fetching a snapshot, drop deltas with `sequenceId <= lastSequenceId`, and verify each subsequent delta satisfies `incomingSeq == expectedSeq`. On detecting a gap (`incomingSeq > expectedSeq`), the subscriber requests the missing range via `GET /api/v1/market-data/{symbol}/replay?fromSeq=481220&toSeq=481225` (falling back to a fresh snapshot if the gap exceeds the replay ring buffer).

### Idempotency, States, and Reject Codes
- **Order States:** `ACCEPTED`, `PARTIALLY_FILLED`, `FILLED`, `CANCELLED`, `REJECTED`.
- **Idempotency:** The gateway maintains a per-session `(clientId, clientOrderId)` map; retrying an identical command returns the cached `ExecutionReport` with the original `orderId` and `sequenceId` without re-sequencing, whereas reusing a `clientOrderId` with different parameters is rejected (`DUPLICATE_CLIENT_ORDER_ID`).
- **Reject / Error Codes:** `INVALID_PRICE_TICK` (`400`), `INVALID_QUANTITY` (`400`), `UNKNOWN_SYMBOL` (`404`), `ORDER_NOT_FOUND` (`404`), `DUPLICATE_CLIENT_ORDER_ID` (`409`), `INSUFFICIENT_FUNDS` (`422`), `RATE_LIMIT_EXCEEDED` (`429`), and `ENGINE_UNAVAILABLE` (`503`).

---

## 4. 🗄️ Core Entities and Data Model

The matching engine is strictly in-memory. Database persistence occurs asynchronously outside the critical path.

```java
// Limit Order Book in-memory model
class PriceLevel {
    long limitPrice;
    long totalVolume;
    DoublyLinkedList<Order> orders;
}

class OrderBook {
    TreeMap<Long, PriceLevel> buyBook;  // DESC
    TreeMap<Long, PriceLevel> sellBook; // ASC
    HashMap<Long, OrderNode> orderMap;  // O(1) cancel lookup
}

// Outbound Fill / Execution Record
class ExecutionFill {
    long fillId;
    long orderId;
    long sequenceId;
    long matchPrice;
    long matchedQuantity;
    long leavesQuantity;
    Side side;
}
```

---

## 5. 🏗️ High-Level Architecture

### Architecture Pattern: LMAX / Sequencer
Traditional microservice hops take 10-50ms, which is unacceptable. Modern exchanges use a single-threaded in-memory core communicating via memory-mapped ring buffers (e.g., LMAX Disruptor pattern) to achieve microsecond latency.

_See diagram: [Architecture](./diagrams/architecture.mmd)_

### Components
1. **API Gateway / FIX Gateways:** Terminate SSL/TCP, perform basic validation, and forward to risk engine.
2. **Pre-Trade Risk Engine:** Checks user balances and withholds funds. Must be ultra-fast (often in-memory cache).
3. **Sequencer:** Assigns a strict monotonic `sequenceId` to every inbound valid order. Multicasts the sequenced stream.
4. **Matching Engine (Primary):** Single-threaded CPU-pinned process that ingests sequenced orders, executes price-time priority matching, and writes execution events to an outbound ring buffer.
5. **Matching Engine (Hot Standby):** Ingests the exact same sequenced stream. Since the matching logic is deterministic, the standby achieves the exact same state. If the primary fails, the standby takes over instantly without data loss.
6. **Market Data Publisher:** Reads outbound execution events and order book deltas, aggregates them (L2 depth, OHLCV), and broadcasts over UDP/WebSockets to subscribers.
7. **Persister (Journaling):** Reads the sequenced stream and writes it to reliable storage (e.g., Kafka / DB) for end-of-day reconciliation and disaster recovery.

---

## 6. 🔍 Deep Dives

_See diagram: [Sequence Flow](./diagrams/sequence.mmd)_

### Deep Dive A: Deterministic Matching & High Availability
- **Problem:** If the primary matching engine crashes, how do we failover without losing orders or double-matching?
- **Chosen Pattern:** Event Sourcing with a Sequencer. The sequencer serializes all inputs into an ordered, append-only log. Both primary and standby consume this log. 
- **Benefit:** The matching engine is a pure deterministic state machine. $State(N) = State(N-1) + Event(N)$. Failover is simply routing outbound connections to the standby, as its internal state is already identical to the primary up to the latest sequence ID.

### Deep Dive B: Ultra-Low Latency Optimizations
- **Problem:** Traditional Java/C++ applications suffer from GC pauses, context switching, and network I/O blocking.
- **Chosen Pattern:** 
  - **Single-Threaded:** No locks, no mutexes, no context switches.
  - **Memory-Mapped Ring Buffers (Disruptor):** Lock-free inter-thread communication.
  - **Zero Object Allocation:** Pre-allocate all `Order` and `PriceLevel` objects in object pools at startup to prevent GC.
  - **CPU Pinning & NUMA:** Pin the matching thread to a specific CPU core to keep the order book entirely in L1/L2/L3 cache.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Architecture | Single-threaded in-memory core | Distributed microservices | Sub-100µs latency requirement | Latency requirements relax |
| State replication | Deterministic sequencer replay | DB replication / 2PC | Avoids coordination overhead in critical path | Need active-active matching (rare) |
| Order lookup | `HashMap<Id, Node>` | Scan `TreeMap` | $O(1)$ cancellation is critical for market makers | Memory limits exceeded |
| Data types | Fixed-point `long` | Floating-point `double` | Avoids precision loss in finance | Never |

---

## 8. 🔗 Cross-Links
- [Problem](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Comparisons](./COMPARISON.md)

---
**Real-world reference**: See how Stripe solved this in the [Stripe case study](../../case-studies/stripe-ledger-engine/)
