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

import os as _os

class RollingFileAppender(Appender):
    def __init__(self, name: str, file_path: str, max_size_bytes: int, backup_count: int, formatter: Optional[Formatter] = None):
        self._name = name
        self._file_path = file_path
        self._max_size_bytes = max_size_bytes
        self._backup_count = backup_count
        self._formatter = formatter or PatternFormatter()
        self._lock = threading.Lock()

    def append(self, event: LogEvent) -> None:
        with self._lock:
            msg = self._formatter.format(event) + "\n"
            if _os.path.exists(self._file_path) and _os.path.getsize(self._file_path) + len(msg.encode("utf-8")) > self._max_size_bytes:
                self._roll_over()
            with open(self._file_path, "a") as file:
                file.write(msg)

    def _roll_over(self) -> None:
        for i in range(self._backup_count - 1, 0, -1):
            sfn = f"{self._file_path}.{i}"
            dfn = f"{self._file_path}.{i + 1}"
            if _os.path.exists(sfn):
                if _os.path.exists(dfn):
                    _os.remove(dfn)
                _os.rename(sfn, dfn)
        dfn = f"{self._file_path}.1"
        if _os.path.exists(dfn):
            _os.remove(dfn)
        if _os.path.exists(self._file_path):
            _os.rename(self._file_path, dfn)

    def get_name(self) -> str:
        return self._name


class CompositeAppender(Appender):
    def __init__(self, name: str, appenders: List[Appender]):
        self._name = name
        self._appenders = appenders

    def append(self, event: LogEvent) -> None:
        for appender in self._appenders:
            appender.append(event)

    def get_name(self) -> str:
        return self._name

    def add_appender(self, appender: Appender) -> None:
        self._appenders.append(appender)
