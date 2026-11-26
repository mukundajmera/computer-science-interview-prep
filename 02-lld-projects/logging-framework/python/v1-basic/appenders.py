import threading
from typing import List, Optional
from abc import ABC, abstractmethod
from log_event import LogEvent
from formatters import Formatter, PatternFormatter

class Appender(ABC):
    @abstractmethod
    def append(self, event: LogEvent) -> None:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

class ConsoleAppender(Appender):
    def __init__(self, name: str, formatter: Optional[Formatter] = None):
        self._name = name
        self._formatter = formatter or PatternFormatter()

    def append(self, event: LogEvent) -> None:
        print(self._formatter.format(event))

    def get_name(self) -> str:
        return self._name

class InMemoryAppender(Appender):
    def __init__(self, name: str, formatter: Optional[Formatter] = None):
        self._name = name
        self._logs: List[LogEvent] = []
        self._lock = threading.Lock()
        self._formatter = formatter or PatternFormatter()

    def append(self, event: LogEvent) -> None:
        with self._lock:
            self._logs.append(event)

    def get_name(self) -> str:
        return self._name

    def get_logs(self) -> List[LogEvent]:
        with self._lock:
            return list(self._logs)

    def clear(self) -> None:
        with self._lock:
            self._logs.clear()

    def get_formatter(self) -> Formatter:
        return self._formatter
