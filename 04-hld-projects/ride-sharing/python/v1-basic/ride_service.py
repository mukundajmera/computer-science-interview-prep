from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Protocol


class RideState(str, Enum):
    REQUESTED = "requested"
    MATCH_PENDING = "match_pending"
    MATCHED = "matched"
    DRIVER_EN_ROUTE = "driver_en_route"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class RequestRideCommand:
    rider_id: str
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float


@dataclass(frozen=True)
class Ride:
    ride_id: str
    rider_id: str
    driver_id: Optional[str]
    state: RideState


@dataclass(frozen=True)
class DriverCandidate:
    driver_id: str
    eta_minutes: float


class LocationIndex(Protocol):
    def find_nearby(self, lat: float, lng: float, radius_km: float, limit: int) -> List[DriverCandidate]: ...


class RideService(Protocol):
    def request_ride(self, command: RequestRideCommand, idempotency_key: str) -> Ride: ...
    def accept_ride(self, ride_id: str, driver_id: str, idempotency_key: str) -> Ride: ...
    def update_ride_state(self, ride_id: str, next_state: RideState) -> Ride: ...
    def get_ride(self, ride_id: str) -> Optional[Ride]: ...
