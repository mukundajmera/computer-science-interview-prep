# Quick Commerce Delivery - Approach

## 1. Lock Requirements Early

- Confirm core scope: availability query + order placement.
- Explicitly separate location availability from general catalog search.
- Clarify consistency expectations for reads versus inventory commits.

## 2. Capacity and Hotspot Framing

- Estimate read-heavy ratio and peak neighborhood hotspots.
- Validate cache strategy and regional partition boundaries.
- Confirm acceptable staleness budget for availability responses.

## 3. Entity and API First Pass

- Entities: `Item`, `InventoryUnit`, `FulfillmentCenter`, `Order`, `OrderLine`.
- APIs: one availability endpoint and one order endpoint to start.
- Keep payload focused; defer non-core fields unless asked.

## 4. Build Two Distinct Paths

### Availability Path

- Resolve nearby centers by geo service.
- Fetch inventory summaries from cache first.
- Return merged availability with pagination.

### Order Path

- Validate stock atomically.
- Reserve/decrement in transaction (or versioned OCC flow).
- Persist order and emit async events.

## 5. Deep Dives to Drive

1. Inventory correctness under contention.
2. Regional partitioning and failover behavior.
3. Cache invalidation and freshness strategy.

## 6. Wrap-Up

- Reconfirm strong correctness on order path.
- Explain why read path can tolerate bounded staleness.
- Describe evolution from simple regional deployment to multi-region scale.
