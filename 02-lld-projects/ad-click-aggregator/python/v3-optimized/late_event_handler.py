"""LateEventHandler for ad-click-aggregator (v3-optimized)."""
from click_event import ClickEvent

class LateEventHandler:
    def __init__(self, max_lateness_ms: int = 5000) -> None:
        self.max_lateness_ms = max_lateness_ms
        self.late_events_dropped = 0

    def is_late(self, event: ClickEvent, current_watermark: int) -> bool:
        if event.timestamp < current_watermark - self.max_lateness_ms:
            self.late_events_dropped += 1
            return True
        return False
