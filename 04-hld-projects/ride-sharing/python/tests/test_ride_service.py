import os
import sys
from typing import Optional, Dict
import pytest

# Add v1-basic to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from ride_service import RideService, Ride, RideState, RequestRideCommand


class InMemoryRideService(RideService):
    def __init__(self):
        self.rides: Dict[str, Ride] = {}

    def request_ride(self, command: RequestRideCommand, idempotency_key: str) -> Ride:
        ride_id = f"ride_{idempotency_key}"
        if ride_id in self.rides:
            return self.rides[ride_id]
        
        ride = Ride(
            ride_id=ride_id,
            rider_id=command.rider_id,
            driver_id=None,
            state=RideState.REQUESTED
        )
        self.rides[ride_id] = ride
        return ride

    def accept_ride(self, ride_id: str, driver_id: str, idempotency_key: str) -> Ride:
        ride = self.rides.get(ride_id)
        if not ride:
            raise ValueError("Ride not found")
        if ride.state != RideState.REQUESTED and ride.state != RideState.MATCH_PENDING:
            raise ValueError("Ride cannot be accepted in its current state")
        
        updated_ride = Ride(
            ride_id=ride.ride_id,
            rider_id=ride.rider_id,
            driver_id=driver_id,
            state=RideState.MATCHED
        )
        self.rides[ride_id] = updated_ride
        return updated_ride

    def update_ride_state(self, ride_id: str, next_state: RideState) -> Ride:
        ride = self.rides.get(ride_id)
        if not ride:
            raise ValueError("Ride not found")
            
        updated_ride = Ride(
            ride_id=ride.ride_id,
            rider_id=ride.rider_id,
            driver_id=ride.driver_id,
            state=next_state
        )
        self.rides[ride_id] = updated_ride
        return updated_ride

    def get_ride(self, ride_id: str) -> Optional[Ride]:
        return self.rides.get(ride_id)


def test_request_ride_creates_new_ride():
    service = InMemoryRideService()
    command = RequestRideCommand(
        rider_id="rider_123",
        pickup_lat=37.7749,
        pickup_lng=-122.4194,
        dropoff_lat=37.3382,
        dropoff_lng=-121.8863
    )
    
    ride = service.request_ride(command, "idemp_abc")
    
    assert ride.ride_id == "ride_idemp_abc"
    assert ride.rider_id == "rider_123"
    assert ride.driver_id is None
    assert ride.state == RideState.REQUESTED
    
    # Verify idempotency
    ride_again = service.request_ride(command, "idemp_abc")
    assert ride_again == ride


def test_accept_ride_updates_driver_and_state():
    service = InMemoryRideService()
    command = RequestRideCommand(
        rider_id="rider_123",
        pickup_lat=37.7749,
        pickup_lng=-122.4194,
        dropoff_lat=37.3382,
        dropoff_lng=-121.8863
    )
    
    ride = service.request_ride(command, "idemp_abc")
    
    accepted_ride = service.accept_ride(ride.ride_id, "driver_456", "acc_idemp_1")
    
    assert accepted_ride.ride_id == ride.ride_id
    assert accepted_ride.rider_id == "rider_123"
    assert accepted_ride.driver_id == "driver_456"
    assert accepted_ride.state == RideState.MATCHED
    
    fetched_ride = service.get_ride(ride.ride_id)
    assert fetched_ride == accepted_ride


def test_update_ride_state_transitions_state_correctly():
    service = InMemoryRideService()
    command = RequestRideCommand(
        rider_id="rider_123",
        pickup_lat=37.7749,
        pickup_lng=-122.4194,
        dropoff_lat=37.3382,
        dropoff_lng=-121.8863
    )
    
    ride = service.request_ride(command, "idemp_abc")
    service.accept_ride(ride.ride_id, "driver_456", "acc_idemp_1")
    
    en_route_ride = service.update_ride_state(ride.ride_id, RideState.DRIVER_EN_ROUTE)
    assert en_route_ride.state == RideState.DRIVER_EN_ROUTE
    
    in_progress_ride = service.update_ride_state(ride.ride_id, RideState.IN_PROGRESS)
    assert in_progress_ride.state == RideState.IN_PROGRESS
    
    completed_ride = service.update_ride_state(ride.ride_id, RideState.COMPLETED)
    assert completed_ride.state == RideState.COMPLETED
    
    fetched_ride = service.get_ride(ride.ride_id)
    assert fetched_ride.state == RideState.COMPLETED
