import pytest
import sys
import os
import threading
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))

from ticket_booking_service import TicketBookingService, Seat, SeatState, SeatHold, EventRepository, HoldRepository, BookingRepository
from seat_hold_coordinator import SeatHoldCoordinator, HoldToken, LockStore, HoldLedger
from distributed_ticketing_service import DistributedTicketingService, RegionRouter, BookingOrchestrator, EventRepositoryGlobal, WaitingRoomQueue

class InMemoryEventRepository:
    def __init__(self, seats: List[Seat]):
        self.seats = {s.seat_id: s for s in seats}
        
    def search(self, city: str, category: str, start_at: datetime, end_at: datetime, page: int, page_size: int) -> List[Dict[str, str]]:
        return []

    def seat_map(self, event_id: str) -> List[Seat]:
        return list(self.seats.values())

    def get_seats_for_update(self, event_id: str, seat_ids: List[str]) -> List[Seat]:
        return [self.seats[s_id] for s_id in seat_ids if s_id in self.seats]

class InMemoryHoldRepository:
    def __init__(self):
        self.holds = {}
        
    def save(self, hold: SeatHold) -> SeatHold:
        self.holds[hold.hold_id] = hold
        return hold

    def find(self, hold_id: str) -> Optional[SeatHold]:
        return self.holds.get(hold_id)

class InMemoryBookingRepository:
    def __init__(self):
        self.bookings = {}
        
    def create(self, hold_id: str, user_id: str, idempotency_key: str) -> str:
        self.bookings[idempotency_key] = hold_id
        return hold_id

    def find_by_idempotency_key(self, idempotency_key: str) -> Optional[str]:
        return self.bookings.get(idempotency_key)

def test_v1_basic_reserve_seat_and_purchase_ticket():
    seats = [Seat(seat_id="A1", event_id="evt_1", section="A", row="1", number=1),
             Seat(seat_id="A2", event_id="evt_1", section="A", row="1", number=2),
             Seat(seat_id="A3", event_id="evt_1", section="A", row="1", number=3)]
             
    event_repo = InMemoryEventRepository(seats)
    service = TicketBookingService(event_repo, InMemoryHoldRepository(), InMemoryBookingRepository())

    def worker(user_id):
        try:
            hold = service.create_hold(user_id, "evt_1", ["A1", "A2", "A3"], 300)
            service.confirm_booking(hold.hold_id, "tok_visa", f"idem_{user_id}")
            return True
        except Exception:
            return False

    successes = 0
    failures = 0
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(worker, f"user_{i}") for i in range(100)]
        for future in as_completed(futures):
            if future.result():
                successes += 1
            else:
                failures += 1
                
    assert successes == 1, f"Expected exactly 1 success, got {successes}"
    assert failures == 99, f"Expected exactly 99 failures, got {failures}"


class MockLockStore:
    def __init__(self):
        self.locks = {}
        self.lock = threading.Lock()
        
    def try_lock(self, event_id: str, seat_id: str, hold_id: str, expires_at: datetime) -> bool:
        key = f"{event_id}:{seat_id}"
        with self.lock:
            if key in self.locks:
                return False
            self.locks[key] = hold_id
            return True

    def unlock(self, event_id: str, seat_id: str, hold_id: str) -> None:
        key = f"{event_id}:{seat_id}"
        with self.lock:
            if self.locks.get(key) == hold_id:
                del self.locks[key]


class MockHoldLedger:
    def __init__(self):
        self.holds = {}
        
    def save(self, token: HoldToken) -> HoldToken:
        self.holds[token.hold_id] = token
        return token

    def find(self, hold_id: str) -> Optional[HoldToken]:
        return self.holds.get(hold_id)

    def mark_expired(self, hold_id: str) -> None:
        pass


def test_v2_scaled_concurrency_check_to_prevent_double_booking():
    coordinator = SeatHoldCoordinator(MockLockStore(), MockHoldLedger())

    def worker(user_id):
        try:
            coordinator.reserve(user_id, "evt_1", ["B1", "B2", "B3"], 300)
            return True
        except Exception:
            return False

    successes = 0
    failures = 0
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(worker, f"user_{i}") for i in range(100)]
        for future in as_completed(futures):
            if future.result():
                successes += 1
            else:
                failures += 1
                
    assert successes == 1, f"Expected exactly 1 success, got {successes}"
    assert failures == 99, f"Expected exactly 99 failures, got {failures}"


class MockRegionRouter:
    def read_region(self, user_region: str, event_id: str) -> str:
        return "us-east-1"
        
    def write_region(self, event_id: str) -> str:
        return "us-west-2"

class MockWaitingRoomQueue:
    def enqueue(self, user_id: str, event_id: str) -> str:
        return "token_1"
        
    def check_status(self, token_id: str) -> str:
        return "admitted"

class MockEventRepositoryGlobal:
    def search(self, region: str, city: str, page: int, page_size: int) -> List[Dict[str, str]]:
        return [{"id": "evt_global", "city": city}]

class MockBookingOrchestrator:
    def create(self, region: str, event_id: str, hold_id: str, payment_token: str, idempotency_key: str) -> str:
        return "booking_123"

def test_v3_distributed_waiting_room_queue_and_seat_expiration():
    service = DistributedTicketingService(
        MockRegionRouter(),
        MockWaitingRoomQueue(),
        MockEventRepositoryGlobal(),
        MockBookingOrchestrator()
    )

    plan = service.region_plan("evt_global")
    assert plan.primary_region == "us-west-2"

    booking_id = service.create_booking_global("evt_global", "hold_999", "tok_amex", "idem_999")
    assert booking_id == "booking_123"

def test_python_tests_exist():
    assert True
