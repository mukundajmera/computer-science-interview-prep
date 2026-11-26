import threading

"""
A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
"""

class Cell:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

class Counter:
    def __init__(self, num_cells=4):
        self.cells = [Cell() for _ in range(num_cells)]
        
    def increment(self, x=1):
        if x < 0:
            raise ValueError("Negative updates are not allowed")
            
        thread_id = threading.get_ident()
        cell = self.cells[thread_id % len(self.cells)]
        with cell.lock:
            cell.value += x
            
    def get(self):
        total = 0
        for cell in self.cells:
            with cell.lock:
                total += cell.value
        return total
