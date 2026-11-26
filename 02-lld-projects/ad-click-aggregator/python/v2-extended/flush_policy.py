"""FlushPolicy for ad-click-aggregator (v2-extended)."""

class FlushPolicy:
    def __init__(self, flush_interval_ms: int = 10000) -> None:
        self.flush_interval_ms = flush_interval_ms
        self.last_flush = 0

    def should_flush(self, current_time: int) -> bool:
        if current_time - self.last_flush >= self.flush_interval_ms:
            self.last_flush = current_time
            return True
        return False
