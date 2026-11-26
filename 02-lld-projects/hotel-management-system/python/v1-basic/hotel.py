import threading
import uuid
import datetime
from enum import Enum
from typing import List, Dict, Optional

class HousekeepingStatus(Enum):
    CLEAN = "CLEAN"
    DIRTY = "DIRTY"
    INSPECTED = "INSPECTED"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class RoomType(Enum):
    STANDARD = "STANDARD"
    DELUXE = "DELUXE"
    SUITE = "SUITE"

class Room:
    def __init__(self, room_id: str, room_type: RoomType):
        self.room_id = room_id
        self.room_type = room_type
        self._status = HousekeepingStatus.CLEAN
        self._is_occupied = False
        self.lock = threading.Lock()

    @property
    def status(self) -> HousekeepingStatus:
        with self.lock:
            return self._status

    @status.setter
    def status(self, val: HousekeepingStatus):
        with self.lock:
            self._status = val

    @property
    def is_occupied(self) -> bool:
        with self.lock:
            return self._is_occupied

    @is_occupied.setter
    def is_occupied(self, val: bool):
        with self.lock:
            self._is_occupied = val

    def mark_dirty(self):
        with self.lock:
            self._status = HousekeepingStatus.DIRTY

    def mark_clean(self):
        with self.lock:
            self._status = HousekeepingStatus.CLEAN

    def mark_inspected(self):
        with self.lock:
            self._status = HousekeepingStatus.INSPECTED

class Charge:
    def __init__(self, description: str, amount: float):
        self.timestamp = datetime.datetime.now()
        self.description = description
        self.amount = amount

class Folio:
    def __init__(self, stay_id: str):
        self.stay_id = stay_id
        self.charges: List[Charge] = []
        self._balance_cents = 0
        self.lock = threading.Lock()

    @property
    def balance(self) -> float:
        with self.lock:
            return self._balance_cents / 100.0

    @balance.setter
    def balance(self, val: float):
        with self.lock:
            self._balance_cents = int(round(val * 100))

    def add_charge(self, charge: Charge):
        with self.lock:
            self.charges.append(charge)
            self._balance_cents += int(round(charge.amount * 100))

    def process_payment(self, amount: float):
        with self.lock:
            amount_cents = int(round(amount * 100))
            if amount_cents <= self._balance_cents:
                self._balance_cents -= amount_cents
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
        self.check_in_time = datetime.datetime.now()
        self.check_out_time = None

    def issue_key(self) -> RoomKey:
        key = RoomKey(self.room.room_id)
        self.keys.append(key)
        return key

    def deactivate_keys(self):
        self.check_out_time = datetime.datetime.now()
        for key in self.keys:
            key.deactivate()

class HotelManager:
    def __init__(self):
        # We need fine-grained locking similar to Java's ConcurrentHashMap
        # Since Python dicts are GIL-protected for simple ops, we wrap modifications
        # but avoid a global lock during iterations when fine-grained locks exist.
        self.rooms: Dict[str, Room] = {}
        self.active_stays: Dict[str, Stay] = {}
        self.rooms_lock = threading.Lock()
        self.active_stays_lock = threading.Lock()

    def add_room(self, room: Room):
        with self.rooms_lock:
            self.rooms[room.room_id] = room

    def check_in(self, reservation_id: str, guest_name: str, room_type: RoomType) -> Optional[Stay]:
        with self.rooms_lock:
            rooms_values = list(self.rooms.values())
        
        for room in rooms_values:
            with room.lock:
                if room.room_type == room_type and not room._is_occupied and room._status == HousekeepingStatus.INSPECTED:
                    room._is_occupied = True
                    stay = Stay(guest_name, room)
                    with self.active_stays_lock:
                        self.active_stays[room.room_id] = stay
                    return stay
        return None

    def post_charge(self, room_id: str, description: str, amount: float):
        with self.active_stays_lock:
            stay = self.active_stays.get(room_id)
        if stay:
            charge = Charge(description, amount)
            stay.folio.add_charge(charge)
        else:
            raise ValueError("Room is not occupied")

    def settle_folio(self, room_id: str, amount: float):
        with self.active_stays_lock:
            stay = self.active_stays.get(room_id)
        if stay:
            stay.folio.process_payment(amount)

    def check_out(self, room_id: str):
        with self.active_stays_lock:
            stay = self.active_stays.get(room_id)
            if stay:
                if stay.folio.balance > 0:
                    raise ValueError("Folio must be settled before check-out")
                del self.active_stays[room_id]
                
        if stay:
            stay.deactivate_keys()
            with stay.room.lock:
                stay.room._is_occupied = False
                stay.room._status = HousekeepingStatus.DIRTY

    def update_housekeeping_status(self, room_id: str, status: HousekeepingStatus):
        with self.rooms_lock:
            room = self.rooms.get(room_id)
        if room:
            with room.lock:
                room._status = status
