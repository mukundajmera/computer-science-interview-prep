"""v2 telemetry batching (v2 improvement #3).

Implements PITFALLS.md #5: mobile clients collect GPS pings continuously
but only send a batched payload every flush_interval_seconds (the pitfall
suggests 15-30s), saving battery and cellular radio overhead. The clock is
injectable so tests can drive the flush window deterministically. See
google_maps_service_v2.py for the full v2 improvement list.
"""
import time
from typing import Callable, List, Optional, Tuple


class TelemetryBatcher:
    def __init__(self, flush_interval_seconds: float = 15.0,
                 clock: Optional[Callable[[], float]] = None):
        if flush_interval_seconds <= 0:
            raise ValueError("flush interval must be positive")
        self.flush_interval_seconds = flush_interval_seconds
        self.clock = clock or time.monotonic
        self._buffer: List[Tuple[float, float, float]] = []
        self._last_flush = self.clock()

    def record_ping(self, lat: float, lng: float, timestamp: Optional[float] = None) -> Optional[list]:
        """Buffers one ping. Returns the flushed batch when the flush
        interval has elapsed since the last send, else None."""
        now = timestamp if timestamp is not None else self.clock()
        self._buffer.append((lat, lng, now))
        if now - self._last_flush >= self.flush_interval_seconds:
            return self.flush(now)
        return None

    def flush(self, now: Optional[float] = None) -> list:
        """Sends everything buffered so far and restarts the window."""
        if now is None:
            now = self.clock()
        batch = self._buffer
        self._buffer = []
        self._last_flush = now
        return batch

    def pending_count(self) -> int:
        return len(self._buffer)
