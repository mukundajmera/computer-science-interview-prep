import time
from typing import Dict, Tuple
import threading

class RecrawlScheduler:
    def __init__(self) -> None:
        self.schedule: Dict[str, Tuple[float, float]] = {}
        self.lock = threading.Lock()

    def schedule_recrawl(self, url: str, interval_seconds: float) -> None:
        with self.lock:
            self.schedule[url] = (time.time() + interval_seconds, interval_seconds)

    def is_ready(self, url: str) -> bool:
        with self.lock:
            if url in self.schedule:
                return time.time() >= self.schedule[url][0]
            return False
