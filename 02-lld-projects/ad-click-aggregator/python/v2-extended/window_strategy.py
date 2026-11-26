"""WindowStrategy for ad-click-aggregator (v2-extended)."""

class WindowStrategy:
    def __init__(self, window_size_ms: int = 60000, slide_step_ms: int = 10000) -> None:
        self.window_size_ms = window_size_ms
        self.slide_step_ms = slide_step_ms

    def get_overlapping_windows(self, timestamp: int) -> list[int]:
        # Returns start timestamps for all sliding windows this timestamp falls into
        windows = []
        # Find the earliest window start that could include this timestamp
        # The window start must be aligned to slide_step_ms
        first_window_start = ((timestamp - self.window_size_ms + self.slide_step_ms) // self.slide_step_ms) * self.slide_step_ms
        
        current_start = first_window_start
        while current_start <= timestamp:
            windows.append(current_start)
            current_start += self.slide_step_ms
            
        return windows
