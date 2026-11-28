import sys
import os
import unittest
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))

from enums_v2 import OrderStatus
from models_v2 import Customer, Restaurant, Driver, MenuItem, OrderItem, Observer
from service_v2 import (Order, OrderService, PlacedState, CancelledState, PreparingState,
                        ReadyForPickupState, OutForDeliveryState, DeliveredState)
from strategies_v2 import (StandardPricingStrategy, SurgePricingStrategy,
                           BasePricingStrategy, PercentDiscountDecorator, FreeDeliveryDecorator)


class MockObserver(Observer):
    def __init__(self):
        self.notified = False
        self.last_order_state = None

    def update(self, order) -> None:
        self.notified = True
        self.last_order_state = order.get_state().get_status().name


class TestFoodDeliveryV2Parity(unittest.TestCase):
    """Every v1 test re-run against the v2 modules: v2 must not regress
    the v1 behavior it keeps."""

    def setUp(self):
        self.restaurant = Restaurant("Burger Joint")
        self.customer = Customer("C1", "Test Customer")
        self.driver = Driver("D1", "Test Driver")
        self.burger = MenuItem("M1", "Burger", 10.0)
        self.fries = MenuItem("M2", "Fries", 5.0)

    def test_order_creation_and_pricing(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        order.add_item(OrderItem(self.burger, 2))
        order.add_item(OrderItem(self.fries, 1))
        self.assertEqual(order.get_total(), 30.0)

        surge_order = Order("O2", self.customer, self.restaurant, SurgePricingStrategy())
        surge_order.add_item(OrderItem(self.burger, 2))
        surge_order.add_item(OrderItem(self.fries, 1))
        self.assertEqual(surge_order.get_total(), 40.0)

    def test_state_transitions_and_observers(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        observer = MockObserver()
        order.add_observer(observer)

        self.assertIsInstance(order.get_state(), PlacedState)
        order.next_state()
        self.assertIsInstance(order.get_state(), PreparingState)
        self.assertEqual(observer.last_order_state, "PREPARING")
        order.next_state()
        self.assertIsInstance(order.get_state(), ReadyForPickupState)
        order.next_state()
        self.assertIsInstance(order.get_state(), OutForDeliveryState)
        order.next_state()
        self.assertIsInstance(order.get_state(), DeliveredState)

    def test_cancellation(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        order.cancel()
        self.assertIsInstance(order.get_state(), CancelledState)

    def test_driver_assignment_thread_safety(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        driver1 = Driver("D1", "Driver 1")
        driver2 = Driver("D2", "Driver 2")
        results = []

        def assign(d):
            results.append(order.assign_driver(d))

        t1 = threading.Thread(target=assign, args=(driver1,))
        t2 = threading.Thread(target=assign, args=(driver2,))
        t1.start(); t2.start(); t1.join(); t2.join()

        self.assertEqual(sorted(results), [False, True])
        self.assertIsNotNone(order.driver)


class TestFoodDeliveryV2(unittest.TestCase):
    """The v2 improvements: state-dependent cancellation refunds,
    decorator pricing, idempotent placement."""

    def setUp(self):
        self.restaurant = Restaurant("Burger Joint")
        self.customer = Customer("C1", "Test Customer")
        self.burger = MenuItem("M1", "Burger", 10.0)
        self.fries = MenuItem("M2", "Fries", 5.0)

    def _order_30(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        order.add_item(OrderItem(self.burger, 2))  # 20
        order.add_item(OrderItem(self.fries, 1))   # 5
        return order  # subtotal 25 + fee 5 = 30

    def test_cancel_before_preparation_full_refund(self):
        order = self._order_30()
        result = order.cancel()
        self.assertTrue(result.cancelled)
        self.assertEqual(result.refund, 30.0)
        self.assertIsInstance(order.get_state(), CancelledState)

    def test_cancel_during_preparation_penalty(self):
        order = self._order_30()
        order.next_state()  # PREPARING
        result = order.cancel()
        self.assertTrue(result.cancelled)
        self.assertAlmostEqual(result.refund, 24.0)  # 30 * 0.8
        self.assertIsInstance(order.get_state(), CancelledState)

    def test_cancel_rejected_once_food_ready(self):
        order = self._order_30()
        order.next_state(); order.next_state()  # READY_FOR_PICKUP
        result = order.cancel()
        self.assertFalse(result.cancelled)
        self.assertEqual(result.refund, 0.0)
        self.assertIsInstance(order.get_state(), ReadyForPickupState)

    def test_cancel_rejected_out_for_delivery(self):
        order = self._order_30()
        order.next_state(); order.next_state(); order.next_state()  # OUT_FOR_DELIVERY
        result = order.cancel()
        self.assertFalse(result.cancelled)
        self.assertIsInstance(order.get_state(), OutForDeliveryState)

    def test_cancelled_order_cannot_advance(self):
        order = self._order_30()
        order.cancel()
        with self.assertRaises(ValueError):
            order.next_state()

    def test_percent_discount_applies_to_food_only(self):
        strategy = PercentDiscountDecorator(StandardPricingStrategy(), 10.0)
        order = Order("O1", self.customer, self.restaurant, strategy)
        order.add_item(OrderItem(self.burger, 2))
        order.add_item(OrderItem(self.fries, 1))
        # 25 subtotal - 10% = 22.5 food, + 5 delivery = 27.5
        self.assertAlmostEqual(order.get_total(), 27.5)

    def test_free_delivery_decorator(self):
        strategy = FreeDeliveryDecorator(StandardPricingStrategy())
        order = Order("O1", self.customer, self.restaurant, strategy)
        order.add_item(OrderItem(self.burger, 2))
        order.add_item(OrderItem(self.fries, 1))
        self.assertAlmostEqual(order.get_total(), 25.0)

    def test_stacked_decorators(self):
        strategy = FreeDeliveryDecorator(PercentDiscountDecorator(StandardPricingStrategy(), 10.0))
        order = Order("O1", self.customer, self.restaurant, strategy)
        order.add_item(OrderItem(self.burger, 2))
        order.add_item(OrderItem(self.fries, 1))
        # 10% off food (22.5) and free delivery (0) = 22.5
        self.assertAlmostEqual(order.get_total(), 22.5)

    def test_idempotent_placement_returns_original(self):
        service = OrderService()
        order1, created1 = service.place_order("key-1", lambda: self._order_30())
        order2, created2 = service.place_order("key-1", lambda: self._order_30())
        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertIs(order1, order2)
        self.assertEqual(service.order_count(), 1)

    def test_distinct_keys_create_distinct_orders(self):
        service = OrderService()
        _, c1 = service.place_order("key-1", lambda: self._order_30())
        _, c2 = service.place_order("key-2", lambda: self._order_30())
        self.assertTrue(c1)
        self.assertTrue(c2)
        self.assertEqual(service.order_count(), 2)


if __name__ == '__main__':
    unittest.main()
