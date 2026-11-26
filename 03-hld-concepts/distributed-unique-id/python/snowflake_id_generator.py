import time
import threading
from dataclasses import dataclass

class ClockMovedBackwardsException(Exception):
    pass

@dataclass
class IdComponents:
    timestamp: int
    datacenter_id: int
    worker_id: int
    sequence: int

class SnowflakeIdGenerator:
    SEQUENCE_BITS = 12
    WORKER_ID_BITS = 5
    DATACENTER_ID_BITS = 5

    MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)
    MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)
    SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

    WORKER_ID_SHIFT = SEQUENCE_BITS
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

    def __init__(self, datacenter_id: int, worker_id: int, custom_epoch_ms: int, max_clock_drift_ms: int):
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f"datacenter_id must be between 0 and {self.MAX_DATACENTER_ID}")
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker_id must be between 0 and {self.MAX_WORKER_ID}")
            
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.custom_epoch_ms = custom_epoch_ms
        self.max_clock_drift_ms = max_clock_drift_ms
        
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def next_id(self) -> int:
        with self.lock:
            timestamp = self._time_gen()

            if timestamp < self.last_timestamp:
                drift = self.last_timestamp - timestamp
                if drift <= self.max_clock_drift_ms:
                    timestamp = self._til_next_millis(self.last_timestamp)
                else:
                    raise ClockMovedBackwardsException(f"Clock moved backwards by {drift} ms")

            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & self.SEQUENCE_MASK
                if self.sequence == 0:
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return ((timestamp - self.custom_epoch_ms) << self.TIMESTAMP_LEFT_SHIFT) | \
                   (self.datacenter_id << self.DATACENTER_ID_SHIFT) | \
                   (self.worker_id << self.WORKER_ID_SHIFT) | \
                   self.sequence

    def parse(self, id: int) -> IdComponents:
        sequence = id & self.SEQUENCE_MASK
        worker_id = (id >> self.WORKER_ID_SHIFT) & self.MAX_WORKER_ID
        datacenter_id = (id >> self.DATACENTER_ID_SHIFT) & self.MAX_DATACENTER_ID
        timestamp = (id >> self.TIMESTAMP_LEFT_SHIFT) + self.custom_epoch_ms
        return IdComponents(timestamp, datacenter_id, worker_id, sequence)

    def _til_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._time_gen()
        while timestamp <= last_timestamp:
            timestamp = self._time_gen()
        return timestamp

    def _time_gen(self) -> int:
        return int(time.time() * 1000)
