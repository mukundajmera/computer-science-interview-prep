"""
Tests for Online Shopping Cart
"""

import unittest
import sys
import threading
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
HELPER_DIR = TEST_DIR.parents[2] / "test_helpers"
if str(HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(HELPER_DIR))

from imports import import_modules_from


SHOPPING_MODULES = ["shopping", "shopping_entities", "v1_basic_entities"]


def version_path(version: str) -> Path:
    return TEST_DIR.parent / version


def shopping_entities(version: str):
    return import_modules_from(
        version_path(version),
        ["shopping_entities"],
        purge_modules=SHOPPING_MODULES,
    )["shopping_entities"]


class TestV1BasicCart(unittest.TestCase):
    """Test V1 basic cart functionality."""
    
    def setUp(self):
        # Note: Tests import from the correct path set in sys.path
        pass
    
    def test_product_creation(self):
        """Test product creation."""
        v1 = shopping_entities("v1-basic")
        cat = v1.Category("C1", "Electronics")
        prod = v1.Product("P1", "Laptop", "A laptop", 999.99, cat, 2.0)

        self.assertEqual(prod.id, "P1")
        self.assertEqual(prod.name, "Laptop")
        self.assertEqual(prod.price, 999.99)
        self.assertEqual(prod.weight, 2.0)
    
    def test_cart_add_remove(self):
        """Test cart add and remove operations."""
        v1 = shopping_entities("v1-basic")
        
        cart = v1.Cart("CART-1", "user1")
        prod1 = v1.Product("P1", "Laptop", "A laptop", 999.99)
        prod2 = v1.Product("P2", "Phone", "A phone", 499.99)
        
        cart.add_item(prod1, 1)
        cart.add_item(prod2, 2)
        
        self.assertEqual(cart.get_total_items(), 3)
        self.assertEqual(cart.get_unique_products(), 2)
        
        cart.remove_item("P1")
        self.assertEqual(cart.get_total_items(), 2)
        self.assertEqual(cart.get_unique_products(), 1)
    
    def test_cart_subtotal(self):
        """Test cart subtotal calculation."""
        v1 = shopping_entities("v1-basic")
        
        cart = v1.Cart("CART-1", "user1")
        prod = v1.Product("P1", "Laptop", "A laptop", 100.00)
        
        cart.add_item(prod, 3)
        self.assertEqual(cart.get_subtotal(), 300.00)
    
    def test_inventory(self):
        """Test inventory operations."""
        v1 = shopping_entities("v1-basic")
        
        inv = v1.Inventory()
        inv.add_stock("P1", 10)
        
        self.assertEqual(inv.get_stock("P1"), 10)
        self.assertTrue(inv.check_stock("P1", 5))
        self.assertFalse(inv.check_stock("P1", 15))
        
        inv.deduct_stock("P1", 3)
        self.assertEqual(inv.get_stock("P1"), 7)


class TestV2ExtendedCart(unittest.TestCase):
    """Test V2 extended cart with coupons."""
    
    def test_coupon_percentage_discount(self):
        """Test percentage coupon discount."""
        v2 = shopping_entities("v2-extended")
        from datetime import datetime, timedelta
        
        coupon = v2.Coupon(
            code="SAVE20",
            discount_type=v2.DiscountType.PERCENTAGE,
            value=20,
            min_amount=50,
            max_discount=100,
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        # 20% of 200 = 40
        discount = coupon.calculate_discount(200)
        self.assertEqual(discount, 40.0)
    
    def test_coupon_fixed_discount(self):
        """Test fixed amount coupon discount."""
        v2 = shopping_entities("v2-extended")
        from datetime import datetime, timedelta
        
        coupon = v2.Coupon(
            code="FLAT30",
            discount_type=v2.DiscountType.FIXED_AMOUNT,
            value=30,
            min_amount=100,
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        discount = coupon.calculate_discount(150)
        self.assertEqual(discount, 30.0)
    
    def test_coupon_min_amount(self):
        """Test coupon minimum amount requirement."""
        v2 = shopping_entities("v2-extended")
        from datetime import datetime, timedelta
        
        coupon = v2.Coupon(
            code="SAVE10",
            discount_type=v2.DiscountType.PERCENTAGE,
            value=10,
            min_amount=100,
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        # Below minimum, no discount
        discount = coupon.calculate_discount(50)
        self.assertEqual(discount, 0)
    
    def test_pricing_engine(self):
        """Test pricing engine calculations."""
        v2 = shopping_entities("v2-extended")
        
        cart = v2.Cart("CART-1", "user1")
        prod = v2.Product("P1", "Laptop", 1000.00, weight=2.0)
        cart.add_item(prod, 1)
        
        engine = v2.PricingEngine(tax_rate=0.1, shipping_per_kg=5.0, free_shipping_threshold=500)
        summary = engine.calculate(cart, None)
        
        self.assertEqual(summary.subtotal, 1000.00)
        self.assertEqual(summary.tax, 100.00)  # 10% of 1000
        self.assertEqual(summary.shipping, 0)  # Free shipping over 500
        self.assertEqual(summary.total, 1100.00)


class TestV3OptimizedCart(unittest.TestCase):
    """Test V3 thread-safe cart with reservations."""
    
    def test_inventory_reservation(self):
        """Test inventory reservation system."""
        v3 = shopping_entities("v3-optimized")
        
        inv = v3.Inventory()
        inv.add_stock("P1", 10)
        
        # Reserve 3 for user1
        self.assertTrue(inv.reserve("P1", 3, "user1"))
        self.assertEqual(inv.get_available("P1"), 7)
        
        # Reserve 5 for user2
        self.assertTrue(inv.reserve("P1", 5, "user2"))
        self.assertEqual(inv.get_available("P1"), 2)
        
        # Try to reserve 3 more (should fail)
        self.assertFalse(inv.reserve("P1", 3, "user3"))
    
    def test_inventory_commit(self):
        """Test inventory commit after reservation."""
        v3 = shopping_entities("v3-optimized")
        
        inv = v3.Inventory()
        inv.add_stock("P1", 10)
        
        inv.reserve("P1", 3, "user1")
        inv.commit("P1", 3, "user1")
        
        self.assertEqual(inv.get_stock("P1"), 7)
        self.assertEqual(inv.get_available("P1"), 7)
    
    def test_inventory_release(self):
        """Test inventory release."""
        v3 = shopping_entities("v3-optimized")
        
        inv = v3.Inventory()
        inv.add_stock("P1", 10)
        
        inv.reserve("P1", 5, "user1")
        self.assertEqual(inv.get_available("P1"), 5)
        
        inv.release("P1", 5, "user1")
        self.assertEqual(inv.get_available("P1"), 10)
    
    def test_concurrent_reservations(self):
        """Test concurrent inventory reservations."""
        v3 = shopping_entities("v3-optimized")
        
        inv = v3.Inventory()
        inv.add_stock("P1", 10)
        
        results = []
        lock = threading.Lock()
        
        def reserve(user_id: str, quantity: int):
            success = inv.reserve("P1", quantity, user_id)
            with lock:
                results.append((user_id, success))
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=reserve, args=(f"user{i}", 3))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        successful = sum(1 for _, success in results if success)
        # At most 3 users can reserve 3 items each (total 9 out of 10)
        self.assertLessEqual(successful, 3)
    
    def test_thread_safe_cart(self):
        """Test thread-safe cart operations."""
        v3 = shopping_entities("v3-optimized")
        
        cart = v3.Cart("CART-1", "user1")
        prod = v3.Product("P1", "Laptop", 999.99)
        
        def add_item():
            for _ in range(10):
                cart.add_item(prod, 1)
        
        threads = [threading.Thread(target=add_item) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have 50 items (5 threads x 10 adds)
        items = cart.get_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].quantity, 50)


class TestShoppingService(unittest.TestCase):
    """Test shopping service end-to-end."""
    
    def test_full_checkout_flow(self):
        """Test complete checkout flow."""
        v1 = shopping_entities("v1-basic")
        
        v1.ShoppingService.reset_instance()
        service = v1.ShoppingService()
        
        # Add products
        prod = v1.Product("P1", "Laptop", "A laptop", 999.99)
        service.add_product(prod, 10)
        
        # Create cart and add items
        cart = service.create_cart("user1")
        service.add_to_cart(cart.id, "P1", 2)
        
        self.assertEqual(cart.get_subtotal(), 1999.98)
        
        # Checkout
        result = service.checkout(cart.id)
        self.assertTrue(result)
        
        # Cart should be empty
        self.assertTrue(cart.is_empty())
        
        # Stock should be reduced
        self.assertEqual(service.inventory.get_stock("P1"), 8)


if __name__ == "__main__":
    unittest.main()
