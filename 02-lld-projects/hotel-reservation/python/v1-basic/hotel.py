"""Hotel Singleton Controller."""
from typing import Dict, List, Optional
from datetime import date
from enums import RoomType, RoomStatus
from models import Guest, Room, Reservation


class Hotel:
    _instance = None
    
    def __new__(cls, name: str = "Hotel"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.name = name
            cls._instance.rooms: Dict[str, Room] = {}
            cls._instance.reservations: Dict[str, Reservation] = {}
            cls._instance.guests: Dict[str, Guest] = {}
        return cls._instance
    
    def add_room(self, room: Room): self.rooms[room.room_number] = room
    def register_guest(self, guest: Guest): self.guests[guest.guest_id] = guest
    
    def search_available(self, check_in: date, check_out: date, 
                         room_type: Optional[RoomType] = None) -> List[Room]:
        available = []
        for room in self.rooms.values():
            if room.status == RoomStatus.AVAILABLE:
                if room_type is None or room.room_type == room_type:
                    if self._is_available(room, check_in, check_out):
                        available.append(room)
        return available
    
    def _is_available(self, room: Room, check_in: date, check_out: date) -> bool:
        for res in self.reservations.values():
            if res.room == room:
                if not (check_out <= res.check_in_date or check_in >= res.check_out_date):
                    return False
        return True
    
    def make_reservation(self, guest: Guest, room: Room, 
                        check_in: date, check_out: date) -> Optional[Reservation]:
        if not self._is_available(room, check_in, check_out):
            print("Room not available")
            return None
        res = Reservation(guest, room, check_in, check_out)
        self.reservations[res.reservation_id] = res
        print(f"Created: {res}")
        return res
    
    def check_in(self, res_id: str):
        res = self.reservations.get(res_id)
        if res:
            res.check_in()
            res.room.status = RoomStatus.OCCUPIED
            print(f"Checked in: {res.guest.name}")
    
    def check_out(self, res_id: str):
        res = self.reservations.get(res_id)
        if res:
            res.check_out()
            res.room.status = RoomStatus.CLEANING
            print(f"Checked out: {res.guest.name} - Total: ${res.total_amount}")
