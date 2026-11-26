# Inventory Management — Code Walkthrough

## v1-basic

- `Warehouse` owns stock and alert data structures.
- `InventoryManager` routes operations by warehouse ID.
- All operations are synchronous and single-thread focused.

## v2-extended

- Adds reservation-oriented helpers and richer validation paths.
- Keeps API backward-compatible with v1.
- Introduces better reporting helpers for availability snapshots.

## v3-optimized

- Adds lock-based thread safety to stock mutation paths.
- Implements deterministic lock ordering for transfers.
- Preserves invariants under concurrent access.

## Key Read Paths

1. `check_availability`: query all warehouses for a product.
2. `get_stock`: fast lookup from warehouse map.

## Key Write Paths

1. `add_stock`: increment then alert-check.
2. `remove_stock`: invariant check then decrement.
3. `transfer_stock`: source check + two-sided mutation.

## Test Focus

- No negative stock under normal operations.
- Transfer rejects insufficient stock.
- Alert listeners are triggered below threshold.
- Concurrent mutation path keeps totals consistent (v3).
