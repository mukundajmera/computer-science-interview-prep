"""
Factory Method Pattern - V2 Variant (Parameterized Factory)

Common variation where a single factory method accepts a parameter
to determine which product to create.

This is more Pythonic than the classic inheritance-based approach.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional


# Product interface
class Vehicle(ABC):
    """Abstract vehicle interface."""
    
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    @property
    @abstractmethod
    def wheels(self) -> int:
        pass
    
    @property
    @abstractmethod
    def vehicle_type(self) -> str:
        pass


# Concrete Products
class Car(Vehicle):
    """Car implementation."""
    
    def __init__(self, model: str):
        self.model = model
    
    def start(self) -> None:
        print(f"{self.model} car engine started")
    
    def stop(self) -> None:
        print(f"{self.model} car engine stopped")
    
    @property
    def wheels(self) -> int:
        return 4
    
    @property
    def vehicle_type(self) -> str:
        return f"Car: {self.model}"


class Motorcycle(Vehicle):
    """Motorcycle implementation."""
    
    def __init__(self, brand: str):
        self.brand = brand
    
    def start(self) -> None:
        print(f"{self.brand} motorcycle revving up!")
    
    def stop(self) -> None:
        print(f"{self.brand} motorcycle stopped")
    
    @property
    def wheels(self) -> int:
        return 2
    
    @property
    def vehicle_type(self) -> str:
        return f"Motorcycle: {self.brand}"


class Truck(Vehicle):
    """Truck implementation."""
    
    def __init__(self, capacity_tons: int):
        self.capacity = capacity_tons
    
    def start(self) -> None:
        print(f"{self.capacity}-ton truck starting...")
    
    def stop(self) -> None:
        print("Truck stopped")
    
    @property
    def wheels(self) -> int:
        return 18 if self.capacity > 10 else 6
    
    @property
    def vehicle_type(self) -> str:
        return f"Truck: {self.capacity} tons"


# Vehicle types enum
class VehicleType(Enum):
    CAR = auto()
    MOTORCYCLE = auto()
    TRUCK = auto()


# Parameterized Factory
class VehicleFactory:
    """Factory with parameterized creation method."""
    
    def create_vehicle(self, vehicle_type: VehicleType, config: str) -> Vehicle:
        """Parameterized factory method."""
        if vehicle_type == VehicleType.CAR:
            return Car(config)
        elif vehicle_type == VehicleType.MOTORCYCLE:
            return Motorcycle(config)
        elif vehicle_type == VehicleType.TRUCK:
            return Truck(int(config))
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
    
    # Convenience methods
    def create_car(self, model: str) -> Car:
        return Car(model)
    
    def create_motorcycle(self, brand: str) -> Motorcycle:
        return Motorcycle(brand)
    
    def create_truck(self, capacity_tons: int) -> Truck:
        return Truck(capacity_tons)


# Demo
if __name__ == "__main__":
    print("=== Parameterized Factory Demo ===\n")
    
    factory = VehicleFactory()
    
    # Create vehicles using parameterized factory method
    car = factory.create_vehicle(VehicleType.CAR, "Tesla Model S")
    bike = factory.create_vehicle(VehicleType.MOTORCYCLE, "Harley Davidson")
    truck = factory.create_vehicle(VehicleType.TRUCK, "20")
    
    # Use vehicles
    print("--- Testing Vehicles ---")
    
    for vehicle in [car, bike, truck]:
        print(f"\nVehicle: {vehicle.vehicle_type}")
        print(f"Wheels: {vehicle.wheels}")
        vehicle.start()
        vehicle.stop()
    
    print("\n--- Using Convenience Methods ---")
    
    sedan = factory.create_car("Honda Accord")
    sportbike = factory.create_motorcycle("Ducati")
    heavy_truck = factory.create_truck(30)
    
    print(f"{sedan.vehicle_type} has {sedan.wheels} wheels")
    print(f"{sportbike.vehicle_type} has {sportbike.wheels} wheels")
    print(f"{heavy_truck.vehicle_type} has {heavy_truck.wheels} wheels")
