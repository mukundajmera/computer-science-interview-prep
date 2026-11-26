"""Inventory Management - V3 Optimized (thread-safe)."""

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
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            self._stock[product_id] = self._stock.get(product_id, 0) + quantity
            self._notify_if_low(product_id)
            return self._stock[product_id]

    def remove_stock(self, product_id: str, quantity: int) -> bool:
        with self._lock:
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            current = self._stock.get(product_id, 0)
            if current < quantity:
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
            self._notify_if_low(product_id)

    def _remove_stock_nolock(self, product_id: str, quantity: int) -> bool:
        current = self._stock.get(product_id, 0)
        if current < quantity:
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
            return self._warehouses[warehouse_id]

    def add_stock(self, warehouse_id: str, product_id: str, quantity: int) -> int:
        return self._get_warehouse(warehouse_id).add_stock(product_id, quantity)

    def remove_stock(self, warehouse_id: str, product_id: str, quantity: int) -> bool:
        return self._get_warehouse(warehouse_id).remove_stock(product_id, quantity)

    def transfer_stock(
        self, from_warehouse_id: str, to_warehouse_id: str, product_id: str, quantity: int
    ) -> bool:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        source = self._get_warehouse(from_warehouse_id)
        destination = self._get_warehouse(to_warehouse_id)

        first, second = sorted([source, destination], key=lambda w: w.id)
        with first._lock:
            with second._lock:
                if not source._remove_stock_nolock(product_id, quantity):
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
        return result

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
            raise ValueError(f"Unknown warehouse: {warehouse_id}")
        return warehouse
