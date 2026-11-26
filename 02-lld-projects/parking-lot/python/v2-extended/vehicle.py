"""
Parking Lot System - V2 Extended

Vehicle classes with Factory pattern for creation.
Supports Motorcycle, Car, and Truck types.
"""
from abc import ABC, abstractmethod
from enum import Enum


class VehicleType(Enum):
    """Enumeration of vehicle types supported by the parking lot."""
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    TRUCK = "TRUCK"


class Vehicle(ABC):
    """Abstract base class for all vehicles."""
    
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self._license_plate = license_plate
        self._type = vehicle_type
    
    @property
    def license_plate(self) -> str:
        return self._license_plate
    
    @property
    def vehicle_type(self) -> VehicleType:
        return self._type
    
    def __str__(self) -> str:
        return f"{self._type.value} [{self._license_plate}]"
    
    def __repr__(self) -> str:
        return self.__str__()


class Motorcycle(Vehicle):
    """Motorcycle - smallest vehicle type."""
    
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)


class Car(Vehicle):
    """Car - medium-sized vehicle type."""
    
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)


class Truck(Vehicle):
    """Truck - largest vehicle type."""
    
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)


class VehicleFactory:
    """Factory for creating vehicles based on type."""
    
    @staticmethod
    def create_vehicle(vehicle_type: VehicleType, license_plate: str) -> Vehicle:
        if vehicle_type == VehicleType.MOTORCYCLE:
            return Motorcycle(license_plate)
        elif vehicle_type == VehicleType.CAR:
            return Car(license_plate)
        elif vehicle_type == VehicleType.TRUCK:
            return Truck(license_plate)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
