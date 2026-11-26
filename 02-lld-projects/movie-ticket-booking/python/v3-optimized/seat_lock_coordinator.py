"""Seat lock coordinator with expiring lock tokens."""

from dataclasses import dataclass
from threading import RLock
from time import time
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass(frozen=True)
class SeatLockToken:
    token_id: str
    show_id: str
    seat_ids: List[str]
    user_id: str
    expires_at_ms: int

    def is_expired(self) -> bool:
        return int(time() * 1000) >= self.expires_at_ms


class SeatLockCoordinator:
    """Tracks ephemeral seat-lock ownership for checkout workflows."""

    def __init__(self) -> None:
        self._locks: Dict[str, SeatLockToken] = {}
        self._lock = RLock()

    def acquire(
        self,
        show_id: str,
        seat_ids: List[str],
        user_id: str,
        ttl_ms: int,
    ) -> Optional[SeatLockToken]:
        if not show_id or not seat_ids or not user_id:
            return None

        token = SeatLockToken(
            token_id=str(uuid4()),
            show_id=show_id,
            seat_ids=list(seat_ids),
            user_id=user_id,
            expires_at_ms=int(time() * 1000) + max(1000, ttl_ms),
        )
        with self._lock:
            self.cleanup_expired()
            self._locks[token.token_id] = token
        return token

    def is_active(self, token_id: str) -> bool:
        with self._lock:
            token = self._locks.get(token_id)
            if token is None:
                return False
            if token.is_expired():
                self._locks.pop(token_id, None)
                return False
            return True

    def release(self, token_id: str) -> bool:
        with self._lock:
            return self._locks.pop(token_id, None) is not None

    def cleanup_expired(self) -> int:
        with self._lock:
            now_ms = int(time() * 1000)
            expired = [
                token_id
                for token_id, token in self._locks.items()
                if token.expires_at_ms <= now_ms
            ]
            for token_id in expired:
                self._locks.pop(token_id, None)
            return len(expired)

    def active_lock_count(self) -> int:
        with self._lock:
            self.cleanup_expired()
            return len(self._locks)
