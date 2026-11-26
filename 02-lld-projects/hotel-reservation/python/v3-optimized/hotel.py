"""Hotel Singleton Controller - v3 Optimized."""
from typing import Dict, List, Optional
from datetime import date
from enums import RoomType, RoomStatus
from models import Guest, Room, Reservation
import threading


class Hotel:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, name: str = "Hotel"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.name = name
                cls._instance.rooms: Dict[str, Room] = {}
                cls._instance.reservations: Dict[str, Reservation] = {}
                cls._instance.guests: Dict[str, Guest] = {}
                cls._instance._booking_lock = threading.RLock()
            return cls._instance
            
    def reset_instance(self):
        with self._lock:
            Hotel._instance = None
    
    def add_room(self, room: Room): 
        with self._booking_lock:
            self.rooms[room.room_number] = room
            
    def register_guest(self, guest: Guest): 
        with self._booking_lock:
            self.guests[guest.guest_id] = guest
    
    def search_available(self, check_in: date, check_out: date, 
                         room_type: Optional[RoomType] = None) -> List[Room]:
        with self._booking_lock:
            available = []
            for room in self.rooms.values():
                if room.status == RoomStatus.AVAILABLE:
                    if room_type is None or room.room_type == room_type:
                        if self._is_available(room, check_in, check_out):
                            available.append(room)
            return available
    
    def _is_available(self, room: Room, check_in: date, check_out: date) -> bool:
        for res in self.reservations.values():
            if room in res.rooms:
                if not (check_out <= res.check_in_date or check_in >= res.check_out_date):
                    return False
        return True
    
    def make_reservation(self, guest: Guest, rooms: List[Room], 
                        check_in: date, check_out: date) -> Optional[Reservation]:
        with self._booking_lock:
            for room in rooms:
                if not self._is_available(room, check_in, check_out):
                    print(f"Room {room.room_number} not available")
                    return None
                    
            res = Reservation(guest, rooms, check_in, check_out)
            self.reservations[res.reservation_id] = res
            print(f"Created: {res}")
            return res
    
    def check_in(self, res_id: str):
        with self._booking_lock:
            res = self.reservations.get(res_id)
            if res:
                res.check_in()
                for room in res.rooms:
                    room.status = RoomStatus.OCCUPIED
                print(f"Checked in: {res.guest.name}")
    
    def check_out(self, res_id: str):
        with self._booking_lock:
            res = self.reservations.get(res_id)
            if res:
                res.check_out()
                for room in res.rooms:
                    room.status = RoomStatus.CLEANING
                print(f"Checked out: {res.guest.name} - Total: ${res.total_amount}")
