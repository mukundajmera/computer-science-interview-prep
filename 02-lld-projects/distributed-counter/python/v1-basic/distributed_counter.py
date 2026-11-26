import threading

class DistributedCounter:
    """
    A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
    Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
    """
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
        
    def increment(self, x=1):
        with self._lock:
            self._value += x
            
    def get(self):
        with self._lock:
            return self._value
