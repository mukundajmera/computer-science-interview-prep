# Quick Commerce Delivery — Model Answer (Time-Boxed)

Say: "I will design around inventory freshness, dispatch latency, and delivery promise accuracy, because a quick-commerce system fails when it accepts orders it cannot fulfill on time."

## 0-5 min: Requirements

- Confirm scope: location-based availability and order placement.
- Separate strong consistency needs (order path) from read freshness needs.

## 5-10 min: Estimates

- Availability QPS, order QPS, and read-heavy ratio.
- Regional hotspot assumptions and cache sizing implications.

## 10-15 min: API + Entities

- Availability endpoint plus idempotent order create endpoint.
- Entities: center, inventory, order, order line.

## 15-30 min: Architecture

- Gateway + geo service + availability service + reservation/order service.
- Cache-first read path and transactional/OCC write path.
- Async event publication for downstream systems.

## 30-40 min: Deep Dives

1. Inventory decrement correctness under contention.
2. Cache invalidation and bounded staleness strategy.
3. Regional failover and degraded mode behavior.

## 40-45 min: Trade-Off Wrap

- Why read path allows bounded staleness.
- Why order path must stay strongly correct.
- Evolution path to scheduled deliveries and substitution intelligence.
