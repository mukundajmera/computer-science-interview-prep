# Brokerage Platform — Interview Approach

## 1. Lock Scope First

- Confirm this is a brokerage interface, not an exchange matching engine.
- Prioritize quote display and order create/cancel lifecycle.
- Explicitly separate in-scope correctness from below-the-line wealth features.

## 2. Quantify Load and Burst Shape

- Estimate quote fanout subscribers during market open.
- Estimate order mutation QPS and retry patterns.
- Use numbers to justify split between read-fanout and command paths.

## 3. Define Core Entities and APIs

- Entities: `Order`, `OrderEvent`, `Quote`, `Execution`.
- APIs: submit order, cancel order, fetch order status, stream quote updates.
- Declare idempotency key and conflict/error model early.

## 4. Draw High-Level Architecture

- Ingestion/fanout pipeline for quotes.
- Durable command pipeline for orders.
- Exchange adapter boundary and reconciliation worker.

## 5. Deep Dives

1. Order-state correctness across partial failures.
2. Market-data fanout scalability and backpressure.
3. Reconciliation loop for out-of-sync external acknowledgements.

## 6. Wrap-Up

- Restate consistency guarantees for order path.
- Mention chosen trade-offs (latency vs reliability) and revisit triggers.
