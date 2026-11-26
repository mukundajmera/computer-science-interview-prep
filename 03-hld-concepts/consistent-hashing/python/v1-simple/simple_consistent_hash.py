"""
V1: Simple Consistent Hash Ring

Basic implementation of consistent hashing using a sorted dictionary
to represent the hash ring. Keys are assigned to the first server
found clockwise from their hash position.

Features:
- Simple hash ring implementation
- Add/remove servers dynamically
- O(log n) key lookup

Limitations:
- No virtual nodes (uneven distribution)
- Uses simple hash function
"""

from typing import Optional, Set, Dict
import bisect


class SimpleConsistentHash:
    """
    Simple consistent hash ring.
    
    Example:
        ch = SimpleConsistentHash()
        ch.add_server("server-a")
        ch.add_server("server-b")
        
        server = ch.get_server("my-key")
    """
    
    def __init__(self):
        self._ring_keys: list = []  # Sorted hash positions
        self._ring_map: Dict[int, str] = {}  # hash -> server
        self._servers: Set[str] = set()
    
    def add_server(self, server: str) -> None:
        """Adds a server to the ring."""
        if server in self._servers:
            return
        
        self._servers.add(server)
        hash_val = self._hash(server)
        
        idx = bisect.bisect_left(self._ring_keys, hash_val)
        self._ring_keys.insert(idx, hash_val)
        self._ring_map[hash_val] = server

    # Backward-compatible alias used by tests and older docs.
    def add_node(self, node_id: str) -> None:
        self.add_server(node_id)
    
    def remove_server(self, server: str) -> None:
        """Removes a server from the ring."""
        if server not in self._servers:
            return
        
        self._servers.remove(server)
        hash_val = self._hash(server)
        
        self._ring_keys.remove(hash_val)
        del self._ring_map[hash_val]

    # Backward-compatible alias used by tests and older docs.
    def remove_node(self, node_id: str) -> None:
        self.remove_server(node_id)
    
    def get_server(self, key: str) -> Optional[str]:
        """
        Gets the server responsible for the given key.
        Walks clockwise from key's hash position.
        """
        if not self._ring_keys:
            return None
        
        hash_val = self._hash(key)
        
        # Find first server at or after this hash
        idx = bisect.bisect_left(self._ring_keys, hash_val)
        
        # Wrap around if past the last server
        if idx >= len(self._ring_keys):
            idx = 0
        
        ring_hash = self._ring_keys[idx]
        return self._ring_map[ring_hash]

    # Backward-compatible alias used by tests and older docs.
    def get_node(self, key: str) -> Optional[str]:
        return self.get_server(key)
    
    def _hash(self, key: str) -> int:
        """Simple hash function."""
        return hash(key) & 0x7FFFFFFF  # Ensure positive
    
    def get_servers(self) -> Set[str]:
        """Returns all servers in the ring."""
        return set(self._servers)
    
    @property
    def server_count(self) -> int:
        """Returns the number of servers."""
        return len(self._servers)

    @property
    def nodes(self) -> Set[str]:
        """Backward-compatible server-set accessor."""
        return self.get_servers()


# ============ Demo ============

def main():
    print("=== Simple Consistent Hash Demo ===\n")
    
    # Demo 1: Basic usage
    print("1. Basic Key-to-Server Mapping:")
    basic_demo()
    
    # Demo 2: Adding a server
    print("\n2. Adding a Server:")
    add_server_demo()
    
    # Demo 3: Consistency check
    print("\n3. Consistency Verification:")
    consistency_demo()
    
    print("\n=== Demo Complete ===")


def basic_demo():
    ch = SimpleConsistentHash()
    ch.add_server("server-a")
    ch.add_server("server-b")
    ch.add_server("server-c")
    
    keys = ["user:1", "user:2", "user:3", "order:100", "product:xyz"]
    
    for key in keys:
        server = ch.get_server(key)
        print(f"   {key} → {server}")


def add_server_demo():
    ch = SimpleConsistentHash()
    ch.add_server("server-a")
    ch.add_server("server-b")
    ch.add_server("server-c")
    
    # Track original mappings
    original_mappings = {}
    for i in range(100):
        key = f"key-{i}"
        original_mappings[key] = ch.get_server(key)
    
    # Count distribution
    dist1 = {}
    for server in original_mappings.values():
        dist1[server] = dist1.get(server, 0) + 1
    
    print("   Before adding server:")
    for s, c in sorted(dist1.items()):
        print(f"      {s}: {c} keys")
    
    # Add new server
    ch.add_server("server-d")
    
    # Count moved keys
    moved = 0
    dist2 = {}
    for i in range(100):
        key = f"key-{i}"
        new_server = ch.get_server(key)
        dist2[new_server] = dist2.get(new_server, 0) + 1
        if new_server != original_mappings[key]:
            moved += 1
    
    print("\n   After adding server-d:")
    for s, c in sorted(dist2.items()):
        print(f"      {s}: {c} keys")
    
    print(f"\n   Keys moved: {moved} ({moved}%)")
    print("   (Ideally ~25% with consistent hashing)")


def consistency_demo():
    ch = SimpleConsistentHash()
    ch.add_server("server-a")
    ch.add_server("server-b")
    ch.add_server("server-c")
    
    key = "user:12345"
    
    # Same key should always map to same server
    server1 = ch.get_server(key)
    server2 = ch.get_server(key)
    server3 = ch.get_server(key)
    
    print(f"   Key '{key}' maps to:")
    print(f"      Call 1: {server1}")
    print(f"      Call 2: {server2}")
    print(f"      Call 3: {server3}")
    print(f"   Consistent: {server1 == server2 == server3}")


if __name__ == "__main__":
    main()
