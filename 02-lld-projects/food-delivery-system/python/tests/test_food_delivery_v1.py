import sys
import os
import unittest
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))

from enums import OrderStatus
from models import Customer, Restaurant, Driver, MenuItem, OrderItem, Observer
from service import Order, PlacedState, CancelledState, PreparingState, ReadyForPickupState, OutForDeliveryState, DeliveredState
from strategies import StandardPricingStrategy, SurgePricingStrategy


class MockObserver(Observer):
    def __init__(self):
        self.notified = False
        self.last_order_state = None

    def update(self, order) -> None:
        self.notified = True
        self.last_order_state = order.get_state().get_status().name


class TestFoodDeliveryV1(unittest.TestCase):
    def setUp(self):
        self.restaurant = Restaurant("Burger Joint")
        self.customer = Customer("C1", "Test Customer")
        self.driver = Driver("D1", "Test Driver")
        self.burger = MenuItem("M1", "Burger", 10.0)
        self.fries = MenuItem("M2", "Fries", 5.0)

    def test_order_creation_and_pricing(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        order.add_item(OrderItem(self.burger, 2))  # 20
        order.add_item(OrderItem(self.fries, 1))  # 5

        self.assertEqual(order.get_total(), 30.0)  # 25 + 5 flat fee

        surge_order = Order("O2", self.customer, self.restaurant, SurgePricingStrategy())
        surge_order.add_item(OrderItem(self.burger, 2))
        surge_order.add_item(OrderItem(self.fries, 1))

        self.assertEqual(surge_order.get_total(), 40.0)  # 25 + 15 surge fee

    def test_state_transitions_and_observers(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        observer = MockObserver()
        order.add_observer(observer)

        self.assertIsInstance(order.get_state(), PlacedState)

        order.next_state()
        self.assertIsInstance(order.get_state(), PreparingState)
        self.assertTrue(observer.notified)
        self.assertEqual(observer.last_order_state, "PREPARING")

        observer.notified = False
        order.next_state()
        self.assertIsInstance(order.get_state(), ReadyForPickupState)
        self.assertTrue(observer.notified)

        observer.notified = False
        order.next_state()
        self.assertIsInstance(order.get_state(), OutForDeliveryState)
        self.assertTrue(observer.notified)

        observer.notified = False
        order.next_state()
        self.assertIsInstance(order.get_state(), DeliveredState)
        self.assertTrue(observer.notified)

    def test_cancellation(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        order.cancel()
        self.assertIsInstance(order.get_state(), CancelledState)

    def test_driver_assignment_thread_safety(self):
        order = Order("O1", self.customer, self.restaurant, StandardPricingStrategy())
        driver1 = Driver("D1", "Driver 1")
        driver2 = Driver("D2", "Driver 2")

        success1 = []
        success2 = []

        def assign_d1():
            success1.append(order.assign_driver(driver1))

        def assign_d2():
            success2.append(order.assign_driver(driver2))

        t1 = threading.Thread(target=assign_d1)
        t2 = threading.Thread(target=assign_d2)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.assertTrue(success1[0] or success2[0])
        self.assertFalse(success1[0] and success2[0])
        self.assertIsNotNone(order.driver)
        if success1[0]:
            self.assertEqual(order.driver, driver1)
        else:
            self.assertEqual(order.driver, driver2)

if __name__ == '__main__':
    unittest.main()
