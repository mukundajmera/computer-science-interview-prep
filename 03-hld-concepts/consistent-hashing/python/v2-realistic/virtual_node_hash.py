"""
V2: Consistent Hash with Virtual Nodes

Improved consistent hashing with virtual nodes for better
load distribution. Each physical server is represented by
multiple points on the hash ring.

Features:
- Virtual nodes for even distribution
- MD5 hashing for better spread
- Configurable vnodes per server
- Server weighting support
"""

import hashlib
import bisect
from typing import Optional, Set, List, Dict


class VirtualNodeConsistentHash:
    """
    Consistent hash ring with virtual nodes.
    
    Example:
        ch = VirtualNodeConsistentHash(default_vnodes=100)
        ch.add_server("server-a")
        ch.add_server("server-b", weight=2)  # Gets 2x the keys
        
        server = ch.get_server("my-key")
        replicas = ch.get_servers("my-key", count=3)
    """
    
    def __init__(self, default_vnodes: int = 100, num_replicas: Optional[int] = None):
        """
        Creates a consistent hash ring with virtual nodes.
        
        Args:
            default_vnodes: Default virtual nodes per server
        """
        if num_replicas is not None:
            default_vnodes = num_replicas

        self._default_vnodes = default_vnodes
        self._ring_keys: List[int] = []  # Sorted hash positions
        self._ring_map: Dict[int, str] = {}  # hash -> server
        self._server_weights: Dict[str, int] = {}
    
    def add_server(self, server: str, weight: int = 1) -> None:
        """
        Adds a server with specified weight.
        Higher weight = more virtual nodes = more keys.
        """
        if server in self._server_weights:
            return
        
        self._server_weights[server] = weight
        vnodes = self._default_vnodes * weight
        
        for i in range(vnodes):
            vnode_key = f"{server}#{i}"
            hash_val = self._hash(vnode_key)
            
            idx = bisect.bisect_left(self._ring_keys, hash_val)
            self._ring_keys.insert(idx, hash_val)
            self._ring_map[hash_val] = server

    # Backward-compatible alias used by tests and older docs.
    def add_node(self, node_id: str, weight: int = 1) -> None:
        self.add_server(node_id, weight)
    
    def remove_server(self, server: str) -> None:
        """Removes a server and all its virtual nodes."""
        weight = self._server_weights.pop(server, None)
        if weight is None:
            return
        
        vnodes = self._default_vnodes * weight
        for i in range(vnodes):
            vnode_key = f"{server}#{i}"
            hash_val = self._hash(vnode_key)
            
            if hash_val in self._ring_map:
                self._ring_keys.remove(hash_val)
                del self._ring_map[hash_val]

    # Backward-compatible alias used by tests and older docs.
    def remove_node(self, node_id: str) -> None:
        self.remove_server(node_id)
    
    def get_server(self, key: str) -> Optional[str]:
        """Gets the server responsible for the given key."""
        if not self._ring_keys:
            return None
        
        hash_val = self._hash(key)
        
        idx = bisect.bisect_left(self._ring_keys, hash_val)
        if idx >= len(self._ring_keys):
            idx = 0
        
        ring_hash = self._ring_keys[idx]
        return self._ring_map[ring_hash]

    # Backward-compatible alias used by tests and older docs.
    def get_node(self, key: str) -> Optional[str]:
        return self.get_server(key)
    
    def get_servers(self, key: str, count: int) -> List[str]:
        """Gets N distinct servers for replication."""
        if not self._ring_keys:
            return []
        
        servers = []
        seen = set()
        
        hash_val = self._hash(key)
        current_idx = bisect.bisect_left(self._ring_keys, hash_val)
        
        attempts = 0
        while len(servers) < count and len(servers) < len(self._server_weights):
            if current_idx >= len(self._ring_keys):
                current_idx = 0
            
            ring_hash = self._ring_keys[current_idx]
            server = self._ring_map[ring_hash]
            
            if server not in seen:
                seen.add(server)
                servers.append(server)
            
            current_idx += 1
            attempts += 1
            
            if attempts > len(self._ring_keys):
                break
        
        return servers
    
    def _hash(self, key: str) -> int:
        """MD5-based hash function for better distribution."""
        digest = hashlib.md5(key.encode('utf-8')).digest()
        return int.from_bytes(digest[:8], 'big')
    
    @property
    def virtual_node_count(self) -> int:
        """Returns the total number of virtual nodes."""
        return len(self._ring_keys)
    
    @property
    def server_count(self) -> int:
        """Returns the number of physical servers."""
        return len(self._server_weights)
    
    def get_servers_list(self) -> Set[str]:
        """Returns all physical servers."""
        return set(self._server_weights.keys())

    @property
    def ring(self) -> Dict[int, str]:
        """Backward-compatible accessor for ring map."""
        return self._ring_map


# ============ Demo ============

def main():
    import math
    
    print("=== Virtual Node Consistent Hash Demo ===\n")
    
    # Demo 1: Better distribution with vnodes
    print("1. Distribution Comparison:")
    distribution_demo()
    
    # Demo 2: Weighted servers
    print("\n2. Weighted Servers:")
    weighted_demo()
    
    # Demo 3: Replication
    print("\n3. Replication:")
    replication_demo()
    
    # Demo 4: Minimal redistribution
    print("\n4. Minimal Redistribution:")
    redistribution_demo()
    
    print("\n=== Demo Complete ===")


def distribution_demo():
    vnode_counts = [1, 10, 100]
    
    for vnodes in vnode_counts:
        ch = VirtualNodeConsistentHash(default_vnodes=vnodes)
        ch.add_server("server-a")
        ch.add_server("server-b")
        ch.add_server("server-c")
        
        dist = {}
        for i in range(10000):
            server = ch.get_server(f"key-{i}")
            dist[server] = dist.get(server, 0) + 1
        
        print(f"   {vnodes} vnodes per server:")
        for s, c in sorted(dist.items()):
            print(f"      {s}: {c} ({c/100:.1f}%)")
        
        # Calculate standard deviation
        avg = 10000 / 3
        variance = sum((c - avg) ** 2 for c in dist.values()) / len(dist)
        print(f"      Std Dev: {variance ** 0.5:.1f}")


def weighted_demo():
    ch = VirtualNodeConsistentHash(default_vnodes=50)
    
    # Server A has 2x capacity
    ch.add_server("server-a", weight=2)
    ch.add_server("server-b", weight=1)
    ch.add_server("server-c", weight=1)
    
    dist = {}
    for i in range(10000):
        server = ch.get_server(f"key-{i}")
        dist[server] = dist.get(server, 0) + 1
    
    print("   Weights: A=2, B=1, C=1")
    for s, c in sorted(dist.items()):
        print(f"      {s}: {c} ({c/100:.1f}%)")
    print("   (A should get ~50%, B and C ~25% each)")


def replication_demo():
    ch = VirtualNodeConsistentHash(default_vnodes=100)
    ch.add_server("server-a")
    ch.add_server("server-b")
    ch.add_server("server-c")
    ch.add_server("server-d")
    
    key = "important:data:123"
    replication_factor = 3
    
    replicas = ch.get_servers(key, replication_factor)
    
    print(f"   Key: '{key}'")
    print(f"   Replication factor: {replication_factor}")
    print(f"   Replica servers: {replicas}")


def redistribution_demo():
    ch = VirtualNodeConsistentHash(default_vnodes=100)
    ch.add_server("server-a")
    ch.add_server("server-b")
    ch.add_server("server-c")
    
    # Store original mappings
    original = {}
    for i in range(10000):
        key = f"key-{i}"
        original[key] = ch.get_server(key)
    
    # Add new server
    ch.add_server("server-d")
    
    # Count moved keys
    moved = 0
    for i in range(10000):
        key = f"key-{i}"
        if ch.get_server(key) != original[key]:
            moved += 1
    
    print(f"   Original: 3 servers, 10000 keys")
    print(f"   Added: server-d")
    print(f"   Keys moved: {moved} ({moved/100:.1f}%)")
    print(f"   Expected: ~25% (1/4 of keys)")


if __name__ == "__main__":
    main()
