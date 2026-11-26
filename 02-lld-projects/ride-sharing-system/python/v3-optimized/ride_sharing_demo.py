"""
Ride Sharing System - V1 Basic Demo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ride_sharing_entities import (
    Location, Vehicle, VehicleType, RideSharingService
)


def main():
    """Demonstrate basic ride sharing functionality."""
    
    print("=" * 60)
    print("Ride Sharing System - V1 Basic Demo")
    print("=" * 60)
    
    # Reset for clean demo
    RideSharingService.reset_instance()
    service = RideSharingService()
    
    # Register riders
    print("\n1. Registering riders...")
    alice = service.register_rider("Alice", "555-0101")
    bob = service.register_rider("Bob", "555-0102")
    print(f"   Registered: {alice}")
    print(f"   Registered: {bob}")
    
    # Register drivers with vehicles
    print("\n2. Registering drivers...")
    car1 = Vehicle("V1", VehicleType.CAR, "ABC-1234")
    car2 = Vehicle("V2", VehicleType.CAR, "XYZ-5678")
    bike1 = Vehicle("V3", VehicleType.BIKE, "BIKE-001")
    
    john = service.register_driver("John", "555-0201", car1)
    mike = service.register_driver("Mike", "555-0202", car2)
    sam = service.register_driver("Sam", "555-0203", bike1)
    
    # Set driver locations and availability
    john.update_location(Location(12.9, 77.6))
    john.set_available()
    
    mike.update_location(Location(12.8, 77.5))
    mike.set_available()
    
    sam.update_location(Location(12.85, 77.55))
    sam.set_available()
    
    print(f"   Registered: {john} at {john.current_location}")
    print(f"   Registered: {mike} at {mike.current_location}")
    print(f"   Registered: {sam} at {sam.current_location}")
    
    # Show available drivers
    print("\n3. Available drivers:")
    for d in service.get_available_drivers():
        print(f"   - {d}")
    
    # Alice requests a ride
    print("\n4. Alice requests a CAR ride...")
    pickup1 = Location(12.85, 77.55)
    dropoff1 = Location(12.95, 77.65)
    
    trip1 = service.request_ride(alice.id, pickup1, dropoff1, VehicleType.CAR)
    print(f"   Trip created: {trip1}")
    print(f"   Estimated fare: {trip1.get_estimated_fare()}")
    
    # Start trip
    print("\n5. Starting trip...")
    service.start_trip(trip1.id)
    print(f"   Trip status: {trip1.status.value}")
    
    # Complete trip
    print("\n6. Completing trip (15 minutes)...")
    service.complete_trip(trip1.id, 15)
    trip1.fare.display()
    
    # Rate driver
    print("\n7. Alice rates driver...")
    service.rate_driver(trip1.id, 5)
    print(f"   Driver {trip1.driver.name} rating: {trip1.driver.rating:.1f}")
    
    # Bob requests a BIKE ride
    print("\n8. Bob requests a BIKE ride...")
    pickup2 = Location(12.82, 77.52)
    dropoff2 = Location(12.88, 77.58)
    
    trip2 = service.request_ride(bob.id, pickup2, dropoff2, VehicleType.BIKE)
    print(f"   Trip: {trip2}")
    
    # Start and complete
    service.start_trip(trip2.id)
    service.complete_trip(trip2.id, 10)
    service.rate_driver(trip2.id, 4)
    
    # Show trip history
    print("\n9. Trip history:")
    print(f"   Alice's trips: {len(alice.trip_history)}")
    print(f"   Bob's trips: {len(bob.trip_history)}")
    
    # Test cancellation
    print("\n10. Testing cancellation...")
    try:
        service.cancel_trip(trip1.id)
    except ValueError:
        print("    Cannot cancel completed trip (expected)")
    
    # New ride and cancel before start
    trip3 = service.request_ride(alice.id, pickup1, dropoff1, VehicleType.CAR)
    service.cancel_trip(trip3.id)
    print(f"    Cancelled pending trip: {trip3.status.value}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
