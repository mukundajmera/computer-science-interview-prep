"""
V1: Simple Primary-Replica Simulation

Basic simulation of master-slave replication with
write/read separation.

Features:
- Single primary for writes
- Multiple replicas for reads
- Simple synchronous replication
"""

from typing import Dict, List, Optional


class Database:
    """Simple in-memory database."""
    
    def __init__(self, name: str):
        self.name = name
        self._data: Dict[str, str] = {}

    def put(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def size(self) -> int:
        return len(self._data)


class SimplePrimaryReplica:
    """
    Simple primary-replica replication system.
    
    Example:
        db = SimplePrimaryReplica(replica_count=3)
        db.write("user:1", "Alice")
        value = db.read("user:1")
    """
    
    def __init__(self, replica_count: int = 2):
        self._primary = Database("primary")
        self._replicas: List[Database] = [
            Database(f"replica-{i}") for i in range(replica_count)
        ]

    def write(self, key: str, value: str) -> None:
        """Writes to primary and replicates to all replicas."""
        # Write to primary
        self._primary.put(key, value)
        print(f"[PRIMARY] Write: {key} = {value}")
        
        # Replicate to all replicas (synchronous)
        for replica in self._replicas:
            replica.put(key, value)
            print(f"[{replica.name}] Replicated: {key}")

    def read(self, key: str) -> Optional[str]:
        """Reads from a replica (round-robin)."""
        if not self._replicas:
            return self._primary.get(key)
        
        # Simple round-robin selection
        index = abs(hash(key)) % len(self._replicas)
        replica = self._replicas[index]
        
        value = replica.get(key)
        print(f"[{replica.name}] Read: {key} = {value}")
        return value

    def read_from_primary(self, key: str) -> Optional[str]:
        """Reads from primary (for read-your-writes consistency)."""
        value = self._primary.get(key)
        print(f"[PRIMARY] Read: {key} = {value}")
        return value

    def print_status(self) -> None:
        """Prints database status."""
        print("\n=== Database Status ===")
        print(f"Primary: {self._primary.size()} records")
        for replica in self._replicas:
            print(f"{replica.name}: {replica.size()} records")


# Demo
if __name__ == "__main__":
    print("=== Simple Primary-Replica Demo ===\n")
    
    # Create system with 3 replicas
    db = SimplePrimaryReplica(replica_count=3)
    
    # Write some data
    print("--- Writing data ---")
    db.write("user:1", "Alice")
    db.write("user:2", "Bob")
    db.write("user:3", "Charlie")
    
    print("\n--- Reading data from replicas ---")
    db.read("user:1")
    db.read("user:2")
    db.read("user:3")
    
    print("\n--- Reading from primary (consistency) ---")
    db.read_from_primary("user:1")
    
    print("\n--- Update and read ---")
    db.write("user:1", "Alice Updated")
    db.read("user:1")
    
    db.print_status()
