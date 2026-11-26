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

## 3. 🔌 System Interface

### External Contract
- Protocol: TCP / FIX (Financial Information eXchange) or fast binary protocol over WebSocket for modern API access.
- Rate limiting is critical to avoid matching engine starvation.

### Core Operations
- `PlaceOrder(symbol, side, price, quantity, clientId)`
- `CancelOrder(orderId, symbol)`

### Outbound Events
- `ExecutionReport(orderId, filledQty, price, status)`
- `MarketDataUpdate(symbol, priceLevel, quantityChange)`

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
