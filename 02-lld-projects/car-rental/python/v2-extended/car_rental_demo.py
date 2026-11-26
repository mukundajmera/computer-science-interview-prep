"""
Car Rental V1 Basic - Demo
"""

from datetime import date, timedelta
from car_rental import (
    RentalService, Vehicle, VehicleType
)


def main():
    print("=== Car Rental V1 (Basic) Demo ===\n")

    RentalService.reset_instance()
    service = RentalService()

    # Add vehicles
    service.add_vehicle(Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0))
    service.add_vehicle(Vehicle("V2", "DEF-456", "Honda", "CR-V", VehicleType.SUV, 75.0))
    service.add_vehicle(Vehicle("V3", "GHI-789", "Ford", "F-150", VehicleType.TRUCK, 85.0))

    print("Vehicles added to inventory")

    # Register customer
    john = service.register_customer("C1", "John Doe", "john@email.com", "DL123456")
    print(f"Customer registered: {john.name}")

    # Search for available SUVs
    print("\n--- Searching for SUVs ---")
    available_suvs = service.search_available(VehicleType.SUV)
    for v in available_suvs:
        print(f"  Available: {v}")

    # Make reservation
    suv = available_suvs[0]
    start = date.today()
    end = start + timedelta(days=5)

    reservation = service.make_reservation(john, suv, start, end)
    print(f"\n--- Reservation Created ---")
    print(f"Reservation ID: {reservation.reservation_id}")
    print(f"Vehicle: {reservation.vehicle}")
    print(f"Duration: {start} to {end}")
    print(f"Total Cost: ${reservation.total_cost}")
    print(f"Status: {reservation.status.value}")

    # Check vehicle is no longer available
    print(f"\n--- After Reservation ---")
    print(f"Vehicle status: {suv.status.value}")
    print(f"Available SUVs: {len(service.search_available(VehicleType.SUV))}")

    # Pickup vehicle
    service.pickup_vehicle(reservation)
    print(f"\n--- After Pickup ---")
    print(f"Reservation status: {reservation.status.value}")
    print(f"Vehicle status: {suv.status.value}")

    # Return vehicle
    service.return_vehicle(reservation)
    print(f"\n--- After Return ---")
    print(f"Reservation status: {reservation.status.value}")
    print(f"Vehicle status: {suv.status.value}")
    print(f"Available SUVs: {len(service.search_available(VehicleType.SUV))}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
