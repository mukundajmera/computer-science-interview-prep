import unittest
import sys
import os
import threading
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from _testutil import load_module

v2 = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled', 'scaled_ecommerce_service.py')), 'scaled_ecommerce_service')

class MockOrderRepo(v2.OrderRepository):
    def __init__(self):
        self.orders = {}
    def save(self, order):
        self.orders[order.order_id] = order
    def find_by_id(self, order_id):
        return self.orders.get(order_id)
    def update_status(self, order_id, status, reason=None):
        if order_id in self.orders:
            self.orders[order_id].status = status
    def update_saga_state(self, order_id, state):
        if order_id in self.orders:
            self.orders[order_id].saga_state = state

class MockCartService(v2.RedisCartService):
    def __init__(self):
        self.carts = {}
    def get_cart(self, user_id):
        return v2.Cart(user_id=user_id, items=[])
    def clear_cart(self, user_id):
        pass
    def save_cart(self, cart):
        pass

class MockInventoryService(v2.InventoryService):
    def __init__(self):
        self.inventory = {"p1": {"avail": 10, "res": 0}}
        self.lock = threading.Lock()
        
    def reserve(self, order_id, items):
        with self.lock:
            # Check all first to avoid partial reserves in mock
            for item in items:
                if item.product_id in self.inventory:
                    if self.inventory[item.product_id]["avail"] < item.quantity:
                        raise Exception("Insufficient inventory")
            for item in items:
                if item.product_id in self.inventory:
                    self.inventory[item.product_id]["avail"] -= item.quantity
                    self.inventory[item.product_id]["res"] += item.quantity

    def commit(self, order_id):
        with self.lock:
            if "p1" in self.inventory and self.inventory["p1"]["res"] >= 2:
                self.inventory["p1"]["res"] -= 2

    def release(self, order_id):
        pass

class MockPaymentService(v2.PaymentService):
    def __init__(self):
        self.fail = False
    def process_payment(self, order_id, amount, payment_method_id):
        if self.fail:
            return v2.PaymentResult(payment_id="", successful=False, failure_reason="Failed")
        return v2.PaymentResult(payment_id="t1", successful=True, failure_reason=None)
    def refund(self, order_id):
        pass

class MockMessageQueue(v2.MessageQueue):
    def publish(self, topic, message):
        pass
    def subscribe(self, topic, handler):
        pass
    def poll_batch(self, topic, batch_size):
        return []

class TestV2EcommerceService(unittest.TestCase):
    def setUp(self):
        self.order_repo = MockOrderRepo()
        self.cart_service = MockCartService()
        self.inventory_service = MockInventoryService()
        self.payment_service = MockPaymentService()
        self.message_queue = MockMessageQueue()
        self.service = v2.SagaOrderService(
            self.order_repo, self.cart_service, self.inventory_service,
            self.payment_service, self.message_queue
        )
        self.cart_service.get_cart = lambda uid: v2.Cart(user_id=uid, items=[v2.CartItem("p1", 2, Decimal("10.0"))])
        
        # In scaled_ecommerce_service.py:
        # reserve_inventory calls inventory_service.reserve(reservation_id, items)
        # However our mock isn't stateful enough to know how many to restore on release.
        # We will manually restore based on the test case, or hardcode it since we know exactly what is reserved.
        
        def dynamic_release(reservation_id):
            with self.inventory_service.lock:
                if "p1" in self.inventory_service.inventory:
                    if self.inventory_service.inventory["p1"]["res"] > 0:
                        # assuming it just restores whatever is reserved
                        res = self.inventory_service.inventory["p1"]["res"]
                        self.inventory_service.inventory["p1"]["avail"] += res
                        self.inventory_service.inventory["p1"]["res"] = 0
        self.inventory_service.release = dynamic_release
        
        def dynamic_commit(reservation_id):
            with self.inventory_service.lock:
                if "p1" in self.inventory_service.inventory:
                    self.inventory_service.inventory["p1"]["res"] = 0
        self.inventory_service.commit = dynamic_commit

    def test_saga_success(self):
        req = v2.CreateOrderRequest(
            shipping_address_id="123 Main St",
            payment_method_id="pm_1"
        )
        order = self.service._create_order_sync("u1", req)
        self.assertEqual(order.status, v2.OrderStatus.CONFIRMED)
        
        self.assertEqual(self.inventory_service.inventory["p1"]["avail"], 8)
        self.assertEqual(self.inventory_service.inventory["p1"]["res"], 0)

    def test_saga_inventory_failure(self):
        self.cart_service.get_cart = lambda uid: v2.Cart(user_id=uid, items=[v2.CartItem("p1", 15, Decimal("10.0"))])
        req = v2.CreateOrderRequest(
            shipping_address_id="123 Main St",
            payment_method_id="pm_1"
        )
        with self.assertRaises(Exception):
            self.service._create_order_sync("u1", req)
            
        self.assertEqual(self.inventory_service.inventory["p1"]["avail"], 10)
        self.assertEqual(self.inventory_service.inventory["p1"]["res"], 0)

    def test_saga_payment_failure_compensation(self):
        self.payment_service.fail = True
        req = v2.CreateOrderRequest(
            shipping_address_id="123 Main St",
            payment_method_id="pm_1"
        )
        try:
            self.service._create_order_sync("u1", req)
        except v2.PaymentFailedException:
            pass 
        
        self.assertEqual(self.inventory_service.inventory["p1"]["avail"], 10)
        self.assertEqual(self.inventory_service.inventory["p1"]["res"], 0)

    def test_concurrent_inventory_reservations(self):
        self.cart_service.get_cart = lambda uid: v2.Cart(user_id=uid, items=[v2.CartItem("p1", 6, Decimal("10.0"))])
        req1 = v2.CreateOrderRequest(
            shipping_address_id="123 Main St", payment_method_id="pm_1"
        )
        req2 = v2.CreateOrderRequest(
            shipping_address_id="123 Main St", payment_method_id="pm_1"
        )
        
        f1 = self.service.create_order_async("u1", req1)
        f2 = self.service.create_order_async("u2", req2)
        
        try: o1 = f1.result()
        except: o1 = None
        try: o2 = f2.result()
        except: o2 = None
        
        statuses = []
        if o1: statuses.append(o1.status)
        if o2: statuses.append(o2.status)
        
        self.assertIn(v2.OrderStatus.CONFIRMED, statuses)
        self.assertEqual(self.inventory_service.inventory["p1"]["avail"], 4)
        self.assertEqual(self.inventory_service.inventory["p1"]["res"], 0)

    def test_compensate_idempotent(self):
        req = v2.CreateOrderRequest(
            shipping_address_id="123 Main St", payment_method_id="pm_1"
        )
        items = [v2.CartItem(product_id="p1", quantity=2, unit_price=Decimal("10.0"))]
        order = v2.Order(order_id="o_1", user_id="u1", items=items, 
                         status=v2.OrderStatus.PENDING_PAYMENT,
                         total=Decimal("20.0"),
                         payment_method_id=req.payment_method_id, created_at=None)
        
        cart = v2.Cart(user_id="u1", items=items)
        saga = v2.OrderSaga("s1", order, cart)
        saga.state = v2.SagaState.INVENTORY_RESERVED
        
        self.inventory_service.reserve("o_1", items)
        self.assertEqual(self.inventory_service.inventory["p1"]["avail"], 8)
        self.assertEqual(self.inventory_service.inventory["p1"]["res"], 2)
        
        saga.compensate(self.inventory_service, self.payment_service)
        saga.compensate(self.inventory_service, self.payment_service)
        
        self.assertIsNotNone(order.status)
        self.assertEqual(self.inventory_service.inventory["p1"]["avail"], 10)
        self.assertEqual(self.inventory_service.inventory["p1"]["res"], 0)
        
    def test_saga_unknown_state_compensation(self):
        req = v2.CreateOrderRequest(
            shipping_address_id="123 Main St", payment_method_id="pm_1"
        )
        items = [v2.CartItem(product_id="p1", quantity=2, unit_price=Decimal("10.0"))]
        order = v2.Order(order_id="o_1", user_id="u1", items=items, 
                         status=v2.OrderStatus.PENDING_PAYMENT,
                         total=Decimal("20.0"),
                         payment_method_id=req.payment_method_id, created_at=None)
        cart = v2.Cart(user_id="u1", items=items)
        saga = v2.OrderSaga("s1", order, cart)
        saga.state = v2.SagaState.STARTED
                         
        saga.compensate(self.inventory_service, self.payment_service)
        self.assertEqual(order.status, v2.OrderStatus.PENDING_PAYMENT)

if __name__ == '__main__':
    unittest.main()
