import time
from abc import ABC, abstractmethod

class Clock(ABC):
    @abstractmethod
    def now(self) -> float:
        pass

class SystemClock(Clock):
    def now(self) -> float:
        return time.time()

class TestClock(Clock):
    def __init__(self, start_time: float = 0.0):
        self._current_time = start_time

    def now(self) -> float:
        return self._current_time

    def advance(self, seconds: float) -> None:
        self._current_time += seconds

    def set_time(self, new_time: float) -> None:
        self._current_time = new_time
