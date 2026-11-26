# Restaurant Management System - Tests

import unittest
import sys
import os
from datetime import datetime, timedelta

# Add v3-optimized to path for comprehensive tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))

from restaurant import (
    RestaurantService, Table, MenuItem, Order, Bill,
    TableStatus, OrderStatus, MenuCategory, WaitlistEntry
)


class TestTable(unittest.TestCase):
    def test_table_creation(self):
        table = Table("T1", 4)
        self.assertEqual(table.id, "T1")
        self.assertEqual(table.capacity, 4)
        self.assertEqual(table.status, TableStatus.AVAILABLE)

    def test_try_reserve(self):
        table = Table("T1", 4)
        self.assertTrue(table.try_reserve(4))
        self.assertEqual(table.status, TableStatus.RESERVED)
        # Cannot reserve again
        self.assertFalse(table.try_reserve(2))

    def test_try_seat(self):
        table = Table("T1", 4)
        self.assertTrue(table.try_seat(4))
        self.assertEqual(table.status, TableStatus.OCCUPIED)
        # Cannot seat again
        self.assertFalse(table.try_seat(2))

    def test_release(self):
        table = Table("T1", 4)
        table.try_seat(4)
        table.release()
        self.assertEqual(table.status, TableStatus.AVAILABLE)


class TestMenuItem(unittest.TestCase):
    def test_menu_item_creation(self):
        item = MenuItem("M1", "Salmon", 24.99, MenuCategory.MAIN_COURSE)
        self.assertEqual(item.id, "M1")
        self.assertEqual(item.name, "Salmon")
        self.assertEqual(item.price, 24.99)
        self.assertEqual(item.category, MenuCategory.MAIN_COURSE)
        self.assertTrue(item.available)


class TestRestaurantService(unittest.TestCase):
    def setUp(self):
        self.restaurant = RestaurantService()
        self.restaurant.add_table("T1", 2)
        self.restaurant.add_table("T2", 4)
        self.restaurant.add_table("T3", 6)
        self.restaurant.add_menu_item("A1", "Appetizer", 10.0, MenuCategory.APPETIZER)
        self.restaurant.add_menu_item("M1", "Main", 25.0, MenuCategory.MAIN_COURSE)
        self.restaurant.add_menu_item("D1", "Dessert", 8.0, MenuCategory.DESSERT)

    def test_table_management(self):
        table = self.restaurant.get_table("T1")
        self.assertIsNotNone(table)
        self.assertEqual(table.capacity, 2)
        self.assertEqual(table.status, TableStatus.AVAILABLE)

    def test_seat_party(self):
        self.assertTrue(self.restaurant.seat_party("T2", 4))
        self.assertEqual(self.restaurant.get_table("T2").status, TableStatus.OCCUPIED)
        # Cannot seat another party at same table
        self.assertFalse(self.restaurant.seat_party("T2", 2))

    def test_available_tables(self):
        available = self.restaurant.get_available_tables(4)
        self.assertEqual(len(available), 2)  # T2 and T3 can fit 4
        
        self.restaurant.seat_party("T2", 4)
        available = self.restaurant.get_available_tables(4)
        self.assertEqual(len(available), 1)  # Only T3 now

    def test_menu_items(self):
        item = self.restaurant.get_menu_item("M1")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Main")
        self.assertEqual(item.price, 25.0)
        self.assertTrue(item.available)

    def test_create_order(self):
        # Cannot create order for unseated table
        self.assertIsNone(self.restaurant.create_order("T1"))
        
        # Seat and create order
        self.restaurant.seat_party("T1", 2)
        order = self.restaurant.create_order("T1")
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrderStatus.PLACED)

    def test_add_items_to_order(self):
        self.restaurant.seat_party("T1", 2)
        order = self.restaurant.create_order("T1")
        
        self.assertIsNotNone(self.restaurant.add_item_to_order(order.id, "A1", 2))
        self.assertIsNotNone(self.restaurant.add_item_to_order(order.id, "M1", 2, "no salt"))
        
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.get_total(), 70.0)  # 2*10 + 2*25 = 70

    def test_order_workflow(self):
        self.restaurant.seat_party("T1", 2)
        order = self.restaurant.create_order("T1")
        self.restaurant.add_item_to_order(order.id, "M1", 1)
        
        self.assertEqual(order.status, OrderStatus.PLACED)
        
        self.restaurant.update_order_status(order.id, OrderStatus.PREPARING)
        self.assertEqual(order.status, OrderStatus.PREPARING)
        
        self.restaurant.update_order_status(order.id, OrderStatus.READY)
        self.assertEqual(order.status, OrderStatus.READY)
        
        self.restaurant.update_order_status(order.id, OrderStatus.SERVED)
        self.assertEqual(order.status, OrderStatus.SERVED)

    def test_bill_generation(self):
        self.restaurant.seat_party("T1", 2)
        order = self.restaurant.create_order("T1")
        self.restaurant.add_item_to_order(order.id, "M1", 2)
        self.restaurant.update_order_status(order.id, OrderStatus.SERVED)
        
        bill = self.restaurant.generate_bill(order.id, 0.10)  # 10% tax
        self.assertIsNotNone(bill)
        self.assertEqual(bill.subtotal, 50.0)  # 2 * 25
        self.assertEqual(bill.tax, 5.0)  # 10% of 50
        self.assertEqual(bill.get_total(), 55.0)  # Before tip

    def test_bill_payment(self):
        self.restaurant.seat_party("T1", 2)
        order = self.restaurant.create_order("T1")
        self.restaurant.add_item_to_order(order.id, "M1", 2)
        self.restaurant.update_order_status(order.id, OrderStatus.SERVED)
        
        bill = self.restaurant.generate_bill(order.id, 0.10)
        self.assertTrue(self.restaurant.pay_bill(bill.id, 10.0))  # $10 tip
        
        self.assertTrue(bill.paid)
        self.assertEqual(bill.tip, 10.0)
        self.assertEqual(bill.get_total(), 65.0)  # 50 + 5 + 10
        self.assertEqual(self.restaurant.get_table("T1").status, TableStatus.AVAILABLE)

    def test_reservation(self):
        res_time = datetime.now() + timedelta(hours=2)
        res = self.restaurant.make_reservation("John", "555-1234", 4, res_time)
        
        self.assertIsNotNone(res)
        self.assertEqual(res.customer_name, "John")
        self.assertTrue(res.confirmed)
        self.assertIsNotNone(res.assigned_table)

    def test_waitlist(self):
        entry = self.restaurant.add_to_waitlist("Jane", "555-5678", 2)
        self.assertIsNotNone(entry)
        self.assertFalse(entry.seated)
        
        self.assertEqual(len(self.restaurant.get_waitlist()), 1)
        
        next_entry = self.restaurant.get_next_from_waitlist(2)
        self.assertIsNotNone(next_entry)
        self.assertEqual(next_entry.customer_name, "Jane")
        self.assertTrue(next_entry.seated)

    def test_kitchen_display(self):
        self.restaurant.seat_party("T1", 2)
        order = self.restaurant.create_order("T1")
        self.restaurant.add_item_to_order(order.id, "M1", 1)
        self.restaurant.submit_order_to_kitchen(order.id)
        
        kitchen = self.restaurant.get_kitchen_display()
        self.assertEqual(len(kitchen.get_pending_orders()), 1)
        
        taken_order = kitchen.take_next_order(timeout=1)
        self.assertEqual(taken_order.id, order.id)
        self.assertEqual(order.status, OrderStatus.PREPARING)
        self.assertEqual(len(kitchen.get_in_progress_orders()), 1)
        
        kitchen.mark_ready(order.id)
        self.assertEqual(order.status, OrderStatus.READY)
        self.assertEqual(len(kitchen.get_ready_orders()), 1)

    def test_split_bill(self):
        self.restaurant.seat_party("T2", 4)
        order = self.restaurant.create_order("T2")
        self.restaurant.add_item_to_order(order.id, "M1", 4)
        
        bill = self.restaurant.generate_bill(order.id, 0.10)
        bill.tip = 20.0
        bill.split_evenly(4)
        
        self.assertEqual(len(bill.splits), 4)
        expected = (100.0 + 10.0 + 20.0) / 4  # 32.5 per person
        for amount in bill.splits.values():
            self.assertAlmostEqual(amount, expected, places=2)


if __name__ == '__main__':
    unittest.main()
