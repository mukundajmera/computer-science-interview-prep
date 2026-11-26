"""
Hotel Reservation System - v1 Basic Implementation
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import date, datetime
import uuid


class RoomType(Enum):
    SINGLE = (1, 100.0)
    DOUBLE = (2, 150.0)
    DELUXE = (3, 200.0)
    SUITE = (4, 350.0)
    
    def __init__(self, max_occupancy: int, base_price: float):
        self._max_occupancy = max_occupancy
        self._base_price = base_price
    
    @property
    def max_occupancy(self) -> int:
        return self._max_occupancy
    
    @property
    def base_price(self) -> float:
        return self._base_price


class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    CLEANING = "CLEANING"


class ReservationStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


class Guest:
    def __init__(self, guest_id: str, name: str, email: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone
        self._reservations: List['Reservation'] = []
    
    def add_reservation(self, reservation: 'Reservation') -> None:
        self._reservations.append(reservation)
    
    @property
    def reservations(self) -> List['Reservation']:
        return list(self._reservations)


class Room:
    def __init__(self, room_number: str, room_type: RoomType, floor: int):
        self.room_number = room_number
        self.room_type = room_type
        self.floor = floor
        self.base_price = room_type.base_price
        self.status = RoomStatus.AVAILABLE
        self.amenities: Set[str] = set()
    
    def __str__(self) -> str:
        return f"Room {self.room_number} ({self.room_type.name}) - ${self.base_price}/night"


class Reservation:
    def __init__(self, reservation_id: str, guest: Guest, room: Room,
                 check_in: date, check_out: date):
        self.reservation_id = reservation_id
        self.guest = guest
        self.room = room
        self.check_in_date = check_in
        self.check_out_date = check_out
        self.status = ReservationStatus.PENDING
        self.total_amount = self._calculate_total()
        self.created_at = datetime.now()
    
    def _calculate_total(self) -> float:
        nights = (self.check_out_date - self.check_in_date).days
        return nights * self.room.base_price
    
    @property
    def nights(self) -> int:
        return (self.check_out_date - self.check_in_date).days
    
    def confirm(self) -> None:
        if self.status == ReservationStatus.PENDING:
            self.status = ReservationStatus.CONFIRMED
    
    def check_in(self) -> None:
        if self.status == ReservationStatus.CONFIRMED:
            self.status = ReservationStatus.CHECKED_IN
            self.room.status = RoomStatus.OCCUPIED
    
    def check_out(self) -> None:
        if self.status == ReservationStatus.CHECKED_IN:
            self.status = ReservationStatus.CHECKED_OUT
            self.room.status = RoomStatus.CLEANING
    
    def cancel(self) -> None:
        if self.status in (ReservationStatus.PENDING, ReservationStatus.CONFIRMED):
            self.status = ReservationStatus.CANCELLED
    
    def __str__(self) -> str:
        return (f"Reservation[{self.reservation_id}]: {self.guest.name} in "
                f"Room {self.room.room_number} ({self.check_in_date} to {self.check_out_date}) "
                f"- ${self.total_amount:.2f} - {self.status.value}")


class Hotel:
    def __init__(self, hotel_id: str, name: str):
        self.hotel_id = hotel_id
        self.name = name
        self._rooms: Dict[str, Room] = {}
        self._reservations: Dict[str, Reservation] = {}
        self._guests: Dict[str, Guest] = {}
        self._room_bookings: Dict[str, Set[date]] = {}
        self._reservation_counter = 0
    
    def add_room(self, room: Room) -> None:
        self._rooms[room.room_number] = room
        self._room_bookings[room.room_number] = set()
    
    def _is_room_available(self, room: Room, check_in: date, check_out: date) -> bool:
        booked = self._room_bookings.get(room.room_number, set())
        current = check_in
        while current < check_out:
            if current in booked:
                return False
            current = date.fromordinal(current.toordinal() + 1)
        return True
    
    def _block_room(self, room: Room, check_in: date, check_out: date) -> None:
        booked = self._room_bookings[room.room_number]
        current = check_in
        while current < check_out:
            booked.add(current)
            current = date.fromordinal(current.toordinal() + 1)
    
    def _release_room(self, room: Room, check_in: date, check_out: date) -> None:
        booked = self._room_bookings[room.room_number]
        current = check_in
        while current < check_out:
            booked.discard(current)
            current = date.fromordinal(current.toordinal() + 1)
    
    def search_available_rooms(self, check_in: date, check_out: date,
                               room_type: Optional[RoomType] = None) -> List[Room]:
        available = []
        for room in self._rooms.values():
            if room_type and room.room_type != room_type:
                continue
            if self._is_room_available(room, check_in, check_out):
                available.append(room)
        return sorted(available, key=lambda r: r.base_price)
    
    def make_reservation(self, guest: Guest, room: Room,
                         check_in: date, check_out: date) -> Optional[Reservation]:
        if check_in >= check_out:
            print("Error: Invalid date range")
            return None
        
        if not self._is_room_available(room, check_in, check_out):
            print(f"Error: Room {room.room_number} not available")
            return None
        
        self._reservation_counter += 1
        res_id = f"RES-{check_in.year}-{self._reservation_counter:04d}"
        
        reservation = Reservation(res_id, guest, room, check_in, check_out)
        reservation.confirm()
        
        self._block_room(room, check_in, check_out)
        self._reservations[res_id] = reservation
        guest.add_reservation(reservation)
        
        if guest.guest_id not in self._guests:
            self._guests[guest.guest_id] = guest
        
        return reservation
    
    def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = self._reservations.get(reservation_id)
        if not reservation:
            return False
        
        if reservation.status == ReservationStatus.CHECKED_IN:
            return False
        
        self._release_room(reservation.room, reservation.check_in_date, 
                          reservation.check_out_date)
        reservation.cancel()
        return True
    
    def check_in(self, reservation_id: str) -> bool:
        reservation = self._reservations.get(reservation_id)
        if reservation and reservation.status == ReservationStatus.CONFIRMED:
            reservation.check_in()
            return True
        return False
    
    def check_out(self, reservation_id: str) -> bool:
        reservation = self._reservations.get(reservation_id)
        if reservation and reservation.status == ReservationStatus.CHECKED_IN:
            reservation.check_out()
            return True
        return False


def main():
    print("=== Hotel Reservation System v1 - Basic Demo ===\n")
    
    hotel = Hotel("H001", "Grand Hotel")
    
    # Add rooms
    hotel.add_room(Room("101", RoomType.SINGLE, 1))
    hotel.add_room(Room("201", RoomType.DOUBLE, 2))
    hotel.add_room(Room("301", RoomType.DELUXE, 3))
    hotel.add_room(Room("401", RoomType.SUITE, 4))
    
    # Create guest
    guest = Guest("G001", "John Smith", "john@email.com", "555-0101")
    
    # Search and book
    check_in = date.today().replace(day=date.today().day + 5)
    check_out = date.today().replace(day=date.today().day + 8)
    
    available = hotel.search_available_rooms(check_in, check_out, RoomType.DOUBLE)
    print(f"Available DOUBLE rooms: {len(available)}")
    
    if available:
        room = available[0]
        res = hotel.make_reservation(guest, room, check_in, check_out)
        print(f"Created: {res}")
        
        # Check-in and check-out
        hotel.check_in(res.reservation_id)
        print(f"After check-in: {res.status.value}")
        
        hotel.check_out(res.reservation_id)
        print(f"After check-out: {res.status.value}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
