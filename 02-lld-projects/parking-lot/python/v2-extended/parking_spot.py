"""
Parking Lot System - V2 Extended

ParkingSpot class with reservation support.
"""
from enum import Enum
from typing import Optional
from vehicle import Vehicle, VehicleType


class SpotType(Enum):
    """Enumeration of parking spot types."""
    MOTORCYCLE_SPOT = "MOTORCYCLE_SPOT"  # Fits: Motorcycle only
    COMPACT_SPOT = "COMPACT_SPOT"        # Fits: Motorcycle, Car
    LARGE_SPOT = "LARGE_SPOT"            # Fits: Motorcycle, Car, Truck


class ParkingSpot:
    """Represents an individual parking spot with reservation support."""
    
    def __init__(self, spot_id: str, spot_type: SpotType, floor_number: int):
        self._spot_id = spot_id
        self._spot_type = spot_type
        self._floor_number = floor_number
        self._vehicle: Optional[Vehicle] = None
        self._is_occupied = False
        self._is_reserved = False
        self._reserved_for: Optional[str] = None
    
    def can_fit(self, vehicle: Vehicle) -> bool:
        """Check if this spot can fit the given vehicle type."""
        if vehicle is None:
            return False
        
        vehicle_type = vehicle.vehicle_type
        
        if self._spot_type == SpotType.MOTORCYCLE_SPOT:
            return vehicle_type == VehicleType.MOTORCYCLE
        elif self._spot_type == SpotType.COMPACT_SPOT:
            return vehicle_type in (VehicleType.MOTORCYCLE, VehicleType.CAR)
        elif self._spot_type == SpotType.LARGE_SPOT:
            return True  # Fits all vehicle types
        return False
    
    def park(self, vehicle: Vehicle) -> bool:
        """
        Park a vehicle in this spot.
        Returns True if successful, False otherwise.
        Rejects parking if the spot is reserved for a different vehicle.
        """
        if self._is_occupied or not self.can_fit(vehicle):
            return False
        if self._is_reserved and self._reserved_for != vehicle.license_plate:
            return False
        self._vehicle = vehicle
        self._is_occupied = True
        return True
    
    def unpark(self) -> Optional[Vehicle]:
        """
        Remove the vehicle from this spot.
        Returns the vehicle that was parked, or None if empty.
        """
        if not self._is_occupied:
            return None
        parked_vehicle = self._vehicle
        self._vehicle = None
        self._is_occupied = False
        self._is_reserved = False
        self._reserved_for = None
        return parked_vehicle
    
    def reserve(self, license_plate: str) -> None:
        """Reserve this spot for a specific vehicle."""
        self._is_reserved = True
        self._reserved_for = license_plate
    
    @property
    def spot_id(self) -> str:
        return self._spot_id
    
    @property
    def spot_type(self) -> SpotType:
        return self._spot_type
    
    @property
    def floor_number(self) -> int:
        return self._floor_number
    
    @property
    def vehicle(self) -> Optional[Vehicle]:
        return self._vehicle
    
    @property
    def is_available(self) -> bool:
        return not self._is_occupied and not self._is_reserved
    
    @property
    def is_occupied(self) -> bool:
        return self._is_occupied
    
    @property
    def is_reserved(self) -> bool:
        return self._is_reserved
    
    def __str__(self) -> str:
        status = f"Occupied by {self._vehicle}" if self._is_occupied else "Available"
        return f"Spot[{self._spot_id}, {self._spot_type.value}, {status}]"
