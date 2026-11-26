import unittest
import sys
import os
import threading
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from _testutil import load_module

v3 = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed', 'distributed_ecommerce_service.py')), 'distributed_ecommerce_service')

class MockReplicationService(v3.InventoryReplicationService):
    def schedule_transfer(self, product_id, to_region, quantity):
        pass

class TestV3EcommerceService(unittest.TestCase):
    def setUp(self):
        self.router = v3.GeoRouter()
        self.replication_service = MockReplicationService()
        
        self.east_inv = v3.RegionalInventory("us-east")
        self.east_inv.inventory["p1"] = v3.InventoryRecord("p1", 10)
        
        self.west_inv = v3.RegionalInventory("us-west")
        self.west_inv.inventory["p1"] = v3.InventoryRecord("p1", 5)
        
        regional_inventories = {
            "us-east": self.east_inv,
            "us-west": self.west_inv
        }
        
        self.coordinator = v3.GlobalInventoryCoordinator(
            regional_inventories, self.replication_service
        )

    def test_routing_local(self):
        # lng = -70 -> us-east
        region = self.router.get_optimal_region(40.0, -70.0)
        self.assertEqual(region, "us-east")

    def test_routing_remote(self):
        # lng = -120 -> us-west
        region = self.router.get_optimal_region(40.0, -120.0)
        self.assertEqual(region, "us-west")

    def test_local_inventory_reservation_success(self):
        items = [v3.OrderItem(product_id="p1", quantity=5)]
        res = self.coordinator.reserve_global("r1", items, "us-east")
        self.assertEqual(res.region, "us-east")
        self.assertEqual(self.east_inv.get_available_quantity("p1"), 5)

    def test_global_inventory_reservation_success_cross_region(self):
        # us-east wants 8, but us-west has 5, us-east has 10
        # Should fulfill from us-east successfully.
        items = [v3.OrderItem(product_id="p1", quantity=8)]
        res = self.coordinator.reserve_global("r1", items, "us-west")
        self.assertEqual(res.region, "us-east")
        self.assertEqual(self.east_inv.get_available_quantity("p1"), 2) 

    def test_global_inventory_failure_never_negative(self):
        items = [v3.OrderItem(product_id="p1", quantity=15)]
        with self.assertRaises(v3.InsufficientGlobalInventoryException):
            self.coordinator.reserve_global("r1", items, "us-east")
        self.assertEqual(self.east_inv.get_available_quantity("p1"), 10) 
        self.assertEqual(self.west_inv.get_available_quantity("p1"), 5) 

    def test_compensation_restores_inventory(self):
        items = [v3.OrderItem(product_id="p1", quantity=5)]
        res = self.coordinator.reserve_global("r1", items, "us-east")
        self.assertEqual(self.east_inv.get_available_quantity("p1"), 5)
        
        self.east_inv.release("r1")
        self.assertEqual(self.east_inv.get_available_quantity("p1"), 10)

    def test_concurrent_reservations_prevent_negative(self):
        items = [v3.OrderItem(product_id="p1", quantity=6)]
        
        def reserve(rid):
            try:
                return self.coordinator.reserve_global(rid, items, "us-east")
            except v3.InsufficientGlobalInventoryException:
                return None
            
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(reserve, "r1")
            f2 = executor.submit(reserve, "r2")
            
            res1 = f1.result()
            res2 = f2.result()
            
        # One of them should fail, but neither should have negative inventory
        self.assertTrue(res1 is None or res2 is None)
        self.assertEqual(self.east_inv.get_available_quantity("p1"), 4) 

if __name__ == '__main__':
    unittest.main()
