"""
Parking Lot System - V3 Optimized

Thread-safe ParkingLot with concurrent parking operations.
"""
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import threading

from vehicle import Vehicle, VehicleType, Car, Motorcycle, Truck  # noqa: F401
from parking_spot import ParkingSpot
from floor import Floor
from ticket import Ticket


class PricingStrategy(ABC):
    """Interface for pricing strategies."""
    
    @abstractmethod
    def calculate_fee(self, ticket: Ticket) -> float:
        pass


class HourlyPricing(PricingStrategy):
    """Hourly pricing strategy - different rates for different vehicle types."""
    
    MOTORCYCLE_RATE = 1.0  # $1/hour
    CAR_RATE = 2.0         # $2/hour
    TRUCK_RATE = 4.0       # $4/hour
    
    def calculate_fee(self, ticket: Ticket) -> float:
        hours = ticket.get_duration_hours()
        vehicle_type = ticket.vehicle.vehicle_type
        
        if vehicle_type == VehicleType.MOTORCYCLE:
            rate = self.MOTORCYCLE_RATE
        elif vehicle_type == VehicleType.CAR:
            rate = self.CAR_RATE
        else:
            rate = self.TRUCK_RATE
        
        return hours * rate


class FlatRatePricing(PricingStrategy):
    """Flat rate pricing - same rate for all vehicles."""
    
    def __init__(self, daily_rate: float):
        self._daily_rate = daily_rate
    
    def calculate_fee(self, ticket: Ticket) -> float:
        hours = ticket.get_duration_hours()
        days = max(1, -(-hours // 24))  # Ceiling division
        return days * self._daily_rate


class ParkingLot:
    """Thread-safe parking lot system using Singleton pattern."""
    
    _instance: Optional['ParkingLot'] = None
    _create_lock = threading.Lock()
    
    def __new__(cls, name: str = "Main Parking Lot"):
        if cls._instance is None:
            with cls._create_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, name: str = "Main Parking Lot"):
        if self._initialized:
            return
        
        self._name = name
        self._floors: List[Floor] = []
        self._active_tickets: Dict[str, Ticket] = {}
        self._vehicle_to_spot: Dict[str, ParkingSpot] = {}
        self._pricing_strategy: PricingStrategy = HourlyPricing()
        self._dict_lock = threading.Lock()
        self._initialized = True
    
    @classmethod
    def get_instance(cls, name: str = "Main Parking Lot") -> 'ParkingLot':
        """Get the singleton instance."""
        return cls(name)
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (for testing only)."""
        cls._instance = None
    
    def add_floor(self, motorcycle_spots: int, compact_spots: int, 
                  large_spots: int) -> None:
        """Add a floor to the parking lot."""
        floor_number = len(self._floors) + 1
        self._floors.append(Floor(floor_number, motorcycle_spots, 
                                  compact_spots, large_spots))
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        """
        Thread-safe parking operation.
        Returns a ticket if successful, None if lot is full.
        """
        if vehicle is None:
            raise ValueError("Vehicle cannot be None")
        
        # Try to find a spot on any floor
        for floor in self._floors:
            spot = floor.park_vehicle(vehicle)
            if spot:
                with self._dict_lock:
                    if vehicle.license_plate in self._vehicle_to_spot:
                        # Vehicle is already parked. Rollback parking.
                        spot.unpark()
                        return None
                    
                    ticket = Ticket(vehicle, spot)
                    self._active_tickets[ticket.ticket_id] = ticket
                    self._vehicle_to_spot[vehicle.license_plate] = spot
                    return ticket
        
        return None
    
    def unpark_vehicle(self, ticket: Ticket) -> float:
        """
        Thread-safe unpark operation.
        Returns the parking fee.
        """
        if ticket is None:
            raise ValueError("Ticket cannot be None")
        
        with self._dict_lock:
            if ticket.ticket_id not in self._active_tickets:
                return -1
            
            # Remove from tracking
            del self._active_tickets[ticket.ticket_id]
            
            spot = ticket.spot
            # It's safe to unpark outside or inside, let's keep it under the lock for removal logic 
            # though unparking spot has its own lock.
            vehicle = spot.unpark()
            if vehicle and vehicle.license_plate in self._vehicle_to_spot:
                del self._vehicle_to_spot[vehicle.license_plate]
                
        # Calculate fee outside the lock
        ticket.set_exit_time()
        fee = self._pricing_strategy.calculate_fee(ticket)
        ticket.mark_paid()
        return fee
    
    def get_available_spots(self, vehicle_type: VehicleType) -> int:
        """Get the number of available spots for a vehicle type."""
        total = 0
        for floor in self._floors:
            total += floor.get_available_spots(vehicle_type)
        return total
    
    def find_vehicle(self, license_plate: str) -> Optional[ParkingSpot]:
        """Find a vehicle by license plate. Returns the parking spot if found."""
        return self._vehicle_to_spot.get(license_plate)
    
    def get_total_capacity(self) -> int:
        """Get the total capacity of the parking lot."""
        return sum(floor.get_total_capacity() for floor in self._floors)
    
    def is_full(self) -> bool:
        """Check if the parking lot is full."""
        return all(floor.is_full() for floor in self._floors)
    
    def display_status(self) -> None:
        """Display the status of the parking lot."""
        print(f"\n=== {self._name} Status ===")
        print(f"Total Floors: {len(self._floors)}")
        print(f"Total Capacity: {self.get_total_capacity()}")
        print(f"Active Vehicles: {len(self._active_tickets)}")
        print()
        
        for floor in self._floors:
            floor.display_status()
        
        print("\nAvailable by vehicle type:")
        print(f"  Motorcycles: {self.get_available_spots(VehicleType.MOTORCYCLE)}")
        print(f"  Cars: {self.get_available_spots(VehicleType.CAR)}")
        print(f"  Trucks: {self.get_available_spots(VehicleType.TRUCK)}")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def floor_count(self) -> int:
        return len(self._floors)
    
    @property
    def active_vehicle_count(self) -> int:
        return len(self._active_tickets)
