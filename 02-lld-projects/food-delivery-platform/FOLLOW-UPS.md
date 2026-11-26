# Follow-Ups: Food Delivery Platform

## 1. Batching Orders
**Question**: How would you modify the system to allow a driver to pick up multiple orders from the same restaurant (or nearby restaurants) going to nearby destinations?
**Answer**: Evolve the `DispatchStrategy` to look for grouped orders. Introduce an `OrderBatch` or `Route` entity that a driver accepts instead of a single `Order`.

## 2. Handling Driver Rejections
**Question**: Drivers can reject an assignment. How do you handle this?
**Answer**: Implement an asynchronous workflow. When dispatched, the order enters a `DISPATCHED_PENDING_ACCEPT` sub-state. If a timeout occurs or the driver rejects, the dispatcher is re-triggered, excluding the rejected driver for that specific order.

## 3. High Concurrency During Promotions
**Question**: During a flash sale, thousands of users might add items to their carts and checkout simultaneously. How do you handle inventory and capacity?
**Answer**: Introduce a reservation pattern during the checkout phase. Use distributed locks or atomic counters for high-demand items or restaurant capacity limits.

## 4. (Optional Staff Follow-up) Distributed State and Re-dispatch
**Question**: If the driver's phone loses network connection during delivery, how does the system recover the state when the connection returns, or how does it re-dispatch if the driver is lost permanently?
**Answer**: Frame this as a distributed systems state ownership problem. The `Order` state (stored in a database) is the source of truth. If a driver misses a heartbeat (e.g., 3 minutes), the system moves the order to an `ORPHANED` or `NEEDS_REDISPATCH` state and re-triggers the `DispatchStrategy`, ensuring idempotency so the customer is not double-billed or duplicate orders dispatched.
