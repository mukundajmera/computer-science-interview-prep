"""v2-extended Snowflake ID generator.

Improvements over v1-basic (each has dedicated tests):

1. Configurable backwards-clock policy (FOLLOW-UPS.md #4, PITFALLS.md
   mitigation #1): v1 always throws when the clock moves backwards. v2 adds
   a WAIT policy that tolerates an NTP correction of up to max_wait_millis
   by blocking until the physical clock catches up to the last recorded
   timestamp, exactly the availability-for-consistency trade the follow-up
   describes; larger jumps still throw. THROW remains the default, so v1
   behavior is unchanged unless opted in.

2. Dynamic worker-ID leasing (FOLLOW-UPS.md #3, PITFALLS.md #2): see
   worker_id_pool.py for the ZooKeeper-style ephemeral lease pool.

3. Timestamp-overflow guard (FOLLOW-UPS.md #1): v1 silently emits
   negative/invalid IDs once the timestamp delta outgrows the 41-bit field.
   v2 raises TimestampOverflowException instead, so the failure is loud and
   operators can migrate the epoch or format before collisions happen.
"""
import threading

from clock import Clock
from exceptions import ClockMovedBackwardsException, TimestampOverflowException


class BackwardsClockPolicy:
    THROW = "throw"
    WAIT = "wait"


class SnowflakeGenerator:
    WORKER_ID_BITS = 10
    SEQUENCE_BITS = 12

    MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)
    SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)
    MAX_TIMESTAMP_DELTA = (1 << 41) - 1  # 41 bits for the timestamp field

    WORKER_ID_SHIFT = SEQUENCE_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS

    def __init__(self, worker_id: int, epoch: int, clock: Clock,
                 backwards_policy: str = BackwardsClockPolicy.THROW,
                 max_wait_millis: int = 10):
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker Id can't be greater than {self.MAX_WORKER_ID} or less than 0")
        if backwards_policy not in (BackwardsClockPolicy.THROW, BackwardsClockPolicy.WAIT):
            raise ValueError(f"unknown backwards clock policy: {backwards_policy}")
        if max_wait_millis < 0:
            raise ValueError("max_wait_millis can't be less than 0")

        self.worker_id = worker_id
        self.epoch = epoch
        self.clock = clock
        self.backwards_policy = backwards_policy
        self.max_wait_millis = max_wait_millis

        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def next_id(self) -> int:
        with self.lock:
            timestamp = self.clock.current_time_millis()

            if timestamp < self.last_timestamp:
                # Improvement #1: tolerate small NTP corrections under WAIT.
                if self.backwards_policy == BackwardsClockPolicy.WAIT:
                    timestamp = self._wait_for_catchup(self.last_timestamp)
                else:
                    raise ClockMovedBackwardsException(
                        f"Clock moved backwards. Refusing to generate id for {self.last_timestamp - timestamp} milliseconds"
                    )

            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.SEQUENCE_MASK
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            # Improvement #3: fail loudly at the 69-year boundary instead of
            # emitting negative or colliding IDs.
            delta = timestamp - self.epoch
            if delta < 0 or delta > self.MAX_TIMESTAMP_DELTA:
                raise TimestampOverflowException(
                    f"Timestamp delta {delta}ms does not fit the 41-bit field; migrate the epoch or ID format"
                )

            self.last_timestamp = timestamp

            return (delta << self.TIMESTAMP_LEFT_SHIFT) | \
                   (self.worker_id << self.WORKER_ID_SHIFT) | \
                   self.sequence

    def _wait_for_catchup(self, last_timestamp: int) -> int:
        timestamp = self.clock.current_time_millis()
        if last_timestamp - timestamp > self.max_wait_millis:
            raise ClockMovedBackwardsException(
                f"Clock moved backwards by {last_timestamp - timestamp}ms, beyond the tolerated {self.max_wait_millis}ms"
            )
        while timestamp < last_timestamp:
            timestamp = self.clock.current_time_millis()
        return timestamp

    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self.clock.current_time_millis()
        while timestamp <= last_timestamp:
            timestamp = self.clock.current_time_millis()
        return timestamp
