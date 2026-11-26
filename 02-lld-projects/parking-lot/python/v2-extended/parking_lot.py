"""
Parking Lot System - V2 Extended

Extends V1 with reservation support, multiple payment methods,
and payment tracking.
"""
from typing import Dict, List, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

from vehicle import Vehicle, VehicleType, Car, Motorcycle, Truck  # noqa: F401
from parking_spot import ParkingSpot
from floor import Floor
from ticket import Ticket


class PaymentMethod(Enum):
    """Supported payment methods."""
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"


@dataclass
class Payment:
    """Payment record for a parking transaction."""
    amount: float
    method: PaymentMethod
    ticket_id: str


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
    """Main parking lot system using Singleton pattern."""
    
    _instance: Optional['ParkingLot'] = None
    
    def __new__(cls, name: str = "Main Parking Lot"):
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
        self._reservations: Dict[str, ParkingSpot] = {}
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
    
    def reserve_spot(self, license_plate: str, vehicle_type: VehicleType) -> Optional[ParkingSpot]:
        """
        Reserve a parking spot for a VIP vehicle.
        Returns the reserved spot if successful, None otherwise.
        """
        from vehicle import VehicleFactory
        temp_vehicle = VehicleFactory.create_vehicle(vehicle_type, "TEMP")
        for floor in self._floors:
            spot = floor.find_available_spot(temp_vehicle)
            if spot:
                spot.reserve(license_plate)
                self._reservations[license_plate] = spot
                return spot
        return None
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        """
        Park a vehicle in the lot.
        Returns a ticket if successful, None if lot is full.
        Checks for reservations first.
        """
        if vehicle is None:
            raise ValueError("Vehicle cannot be None")
        
        # Check if vehicle is already parked
        if vehicle.license_plate in self._vehicle_to_spot:
            print(f"Vehicle {vehicle.license_plate} is already parked")
            return None
        
        # Check for reservation
        if vehicle.license_plate in self._reservations:
            spot = self._reservations[vehicle.license_plate]
            if not spot.park(vehicle):
                print(f"Failed to park in reserved spot {spot.spot_id}")
                return None
            ticket = Ticket(vehicle, spot, is_reservation=True)
            self._active_tickets[ticket.ticket_id] = ticket
            self._vehicle_to_spot[vehicle.license_plate] = spot
            del self._reservations[vehicle.license_plate]
            print(f"VIP vehicle parked at reserved spot {spot.spot_id}")
            return ticket
        
        # Try to find a spot on any floor
        for floor in self._floors:
            spot = floor.park_vehicle(vehicle)
            if spot:
                ticket = Ticket(vehicle, spot)
                self._active_tickets[ticket.ticket_id] = ticket
                self._vehicle_to_spot[vehicle.license_plate] = spot
                
                print(f"Vehicle parked successfully at {spot.spot_id}")
                return ticket
        
        print(f"No available spot for {vehicle.vehicle_type.value}")
        return None
    
    def unpark_vehicle(self, ticket: Ticket, 
                       payment_method: Optional['PaymentMethod'] = None) -> Union['Payment', float]:
        """
        Unpark a vehicle using the ticket.
        If payment_method is provided, returns a Payment object.
        Otherwise returns the parking fee as a float.
        """
        if ticket is None:
            raise ValueError("Ticket cannot be None")
        
        if ticket.ticket_id not in self._active_tickets:
            print("Invalid or already used ticket")
            return -1
        
        # Calculate fee
        ticket.set_exit_time()
        fee = self._pricing_strategy.calculate_fee(ticket)
        
        # Free the spot
        spot = ticket.spot
        vehicle = spot.unpark()
        
        # Remove from tracking
        del self._active_tickets[ticket.ticket_id]
        del self._vehicle_to_spot[vehicle.license_plate]
        
        ticket.mark_paid()
        print(f"Vehicle unparked. Fee: ${fee:.2f}")
        
        if payment_method is not None:
            return Payment(amount=fee, method=payment_method,
                           ticket_id=ticket.ticket_id)
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
