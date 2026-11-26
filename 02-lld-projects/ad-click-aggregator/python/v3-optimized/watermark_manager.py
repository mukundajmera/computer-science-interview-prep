"""WatermarkManager for ad-click-aggregator (v3-optimized)."""

class WatermarkManager:
    def __init__(self) -> None:
        self.current_watermark = 0

    def update_watermark(self, timestamp: int) -> None:
        if timestamp > self.current_watermark:
            self.current_watermark = timestamp

    def get_watermark(self) -> int:
        return self.current_watermark
