"""
V2: Async Replication with Lag Simulation

Demonstrates asynchronous replication with configurable lag
and read routing based on consistency requirements.

Features:
- Asynchronous replication
- Simulated replication lag
- Read-your-writes consistency option
- Lag monitoring
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class Entry:
    """Database entry with timestamp."""
    value: str
    timestamp: float


class ReplicaDatabase:
    """Replica database with simulated lag."""
    
    def __init__(self, name: str, replication_delay_ms: int):
        self.name = name
        self._replication_delay_ms = replication_delay_ms
        self._data: Dict[str, Entry] = {}
        self._last_replication_time = time.time()
        self._lock = threading.Lock()

    def replicate_with_delay(self, key: str, value: str, timestamp: float) -> None:
        """Replicates data with simulated delay."""
        time.sleep(self._replication_delay_ms / 1000.0)
        
        with self._lock:
            self._data[key] = Entry(value, timestamp)
            self._last_replication_time = time.time()
        
        print(f"[{self.name}] Replicated: {key} (delay: {self._replication_delay_ms}ms)")

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            entry = self._data.get(key)
            return entry.value if entry else None

    def get_last_applied_time(self, key: str) -> float:
        with self._lock:
            entry = self._data.get(key)
            return entry.timestamp if entry else 0

    @property
    def current_lag(self) -> int:
        return int((time.time() - self._last_replication_time) * 1000)


class AsyncReplication:
    """
    Async replication with lag simulation.
    
    Example:
        db = AsyncReplication(replica_count=2, replication_delay_ms=500)
        db.write("user:1", "Alice")
        time.sleep(0.6)
        value = db.read_eventual("user:1")
    """
    
    def __init__(self, replica_count: int, replication_delay_ms: int):
        self._primary: Dict[str, Entry] = {}
        self._replicas = [
            ReplicaDatabase(f"replica-{i}", replication_delay_ms)
            for i in range(replica_count)
        ]
        self._executor = ThreadPoolExecutor(max_workers=replica_count)
        self._write_timestamps: Dict[str, float] = {}
        self._round_robin_index = 0
        self._lock = threading.Lock()

    def write(self, key: str, value: str) -> None:
        """Writes to primary and asynchronously replicates."""
        timestamp = time.time()
        
        # Write to primary immediately
        with self._lock:
            self._primary[key] = Entry(value, timestamp)
            self._write_timestamps[key] = timestamp
        
        print(f"[PRIMARY] Write: {key} = {value}")
        
        # Async replication
        for replica in self._replicas:
            self._executor.submit(
                replica.replicate_with_delay, key, value, timestamp
            )

    def read_eventual(self, key: str) -> Optional[str]:
        """Reads with eventual consistency."""
        if not self._replicas:
            entry = self._primary.get(key)
            return entry.value if entry else None
        
        with self._lock:
            self._round_robin_index = (self._round_robin_index + 1) % len(self._replicas)
            replica = self._replicas[self._round_robin_index]
        
        value = replica.get(key)
        print(f"[{replica.name}] Read (eventual): {key} = {value} (lag: {replica.current_lag}ms)")
        return value

    def read_consistent(self, key: str) -> Optional[str]:
        """Reads with read-your-writes consistency."""
        write_time = self._write_timestamps.get(key)
        
        if write_time is None:
            return self.read_eventual(key)
        
        # Check if any replica is caught up
        for replica in self._replicas:
            if replica.get_last_applied_time(key) >= write_time:
                value = replica.get(key)
                print(f"[{replica.name}] Read (consistent): {key} = {value}")
                return value
        
        # Fall back to primary
        with self._lock:
            entry = self._primary.get(key)
        value = entry.value if entry else None
        print(f"[PRIMARY] Read (consistent, fallback): {key} = {value}")
        return value

    def print_lag_status(self) -> None:
        """Prints replication lag status."""
        print("\n=== Replication Lag Status ===")
        for replica in self._replicas:
            print(f"{replica.name}: lag={replica.current_lag}ms")

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False)


# Demo
if __name__ == "__main__":
    print("=== Async Replication Demo ===\n")
    
    # Create system with 2 replicas, 500ms replication delay
    db = AsyncReplication(replica_count=2, replication_delay_ms=500)
    
    # Write data
    print("--- Writing data ---")
    db.write("user:1", "Alice")
    
    # Immediate read - replica might not have data yet
    print("\n--- Immediate read (might miss) ---")
    db.read_eventual("user:1")
    
    # Consistent read - falls back to primary
    print("\n--- Consistent read (falls back to primary) ---")
    db.read_consistent("user:1")
    
    # Wait for replication
    print("\n--- Waiting for replication (600ms) ---")
    time.sleep(0.6)
    
    # Now replica has data
    print("\n--- Read after replication ---")
    db.read_eventual("user:1")
    db.read_consistent("user:1")
    
    # Status
    db.print_lag_status()
    
    db.shutdown()
