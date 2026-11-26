"""
Parking Lot System - V2 Extended

Ticket class with reservation support.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from vehicle import Vehicle
from parking_spot import ParkingSpot


class TicketStatus(Enum):
    """Enumeration of ticket statuses."""
    ACTIVE = "ACTIVE"      # Vehicle is parked
    PAID = "PAID"          # Fee has been paid
    LOST = "LOST"          # Ticket was lost


class Ticket:
    """Represents a parking ticket issued when a vehicle enters."""
    
    def __init__(self, vehicle: Vehicle, spot: ParkingSpot,
                 is_reservation: bool = False):
        self._ticket_id = self._generate_ticket_id()
        self._vehicle = vehicle
        self._spot = spot
        self._entry_time = datetime.now()
        self._exit_time: Optional[datetime] = None
        self._status = TicketStatus.ACTIVE
        self._is_reservation = is_reservation
    
    def _generate_ticket_id(self) -> str:
        """Generate a unique ticket ID."""
        return f"TKT-{uuid.uuid4().hex[:8].upper()}"
    
    def get_duration_hours(self) -> int:
        """Calculate the parking duration in hours (rounded up)."""
        end_time = self._exit_time if self._exit_time else datetime.now()
        duration = end_time - self._entry_time
        total_seconds = duration.total_seconds()
        hours = int(total_seconds // 3600)
        # Round up if there are remaining minutes/seconds
        if total_seconds % 3600 > 0:
            hours += 1
        return max(1, hours)  # Minimum 1 hour
    
    def set_exit_time(self) -> None:
        """Mark the ticket as exited."""
        self._exit_time = datetime.now()
    
    def mark_paid(self) -> None:
        """Mark the ticket as paid."""
        self._status = TicketStatus.PAID
    
    def mark_lost(self) -> None:
        """Mark the ticket as lost."""
        self._status = TicketStatus.LOST
    
    @property
    def ticket_id(self) -> str:
        return self._ticket_id
    
    @property
    def vehicle(self) -> Vehicle:
        return self._vehicle
    
    @property
    def spot(self) -> ParkingSpot:
        return self._spot
    
    @property
    def entry_time(self) -> datetime:
        return self._entry_time
    
    @property
    def exit_time(self) -> Optional[datetime]:
        return self._exit_time
    
    @property
    def status(self) -> TicketStatus:
        return self._status
    
    @property
    def is_reservation(self) -> bool:
        return self._is_reservation
    
    def __str__(self) -> str:
        return (f"Ticket[{self._ticket_id}, {self._vehicle}, "
                f"Spot: {self._spot.spot_id}, Entry: {self._entry_time}, "
                f"Status: {self._status.value}]")
