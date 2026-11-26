"""
Parking Lot System - V2 Extended

Floor class representing a parking floor with multiple spots.
"""
from typing import List, Optional

from vehicle import Vehicle, VehicleType, VehicleFactory
from parking_spot import ParkingSpot, SpotType


class Floor:
    """Represents a single floor in the parking lot."""
    
    def __init__(self, floor_number: int, motorcycle_spots: int, 
                 compact_spots: int, large_spots: int):
        self._floor_number = floor_number
        self._spots: List[ParkingSpot] = []
        
        self._initialize_spots(motorcycle_spots, compact_spots, large_spots)
    
    def _initialize_spots(self, motorcycle_spots: int, compact_spots: int, 
                          large_spots: int) -> None:
        """Initialize parking spots for this floor."""
        spot_number = 1
        
        # Create motorcycle spots
        for _ in range(motorcycle_spots):
            spot_id = f"F{self._floor_number}-M{spot_number:03d}"
            self._spots.append(ParkingSpot(spot_id, SpotType.MOTORCYCLE_SPOT, 
                                           self._floor_number))
            spot_number += 1
        
        # Create compact spots
        spot_number = 1
        for _ in range(compact_spots):
            spot_id = f"F{self._floor_number}-C{spot_number:03d}"
            self._spots.append(ParkingSpot(spot_id, SpotType.COMPACT_SPOT, 
                                           self._floor_number))
            spot_number += 1
        
        # Create large spots
        spot_number = 1
        for _ in range(large_spots):
            spot_id = f"F{self._floor_number}-L{spot_number:03d}"
            self._spots.append(ParkingSpot(spot_id, SpotType.LARGE_SPOT, 
                                           self._floor_number))
            spot_number += 1
    
    def _get_preferred_spot_type(self, vehicle_type: VehicleType) -> SpotType:
        """Get the preferred spot type for a vehicle type."""
        if vehicle_type == VehicleType.MOTORCYCLE:
            return SpotType.MOTORCYCLE_SPOT
        elif vehicle_type == VehicleType.CAR:
            return SpotType.COMPACT_SPOT
        else:
            return SpotType.LARGE_SPOT
    
    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """
        Find an available spot for the given vehicle.
        Returns None if no suitable spot is available.
        """
        preferred_type = self._get_preferred_spot_type(vehicle.vehicle_type)
        
        # First try to find exact match spot type
        for spot in self._spots:
            if spot.is_available and spot.spot_type == preferred_type:
                return spot
        
        # If no exact match, find any compatible spot
        for spot in self._spots:
            if spot.is_available and spot.can_fit(vehicle):
                return spot
        
        return None
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """
        Park a vehicle on this floor.
        Returns the assigned spot, or None if no spot available.
        """
        spot = self.find_available_spot(vehicle)
        if spot and spot.park(vehicle):
            return spot
        return None
    
    def unpark_vehicle(self, spot: ParkingSpot) -> Optional[Vehicle]:
        """Unpark a vehicle from the given spot."""
        return spot.unpark()
    
    def get_available_spots(self, vehicle_type: VehicleType) -> int:
        """Get the count of available spots for a vehicle type."""
        count = 0
        temp_vehicle = VehicleFactory.create_vehicle(vehicle_type, "TEMP")
        for spot in self._spots:
            if spot.is_available and spot.can_fit(temp_vehicle):
                count += 1
        return count
    
    def is_full(self) -> bool:
        """Check if the floor is full."""
        return all(spot.is_occupied for spot in self._spots)
    
    def get_total_capacity(self) -> int:
        """Get the total capacity of this floor."""
        return len(self._spots)
    
    def display_status(self) -> None:
        """Display floor status."""
        available = sum(1 for spot in self._spots if spot.is_available)
        occupied = sum(1 for spot in self._spots if spot.is_occupied)
        
        print(f"Floor {self._floor_number} Status:")
        print(f"  Total Spots: {len(self._spots)}")
        print(f"  Available: {available}")
        print(f"  Occupied: {occupied}")
    
    @property
    def floor_number(self) -> int:
        return self._floor_number
    
    @property
    def spots(self) -> List[ParkingSpot]:
        return self._spots.copy()
