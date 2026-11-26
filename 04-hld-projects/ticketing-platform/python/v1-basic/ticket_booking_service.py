
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Protocol

class SeatState(str, Enum):
    AVAILABLE = "AVAILABLE"
    HELD = "HELD"
    BOOKED = "BOOKED"

@dataclass
class Seat:
    seat_id: str
    event_id: str
    section: str
    row: str
    number: int
    state: SeatState = SeatState.AVAILABLE
    version: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

@dataclass
class SeatHold:
    hold_id: str
    user_id: str
    event_id: str
    seat_ids: List[str]
    expires_at: datetime

class EventRepository(Protocol):
    def search(self, city: str, category: str, start_at: datetime, end_at: datetime, page: int, page_size: int) -> List[Dict[str, str]]:
        ...

    def seat_map(self, event_id: str) -> List[Seat]:
        ...

    def get_seats_for_update(self, event_id: str, seat_ids: List[str]) -> List[Seat]:
        ...

class HoldRepository(Protocol):
    def save(self, hold: SeatHold) -> SeatHold:
        ...

    def find(self, hold_id: str) -> Optional[SeatHold]:
        ...

class BookingRepository(Protocol):
    def create(self, hold_id: str, user_id: str, idempotency_key: str) -> str:
        ...

    def find_by_idempotency_key(self, idempotency_key: str) -> Optional[str]:
        ...

class TicketBookingService:
    def __init__(self, event_repo: EventRepository, hold_repo: HoldRepository, booking_repo: BookingRepository):
        self.event_repo = event_repo
        self.hold_repo = hold_repo
        self.booking_repo = booking_repo

    def search_events(self, city: str, category: str, start_at: datetime, end_at: datetime, page: int, page_size: int) -> List[Dict[str, str]]:
        return self.event_repo.search(city, category, start_at, end_at, page, page_size)

    def create_hold(self, user_id: str, event_id: str, seat_ids: List[str], ttl_seconds: int) -> SeatHold:
        seats = self.event_repo.get_seats_for_update(event_id, seat_ids)
        if len(seats) != len(seat_ids):
            raise ValueError("Some seats do not exist")

        now = datetime.now(timezone.utc)
        
        # Lock in consistent order to prevent deadlocks
        seats.sort(key=lambda s: s.seat_id)
        
        acquired_locks = []
        try:
            for seat in seats:
                if not seat._lock.acquire(timeout=5.0): # simulated pessimistic row locking
                    raise RuntimeError("Lock contention")
                acquired_locks.append(seat)
                
                # Check version (optimistic locking part)
                if seat.state != SeatState.AVAILABLE:
                    raise RuntimeError("Seat not available")
            
            # If all are available, hold them
            for seat in seats:
                seat.state = SeatState.HELD
                seat.version += 1
                
            hold_id = str(uuid.uuid4())
            hold = SeatHold(
                hold_id=hold_id,
                user_id=user_id,
                event_id=event_id,
                seat_ids=seat_ids,
                expires_at=now + timedelta(seconds=ttl_seconds)
            )
            return self.hold_repo.save(hold)
            
        finally:
            for seat in reversed(acquired_locks):
                seat._lock.release()


    def confirm_booking(self, hold_id: str, payment_token: str, idempotency_key: str) -> str:
        existing = self.booking_repo.find_by_idempotency_key(idempotency_key)
        if existing:
            return existing
            
        hold = self.hold_repo.find(hold_id)
        if not hold:
            raise ValueError("Hold not found")
            
        if datetime.now(timezone.utc) > hold.expires_at:
            raise ValueError("Hold expired")
            
        seats = self.event_repo.get_seats_for_update(hold.event_id, hold.seat_ids)
        seats.sort(key=lambda s: s.seat_id)
        
        acquired_locks = []
        try:
            for seat in seats:
                if not seat._lock.acquire(timeout=5.0):
                    raise RuntimeError("Lock contention")
                acquired_locks.append(seat)
                
                if seat.state != SeatState.HELD:
                    raise RuntimeError("Seat not held")
                    
            for seat in seats:
                seat.state = SeatState.BOOKED
                seat.version += 1
                
            return self.booking_repo.create(hold_id, hold.user_id, idempotency_key)
        finally:
            for seat in reversed(acquired_locks):
                seat._lock.release()

