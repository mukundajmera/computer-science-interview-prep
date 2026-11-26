import threading
from clock import Clock
from exceptions import ClockMovedBackwardsException

class SnowflakeGenerator:
    WORKER_ID_BITS = 10
    SEQUENCE_BITS = 12

    MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)
    SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

    WORKER_ID_SHIFT = SEQUENCE_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS

    def __init__(self, worker_id: int, epoch: int, clock: Clock):
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker Id can't be greater than {self.MAX_WORKER_ID} or less than 0")
        
        self.worker_id = worker_id
        self.epoch = epoch
        self.clock = clock
        
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def next_id(self) -> int:
        with self.lock:
            timestamp = self.clock.current_time_millis()

            if timestamp < self.last_timestamp:
                raise ClockMovedBackwardsException(
                    f"Clock moved backwards. Refusing to generate id for {self.last_timestamp - timestamp} milliseconds"
                )

            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.SEQUENCE_MASK
                if self.sequence == 0:
                    # Sequence exhausted, wait for next millisecond
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return ((timestamp - self.epoch) << self.TIMESTAMP_LEFT_SHIFT) | \
                   (self.worker_id << self.WORKER_ID_SHIFT) | \
                   self.sequence

    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self.clock.current_time_millis()
        while timestamp <= last_timestamp:
            timestamp = self.clock.current_time_millis()
        return timestamp
