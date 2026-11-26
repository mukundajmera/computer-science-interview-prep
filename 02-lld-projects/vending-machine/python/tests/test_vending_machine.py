"""
Tests for Vending Machine System
"""
import unittest
import sys
import os
import threading

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))


class TestV1BasicVendingMachine(unittest.TestCase):
    """Tests for V1 Basic Vending Machine"""
    
    def test_coin_values(self):
        """Coin values should be correct"""
        from coin import Coin
        
        self.assertAlmostEqual(Coin.PENNY.value, 0.01, places=2)
        self.assertAlmostEqual(Coin.NICKEL.value, 0.05, places=2)
        self.assertAlmostEqual(Coin.DIME.value, 0.10, places=2)
        self.assertAlmostEqual(Coin.QUARTER.value, 0.25, places=2)
        self.assertAlmostEqual(Coin.DOLLAR.value, 1.00, places=2)
    
    def test_product_creation(self):
        """Product should be created with valid data"""
        from product import Product
        
        product = Product("A1", "Chips", 1.50)
        
        self.assertEqual(product.code, "A1")
        self.assertEqual(product.name, "Chips")
        self.assertAlmostEqual(product.price, 1.50, places=2)
    
    def test_product_invalid_data(self):
        """Product should raise exception for invalid data"""
        from product import Product
        
        with self.assertRaises(ValueError):
            Product(None, "Chips", 1.50)
        with self.assertRaises(ValueError):
            Product("A1", None, 1.50)
        with self.assertRaises(ValueError):
            Product("A1", "Chips", -1.0)
    
    def test_slot_dispense(self):
        """Slot should dispense product correctly"""
        from product import Product
        from slot import Slot
        
        product = Product("A1", "Chips", 1.50)
        slot = Slot("A1", product, 5, 10)
        
        self.assertEqual(slot.quantity, 5)
        self.assertFalse(slot.is_empty)
        
        dispensed = slot.dispense_one()
        
        self.assertIsNotNone(dispensed)
        self.assertEqual(dispensed.name, "Chips")
        self.assertEqual(slot.quantity, 4)
    
    def test_slot_empty(self):
        """Slot should return None when empty"""
        from product import Product
        from slot import Slot
        
        product = Product("A1", "Chips", 1.50)
        slot = Slot("A1", product, 0, 10)
        
        self.assertTrue(slot.is_empty)
        self.assertIsNone(slot.dispense_one())
    
    def test_slot_restock(self):
        """Slot restock should work correctly"""
        from product import Product
        from slot import Slot
        
        product = Product("A1", "Chips", 1.50)
        slot = Slot("A1", product, 5, 10)
        
        added = slot.restock(3)
        self.assertEqual(added, 3)
        self.assertEqual(slot.quantity, 8)
        
        added = slot.restock(10)
        self.assertEqual(added, 2)
        self.assertEqual(slot.quantity, 10)
        self.assertTrue(slot.is_full)
    
    def test_inventory_change(self):
        """Inventory should calculate change correctly"""
        from coin import Coin
        from inventory import Inventory
        
        inventory = Inventory()
        inventory.add_coins(Coin.QUARTER, 10)
        inventory.add_coins(Coin.DIME, 10)
        
        change = inventory.get_change(0.50)
        
        self.assertGreater(len(change), 0)
        total = sum(c.value for c in change)
        self.assertAlmostEqual(total, 0.50, places=2)
    
    def test_inventory_no_change(self):
        """Inventory should return empty list when change impossible"""
        from inventory import Inventory
        
        inventory = Inventory()
        change = inventory.get_change(0.50)
        
        self.assertEqual(len(change), 0)
    
    def test_machine_initial_state(self):
        """Machine should start in IDLE state"""
        from vending_machine import VendingMachine
        
        machine = VendingMachine()
        self.assertEqual(machine.current_state_name, "IDLE")
    
    def test_insert_money_state(self):
        """Inserting money should change state to HAS_MONEY"""
        from coin import Coin
        from vending_machine import VendingMachine
        
        machine = VendingMachine()
        machine.insert_money(Coin.DOLLAR)
        
        self.assertEqual(machine.current_state_name, "HAS_MONEY")
        self.assertAlmostEqual(machine.balance, 1.00, places=2)
    
    def test_complete_purchase(self):
        """Complete purchase workflow should work"""
        from coin import Coin
        from product import Product
        from slot import Slot
        from vending_machine import VendingMachine
        
        machine = VendingMachine()
        product = Product("A1", "Chips", 1.50)
        slot = Slot("A1", product, 5, 10)
        machine.inventory.add_slot(slot)
        machine.inventory.add_coins(Coin.QUARTER, 20)
        
        machine.insert_money(Coin.DOLLAR)
        machine.insert_money(Coin.QUARTER)
        machine.insert_money(Coin.QUARTER)
        machine.select_product("A1")
        dispensed = machine.dispense()
        
        self.assertIsNotNone(dispensed)
        self.assertEqual(dispensed.name, "Chips")
        self.assertEqual(slot.quantity, 4)
        self.assertEqual(machine.current_state_name, "IDLE")
    
    def test_cancel_transaction(self):
        """Cancel transaction should return coins"""
        from coin import Coin
        from vending_machine import VendingMachine
        
        machine = VendingMachine()
        machine.insert_money(Coin.DOLLAR)
        machine.insert_money(Coin.QUARTER)
        
        returned = machine.cancel_transaction()
        
        self.assertEqual(len(returned), 2)
        self.assertEqual(machine.current_state_name, "IDLE")
        self.assertAlmostEqual(machine.balance, 0.0, places=2)
    
    def test_insufficient_funds(self):
        """Insufficient funds should prevent selection"""
        from coin import Coin
        from product import Product
        from slot import Slot
        from vending_machine import VendingMachine
        
        machine = VendingMachine()
        product = Product("A1", "Chips", 1.50)
        slot = Slot("A1", product, 5, 10)
        machine.inventory.add_slot(slot)
        
        machine.insert_money(Coin.QUARTER)
        machine.select_product("A1")
        
        self.assertEqual(machine.current_state_name, "HAS_MONEY")
        self.assertIsNone(machine.selected_slot)


class TestV3ConcurrentVendingMachine(unittest.TestCase):
    """Tests for V3 Concurrent Vending Machine"""
    
    def setUp(self):
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        import importlib
        # Clear cached modules so importlib loads from v3-optimized
        for mod_name in ['vending_machine', 'vending_machine_state', 'inventory',
                         'currency', 'product', 'slot', 'coin']:
            sys.modules.pop(mod_name, None)
        self.currency = importlib.import_module('currency')
        self.product = importlib.import_module('product')
        self.vending_machine = importlib.import_module('vending_machine')
    
    def tearDown(self):
        # Clear v3 modules so subsequent tests reimport from v1 paths
        for mod_name in ['vending_machine', 'vending_machine_state', 'inventory',
                         'currency', 'product', 'slot', 'coin']:
            sys.modules.pop(mod_name, None)
    
    def test_concurrent_purchases(self):
        """Multiple threads should be able to purchase concurrently"""
        VendingMachine = self.vending_machine.VendingMachine
        Coin = self.currency.Coin
        ProductCategory = self.currency.ProductCategory
        
        machine = VendingMachine("TEST-001")
        machine.add_slot("A1", "Chips", 1.50, ProductCategory.SNACK, 20, 25)
        machine.add_coins_to_inventory(Coin.QUARTER, 100)
        
        successful = [0]
        lock = threading.Lock()
        
        def purchase_worker(worker_id):
            machine.insert_money(Coin.DOLLAR)
            machine.insert_money(Coin.DOLLAR)
            machine.select_product("A1")
            product = machine.dispense()
            if product:
                with lock:
                    successful[0] += 1
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=purchase_worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All 10 should succeed since we have 20 items
        self.assertEqual(successful[0], 10)


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow"""
    
    def test_full_workflow(self):
        """Test complete vending machine workflow"""
        from coin import Coin
        from product import Product
        from slot import Slot
        from vending_machine import VendingMachine
        
        machine = VendingMachine()
        
        # Setup
        chips = Product("A1", "Chips", 1.50)
        water = Product("B1", "Water", 1.00)
        machine.inventory.add_slot(Slot("A1", chips, 5, 10))
        machine.inventory.add_slot(Slot("B1", water, 5, 10))
        machine.inventory.add_coins(Coin.QUARTER, 20)
        machine.inventory.add_coins(Coin.DIME, 20)
        
        # First purchase
        machine.insert_money(Coin.DOLLAR)
        machine.insert_money(Coin.DOLLAR)
        machine.select_product("A1")
        p1 = machine.dispense()
        self.assertIsNotNone(p1)
        self.assertEqual(p1.name, "Chips")
        
        # Second purchase
        machine.insert_money(Coin.DOLLAR)
        machine.select_product("B1")
        p2 = machine.dispense()
        self.assertIsNotNone(p2)
        self.assertEqual(p2.name, "Water")
        
        # Cancel
        machine.insert_money(Coin.DOLLAR)
        returned = machine.cancel_transaction()
        self.assertEqual(len(returned), 1)


if __name__ == "__main__":
    unittest.main()
