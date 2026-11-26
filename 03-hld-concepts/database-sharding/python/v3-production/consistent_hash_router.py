"""
Production-grade sharding with consistent hashing for dynamic shard management.
Supports adding/removing shards with minimal data movement.
"""

import hashlib
import threading
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from bisect import bisect_right, insort


@dataclass
class VirtualNode:
    """Virtual node on the hash ring."""
    shard_id: str
    vnode_index: int
    position: int


@dataclass
class ShardDatabase:
    """Simulated shard database with replication support."""
    shard_id: str
    data: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    is_healthy: bool = True
    last_health_check: float = 0.0

    def put(self, key: str, value: Dict[str, Any]) -> None:
        self.data[key] = value

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self.data.get(key)

    def delete(self, key: str) -> bool:
        if key in self.data:
            del self.data[key]
            return True
        return False

    def size(self) -> int:
        return len(self.data)

    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        return dict(self.data)


class ConsistentHashShardRouter:
    """Production-grade consistent hash shard router with replication."""

    def __init__(self, virtual_nodes_per_shard: int = 100, replication_factor: int = 1):
        self.ring: Dict[int, VirtualNode] = {}
        self.sorted_positions: List[int] = []
        self.shards: Dict[str, ShardDatabase] = {}
        self.shard_to_vnodes: Dict[str, List[int]] = {}
        self.virtual_nodes_per_shard = virtual_nodes_per_shard
        self.replication_factor = replication_factor
        self._lock = threading.Lock()

    def _hash(self, key: str) -> int:
        digest = hashlib.md5(key.encode()).digest()
        return (digest[0] << 24) | (digest[1] << 16) | (digest[2] << 8) | digest[3]

    def add_shard(self, shard_id: str) -> None:
        if shard_id in self.shards:
            raise ValueError(f"Shard already exists: {shard_id}")

        self.shards[shard_id] = ShardDatabase(shard_id)
        vnode_positions: List[int] = []

        for i in range(self.virtual_nodes_per_shard):
            position = self._hash(f"{shard_id}#{i}")
            self.ring[position] = VirtualNode(shard_id, i, position)
            insort(self.sorted_positions, position)
            vnode_positions.append(position)

        self.shard_to_vnodes[shard_id] = vnode_positions

    def remove_shard(self, shard_id: str) -> Dict[str, Dict[str, Any]]:
        if shard_id not in self.shards:
            raise ValueError(f"Shard not found: {shard_id}")

        data_to_migrate = self.shards[shard_id].get_all_data()

        positions = self.shard_to_vnodes.pop(shard_id, [])
        for pos in positions:
            del self.ring[pos]
            self.sorted_positions.remove(pos)

        del self.shards[shard_id]
        return data_to_migrate

    def get_shard_for_key(self, key: str) -> str:
        if not self.ring:
            raise RuntimeError("No shards available")

        hash_value = self._hash(key)
        idx = bisect_right(self.sorted_positions, hash_value)
        if idx >= len(self.sorted_positions):
            idx = 0

        return self.ring[self.sorted_positions[idx]].shard_id

    def get_shards_for_replication(self, key: str) -> List[str]:
        if not self.ring:
            return []

        replicas: List[str] = []
        seen: Set[str] = set()
        hash_value = self._hash(key)
        idx = bisect_right(self.sorted_positions, hash_value)

        while len(replicas) < self.replication_factor and len(replicas) < len(self.shards):
            if idx >= len(self.sorted_positions):
                idx = 0

            shard_id = self.ring[self.sorted_positions[idx]].shard_id
            shard = self.shards.get(shard_id)

            if shard_id not in seen and shard and shard.is_healthy:
                replicas.append(shard_id)
                seen.add(shard_id)

            idx += 1

        return replicas

    def put(self, key: str, value: Dict[str, Any]) -> None:
        replica_shards = self.get_shards_for_replication(key)
        if not replica_shards:
            raise RuntimeError("No healthy shards available")

        for shard_id in replica_shards:
            self.shards[shard_id].put(key, value)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        for shard_id in self.get_shards_for_replication(key):
            shard = self.shards.get(shard_id)
            if shard and shard.is_healthy:
                value = shard.get(key)
                if value is not None:
                    return value
        return None

    def mark_shard_unhealthy(self, shard_id: str) -> None:
        shard = self.shards.get(shard_id)
        if shard:
            shard.is_healthy = False

    def mark_shard_healthy(self, shard_id: str) -> None:
        shard = self.shards.get(shard_id)
        if shard:
            shard.is_healthy = True

    def print_distribution(self) -> None:
        print("=== Shard Distribution ===")
        total_items = sum(s.size() for s in self.shards.values())

        for shard_id, shard in self.shards.items():
            status = "healthy" if shard.is_healthy else "unhealthy"
            pct = (shard.size() * 100 // total_items) if total_items > 0 else 0
            print(f"Shard {shard_id}: {shard.size()} items ({pct}%) [{status}]")

    def get_shard_count(self) -> int:
        return len(self.shards)

    def get_virtual_node_count(self) -> int:
        return len(self.ring)


def remap_comparison_demo() -> None:
    total = 10000
    keys = [f"user_{i}" for i in range(total)]

    modulo_moved = 0
    for key in keys:
        if (hash(key) % 3) != (hash(key) % 4):
            modulo_moved += 1

    router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=1)
    router.add_shard("shard_1")
    router.add_shard("shard_2")
    router.add_shard("shard_3")

    before = {key: router.get_shard_for_key(key) for key in keys}
    router.add_shard("shard_4")

    consistent_moved = sum(
        1 for key in keys if before[key] != router.get_shard_for_key(key)
    )

    print("   Modulo (3 -> 4 shards): moved "
          f"{modulo_moved}/{total} ({modulo_moved * 100 / total:.1f}%)")
    print("   Consistent hash (3 -> 4 shards): moved "
          f"{consistent_moved}/{total} ({consistent_moved * 100 / total:.1f}%)")


def replication_and_failure_demo() -> None:
    router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=2)
    router.add_shard("shard_1")
    router.add_shard("shard_2")
    router.add_shard("shard_3")

    key = "critical:order:123"
    router.put(key, {"order_id": 123, "status": "confirmed"})
    print(f"   Replicas for {key}: {router.get_shards_for_replication(key)}")

    primary = router.get_shard_for_key(key)
    router.mark_shard_unhealthy(primary)
    print(f"   Marked primary unhealthy: {primary}")
    print(f"   Read from healthy replica path: {router.get(key)}")


def hotspot_demo() -> None:
    router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=2)
    router.add_shard("shard_1")
    router.add_shard("shard_2")
    router.add_shard("shard_3")

    hot_key = "user:celebrity"
    owner_count: Dict[str, int] = {}
    for _ in range(5000):
        owner = router.get_shard_for_key(hot_key)
        owner_count[owner] = owner_count.get(owner, 0) + 1

    print(f"   Hot key ownership counts: {owner_count}")
    print("   Note: remap behavior improves, but traffic skew still needs separate controls.")
    print("   Mitigations: replica reads, key bucketing, cache and rate limits.")


def rebalance_summary_demo() -> None:
    router = ConsistentHashShardRouter(virtual_nodes_per_shard=100, replication_factor=1)
    router.add_shard("shard_1")
    router.add_shard("shard_2")
    router.add_shard("shard_3")

    for i in range(3000):
        router.put(f"user_{i}", {"id": i})

    print("   Distribution before rebalance:")
    router.print_distribution()

    router.add_shard("shard_4")
    for i in range(3000, 5000):
        router.put(f"user_{i}", {"id": i})

    print("   Distribution after adding shard_4 (new writes):")
    router.print_distribution()
    print(f"   Cluster summary: shards={router.get_shard_count()} vnodes={router.get_virtual_node_count()}")


def main() -> None:
    print("=== Consistent Hash Sharding Demo ===\n")

    print("1. Remap Comparison: Modulo vs Consistent Hash Sharding")
    remap_comparison_demo()

    print("\n2. Replication and Failure Behavior")
    replication_and_failure_demo()

    print("\n3. Hotspot Narrative and Mitigation")
    hotspot_demo()

    print("\n4. Rebalance Summary")
    rebalance_summary_demo()

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
