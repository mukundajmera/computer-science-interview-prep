# Approach for Price Tracking Service

## Overview and Core Strategy
The Price Tracking Service evaluates product prices across multiple merchants, maintaining history and alerting users when prices cross configured thresholds. Our approach uses an in-memory execution model to evaluate these rules reliably and efficiently without relying on distributed systems overhead.

## Implementation Versions

### v1-basic: Fundamental Tracking
The `v1-basic` implementation introduces basic price observation and aggregation. It accepts incoming price ticks via a simple `recordPrice` interface and calculates summaries like minimum, maximum, and current price per product.

### v2-extended: Event-Driven Subscriptions and Contracts
The `v2-extended` version separates the concern of fetching prices from evaluating them.
- A `PriceCollector` runs on a poll interval, requesting prices from an injected `Transport`.
- A `SubscriptionService` (Java) or `PriceService` (Python) evaluates active `PriceAlertSubscription` records when new prices arrive.
- The `PriceHistoryStore` maintains history, automatically purging data older than the retention window based on an injected clock.

**Key Invariants:**
- Exact price-unit histories maintain configured retention and trigger one alert per threshold crossing, not every poll.
- Out-of-order timestamps (events older than the current max) are dropped to maintain timeline integrity.
- Repeated merchant events, out-of-order timestamps, missing product, failed polling, and unsubscribe are tested deterministically using an injected `Transport` and `Clock`. This allows full simulation without real network I/O or waiting for real time to pass.

### v3-optimized: Ring Buffer Store
The `v3-optimized` version builds upon `v2-extended` by introducing a custom `RingBuffer` implementation for the `PriceHistoryStore`. This optimization bounds memory usage strictly by count rather than just a time-based retention sweep, ensuring stable heap usage under high-throughput conditions.
