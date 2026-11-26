"""
Hotel Reservation System Tests
"""
import unittest
import sys
import importlib.util
from datetime import date, timedelta
from typing import Any

def load_version(version: str):
    """Helper to dynamically load versioned modules by manipulating sys.path"""
    base_path = f"02-lld-projects/hotel-reservation/python/{version}"
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    # Reload modules if they exist
    modules = ['enums', 'enums.types', 'models', 'models.models', 'hotel']
    for m in modules:
        if m in sys.modules:
            del sys.modules[m]

    import enums
    import models
    import hotel
    return enums, models, hotel

class TestHotelReservationV1(unittest.TestCase):
    def setUp(self):
        self.enums, self.models, self.hotel = load_version("v1-basic")
        
        self.guest = self.models.Guest("G001", "John", "john@email.com", "555-123")
        self.room = self.models.Room("201", self.enums.RoomType.DOUBLE, 2)
        self.check_in = date.today() + timedelta(days=5)
        self.check_out = date.today() + timedelta(days=8)
    
    def test_room_creation(self):
        self.assertEqual("201", self.room.room_number)
        self.assertEqual(120.0, self.room.base_price)
    
    def test_reservation_total(self):
        res = self.models.Reservation(self.guest, self.room, self.check_in, self.check_out)
        self.assertEqual(360.0, res.total_amount)  # 3 nights * $120
    
    def test_reservation_flow(self):
        res = self.models.Reservation(self.guest, self.room, self.check_in, self.check_out)
        self.assertEqual(self.enums.ReservationStatus.PENDING, res.status)
        
        res.confirm()
        self.assertEqual(self.enums.ReservationStatus.CONFIRMED, res.status)
        
        res.check_in()
        self.assertEqual(self.enums.ReservationStatus.CHECKED_IN, res.status)
        
        res.check_out()
        self.assertEqual(self.enums.ReservationStatus.CHECKED_OUT, res.status)

class TestHotelReservationV2(unittest.TestCase):
    def setUp(self):
        self.enums, self.models, self.hotel = load_version("v2-extended")
        
        self.guest = self.models.Guest("G001", "John", "john@email.com", "555-123")
        self.room = self.models.Room("201", self.enums.RoomType.DOUBLE, 2)
        self.check_in = date.today() + timedelta(days=5)
        self.check_out = date.today() + timedelta(days=8)
        
    def test_room_decorators(self):
        base_price = self.room.base_price
        
        wifi_room = self.models.WiFiAddon(self.room)
        self.assertEqual(base_price + 10.0, wifi_room.base_price)
        
        breakfast_room = self.models.BreakfastAddon(wifi_room)
        self.assertEqual(base_price + 30.0, breakfast_room.base_price)
        self.assertTrue("WiFi" in breakfast_room.description)
        self.assertTrue("Breakfast" in breakfast_room.description)

class TestHotelReservationV3(unittest.TestCase):
    def setUp(self):
        self.enums, self.models, self.hotel = load_version("v3-optimized")
        
        self.guest = self.models.Guest("G001", "John", "john@email.com", "555-123")
        self.room1 = self.models.Room("201", self.enums.RoomType.DOUBLE, 2)
        self.room2 = self.models.Room("202", self.enums.RoomType.DOUBLE, 2)
        self.check_in = date.today() + timedelta(days=5)
        self.check_out = date.today() + timedelta(days=8)
        
    def test_multi_room_booking(self):
        h = self.hotel.Hotel("Test Hotel")
        h.reset_instance()
        h = self.hotel.Hotel("Test Hotel")
        
        h.add_room(self.room1)
        h.add_room(self.room2)
        h.register_guest(self.guest)
        
        res = h.make_reservation(self.guest, [self.room1, self.room2], self.check_in, self.check_out)
        self.assertIsNotNone(res)
        self.assertEqual(2, len(res.rooms))
        
        # 3 nights * $120 * 2 rooms = $720
        self.assertEqual(720.0, res.total_amount)

if __name__ == "__main__":
    unittest.main(verbosity=2)
