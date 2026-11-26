import unittest
import sys
import os

# Add parent dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from _testutil import load_module

v1 = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic', 'ecommerce_service.py')), 'ecommerce_service')

class InMemoryInventoryRepository(v1.InventoryRepository):
    def __init__(self):
        self.inventories = {}
        self.reservations = {}
        
    def find_by_product_id(self, product_id: str) -> v1.Inventory:
        return self.inventories.get(product_id)
        
    def save(self, inventory: v1.Inventory) -> None:
        self.inventories[inventory.product_id] = inventory
        
    def find_reservation(self, reservation_id: str) -> v1.InventoryReservation:
        return self.reservations.get(reservation_id)

    def save_reservation(self, reservation: v1.InventoryReservation) -> None:
        self.reservations[reservation.reservation_id] = reservation


class TestV1EcommerceService(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryInventoryRepository()
        self.repo.save(v1.Inventory(product_id="p1", available_quantity=10, reserved_quantity=0))
        self.service = v1.InventoryService(self.repo)

    def test_check_availability_success(self):
        self.assertTrue(self.service.check_availability("p1", 5))

    def test_check_availability_insufficient(self):
        self.assertFalse(self.service.check_availability("p1", 15))

    def test_reserve_inventory_success(self):
        reservation = self.service.reserve("r1", [v1.OrderItem(product_id="p1", quantity=5, unit_price=10.0)])
        self.assertEqual(reservation.status, v1.ReservationStatus.ACTIVE)
        inv = self.repo.find_by_product_id("p1")
        self.assertEqual(inv.available_quantity, 5)
        self.assertEqual(inv.reserved_quantity, 5)
        self.repo.save_reservation(reservation)

    def test_reserve_inventory_failure_never_negative(self):
        with self.assertRaises(v1.InsufficientInventoryException):
            self.service.reserve("r2", [v1.OrderItem(product_id="p1", quantity=15, unit_price=10.0)])
        inv = self.repo.find_by_product_id("p1")
        self.assertEqual(inv.available_quantity, 10) # Unchanged
        self.assertEqual(inv.reserved_quantity, 0)
        
    def test_commit_reservation_success(self):
        reservation = self.service.reserve("r3", [v1.OrderItem(product_id="p1", quantity=2, unit_price=10.0)])
        self.repo.save_reservation(reservation)
        self.service.commit("r3")
        inv = self.repo.find_by_product_id("p1")
        self.assertEqual(inv.available_quantity, 8)
        self.assertEqual(inv.reserved_quantity, 0)
        r = self.repo.find_reservation("r3")
        self.assertEqual(r.status, v1.ReservationStatus.COMMITTED)

    def test_cancel_reservation_success(self):
        reservation = self.service.reserve("r4", [v1.OrderItem(product_id="p1", quantity=3, unit_price=10.0)])
        self.repo.save_reservation(reservation)
        self.service.release("r4")
        inv = self.repo.find_by_product_id("p1")
        self.assertEqual(inv.available_quantity, 10)
        self.assertEqual(inv.reserved_quantity, 0)
        r = self.repo.find_reservation("r4")
        self.assertEqual(r.status, v1.ReservationStatus.RELEASED)

if __name__ == '__main__':
    unittest.main()
