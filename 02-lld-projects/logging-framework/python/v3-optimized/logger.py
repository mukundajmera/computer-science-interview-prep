from typing import List, Optional
from log_level import LogLevel
from log_event import LogEvent
from appenders import Appender
from async_processor import AsyncLogProcessor

class Logger:
    def __init__(self, name: str, parent: Optional['Logger'], async_processor: Optional[AsyncLogProcessor]):
        self.name = name
        self.level: Optional[LogLevel] = None
        self.parent = parent
        self.appenders: List[Appender] = []
        self.additive = True
        self._async_processor = async_processor

    def set_level(self, level: LogLevel) -> None:
        self.level = level

    def get_effective_level(self) -> LogLevel:
        current = self
        while current is not None:
            if current.level is not None:
                return current.level
            current = current.parent
        return LogLevel.INFO  # Fallback

    def add_appender(self, appender: Appender) -> None:
        self.appenders.append(appender)

    def is_enabled_for(self, level: LogLevel) -> bool:
        return level.is_greater_or_equal(self.get_effective_level())

    def log(self, level: LogLevel, message: str) -> None:
        if self.is_enabled_for(level):
            event = LogEvent(self.name, level, message)
            self._dispatch(event)

    def _dispatch(self, event: LogEvent) -> None:
        target_appenders = []
        current = self
        while current is not None:
            target_appenders.extend(current.appenders)
            if not current.additive:
                break
            current = current.parent

        if self._async_processor:
            self._async_processor.submit(event, target_appenders)
        else:
            for appender in target_appenders:
                appender.append(event)

    def trace(self, message: str) -> None: self.log(LogLevel.TRACE, message)
    def debug(self, message: str) -> None: self.log(LogLevel.DEBUG, message)
    def info(self, message: str) -> None: self.log(LogLevel.INFO, message)
    def warn(self, message: str) -> None: self.log(LogLevel.WARN, message)
    def error(self, message: str) -> None: self.log(LogLevel.ERROR, message)
    def fatal(self, message: str) -> None: self.log(LogLevel.FATAL, message)

