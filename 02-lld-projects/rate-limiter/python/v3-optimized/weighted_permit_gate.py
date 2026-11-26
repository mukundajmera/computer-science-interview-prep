"""Weighted permit gate for scarcity-aware admission control."""

from threading import Condition
from time import monotonic


class WeightedPermitGate:
    """Allows timed acquisition of weighted permits from a fixed pool."""

    def __init__(self, max_permits: int):
        if max_permits <= 0:
            raise ValueError("max_permits must be > 0")
        self._max_permits = max_permits
        self._used_permits = 0
        self._condition = Condition()

    def try_acquire(self, permits: int, timeout_ms: int) -> bool:
        self._validate_permits(permits)
        deadline = monotonic() + max(0, timeout_ms) / 1000.0

        with self._condition:
            while self._used_permits + permits > self._max_permits:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return False
                self._condition.wait(timeout=remaining)

            self._used_permits += permits
            return True

    def release(self, permits: int) -> None:
        self._validate_permits(permits)
        with self._condition:
            self._used_permits = max(0, self._used_permits - permits)
            self._condition.notify_all()

    @property
    def max_permits(self) -> int:
        return self._max_permits

    @property
    def available_permits(self) -> int:
        with self._condition:
            return self._max_permits - self._used_permits

    def _validate_permits(self, permits: int) -> None:
        if permits <= 0 or permits > self._max_permits:
            raise ValueError("permits must be in range [1, max_permits]")
