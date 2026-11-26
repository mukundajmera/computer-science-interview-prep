"""Tests for Inventory Management versions."""

import importlib
import os
import sys
import threading
import unittest


def load_version(version_folder: str):
    base = os.path.dirname(__file__)
    version_path = os.path.join(base, "..", version_folder)
    if version_path in sys.path:
        sys.path.remove(version_path)
    sys.path.insert(0, version_path)
    if "inventory" in sys.modules:
        del sys.modules["inventory"]
    return importlib.import_module("inventory")


class RecordingListener:
    def __init__(self):
        self.events = []

    def on_low_stock(self, warehouse_id: str, product_id: str, current_qty: int) -> None:
        self.events.append((warehouse_id, product_id, current_qty))


class TestV1Basic(unittest.TestCase):
    def test_core_operations(self):
        inv = load_version("v1-basic")
        manager = inv.InventoryManager()
        manager.add_warehouse("W1")
        manager.add_warehouse("W2")

        manager.add_stock("W1", "P1", 10)
        self.assertTrue(manager.remove_stock("W1", "P1", 4))
        self.assertTrue(manager.transfer_stock("W1", "W2", "P1", 3))

        self.assertEqual(manager.check_availability("P1", 3), ["W1", "W2"])
        self.assertFalse(manager.remove_stock("W1", "P1", 10))

    def test_alerts(self):
        inv = load_version("v1-basic")
        manager = inv.InventoryManager()
        manager.add_warehouse("W1")
        manager.add_stock("W1", "P2", 5)

        listener = RecordingListener()
        manager.register_low_stock_alert("W1", "P2", 4, listener)
        manager.remove_stock("W1", "P2", 2)

        self.assertEqual(len(listener.events), 1)
        self.assertEqual(listener.events[0], ("W1", "P2", 3))


class TestV2Extended(unittest.TestCase):
    def test_reservation_flow(self):
        inv = load_version("v2-extended")
        manager = inv.InventoryManager()
        manager.add_warehouse("W1")
        manager.add_stock("W1", "P3", 12)

        reservation = manager.reserve_stock("W1", "P3", 5)
        self.assertIsNotNone(reservation)
        self.assertEqual(manager.availability_snapshot("P3")["W1"], 7)

        self.assertTrue(manager.release_reservation(reservation.reservation_id))
        self.assertEqual(manager.availability_snapshot("P3")["W1"], 12)


class TestV3Optimized(unittest.TestCase):
    def test_concurrent_no_negative(self):
        inv = load_version("v3-optimized")
        manager = inv.InventoryManager()
        manager.add_warehouse("W1")
        manager.add_stock("W1", "PX", 100)

        success_count = 0
        lock = threading.Lock()

        def worker():
            nonlocal success_count
            ok = manager.remove_stock("W1", "PX", 10)
            if ok:
                with lock:
                    success_count += 1

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=2)

        self.assertEqual(success_count, 10)
        self.assertEqual(manager.check_availability("PX", 1), [])

    def test_transfer(self):
        inv = load_version("v3-optimized")
        manager = inv.InventoryManager()
        manager.add_warehouse("A")
        manager.add_warehouse("B")
        manager.add_stock("A", "P", 9)

        self.assertTrue(manager.transfer_stock("A", "B", "P", 4))
        self.assertEqual(manager.check_availability("P", 5), ["A"])
        self.assertEqual(manager.check_availability("P", 4), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
