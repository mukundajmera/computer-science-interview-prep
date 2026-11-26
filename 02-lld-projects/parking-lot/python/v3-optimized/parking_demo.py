"""
Parking Lot System - V1 Basic Demo

Demonstrates the basic functionality of the parking lot system.
"""
from vehicle import VehicleFactory, VehicleType
from parking_lot import ParkingLot


def main():
    print("=== Parking Lot System Demo ===\n")

    # Reset and get parking lot instance
    ParkingLot.reset_instance()
    parking_lot = ParkingLot.get_instance("Downtown Parking")

    # Add floors with different spot configurations
    # Floor 1: 10 motorcycle, 20 compact, 5 large spots
    parking_lot.add_floor(10, 20, 5)
    # Floor 2: 10 motorcycle, 20 compact, 5 large spots
    parking_lot.add_floor(10, 20, 5)

    # Display initial status
    parking_lot.display_status()

    # Create some vehicles
    car1 = VehicleFactory.create_vehicle(VehicleType.CAR, "CAR-001")
    car2 = VehicleFactory.create_vehicle(VehicleType.CAR, "CAR-002")
    motorcycle1 = VehicleFactory.create_vehicle(VehicleType.MOTORCYCLE, "MOTO-001")
    truck1 = VehicleFactory.create_vehicle(VehicleType.TRUCK, "TRUCK-001")

    print("\n--- Parking Vehicles ---\n")

    # Park vehicles
    ticket1 = parking_lot.park_vehicle(car1)
    ticket2 = parking_lot.park_vehicle(car2)
    ticket3 = parking_lot.park_vehicle(motorcycle1)
    ticket4 = parking_lot.park_vehicle(truck1)

    # Display tickets
    print("\n--- Issued Tickets ---")
    print(ticket1)
    print(ticket2)
    print(ticket3)
    print(ticket4)

    # Find a vehicle
    print("\n--- Finding Vehicle ---")
    found_spot = parking_lot.find_vehicle("CAR-001")
    if found_spot:
        print(f"Found CAR-001 at: {found_spot.spot_id}")

    # Display status after parking
    parking_lot.display_status()

    # Try to park the same vehicle again
    print("\n--- Attempting Double Park ---")
    duplicate_ticket = parking_lot.park_vehicle(car1)
    print(f"Duplicate ticket: {duplicate_ticket}")

    # Unpark a vehicle
    print("\n--- Unparking Vehicle ---")
    fee = parking_lot.unpark_vehicle(ticket1)
    print(f"Paid fee: ${fee:.2f}")

    # Display final status
    parking_lot.display_status()

    # Unpark remaining vehicles
    print("\n--- Unparking Remaining Vehicles ---")
    parking_lot.unpark_vehicle(ticket2)
    parking_lot.unpark_vehicle(ticket3)
    parking_lot.unpark_vehicle(ticket4)

    # Final status
    parking_lot.display_status()

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
