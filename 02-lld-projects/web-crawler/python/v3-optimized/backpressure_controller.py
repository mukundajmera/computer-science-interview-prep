import threading

class BackpressureController:
    def __init__(self, max_concurrent: int) -> None:
        self.max_concurrent = max_concurrent
        self.current = 0
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        with self.lock:
            if self.current < self.max_concurrent:
                self.current += 1
                return True
            return False

    def release(self) -> None:
        with self.lock:
            if self.current > 0:
                self.current -= 1
