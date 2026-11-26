import threading

class HostRateLimiter:
    def __init__(self, max_concurrent: int = 1) -> None:
        self.max_concurrent = max_concurrent
        self.host_semaphores = {}
        self.lock = threading.Lock()
        
    def try_acquire(self, host: str) -> bool:
        with self.lock:
            if host not in self.host_semaphores:
                self.host_semaphores[host] = threading.Semaphore(self.max_concurrent)
        return self.host_semaphores[host].acquire(blocking=False)
        
    def release(self, host: str) -> None:
        with self.lock:
            if host in self.host_semaphores:
                self.host_semaphores[host].release()
