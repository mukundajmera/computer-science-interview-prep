import threading
import time
from typing import Dict, List, Optional, Any, Set
from collections import OrderedDict

class Row:
    def __init__(self, primary_key: int, data: Dict[str, Any]):
        self.primary_key = primary_key
        self.data = data
        self.transaction_id = 0  # To track which tx created this version
        self.deleted = False

class BufferPool:
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        # OrderedDict simulates LRU cache: key -> Row
        self.pages: OrderedDict[int, Row] = OrderedDict()
        self.dirty_pages: Set[int] = set()
        self.lock = threading.Lock()

    def get(self, primary_key: int) -> Optional[Row]:
        with self.lock:
            if primary_key in self.pages:
                # Move to end to show it was recently used
                self.pages.move_to_end(primary_key)
                return self.pages[primary_key]
            return None

    def put(self, primary_key: int, row: Row, is_dirty: bool = True):
        with self.lock:
            if primary_key in self.pages:
                self.pages.move_to_end(primary_key)
            self.pages[primary_key] = row
            if is_dirty:
                self.dirty_pages.add(primary_key)
            if len(self.pages) > self.capacity:
                # Evict oldest
                evicted_key, _ = self.pages.popitem(last=False)
                if evicted_key in self.dirty_pages:
                    self.dirty_pages.remove(evicted_key)
                    # In a real DB, flush to disk here

class RedoLog:
    def __init__(self):
        self.log_entries: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def append(self, tx_id: int, operation: str, primary_key: int, data: Dict[str, Any]):
        with self.lock:
            self.log_entries.append({
                "tx_id": tx_id,
                "operation": operation,
                "primary_key": primary_key,
                "data": data.copy(),
                "timestamp": time.time()
            })

class UndoLog:
    def __init__(self):
        # Maps transaction ID to list of previous versions
        self.logs: Dict[int, List[Row]] = {}
        self.lock = threading.Lock()

    def add(self, tx_id: int, previous_row: Optional[Row]):
        with self.lock:
            if tx_id not in self.logs:
                self.logs[tx_id] = []
            if previous_row:
                # Store a copy of the old row
                row_copy = Row(previous_row.primary_key, previous_row.data.copy())
                row_copy.transaction_id = previous_row.transaction_id
                row_copy.deleted = previous_row.deleted
                self.logs[tx_id].append(row_copy)

    def get_old_versions(self, tx_id: int) -> List[Row]:
        with self.lock:
            return self.logs.get(tx_id, [])

class InnoDBEngineSimulator:
    def __init__(self):
        self.buffer_pool = BufferPool(capacity=100)
        self.redo_log = RedoLog()
        self.undo_log = UndoLog()

        # Disk simulation (primary key -> Row)
        self.disk_storage: Dict[int, Row] = {}

        # Transaction management
        self.next_tx_id = 1
        self.active_transactions: Set[int] = set()

        # Row level locks: primary_key -> tx_id holding the lock
        self.locks: Dict[int, int] = {}
        self.lock_mutex = threading.Lock()

    def start_transaction(self) -> int:
        with self.lock_mutex:
            tx_id = self.next_tx_id
            self.next_tx_id += 1
            self.active_transactions.add(tx_id)
            return tx_id

    def _acquire_lock(self, tx_id: int, primary_key: int, timeout: float = 1.0) -> bool:
        start_time = time.time()
        while True:
            with self.lock_mutex:
                owner = self.locks.get(primary_key)
                if owner is None or owner == tx_id:
                    self.locks[primary_key] = tx_id
                    return True

            # Deadlock detection/timeout
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.01)

    def _release_locks(self, tx_id: int):
        with self.lock_mutex:
            keys_to_remove = [k for k, v in self.locks.items() if v == tx_id]
            for k in keys_to_remove:
                del self.locks[k]

    def read(self, tx_id: int, primary_key: int) -> Optional[Dict[str, Any]]:
        # Simulate MVCC read
        row = self.buffer_pool.get(primary_key)
        if not row:
            # Fetch from disk
            if primary_key in self.disk_storage:
                row = self.disk_storage[primary_key]
                self.buffer_pool.put(primary_key, row, is_dirty=False)
            else:
                return None

        if row.deleted:
            return None

        # MVCC simplified: If modified by a younger uncommitted transaction, look in undo log
        if row.transaction_id > tx_id or (row.transaction_id in self.active_transactions and row.transaction_id != tx_id):
            # Check undo logs of the transaction that modified it
            old_versions = self.undo_log.get_old_versions(row.transaction_id)
            for old_row in reversed(old_versions):
                if old_row.primary_key == primary_key:
                    if old_row.transaction_id <= tx_id and old_row.transaction_id not in self.active_transactions:
                        if old_row.deleted:
                            return None
                        return old_row.data.copy()
            # If no suitable old version found, it might have been created by the newer tx
            return None

        return row.data.copy()

    def write(self, tx_id: int, primary_key: int, data: Dict[str, Any]) -> bool:
        if not self._acquire_lock(tx_id, primary_key):
            raise Exception("Deadlock detected or lock timeout")

        old_row = self.buffer_pool.get(primary_key)
        if not old_row and primary_key in self.disk_storage:
            old_row = self.disk_storage[primary_key]

        # Add to undo log for MVCC
        if old_row:
            self.undo_log.add(tx_id, old_row)

        # Create new version
        new_row = Row(primary_key, data.copy())
        new_row.transaction_id = tx_id

        # Write ahead logging
        self.redo_log.append(tx_id, "WRITE", primary_key, data)

        # Update buffer pool
        self.buffer_pool.put(primary_key, new_row, is_dirty=True)
        return True

    def commit(self, tx_id: int):
        with self.lock_mutex:
            if tx_id in self.active_transactions:
                self.active_transactions.remove(tx_id)
        self._release_locks(tx_id)

    def rollback(self, tx_id: int):
        # Retrieve old versions and restore them
        old_versions = self.undo_log.get_old_versions(tx_id)
        for old_row in old_versions:
            # Need lock to restore, but we should already have it from the write operation
            self.buffer_pool.put(old_row.primary_key, old_row, is_dirty=True)
            self.redo_log.append(tx_id, "ROLLBACK_RESTORE", old_row.primary_key, old_row.data)

        with self.lock_mutex:
            if tx_id in self.active_transactions:
                self.active_transactions.remove(tx_id)
        self._release_locks(tx_id)

    def flush_dirty_pages(self):
        with self.buffer_pool.lock:
            for key in list(self.buffer_pool.dirty_pages):
                if key in self.buffer_pool.pages:
                    self.disk_storage[key] = self.buffer_pool.pages[key]
            self.buffer_pool.dirty_pages.clear()
