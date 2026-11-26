import threading
import os

"""
v3-optimized DistributedCounter implementation.

A highly concurrent counter that dynamically resizes its cell array based on 
contention and CPU count, using probe hashing to minimize lock collisions.

LongAdder/striped local state is not a distributed counter, and a concurrent 
sum is not an atomic snapshot suitable for strict quota limits.
Overflow, negative-update policy, shard lifecycle and contention histories 
preserve the documented local-not network-distributed-counter contract.
"""

class Cell:
    def __init__(self, value=0):
        self.value = value
        self.lock = threading.Lock()

class DistributedCounter:
    def __init__(self):
        self.base = 0
        self.base_lock = threading.Lock()
        self.cells = None
        self.cells_busy = threading.Lock()
        self.NCPU = os.cpu_count() or 1
        if self.NCPU < 2:
            self.NCPU = 4  # Allow some resizing for tests
            
    def increment(self, x=1):
        thread_probe = threading.get_ident()
        
        cells = self.cells
        if cells is not None or not self._cas_base(x):
            uncontended = True
            
            if cells is None or len(cells) == 0:
                self._long_accumulate(x, thread_probe, uncontended)
                return
                
            cell = cells[thread_probe % len(cells)]
            if cell is None:
                self._long_accumulate(x, thread_probe, uncontended)
                return
                
            if not self._cas_cell(cell, x):
                uncontended = False
                self._long_accumulate(x, thread_probe, uncontended)
                return

    def _cas_base(self, x):
        if self.base_lock.acquire(blocking=False):
            try:
                self.base += x
                return True
            finally:
                self.base_lock.release()
        return False
        
    def _cas_cell(self, cell, x):
        if cell.lock.acquire(blocking=False):
            try:
                cell.value += x
                return True
            finally:
                cell.lock.release()
        return False
        
    def _long_accumulate(self, x, probe, uncontended):
        collide = False
        
        while True:
            cells = self.cells
            if cells is not None and len(cells) > 0:
                n = len(cells)
                cell = cells[probe % n]
                
                if cell is None:
                    if not self.cells_busy.locked():
                        new_cell = Cell(x)
                        if self.cells_busy.acquire(blocking=False):
                            try:
                                if self.cells is cells and self.cells[probe % n] is None:
                                    self.cells[probe % n] = new_cell
                                    break
                            finally:
                                self.cells_busy.release()
                            continue
                    collide = False
                elif not uncontended:
                    uncontended = True
                elif self._cas_cell(cell, x):
                    break
                elif n >= self.NCPU or self.cells is not cells:
                    collide = False
                elif not collide:
                    collide = True
                elif not self.cells_busy.locked() and self.cells_busy.acquire(blocking=False):
                    try:
                        if self.cells is cells:
                            new_cells = [None] * (n * 2)
                            for i in range(n):
                                new_cells[i] = cells[i]
                            self.cells = new_cells
                    finally:
                        self.cells_busy.release()
                    collide = False
                    
                    # Advance probe after resize so we don't hit the same index
                    probe ^= (probe << 13) & 0xFFFFFFFF
                    probe ^= (probe >> 17) & 0xFFFFFFFF
                    probe ^= (probe << 5) & 0xFFFFFFFF
                    
                    continue
                    
                # Advance probe
                probe ^= (probe << 13) & 0xFFFFFFFF
                probe ^= (probe >> 17) & 0xFFFFFFFF
                probe ^= (probe << 5) & 0xFFFFFFFF
            elif not self.cells_busy.locked() and self.cells is cells and self.cells_busy.acquire(blocking=False):
                init = False
                try:
                    if self.cells is cells:
                        new_cells = [None] * 2
                        new_cells[probe & 1] = Cell(x)
                        self.cells = new_cells
                        init = True
                finally:
                    self.cells_busy.release()
                if init:
                    break
            elif self._cas_base(x):
                break
                
    def get(self):
        total = self.base
        cells = self.cells
        if cells is not None:
            for cell in cells:
                if cell is not None:
                    with cell.lock:
                        total += cell.value
        return total
