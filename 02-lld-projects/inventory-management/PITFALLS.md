# Pitfalls in Inventory Management

This document details critical pitfalls in designing and implementing an inventory management system, shifting from conceptual issues to implementation-grounded explicit reference contracts and failure boundaries.

## 1. Concurrency Control: The Lost Update Problem & Resource Ownership

The most critical and devastating pitfall in inventory management occurs when multiple concurrent transactions attempt to modify the same Stock Keeping Unit (SKU) simultaneously without proper isolation. A naive read-modify-write cycle leads to lost updates and overselling. 

### Atomic Resource Ownership and Locks
Inventory systems must enforce atomic resource ownership. When scanning for available resources using explicit locks, implementations must use explicit **blocking locks** rather than non-blocking equivalents (e.g. `tryLock()`). Non-blocking approaches spuriously skip inventory due to momentary concurrent reads, resulting in falsely reported stockouts even when capacity exists.

### Contract Validation

- **Normal use-case:** Positive stock additions increase total capacity. Removals strictly decrease capacity if sufficient stock is present, locking correctly.
- **Empty/invalid input:** Requesting zero or negative operations throws `ValueError` or `IllegalArgumentException`.
- **Capacity boundary:** Attempting to remove more stock than available safely rejects the operation, returning `false` without locking a negative state.
- **Failure rollback:** In transfers between warehouses, if the source warehouse has sufficient stock but the destination addition fails (e.g., due to an unexpected system error), the deducted stock must be restored or the transaction entirely rolled back.

**Java (v3-optimized)**
```java
// Uses blocking locks (lock.lock()) instead of tryLock()
public boolean removeStock(String productId, int quantity) {
    if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive");
    lock.lock();
    try {
        int current = stock.getOrDefault(productId, 0);
        if (current < quantity) return false; // Capacity boundary
        stock.put(productId, current - quantity);
        notifyIfLow(productId);
        return true;
    } finally {
        lock.unlock();
    }
}
```

**Python (v3-optimized)**
```python
# Uses blocking locks (with self._lock) instead of non-blocking acquisitions
def remove_stock(self, product_id: str, quantity: int) -> bool:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    with self._lock:
        current = self._stock.get(product_id, 0)
        if current < quantity:
            return False  # Capacity boundary
        self._stock[product_id] = current - quantity
        self._notify_if_low(product_id)
        return True
```

## 2. Ignoring Idempotency on Deduction APIs

Network unreliability dictates that HTTP requests will occasionally time out or connections will drop after the server processes the request but before the client receives the response.

### Duplicate Operations
If the checkout API is not idempotent, the client's automated retry logic will send the deduction request a second time. The server will process it again, deducting the inventory twice. Every state-mutating API must require a unique, client-generated `Idempotency-Key`.

- **Duplicate operation:** A repeated idempotency key with the exact same payload returns the cached success intent (or error). A changed payload is rejected without creating a second deduction.

## 3. Financial and Quantity Ledgers

Financial ledgers must use **integer-minor-unit balances** (e.g., `long` or `int` cents/units) to avoid floating-point errors. For standard inventory, fractional quantities should similarly be modeled as integer counts of the smallest divisable unit to prevent accumulation of drift across millions of transactions.

## 4. Poor Handling of Stock Reservations (Deadlocks)

To guarantee items are available during checkout, systems often reserve inventory temporarily (half-open dates for overlapping periods). 

If reservations are held indefinitely, abandoned carts will exhaust the available inventory. All reservations must have a strict Time-To-Live (TTL). Furthermore, to prevent classic deadlocks during multi-warehouse transfers or multi-item carts, the application must enforce strict global ordering (e.g., locking SKUs/Warehouses lexicographically).

### Transfer Failure Rollback (Saga Alternative)

- **One failure rollback:** In a `transferStock` method across warehouses, both source and destination locks must be acquired in a globally consistent order (sorted by warehouse ID) to prevent deadlocks. If the destination update were to throw an exception, the source deduction must be rolled back.

**Java (v3-optimized)**
```java
public boolean transferStock(String fromWarehouseId, String toWarehouseId, String productId, int quantity) {
    if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive");
    Warehouse source = getWarehouse(fromWarehouseId);
    Warehouse destination = getWarehouse(toWarehouseId);

    // Global ordering to prevent deadlock
    Warehouse first = source.getId().compareTo(destination.getId()) <= 0 ? source : destination;
    Warehouse second = first == source ? destination : source;

    first.getLock().lock();
    second.getLock().lock();
    try {
        if (!source.removeStockNoLock(productId, quantity)) return false;
        // If the destination fails (e.g. throws), source must be rolled back.
        // In this simple in-memory v3 implementation, addStockNoLock does not throw, 
        // ensuring atomic transfer.
        destination.addStockNoLock(productId, quantity);
        return true;
    } finally {
        second.getLock().unlock();
        first.getLock().unlock();
    }
}
```

**Python (v3-optimized)**
```python
def transfer_stock(
    self, from_warehouse_id: str, to_warehouse_id: str, product_id: str, quantity: int
) -> bool:
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    source = self._get_warehouse(from_warehouse_id)
    destination = self._get_warehouse(to_warehouse_id)

    # Global ordering to prevent deadlock
    first, second = sorted([source, destination], key=lambda w: w.id)
    with first._lock:
        with second._lock:
            if not source._remove_stock_nolock(product_id, quantity):
                return False
            # Atomic commit; rollback would be required if destination could fail.
            destination._add_stock_nolock(product_id, quantity)
            return True
```

## Public APIs and Version-Specific Feature Deltas

The inventory components are implemented across different iterations, with specific API contracts:
- `v1-basic`: Core entities, standard `add_stock` / `remove_stock` functionality without concurrency guarantees.
- `v2-extended`: Introduces `reserve_stock`, `availability_snapshot`, and `release_reservation`.
- `v3-optimized`: Implements pessimistic concurrency using explicit blocking locks (`threading.RLock()` / `ReentrantLock`), providing thread-safe mutations and contention-safe `transfer_stock`. 

### Testing Notes
Each assigned document describes actual supported versions. Focused tests target this exact version (`v3-optimized` or `v2-extended`) rather than silently importing `v1-basic`. Ensure testing executes the target specific directories directly, isolating their concurrency behaviors.
