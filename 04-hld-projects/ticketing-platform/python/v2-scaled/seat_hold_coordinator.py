
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Protocol


@dataclass
class HoldToken:
    hold_id: str
    event_id: str
    user_id: str
    seat_ids: List[str]
    expires_at: datetime


class LockStore(Protocol):
    def try_lock(self, event_id: str, seat_id: str, hold_id: str, expires_at: datetime) -> bool:
        ...

    def unlock(self, event_id: str, seat_id: str, hold_id: str) -> None:
        ...


class HoldLedger(Protocol):
    def save(self, token: HoldToken) -> HoldToken:
        ...

    def find(self, hold_id: str) -> Optional[HoldToken]:
        ...

    def mark_expired(self, hold_id: str) -> None:
        ...


class SeatHoldCoordinator:
    def __init__(self, lock_store: LockStore, ledger: HoldLedger):
        self.lock_store = lock_store
        self.ledger = ledger

    def reserve(self, user_id: str, event_id: str, seat_ids: List[str], ttl_seconds: int) -> HoldToken:
        hold_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)

        # In real redis this would be an atomic MULTI or lua script.
        # Here we attempt to lock each seat. If one fails, we rollback.
        
        acquired = []
        try:
            for seat_id in seat_ids:
                if self.lock_store.try_lock(event_id, seat_id, hold_id, expires_at):
                    acquired.append(seat_id)
                else:
                    raise RuntimeError(f"Seat {seat_id} is already held or booked")

            token = HoldToken(
                hold_id=hold_id,
                event_id=event_id,
                user_id=user_id,
                seat_ids=seat_ids,
                expires_at=expires_at
            )
            return self.ledger.save(token)
            
        except Exception as e:
            for seat_id in acquired:
                self.lock_store.unlock(event_id, seat_id, hold_id)
            raise e

    def release(self, hold_id: str, reason: str) -> bool:
        token = self.ledger.find(hold_id)
        if not token:
            return False

        for seat_id in token.seat_ids:
            self.lock_store.unlock(token.event_id, seat_id, hold_id)
            
        self.ledger.mark_expired(hold_id)
        return True

    def expire_stale(self, now: datetime) -> int:
        # In a real system this would be handled by Redis TTL automatically for locks.
        # But we need to clean up the ledger or emit events. This depends on implementation.
        return 0
