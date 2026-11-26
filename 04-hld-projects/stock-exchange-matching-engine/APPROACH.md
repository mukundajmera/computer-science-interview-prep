# Approach: Stock Exchange Matching Engine

## Strategic Framing

Designing an exchange matching engine fundamentally tests a candidate's understanding of **extreme latency optimization** and **deterministic state machines**.

Unlike typical web services where stateless horizontal scaling is the answer, a matching engine for a specific stock (e.g., AAPL) must be strictly serialized to prevent race conditions. The approach must pivot from "distributed databases" to "in-memory, lock-free, mechanical sympathy."

### Key Themes to Address

1. **The Critical Path:** Network I/O and disk I/O must be removed from the order matching flow.
2. **Determinism:** How sequence IDs enable perfect active-passive replication without distributed locking.
3. **Data Structures:** Why `TreeMap` + `DoublyLinkedList` + `HashMap` is the optimal combination for limit order books.

## Architectural Patterns

### The LMAX Disruptor Pattern
A recognized standard for high-performance financial systems.
- Employs lock-free ring buffers.
- Separates network I/O, journaling, and business logic into different pipeline stages running on pinned CPU cores.

### Event Sourcing
- The matching core does not read from a database. It builds its state purely from an ordered stream of incoming commands (orders/cancels).

## Execution Strategy

1. **Establish constraints early:** Acknowledge that 100µs latency precludes database writes in the critical path.
2. **Define the Data Structures:** Immediately write out the `TreeMap` and `DoublyLinkedList` structures. This proves deep understanding of price-time priority.
3. **Trace the flow:** Walk through a limit order arriving, getting sequenced, matching against the opposite book, generating a fill, and emitting market data.
