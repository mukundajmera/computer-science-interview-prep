# Inventory Management — Interview Approach

## 1) Scope the problem first

Start by locking scope in 2 minutes:

- Stock unit model (integer counts)
- Warehouse model (static vs dynamic)
- Transfer guarantees (all-or-nothing)
- Alert semantics (threshold crossing behavior)
- Out-of-scope systems (catalog, orders, persistence)

## 2) Identify invariants

State invariants early to guide design:

1. Stock cannot be negative.
2. Transfer must not partially apply.
3. Alert evaluation happens after successful mutation.

## 3) Model the minimum useful entities

- `InventoryManager` as entry point
- `Warehouse` as stock owner
- `AlertConfig` and `AlertListener` for pluggable notifications

Avoid over-modeling product catalog, order lifecycle, or notification transports.

## 4) Define the core APIs

- `add_stock(warehouse_id, product_id, quantity)`
- `remove_stock(warehouse_id, product_id, quantity)`
- `transfer_stock(from, to, product_id, quantity)`
- `check_availability(product_id, required_quantity)`
- `register_low_stock_alert(warehouse_id, product_id, threshold, listener)`

## 5) Add concurrency strategy (v3)

- Use per-warehouse locks for basic safety.
- For transfer, lock two warehouses in deterministic order to avoid deadlock.
- Keep mutation + alert evaluation in the same critical section.

## 6) Talk through complexity and tradeoffs

- O(1) expected stock updates/lookups per warehouse-product key.
- `check_availability` is O(number_of_warehouses).
- Coarse locks are simpler; fine-grained locks scale better but are harder to reason about.

## 7) Close with extensions

- Reservation holds with TTL
- Event sourcing/audit trail
- Distributed inventory ownership and conflict handling
