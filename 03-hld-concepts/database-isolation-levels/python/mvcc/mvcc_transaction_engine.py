import threading
from typing import Dict, List, Optional, Set
from enum import Enum

class IsolationLevel(Enum):
    READ_COMMITTED = 1
    SNAPSHOT_ISOLATION = 2

class RecordVersion:
    def __init__(self, tx_id: int, value: Optional[str], is_deleted: bool):
        self.tx_id = tx_id
        self.value = value
        self.is_deleted = is_deleted

class ReadView:
    def __init__(self, min_trx_id: int, max_trx_id: int, active_trx_ids: Set[int]):
        self.min_trx_id = min_trx_id
        self.max_trx_id = max_trx_id
        self.active_trx_ids = set(active_trx_ids)

    def is_visible(self, tx_id: int) -> bool:
        if tx_id < self.min_trx_id:
            return True
        if tx_id >= self.max_trx_id:
            return False
        if tx_id in self.active_trx_ids:
            return False
        return True

class Transaction:
    def __init__(self, tx_id: int, isolation_level: IsolationLevel, read_view: ReadView):
        self.tx_id = tx_id
        self.isolation_level = isolation_level
        self.read_view = read_view
        self.writes: Dict[str, RecordVersion] = {}
        self.read_set: Set[str] = set()

class MvccTransactionEngine:
    def __init__(self):
        self.store: Dict[str, List[RecordVersion]] = {}
        self.active_transactions: Dict[int, Transaction] = {}
        self.next_tx_id = 1
        self.lock = threading.RLock()
        self.committed_txs: Set[int] = set()

    def _get_active_tx_ids(self) -> Set[int]:
        return set(self.active_transactions.keys())

    def _create_read_view(self) -> ReadView:
        active_ids = self._get_active_tx_ids()
        min_trx = min(active_ids) if active_ids else self.next_tx_id
        return ReadView(min_trx, self.next_tx_id, active_ids)

    def begin(self, isolation_level: IsolationLevel = IsolationLevel.SNAPSHOT_ISOLATION) -> int:
        with self.lock:
            tx_id = self.next_tx_id
            self.next_tx_id += 1
            read_view = self._create_read_view()
            tx = Transaction(tx_id, isolation_level, read_view)
            self.active_transactions[tx_id] = tx
            return tx_id

    def read(self, tx_id: int, key: str) -> Optional[str]:
        with self.lock:
            if tx_id not in self.active_transactions:
                raise ValueError(f"Transaction {tx_id} is not active")
            
            tx = self.active_transactions[tx_id]
            tx.read_set.add(key)
            
            # Check local writes first
            if key in tx.writes:
                version = tx.writes[key]
                return None if version.is_deleted else version.value
            
            # In READ_COMMITTED, read view is created per statement
            if tx.isolation_level == IsolationLevel.READ_COMMITTED:
                tx.read_view = self._create_read_view()
                
            if key not in self.store:
                return None
                
            # Read from store based on visibility
            for version in reversed(self.store[key]):
                if tx.read_view.is_visible(version.tx_id):
                    return None if version.is_deleted else version.value
                    
            return None

    def write(self, tx_id: int, key: str, value: str):
        with self.lock:
            if tx_id not in self.active_transactions:
                raise ValueError(f"Transaction {tx_id} is not active")
            tx = self.active_transactions[tx_id]
            tx.writes[key] = RecordVersion(tx_id, value, False)

    def delete(self, tx_id: int, key: str):
        with self.lock:
            if tx_id not in self.active_transactions:
                raise ValueError(f"Transaction {tx_id} is not active")
            tx = self.active_transactions[tx_id]
            tx.writes[key] = RecordVersion(tx_id, None, True)

    def commit(self, tx_id: int) -> bool:
        with self.lock:
            if tx_id not in self.active_transactions:
                return False
                
            tx = self.active_transactions[tx_id]
            
            # Write conflict detection (First-Committer-Wins)
            for key in tx.writes.keys():
                if key in self.store and self.store[key]:
                    latest_version = self.store[key][-1]
                    # If the latest committed version was not visible to our transaction's read view,
                    # it means another transaction committed a write to this key concurrently.
                    if not tx.read_view.is_visible(latest_version.tx_id):
                        # Write conflict
                        self.rollback(tx_id)
                        return False
            
            # Apply writes
            for key, version in tx.writes.items():
                if key not in self.store:
                    self.store[key] = []
                self.store[key].append(version)
                
            self.committed_txs.add(tx_id)
            del self.active_transactions[tx_id]
            return True

    def rollback(self, tx_id: int):
        with self.lock:
            if tx_id in self.active_transactions:
                del self.active_transactions[tx_id]
