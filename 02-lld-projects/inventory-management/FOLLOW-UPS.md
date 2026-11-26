# Inventory Management — Follow-Up Questions

## 1. How would you prevent duplicate mutation requests?
Use idempotency keys stored per warehouse mutation window.

## 2. How would you add reservation TTL?
Create reservation records with expiry and periodic cleanup/release.

## 3. How would you scale to multi-region warehouses?
Partition ownership by warehouse region and use asynchronous replication.

## 4. How would you support auditability?
Append immutable stock-mutation events and derive current state.

## 5. How would you avoid alert storms?
Add threshold-crossing semantics and cooldown windows per product.
