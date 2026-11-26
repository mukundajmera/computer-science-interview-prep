# Stock Exchange Matching Engine

## Problem Statement

Design a centralized electronic stock exchange matching engine. The system must accept buy and sell limit orders, match them deterministically using price-time priority, and publish execution reports and real-time market data.

---

## Requirements and Constraints

### Functional Requirements

1. **Order Management:** Place and cancel limit orders for stocks.
2. **Matching Logic:** Match orders using price-time priority (FIFO matching at the same price level).
3. **Determinism:** Sequencer assigning monotonic sequence IDs to ensure identical state machine execution.
4. **Market Data:** Generate real-time L2 order book depth and candlestick (OHLCV) chart data.
5. **Pre-trade Risk:** Perform risk checks and withhold wallet funds prior to matching.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Latency | $< 100\text{ }\mu\text{s}$ P99 on matching core ($< 10\text{ ms}$ round trip) |
| Throughput | $43,000\text{ avg QPS}$, $215,000\text{ peak QPS}$ |
| High Availability | $99.99\%$; deterministic standby replica failover without data loss |
| Scale | $1\text{B orders/day}$ across 6.5 trading hours |
| Consistency | Strict consistency, deterministic matching |
| Active Symbols | 100 active symbols |

### Out of Scope

- User authentication and UI
- Complex order types (e.g., Iceberg, Stop-Loss, Trailing Stop)
- End-of-day settlement systems

---

## Data Constraints & Back-of-the-Envelope

- **Traffic:** $1\text{B orders} / (6.5 \times 3600\text{ s}) \approx 42,735\text{ QPS} \approx 43,000\text{ QPS}$. Peak QPS (market open) $= 5 \times 43,000 = 215,000\text{ QPS}$.
- **Storage Profile:** Order book fits entirely in L3 CPU cache / RAM ($< 10\text{ MB}$ per symbol).
- **Object Sizes:** Pre-allocated ring buffer entries of 64 bytes per order.
