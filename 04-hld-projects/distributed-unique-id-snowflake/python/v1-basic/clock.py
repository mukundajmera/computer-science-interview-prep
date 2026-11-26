import time
from abc import ABC, abstractmethod

class Clock(ABC):
    @abstractmethod
    def current_time_millis(self) -> int:
        pass

class SystemClock(Clock):
    def current_time_millis(self) -> int:
        return int(time.time() * 1000)
