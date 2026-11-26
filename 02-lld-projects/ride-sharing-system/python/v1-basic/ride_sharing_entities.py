"""
Ride Sharing System - V1 Basic
Core entities for the ride sharing system.
"""

from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import math


class VehicleType(Enum):
    BIKE = ("BIKE", 1, 1.0)
    AUTO = ("AUTO", 3, 1.5)
    CAR = ("CAR", 4, 2.0)
    PREMIUM = ("PREMIUM", 4, 3.0)
    
    def __init__(self, name: str, capacity: int, multiplier: float):
        self._name = name
        self.capacity = capacity
        self.multiplier = multiplier


class DriverStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class TripStatus(Enum):
    REQUESTED = "requested"
    MATCHED = "matched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Location:
    """Represents GPS coordinates."""
    
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate distance in km (simplified Euclidean)."""
        lat_diff = self.latitude - other.latitude
        lon_diff = self.longitude - other.longitude
        # 1 degree ≈ 111 km
        return math.sqrt(lat_diff ** 2 + lon_diff ** 2) * 111
    
    def __str__(self) -> str:
        return f"({self.latitude:.4f}, {self.longitude:.4f})"


class Vehicle:
    """Represents a vehicle."""
    
    def __init__(self, id: str, vehicle_type: VehicleType, license_plate: str):
        self.id = id
        self.type = vehicle_type
        self.license_plate = license_plate
    
    def __str__(self) -> str:
        return f"{self.type.name} ({self.license_plate})"


class Rider:
    """Represents a rider/passenger."""
    
    def __init__(self, id: str, name: str, phone: str):
        self.id = id
        self.name = name
        self.phone = phone
        self.current_location: Optional[Location] = None
        self.trip_history: List['Trip'] = []
        self.rating = 5.0
        self._rating_count = 0
    
    def add_trip(self, trip: 'Trip') -> None:
        self.trip_history.append(trip)
    
    def add_rating(self, stars: int) -> None:
        self._rating_count += 1
        self.rating = ((self.rating * (self._rating_count - 1)) + stars) / self._rating_count
    
    def __str__(self) -> str:
        return f"Rider[{self.id}] {self.name}"


class Driver:
    """Represents a driver."""
    
    def __init__(self, id: str, name: str, phone: str, vehicle: Vehicle):
        self.id = id
        self.name = name
        self.phone = phone
        self.vehicle = vehicle
        self.current_location: Optional[Location] = None
        self.status = DriverStatus.OFFLINE
        self.rating = 5.0
        self._rating_count = 0
        self.trip_history: List['Trip'] = []
    
    def update_location(self, location: Location) -> None:
        self.current_location = location
    
    def set_available(self) -> None:
        self.status = DriverStatus.AVAILABLE
    
    def set_busy(self) -> None:
        self.status = DriverStatus.BUSY
    
    def set_offline(self) -> None:
        self.status = DriverStatus.OFFLINE
    
    def is_available(self) -> bool:
        return self.status == DriverStatus.AVAILABLE and self.current_location is not None
    
    def add_trip(self, trip: 'Trip') -> None:
        self.trip_history.append(trip)
    
    def add_rating(self, stars: int) -> None:
        self._rating_count += 1
        self.rating = ((self.rating * (self._rating_count - 1)) + stars) / self._rating_count
    
    def __str__(self) -> str:
        return f"Driver[{self.id}] {self.name} ({self.vehicle.type.name})"


class Fare:
    """Represents fare calculation."""
    
    BASE_FARE = 5.0
    PER_KM_RATE = 1.0
    PER_MINUTE_RATE = 0.15
    
    def __init__(self, distance: float, duration_minutes: int, vehicle_type: VehicleType):
        self.distance = distance
        self.duration_minutes = duration_minutes
        self.vehicle_type = vehicle_type
        self.total = self._calculate()
    
    def _calculate(self) -> float:
        base = self.BASE_FARE
        distance_cost = self.distance * self.PER_KM_RATE
        time_cost = self.duration_minutes * self.PER_MINUTE_RATE
        return (base + distance_cost + time_cost) * self.vehicle_type.multiplier
    
    def display(self) -> None:
        print(f"Fare: ${self.total:.2f} ({self.distance:.1f} km, {self.duration_minutes} min)")
    
    def __str__(self) -> str:
        return f"${self.total:.2f}"


class Trip:
    """Represents a trip/ride."""
    
    def __init__(self, id: str, rider: Rider, pickup: Location, 
                 dropoff: Location, vehicle_type: VehicleType):
        self.id = id
        self.rider = rider
        self.driver: Optional[Driver] = None
        self.pickup = pickup
        self.dropoff = dropoff
        self.vehicle_type = vehicle_type
        self.status = TripStatus.REQUESTED
        self.fare: Optional[Fare] = None
        self.request_time = datetime.now()
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.driver_rating: Optional[int] = None
        self.rider_rating: Optional[int] = None
    
    def assign_driver(self, driver: Driver) -> None:
        self.driver = driver
        self.status = TripStatus.MATCHED
        driver.set_busy()
    
    def start(self) -> None:
        if self.status != TripStatus.MATCHED:
            raise ValueError(f"Cannot start trip in state: {self.status}")
        self.status = TripStatus.IN_PROGRESS
        self.start_time = datetime.now()
    
    def complete(self, duration_minutes: int) -> None:
        if self.status != TripStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete trip in state: {self.status}")
        
        self.status = TripStatus.COMPLETED
        self.end_time = datetime.now()
        
        distance = self.pickup.distance_to(self.dropoff)
        self.fare = Fare(distance, duration_minutes, self.vehicle_type)
        
        if self.driver:
            self.driver.set_available()
            self.driver.add_trip(self)
        self.rider.add_trip(self)
    
    def cancel(self) -> None:
        if self.status in (TripStatus.IN_PROGRESS, TripStatus.COMPLETED):
            raise ValueError(f"Cannot cancel trip in state: {self.status}")
        self.status = TripStatus.CANCELLED
        if self.driver:
            self.driver.set_available()
    
    def rate_driver(self, stars: int) -> None:
        if self.status != TripStatus.COMPLETED:
            raise ValueError("Can only rate after completion")
        if not 1 <= stars <= 5:
            raise ValueError("Rating must be 1-5")
        self.driver_rating = stars
        if self.driver:
            self.driver.add_rating(stars)
    
    def rate_rider(self, stars: int) -> None:
        if self.status != TripStatus.COMPLETED:
            raise ValueError("Can only rate after completion")
        if not 1 <= stars <= 5:
            raise ValueError("Rating must be 1-5")
        self.rider_rating = stars
        self.rider.add_rating(stars)
    
    def get_estimated_distance(self) -> float:
        return self.pickup.distance_to(self.dropoff)
    
    def get_estimated_fare(self) -> Fare:
        distance = self.get_estimated_distance()
        est_minutes = int(distance * 3)  # ~3 min per km
        return Fare(distance, est_minutes, self.vehicle_type)
    
    def __str__(self) -> str:
        return f"Trip[{self.id}] {self.pickup} -> {self.dropoff} [{self.status.value}]"


class RideSharingService:
    """Ride sharing service (Singleton)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._riders: Dict[str, Rider] = {}
        self._drivers: Dict[str, Driver] = {}
        self._trips: Dict[str, Trip] = {}
        self._rider_counter = 0
        self._driver_counter = 0
        self._trip_counter = 0
        self._initialized = True
    
    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
    
    # Registration
    def register_rider(self, name: str, phone: str) -> Rider:
        self._rider_counter += 1
        rider_id = f"R{self._rider_counter}"
        rider = Rider(rider_id, name, phone)
        self._riders[rider_id] = rider
        return rider
    
    def register_driver(self, name: str, phone: str, vehicle: Vehicle) -> Driver:
        self._driver_counter += 1
        driver_id = f"D{self._driver_counter}"
        driver = Driver(driver_id, name, phone, vehicle)
        self._drivers[driver_id] = driver
        return driver
    
    # Trip management
    def request_ride(self, rider_id: str, pickup: Location, 
                     dropoff: Location, vehicle_type: VehicleType) -> Trip:
        rider = self._riders.get(rider_id)
        if not rider:
            raise ValueError(f"Rider not found: {rider_id}")
        
        self._trip_counter += 1
        trip_id = f"T{self._trip_counter}"
        trip = Trip(trip_id, rider, pickup, dropoff, vehicle_type)
        self._trips[trip_id] = trip
        
        # Try to match driver
        matched = self._find_nearest_driver(pickup, vehicle_type)
        if matched:
            trip.assign_driver(matched)
            distance = matched.current_location.distance_to(pickup)
            print(f"Matched with {matched.name} ({distance:.1f} km away)")
        else:
            print("No drivers available. Waiting...")
        
        return trip
    
    def _find_nearest_driver(self, pickup: Location, 
                             vehicle_type: VehicleType) -> Optional[Driver]:
        nearest = None
        min_distance = float('inf')
        
        for driver in self._drivers.values():
            if not driver.is_available():
                continue
            if driver.vehicle.type != vehicle_type:
                continue
            
            distance = driver.current_location.distance_to(pickup)
            if distance < min_distance:
                min_distance = distance
                nearest = driver
        
        return nearest
    
    def start_trip(self, trip_id: str) -> None:
        trip = self._trips.get(trip_id)
        if not trip:
            raise ValueError(f"Trip not found: {trip_id}")
        trip.start()
        print(f"Trip started: {trip_id}")
    
    def complete_trip(self, trip_id: str, duration_minutes: int) -> None:
        trip = self._trips.get(trip_id)
        if not trip:
            raise ValueError(f"Trip not found: {trip_id}")
        trip.complete(duration_minutes)
        print(f"Trip completed: {trip_id} - Fare: {trip.fare}")
    
    def cancel_trip(self, trip_id: str) -> None:
        trip = self._trips.get(trip_id)
        if not trip:
            raise ValueError(f"Trip not found: {trip_id}")
        trip.cancel()
        print(f"Trip cancelled: {trip_id}")
    
    def rate_driver(self, trip_id: str, stars: int) -> None:
        trip = self._trips.get(trip_id)
        if not trip:
            raise ValueError(f"Trip not found: {trip_id}")
        trip.rate_driver(stars)
        print(f"Driver rated: {stars} stars")
    
    # Getters
    def get_rider(self, id: str) -> Optional[Rider]:
        return self._riders.get(id)
    
    def get_driver(self, id: str) -> Optional[Driver]:
        return self._drivers.get(id)
    
    def get_trip(self, id: str) -> Optional[Trip]:
        return self._trips.get(id)
    
    def get_available_drivers(self, vehicle_type: Optional[VehicleType] = None) -> List[Driver]:
        drivers = [d for d in self._drivers.values() if d.is_available()]
        if vehicle_type:
            drivers = [d for d in drivers if d.vehicle.type == vehicle_type]
        return drivers
