from abc import ABC, abstractmethod
from log_event import LogEvent
from datetime import datetime, timezone

class Formatter(ABC):
    @abstractmethod
    def format(self, event: LogEvent) -> str:
        pass

class PatternFormatter(Formatter):
    def __init__(self, pattern: str = "[%d] [%t] [%l] %c - %m"):
        self.pattern = pattern

    def format(self, event: LogEvent) -> str:
        result = self.pattern
        
        dt_str = datetime.fromtimestamp(event.timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        result = result.replace("%d", dt_str)
        result = result.replace("%t", event.thread_name)
        result = result.replace("%l", event.level.name)
        result = result.replace("%c", event.logger_name)
        result = result.replace("%m", event.message)
        
        return result
