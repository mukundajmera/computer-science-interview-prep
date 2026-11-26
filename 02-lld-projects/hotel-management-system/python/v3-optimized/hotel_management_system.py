from enum import Enum
from typing import List, Dict, Optional
import uuid
import threading

class HousekeepingStatus(Enum):
    CLEAN = "CLEAN"
    DIRTY = "DIRTY"
    INSPECTED = "INSPECTED"

class RoomType(Enum):
    STANDARD = "STANDARD"
    DELUXE = "DELUXE"
    SUITE = "SUITE"

class Room:
    def __init__(self, room_id: str, room_type: RoomType):
        self.room_id = room_id
        self.room_type = room_type
        self.status = HousekeepingStatus.CLEAN
        self.is_occupied = False
        self.lock = threading.Lock()

    def mark_dirty(self):
        with self.lock:
            self.status = HousekeepingStatus.DIRTY

    def mark_clean(self):
        with self.lock:
            self.status = HousekeepingStatus.CLEAN

    def mark_inspected(self):
        with self.lock:
            self.status = HousekeepingStatus.INSPECTED

import datetime

class Charge:
    def __init__(self, description: str, amount: float):
        self.timestamp = datetime.datetime.now()
        self.description = description
        self.amount = amount

class Folio:
    def __init__(self, stay_id: str):
        self.stay_id = stay_id
        self.charges: List[Charge] = []
        self.balance = 0.0
        self.lock = threading.Lock()

    def add_charge(self, charge: Charge):
        with self.lock:
            self.charges.append(charge)
            self.balance += charge.amount

    def process_payment(self, amount: float):
        with self.lock:
            if amount <= self.balance:
                self.balance -= amount
            else:
                raise ValueError("Overpayment not allowed")

class RoomKey:
    def __init__(self, room_id: str):
        self.key_id = str(uuid.uuid4())
        self.room_id = room_id
        self.is_active = True

    def deactivate(self):
        self.is_active = False

class Stay:
    def __init__(self, guest_name: str, room: Room):
        self.stay_id = str(uuid.uuid4())
        self.guest_name = guest_name
        self.room = room
        self.folio = Folio(self.stay_id)
        self.keys: List[RoomKey] = []
        self.lock = threading.Lock()

    def issue_key(self) -> RoomKey:
        with self.lock:
            key = RoomKey(self.room.room_id)
            self.keys.append(key)
            return key

    def deactivate_keys(self):
        with self.lock:
            for key in self.keys:
                key.deactivate()

class HotelManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.active_stays: Dict[str, Stay] = {} # room_id -> Stay
        self.manager_lock = threading.Lock()

    def add_room(self, room: Room):
        with self.manager_lock:
            self.rooms[room.room_id] = room

    def check_in(self, reservation_id: str, guest_name: str, room_type: RoomType) -> Optional[Stay]:
        with self.manager_lock:
            for room in self.rooms.values():
                with room.lock:
                    if room.room_type == room_type and not room.is_occupied and room.status == HousekeepingStatus.INSPECTED:
                        room.is_occupied = True
                        stay = Stay(guest_name, room)
                        self.active_stays[room.room_id] = stay
                        return stay
        return None

    def post_charge(self, room_id: str, description: str, amount: float):
        with self.manager_lock:
            stay = self.active_stays.get(room_id)
        if stay:
            charge = Charge(description, amount)
            stay.folio.add_charge(charge)
        else:
            raise ValueError("Room is not occupied")

    def settle_folio(self, room_id: str, amount: float):
        with self.manager_lock:
            stay = self.active_stays.get(room_id)
        if stay:
            stay.folio.process_payment(amount)
        else:
            raise ValueError("Room is not occupied")

    def check_out(self, room_id: str):
        with self.manager_lock:
            stay = self.active_stays.get(room_id)
            if not stay:
                raise ValueError("Room is not occupied")
            
            # Need to ensure no one is modifying folio balance while checking out
            with stay.folio.lock:
                if stay.folio.balance > 0:
                    raise ValueError("Folio must be settled before check-out")
                
            stay.deactivate_keys()
            with stay.room.lock:
                stay.room.is_occupied = False
                stay.room.status = HousekeepingStatus.DIRTY
            del self.active_stays[room_id]

    def update_housekeeping_status(self, room_id: str, status: HousekeepingStatus):
        room = self.rooms.get(room_id)
        if room:
            with room.lock:
                room.status = status
