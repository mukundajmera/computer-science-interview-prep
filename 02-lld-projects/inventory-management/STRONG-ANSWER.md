# Canonical Interview Answer: Inventory Management System

This document outlines a strong candidate response for the Inventory Management LLD problem, focusing on the `v3-optimized` version, which introduces thread safety and concurrent mutations.


---

## Phase 6 — Tests and Verification (v3-optimized)

Tests should specifically target the `v3-optimized` functionality rather than importing earlier versions.

### Java
```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class InventoryManagementTest {
    @Test
    void basicStockMutationAndTransfer() {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("W1");
        manager.addWarehouse("W2");

        manager.addStock("W1", "SKU", 10);
        assertTrue(manager.removeStock("W1", "SKU", 3));
        assertTrue(manager.transferStock("W1", "W2", "SKU", 4));

        assertEquals(2, manager.checkAvailability("SKU", 3).size());
    }

    @Test
    void rejectsOverRemoval() {
        InventoryManager manager = new InventoryManager();
        manager.addWarehouse("W1");
        manager.addStock("W1", "SKU", 2);

        assertFalse(manager.removeStock("W1", "SKU", 5));
    }
}
```

### Python
```python
import threading
import unittest
from inventory import InventoryManager

class TestV3Optimized(unittest.TestCase):
    def test_concurrent_no_negative(self):
        manager = InventoryManager()
        manager.add_warehouse("W1")
        manager.add_stock("W1", "PX", 100)
        success_count = 0
        lock = threading.Lock()

        def worker():
            nonlocal success_count
            if manager.remove_stock("W1", "PX", 10):
                with lock:
                    success_count += 1

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=2)

        self.assertEqual(success_count, 10)
        self.assertEqual(manager.check_availability("PX", 1), [])

    def test_transfer(self):
        manager = InventoryManager()
        manager.add_warehouse("A")
        manager.add_warehouse("B")
        manager.add_stock("A", "P", 9)

        self.assertTrue(manager.transfer_stock("A", "B", "P", 4))
        self.assertEqual(manager.check_availability("P", 5), ["A"])
        self.assertEqual(manager.check_availability("P", 4), ["A", "B"])
```

---

## Phase 1 — Requirements Clarification

### Functional
1. **Multi-warehouse inventory**: Track stock counts per `(warehouse_id, product_id)`.
2. **Add stock**: Increase quantity for inbound inventory.
3. **Remove stock**: Decrease quantity for fulfillment; explicitly reject insufficient stock (never allow negative inventory).
4. **Transfer stock**: Move stock between warehouses atomically.
5. **Availability check**: Return warehouses that can fulfill a requested quantity.
6. **Low-stock alerts**: Register threshold-based callbacks via an `AlertListener` per product and warehouse.

### Non-Functional
- **Correctness**: Preserve the no-negative-stock invariant strictly.
- **Thread Safety**: Safely handle concurrent mutations across different threads (`v3-optimized`).
- **Performance**: Ensure O(1) average lookup for warehouse-product stock.
- **Extensibility**: Support pluggable alerts without rewriting core logic.

---

## Phase 2 — Core Entities

| Entity | Responsibility |
|---|---|
| `InventoryManager` | Public API orchestration, manages the map of Warehouses, handles cross-warehouse transfers. |
| `Warehouse` | Manages localized stock counts, locks, and alert configurations for a specific warehouse. |
| `AlertConfig` | Binds a threshold to an `AlertListener`. |
| `AlertListener` | Interface/Protocol for receiving low-stock notifications. |

---

## Phase 3 — API Contract and Code Walkthrough

We focus on the `v3-optimized` design using the standard library.

### Normal Use-Case & Invariant Preservation

Stock can be added or removed. For removals, if the quantity requested exceeds available stock, the operation fails (returning `false` in Java/Python), preserving the non-negative invariant.

### Concurrent Transfers & Failure Rollback (Deadlock Prevention)

Transferring stock requires modifying two distinct `Warehouse` entities atomically. To prevent deadlock during concurrent, overlapping transfers, locks must be acquired in a deterministic order (e.g., sorting by Warehouse ID). If the source warehouse lacks sufficient stock, the operation rolls back (fails cleanly) without modifying the destination or holding locks indefinitely.

---

## Phase 4 — Version-Specific Feature Deltas (v3-optimized)

### Java 11+ (Standard Library)
```java
import java.util.*;
import java.util.concurrent.locks.ReentrantLock;

interface AlertListener {
    void onLowStock(String warehouseId, String productId, int currentQty);
}

class AlertConfig {
    private final int threshold;
    private final AlertListener listener;
    public AlertConfig(int threshold, AlertListener listener) {
        this.threshold = threshold;
        this.listener = listener;
    }
    public int getThreshold() { return threshold; }
    public AlertListener getListener() { return listener; }
}

class Warehouse {
    private final String id;
    private final Map<String, Integer> stock = new HashMap<>();
    private final Map<String, List<AlertConfig>> alerts = new HashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public Warehouse(String id) { this.id = id; }
    public String getId() { return id; }
    public ReentrantLock getLock() { return lock; }

    public int addStock(String productId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive"); // Invalid input
        lock.lock();
        try {
            stock.put(productId, stock.getOrDefault(productId, 0) + quantity);
            notifyIfLow(productId);
            return stock.get(productId);
        } finally { lock.unlock(); }
    }

    public boolean removeStock(String productId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive"); // Invalid input
        lock.lock();
        try { return removeStockNoLock(productId, quantity); }
        finally { lock.unlock(); }
    }

    public boolean removeStockNoLock(String productId, int quantity) {
        int current = stock.getOrDefault(productId, 0);
        if (current < quantity) return false; // Capacity boundary / Failure rollback
        stock.put(productId, current - quantity);
        notifyIfLow(productId);
        return true;
    }
    
    public void addStockNoLock(String productId, int quantity) {
        stock.put(productId, stock.getOrDefault(productId, 0) + quantity);
        notifyIfLow(productId);
    }

    public int getStock(String productId) {
        lock.lock();
        try { return stock.getOrDefault(productId, 0); }
        finally { lock.unlock(); }
    }

    public void registerAlert(String productId, AlertConfig config) {
        lock.lock();
        try {
            alerts.computeIfAbsent(productId, k -> new ArrayList<>()).add(config);
            notifyIfLow(productId);
        } finally { lock.unlock(); }
    }

    private void notifyIfLow(String productId) {
        int qty = stock.getOrDefault(productId, 0);
        for (AlertConfig config : alerts.getOrDefault(productId, Collections.emptyList())) {
            if (qty < config.getThreshold()) {
                config.getListener().onLowStock(id, productId, qty);
            }
        }
    }
}

class InventoryManager {
    private final Map<String, Warehouse> warehouses = new java.util.concurrent.ConcurrentHashMap<>();

    public Warehouse addWarehouse(String warehouseId) {
        return warehouses.computeIfAbsent(warehouseId, Warehouse::new); // Duplicate operation idempotency
    }

    public int addStock(String warehouseId, String productId, int quantity) {
        return getWarehouse(warehouseId).addStock(productId, quantity);
    }

    public boolean removeStock(String warehouseId, String productId, int quantity) {
        return getWarehouse(warehouseId).removeStock(productId, quantity);
    }

    public boolean transferStock(String fromWarehouseId, String toWarehouseId, String productId, int quantity) {
        if (quantity <= 0) throw new IllegalArgumentException("Quantity must be positive"); // Invalid input
        Warehouse source = getWarehouse(fromWarehouseId);
        Warehouse destination = getWarehouse(toWarehouseId);

        // Deadlock prevention via consistent lock ordering
        Warehouse first = source.getId().compareTo(destination.getId()) <= 0 ? source : destination;
        Warehouse second = first == source ? destination : source;

        first.getLock().lock();
        second.getLock().lock();
        try {
            if (!source.removeStockNoLock(productId, quantity)) return false; // Failure rollback
            destination.addStockNoLock(productId, quantity);
            return true;
        } finally {
            second.getLock().unlock();
            first.getLock().unlock();
        }
    }

    public List<String> checkAvailability(String productId, int requiredQuantity) {
        if (requiredQuantity <= 0) throw new IllegalArgumentException("Required quantity must be positive"); // Invalid input
        List<String> available = new ArrayList<>();
        // Note: Iterator check might race slightly against mutations in high throughput,
        // but locking all warehouses globally destroys performance.
        for (Map.Entry<String, Warehouse> entry : warehouses.entrySet()) {
            if (entry.getValue().getStock(productId) >= requiredQuantity) {
                available.add(entry.getKey());
            }
        }
        Collections.sort(available);
        return available;
    }

    public void registerLowStockAlert(String warehouseId, String productId, int threshold, AlertListener listener) {
        getWarehouse(warehouseId).registerAlert(productId, new AlertConfig(threshold, listener));
    }

    private Warehouse getWarehouse(String warehouseId) {
        Warehouse warehouse = warehouses.get(warehouseId);
        if (warehouse == null) throw new IllegalArgumentException("Unknown warehouse: " + warehouseId); // Empty/invalid input handling
        return warehouse;
    }
}
```

### Python 3.8+ (Standard Library)
```python
from dataclasses import dataclass
from typing import Dict, List, Protocol
import threading


class AlertListener(Protocol):
    def on_low_stock(self, warehouse_id: str, product_id: str, current_qty: int) -> None:
        ...

@dataclass(frozen=True)
class AlertConfig:
    threshold: int
    listener: AlertListener

class Warehouse:
    def __init__(self, warehouse_id: str):
        self.id = warehouse_id
        self._stock: Dict[str, int] = {}
        self._alerts: Dict[str, List[AlertConfig]] = {}
        self._lock = threading.RLock()

    def add_stock(self, product_id: str, quantity: int) -> int:
        with self._lock:
            if quantity <= 0: # Invalid input
                raise ValueError("Quantity must be positive")
            self._stock[product_id] = self._stock.get(product_id, 0) + quantity
            self._notify_if_low(product_id)
            return self._stock[product_id]

    def remove_stock(self, product_id: str, quantity: int) -> bool:
        with self._lock:
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            current = self._stock.get(product_id, 0)
            if current < quantity: # Capacity boundary / failure rollback
                return False
            self._stock[product_id] = current - quantity
            self._notify_if_low(product_id)
            return True

    def get_stock(self, product_id: str) -> int:
        with self._lock:
            return self._stock.get(product_id, 0)

    def register_alert(self, product_id: str, config: AlertConfig) -> None:
        with self._lock:
            self._alerts.setdefault(product_id, []).append(config)
            self._notify_if_low(product_id) # Duplicate registration evaluates on current stock

    def _remove_stock_nolock(self, product_id: str, quantity: int) -> bool:
        current = self._stock.get(product_id, 0)
        if current < quantity: # Failure rollback
            return False
        self._stock[product_id] = current - quantity
        self._notify_if_low(product_id)
        return True

    def _add_stock_nolock(self, product_id: str, quantity: int) -> int:
        self._stock[product_id] = self._stock.get(product_id, 0) + quantity
        self._notify_if_low(product_id)
        return self._stock[product_id]

    def _notify_if_low(self, product_id: str) -> None:
        qty = self._stock.get(product_id, 0)
        for config in self._alerts.get(product_id, []):
            if qty < config.threshold:
                config.listener.on_low_stock(self.id, product_id, qty)

class InventoryManager:
    def __init__(self):
        self._warehouses: Dict[str, Warehouse] = {}
        self._manager_lock = threading.RLock()

    def add_warehouse(self, warehouse_id: str) -> Warehouse:
        with self._manager_lock:
            if warehouse_id not in self._warehouses:
                self._warehouses[warehouse_id] = Warehouse(warehouse_id)
            return self._warehouses[warehouse_id] # Duplicate operation idempotency

    def add_stock(self, warehouse_id: str, product_id: str, quantity: int) -> int:
        return self._get_warehouse(warehouse_id).add_stock(product_id, quantity)

    def remove_stock(self, warehouse_id: str, product_id: str, quantity: int) -> bool:
        return self._get_warehouse(warehouse_id).remove_stock(product_id, quantity)

    def transfer_stock(
        self, from_warehouse_id: str, to_warehouse_id: str, product_id: str, quantity: int
    ) -> bool:
        if quantity <= 0: # Invalid input
            raise ValueError("Quantity must be positive")
        source = self._get_warehouse(from_warehouse_id)
        destination = self._get_warehouse(to_warehouse_id)

        # Deadlock prevention: sort by ID
        first, second = sorted([source, destination], key=lambda w: w.id)
        with first._lock:
            with second._lock:
                if not source._remove_stock_nolock(product_id, quantity): # Rollback early
                    return False
                destination._add_stock_nolock(product_id, quantity)
                return True

    def check_availability(self, product_id: str, required_quantity: int) -> List[str]:
        if required_quantity <= 0:
            raise ValueError("Required quantity must be positive")
        with self._manager_lock:
            warehouse_items = list(self._warehouses.items())

        result: List[str] = []
        for warehouse_id, warehouse in warehouse_items:
            if warehouse.get_stock(product_id) >= required_quantity:
                result.append(warehouse_id)
        return sorted(result)

    def register_low_stock_alert(
        self, warehouse_id: str, product_id: str, threshold: int, listener: AlertListener
    ) -> None:
        self._get_warehouse(warehouse_id).register_alert(
            product_id, AlertConfig(threshold=threshold, listener=listener)
        )

    def _get_warehouse(self, warehouse_id: str) -> Warehouse:
        with self._manager_lock:
            warehouse = self._warehouses.get(warehouse_id)
        if warehouse is None:
            raise ValueError(f"Unknown warehouse: {warehouse_id}") # Invalid/empty input
        return warehouse
```

---

## Phase 5 — Follow-Up Hooks

1. **Distributed System**: Shifting from single-machine locks to a distributed lock manager (like Redis/Redlock or ZooKeeper), partitioning warehouses across shards.
2. **Persistent Store**: Using database transactions or optimistic concurrency control (CAS) over `ReentrantLock` for durability.
3. **Reservations vs Immediate Decrement**: Transitioning to a two-phase `reserve()` and `commit()`/`release()` flow to handle payment and fulfillment delays.

---

## What Strong Answers Emphasize

1. **Clear Domain Boundary:** Delineating `InventoryManager` (cross-warehouse logic) from `Warehouse` (local logic and locks).
2. **Locking Strategy:** Using a strict global ordering for acquiring multiple locks during the `transfer` operation to prevent `A -> B` and `B -> A` concurrent deadlocks.
3. **Event Notification decoupled via Interfaces:** The `AlertListener` allows different transports (Kafka, Email, SMS) without breaking the core system's SRP.
