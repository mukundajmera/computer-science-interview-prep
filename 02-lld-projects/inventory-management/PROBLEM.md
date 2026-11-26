# Inventory Management System

## Problem Statement

Design an inventory management system that tracks stock for products across multiple warehouses, supports stock mutations and transfers, and emits low-stock alerts through pluggable listeners.

---

## Functional Requirements

1. **Multi-warehouse inventory**: Track stock counts per `(warehouse_id, product_id)`.
2. **Add stock**: Increase quantity for inbound inventory.
3. **Remove stock**: Decrease quantity for fulfillment; reject insufficient stock.
4. **Transfer stock**: Move stock between warehouses atomically.
5. **Availability check**: Return warehouses that can fulfill a requested quantity.
6. **Low-stock alerts**: Register threshold-based callbacks per product per warehouse.
7. **Invariant enforcement**: Never allow negative stock.

---

## Non-Functional Requirements

1. **Correctness**: Preserve no-negative-stock invariant under all operations.
2. **Thread safety (v3)**: Handle concurrent mutations safely.
3. **Performance**: O(1) average warehouse-product lookup.
4. **Extensibility**: Add alert channels and reservation semantics without rewriting core entities.

---

## Requirements and Constraints

- Warehouses are preconfigured for the interview baseline.
- Products are external identifiers; catalog ownership is out of scope.
- Persistence and distributed coordination are out of scope for v1-v3.
- Alerting is callback-based (`AlertListener`); delivery mechanism is external.
- Transfers validate source stock before applying destination updates.

---

## Clarifying Questions to Ask

1. Should stock be tracked as integers only, or support fractional units?
2. Are transfers required to be all-or-nothing in a single process?
3. Do low-stock alerts fire on every mutation below threshold or only on threshold crossing?
4. Do we need reservation/hold semantics, or immediate decrement only?
5. Is the design single-process in-memory or distributed?

---

## Core Entities

| Entity | Responsibility |
|--------|---------------|
| `InventoryManager` | Public API and cross-warehouse orchestration |
| `Warehouse` | Per-warehouse stock map and alert configuration |
| `AlertConfig` | Threshold + listener binding |
| `AlertListener` | Callback contract for low-stock notifications |

---

## Scoring Rubric

See [RUBRIC.md](./RUBRIC.md).

## Common Pitfalls

See [PITFALLS.md](./PITFALLS.md).

## Follow-up Questions

See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

---

## Variants and Extensions

1. Add stock reservations with TTL and release flow.
2. Add idempotency keys for mutation requests.
3. Add event stream publishing for downstream analytics.
4. Add warehouse-level permissions and audit logs.

---

## Version Roadmap

| Version | Focus |
|---------|-------|
| v1-basic | Core entities and stock mutation APIs |
| v2-extended | Reservation-like extensions and richer validation/reporting |
| v3-optimized | Thread-safe mutations and contention-safe transfer path |
