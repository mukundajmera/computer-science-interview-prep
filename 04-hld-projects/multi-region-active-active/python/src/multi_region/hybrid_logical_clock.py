import time
import threading

class HybridLogicalClock:
    def __init__(self, physical_time: int, logical_counter: int):
        self.physical_time = physical_time
        self.logical_counter = logical_counter
        self._lock = threading.Lock()

    def tick(self, current_physical_time: int):
        with self._lock:
            if current_physical_time > self.physical_time:
                self.physical_time = current_physical_time
                self.logical_counter = 0
            else:
                self.logical_counter += 1

    def update(self, other: 'HybridLogicalClock', current_physical_time: int):
        with self._lock:
            if current_physical_time > self.physical_time and current_physical_time > other.physical_time:
                self.physical_time = current_physical_time
                self.logical_counter = 0
            elif self.physical_time == other.physical_time:
                self.logical_counter = max(self.logical_counter, other.logical_counter) + 1
            elif self.physical_time > other.physical_time:
                self.logical_counter += 1
            else:
                self.physical_time = other.physical_time
                self.logical_counter = other.logical_counter + 1

    def clone_clock(self):
        with self._lock:
            return HybridLogicalClock(self.physical_time, self.logical_counter)

    def __lt__(self, other):
        if self.physical_time == other.physical_time:
            return self.logical_counter < other.logical_counter
        return self.physical_time < other.physical_time

    def __eq__(self, other):
        return self.physical_time == other.physical_time and self.logical_counter == other.logical_counter

    def __gt__(self, other):
        return not (self < other or self == other)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other
