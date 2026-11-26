"""Hotel Reservation Models."""
from datetime import date, datetime
from typing import List, Set, Optional
import uuid

class Guest:
    def __init__(self, guest_id: str, name: str, email: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone
        self._reservations: List['Reservation'] = []
    
    def add_reservation(self, res: 'Reservation'): self._reservations.append(res)
    def __str__(self): return f"Guest[{self.guest_id}: {self.name}]"


class Room:
    def __init__(self, room_number: str, room_type, floor: int):
        from enums import RoomType, RoomStatus
        self.room_number = room_number
        self.room_type = room_type
        self.floor = floor
        self.base_price = room_type.base_price
        self.status = RoomStatus.AVAILABLE
        self.amenities: Set[str] = set()
    
    def __str__(self): return f"Room[{self.room_number}, {self.room_type.name}, ${self.base_price}/night]"


class Reservation:
    def __init__(self, guest: Guest, rooms: List[Room], check_in: date, check_out: date):
        from enums import ReservationStatus
        self.reservation_id = f"RES-{str(uuid.uuid4())[:8]}"
        self.guest = guest
        self.rooms = rooms
        self.check_in_date = check_in
        self.check_out_date = check_out
        self.status = ReservationStatus.PENDING
        self.total_amount = self._calculate_total()
    
    def _calculate_total(self) -> float:
        nights = (self.check_out_date - self.check_in_date).days
        total = 0.0
        for room in self.rooms:
            total += room.base_price * nights
        return total
    
    def confirm(self): 
        from enums import ReservationStatus
        self.status = ReservationStatus.CONFIRMED
    def check_in(self): 
        from enums import ReservationStatus
        self.status = ReservationStatus.CHECKED_IN
    def check_out(self): 
        from enums import ReservationStatus
        self.status = ReservationStatus.CHECKED_OUT
    
    def __str__(self): 
        rooms_str = ", ".join([r.room_number for r in self.rooms])
        return f"Reservation[{self.reservation_id}: {self.guest.name} -> [{rooms_str}]]"
