import enum
import math
import threading
from dataclasses import dataclass
from typing import Optional

class DriverState(enum.Enum):
    OFFLINE = "OFFLINE"
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    IN_TRIP = "IN_TRIP"

    @property
    def value_str(self):
        return self.value

class TripState(enum.Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    @property
    def value_str(self):
        return self.value

@dataclass
class Location:
    lat: float
    lon: float
    timestamp: float = 0.0

    def distance_to(self, other: 'Location') -> float:
        # Simple Euclidean distance for the sake of the engine simulation.
        # Alternatively, Haversine formula can be used.
        return math.hypot(self.lat - other.lat, self.lon - other.lon)

class Driver:
    def __init__(self, driver_id: str, location: Location):
        self.driver_id = driver_id
        self.location = location
        self.state = DriverState.OFFLINE
        self.lock = threading.RLock()

    def update_location(self, location: Location):
        with self.lock:
            if location.timestamp >= self.location.timestamp:
                self.location = location

    def transition_state(self, new_state: DriverState) -> bool:
        with self.lock:
            # FSM valid transitions
            valid = False
            if self.state == DriverState.OFFLINE and new_state == DriverState.IDLE:
                valid = True
            elif self.state == DriverState.IDLE and new_state == DriverState.ASSIGNED:
                valid = True
            elif self.state == DriverState.IDLE and new_state == DriverState.OFFLINE:
                valid = True
            elif self.state == DriverState.ASSIGNED and new_state == DriverState.IN_TRIP:
                valid = True
            elif self.state == DriverState.ASSIGNED and new_state == DriverState.IDLE:
                valid = True
            elif self.state == DriverState.IN_TRIP and new_state == DriverState.IDLE:
                valid = True
            elif self.state == DriverState.IN_TRIP and new_state == DriverState.OFFLINE:
                valid = True
            
            if valid:
                self.state = new_state
                return True
            return False

class Rider:
    def __init__(self, rider_id: str, location: Location):
        self.rider_id = rider_id
        self.location = location

class Trip:
    def __init__(self, trip_id: str, rider: Rider, origin: Location, destination: Location, price: float):
        self.trip_id = trip_id
        self.rider = rider
        self.driver: Optional[Driver] = None
        self.origin = origin
        self.destination = destination
        self.price = price
        self.state = TripState.REQUESTED
        self.lock = threading.RLock()

    def assign_driver(self, driver: Driver):
        with self.lock:
            if self.state == TripState.REQUESTED:
                self.driver = driver
                self.state = TripState.ACCEPTED
                return True
            return False
