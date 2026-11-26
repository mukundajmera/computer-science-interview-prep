"""Hotel Reservation Enums."""
from enum import Enum


class RoomType(Enum):
    SINGLE = ("SINGLE", 1, 80.0)
    DOUBLE = ("DOUBLE", 2, 120.0)
    DELUXE = ("DELUXE", 3, 200.0)
    SUITE = ("SUITE", 4, 350.0)
    
    def __init__(self, name, max_occupancy, base_price):
        self._max_occupancy = max_occupancy
        self._base_price = base_price
    
    @property
    def max_occupancy(self): return self._max_occupancy
    @property
    def base_price(self): return self._base_price


class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    CLEANING = "CLEANING"


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"
