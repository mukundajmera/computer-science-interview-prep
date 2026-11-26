import time
import threading
from log_level import LogLevel
from datetime import datetime, timezone

class LogEvent:
    def __init__(self, logger_name: str, level: LogLevel, message: str):
        self.logger_name = logger_name
        self.level = level
        self.message = message
        self.timestamp = time.time()
        self.thread_name = threading.current_thread().name

    def __str__(self):
        dt = datetime.fromtimestamp(self.timestamp, timezone.utc).strftime('%H:%M:%S')
        return f"[{dt}] [{self.thread_name}] [{self.level.name}] {self.logger_name} - {self.message}"

