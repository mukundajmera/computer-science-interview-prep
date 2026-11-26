"""Ride Sharing System Python Module."""
from enum import Enum
from typing import Dict, Optional
import math

class RideStatus(Enum):
    REQUESTED = "REQUESTED"
    MATCHED = "MATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Location:
    def __init__(self, lat: float, lng: float, address: str):
        self.latitude = lat
        self.longitude = lng
        self.address = address
    
    def distance_to(self, other: 'Location') -> float:
        lat_diff = abs(self.latitude - other.latitude)
        lng_diff = abs(self.longitude - other.longitude)
        return math.sqrt(lat_diff**2 + lng_diff**2) * 111
    
    def __str__(self): return self.address

class Driver:
    def __init__(self, id: str, name: str, vehicle: str):
        self.id = id
        self.name = name
        self.vehicle = vehicle
        self.location: Optional[Location] = None
        self.is_available = True

class Rider:
    def __init__(self, id: str, name: str, phone: str):
        self.id = id
        self.name = name
        self.phone = phone

class Ride:
    BASE_FARE = 5.0
    PER_KM = 2.0
    
    def __init__(self, id: str, rider: Rider, pickup: Location, dropoff: Location):
        self.id = id
        self.rider = rider
        self.driver: Optional[Driver] = None
        self.pickup = pickup
        self.dropoff = dropoff
        self.status = RideStatus.REQUESTED
        self.fare = self.BASE_FARE + (pickup.distance_to(dropoff) * self.PER_KM)
    
    def assign_driver(self, d: Driver):
        self.driver = d
        self.status = RideStatus.MATCHED
    
    def complete(self): self.status = RideStatus.COMPLETED

class RideService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.drivers: Dict[str, Driver] = {}
            cls._instance.riders: Dict[str, Rider] = {}
            cls._instance.rides: Dict[str, Ride] = {}
            cls._instance._ride_counter = 0
        return cls._instance
    
    def register_driver(self, d: Driver): self.drivers[d.id] = d
    def register_rider(self, r: Rider): self.riders[r.id] = r
    
    def request_ride(self, rider_id: str, pickup: Location, dropoff: Location):
        rider = self.riders.get(rider_id)
        if not rider: return None
        
        self._ride_counter += 1
        ride = Ride(f"RIDE-{self._ride_counter}", rider, pickup, dropoff)
        self.rides[ride.id] = ride
        
        # Match nearest driver
        driver = self._find_nearest(pickup)
        if driver:
            ride.assign_driver(driver)
            driver.is_available = False
            print(f"Matched: {driver.name}")
        
        return ride
    
    def _find_nearest(self, pickup: Location) -> Optional[Driver]:
        nearest = None
        min_dist = float('inf')
        for d in self.drivers.values():
            if d.is_available and d.location:
                dist = d.location.distance_to(pickup)
                if dist < min_dist:
                    min_dist = dist
                    nearest = d
        return nearest
    
    def complete_ride(self, ride_id: str):
        ride = self.rides.get(ride_id)
        if ride and ride.driver:
            ride.complete()
            ride.driver.is_available = True
            print(f"Ride completed. Fare: ${ride.fare:.2f}")
