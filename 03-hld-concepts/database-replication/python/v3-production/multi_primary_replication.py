"""
V3: Multi-Primary Replication with Conflict Resolution

Demonstrates multi-master replication with last-write-wins
conflict resolution strategy.

Features:
- Multiple primary nodes
- Bi-directional replication
- Last-write-wins conflict resolution
- Conflict detection and logging
"""

import time
import threading
from typing import Dict, List, Optional, Protocol
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class VersionedValue:
    """Value with version information."""
    value: str
    timestamp: float
    origin: str


class ConflictResolver(Protocol):
    """Protocol for conflict resolution strategies."""
    def resolve(self, a: VersionedValue, b: VersionedValue) -> VersionedValue:
        ...


class LastWriteWinsResolver:
    """Last-write-wins resolution strategy."""
    
    def resolve(self, a: VersionedValue, b: VersionedValue) -> VersionedValue:
        return a if a.timestamp >= b.timestamp else b


class PrimaryNode:
    """Primary node with local storage and replication."""
    
    def __init__(self, name: str, replication_delay_ms: int, resolver: ConflictResolver):
        self.name = name
        self._replication_delay_ms = replication_delay_ms
        self._resolver = resolver
        self._data: Dict[str, VersionedValue] = {}
        self._peers: List['PrimaryNode'] = []
        self._lock = threading.Lock()
        self._conflict_count = 0

    def set_peers(self, peers: List['PrimaryNode']) -> None:
        self._peers = peers

    def local_write(self, key: str, value: str, timestamp: float) -> None:
        """Writes locally without replication."""
        new_value = VersionedValue(value, timestamp, self.name)
        
        with self._lock:
            existing = self._data.get(key)
            if existing is not None and existing.timestamp >= timestamp:
                print(f"[{self.name}] Local write rejected (stale): {key}")
                return
            
            self._data[key] = new_value
        
        print(f"[{self.name}] Local write: {key} = {value} (ts={timestamp:.3f})")

    def replicate_to_peers(self, key: str) -> None:
        """Replicates to all peers."""
        with self._lock:
            value = self._data.get(key)
        
        if value is None:
            return
        
        for peer in self._peers:
            time.sleep(self._replication_delay_ms / 1000.0)
            peer.apply_replication(key, value)

    def apply_replication(self, key: str, incoming: VersionedValue) -> None:
        """Applies replicated data with conflict resolution."""
        with self._lock:
            existing = self._data.get(key)
            
            if existing is None:
                self._data[key] = incoming
                print(f"[{self.name}] Replicated: {key} = {incoming.value} from {incoming.origin}")
                return
            
            # Conflict detection
            if existing.origin != incoming.origin:
                self._conflict_count += 1
                
                # Resolve using strategy
                winner = self._resolver.resolve(existing, incoming)
                self._data[key] = winner
                
                print(f"[{self.name}] CONFLICT on {key}: "
                      f"{existing.value}(ts={existing.timestamp:.3f}) vs "
                      f"{incoming.value}(ts={incoming.timestamp:.3f}) -> Winner: {winner.value}")
                return
            
            # Same origin, apply if newer
            if incoming.timestamp > existing.timestamp:
                self._data[key] = incoming

    def read(self, key: str) -> Optional[str]:
        """Reads a value."""
        with self._lock:
            value = self._data.get(key)
        result = value.value if value else None
        print(f"[{self.name}] Read: {key} = {result}")
        return result

    def size(self) -> int:
        with self._lock:
            return len(self._data)

    @property
    def conflict_count(self) -> int:
        return self._conflict_count


class MultiPrimaryReplication:
    """
    Multi-primary replication with conflict resolution.
    
    Example:
        db = MultiPrimaryReplication(node_count=3, replication_delay_ms=100)
        db.write(0, "key", "value1")
        db.write(1, "key", "value2")  # Conflict!
        time.sleep(0.3)
        db.read(0, "key")  # Returns winner
    """
    
    def __init__(self, node_count: int, replication_delay_ms: int):
        self._resolver = LastWriteWinsResolver()
        self._primaries = [
            PrimaryNode(f"primary-{i}", replication_delay_ms, self._resolver)
            for i in range(node_count)
        ]
        self._executor = ThreadPoolExecutor(max_workers=node_count * 2)
        
        # Set up bi-directional replication
        for node in self._primaries:
            peers = [p for p in self._primaries if p != node]
            node.set_peers(peers)

    def write(self, node_index: int, key: str, value: str) -> None:
        """Writes to a specific primary."""
        if node_index < 0 or node_index >= len(self._primaries):
            raise ValueError("Invalid node index")
        
        node = self._primaries[node_index]
        timestamp = time.time()
        
        node.local_write(key, value, timestamp)
        
        # Async replication
        self._executor.submit(node.replicate_to_peers, key)

    def read(self, node_index: int, key: str) -> Optional[str]:
        """Reads from a specific primary."""
        if node_index < 0 or node_index >= len(self._primaries):
            raise ValueError("Invalid node index")
        
        return self._primaries[node_index].read(key)

    def simulate_concurrent_writes(self, key: str, value1: str, value2: str) -> None:
        """Simulates concurrent writes to different primaries."""
        print("\n=== Simulating Concurrent Writes ===")
        print(f"Primary-0 writing: {value1}")
        print(f"Primary-1 writing: {value2}")
        
        barrier = threading.Barrier(2)
        
        def write_0():
            self._primaries[0].local_write(key, value1, time.time())
            barrier.wait()
        
        def write_1():
            time.sleep(0.01)  # Slight delay for different timestamps
            self._primaries[1].local_write(key, value2, time.time())
            barrier.wait()
        
        t1 = threading.Thread(target=write_0)
        t2 = threading.Thread(target=write_1)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Trigger replication
        for node in self._primaries:
            self._executor.submit(node.replicate_to_peers, key)

    def print_status(self) -> None:
        """Prints system status."""
        print("\n=== Multi-Primary Status ===")
        for node in self._primaries:
            print(f"{node.name}: {node.size()} records")
        
        total_conflicts = sum(n.conflict_count for n in self._primaries)
        print(f"\nConflicts detected: {total_conflicts}")

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False)


# Demo
if __name__ == "__main__":
    print("=== Multi-Primary Replication Demo ===\n")
    
    # Create system with 3 primaries, 100ms replication delay
    db = MultiPrimaryReplication(node_count=3, replication_delay_ms=100)
    
    # Write to different primaries
    print("--- Writing to different primaries ---")
    db.write(0, "user:1", "Alice")
    db.write(1, "user:2", "Bob")
    db.write(2, "user:3", "Charlie")
    
    # Wait for replication
    time.sleep(0.3)
    
    # Read from any primary
    print("\n--- Reading from different primaries ---")
    db.read(0, "user:1")
    db.read(1, "user:1")  # Replicated from primary-0
    db.read(2, "user:2")  # Replicated from primary-1
    
    # Simulate conflict
    db.simulate_concurrent_writes("config", "value-from-dc1", "value-from-dc2")
    
    # Wait for conflict resolution
    time.sleep(0.3)
    
    # Check final values
    print("\n--- Final values after conflict resolution ---")
    db.read(0, "config")
    db.read(1, "config")
    db.read(2, "config")
    
    # Status
    db.print_status()
    
    db.shutdown()
