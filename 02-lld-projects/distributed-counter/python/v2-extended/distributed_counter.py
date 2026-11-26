import threading
from .counter import Counter

"""
A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
"""

class DistributedCounter:
    def __init__(self, num_cells=4):
        self.counter = Counter(num_cells)
        
    def increment(self, x=1):
        self.counter.increment(x)
            
    def get(self):
        return self.counter.get()
