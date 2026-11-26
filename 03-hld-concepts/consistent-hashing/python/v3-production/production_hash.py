"""
V3: Production Consistent Hashing with replication and operations-focused demos.
"""

import bisect
import hashlib
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Set


@dataclass
class NodeInfo:
    """Node metadata for health and request distribution."""

    node_id: str
    weight: int
    healthy: bool = True
    request_count: int = 0


@dataclass
class LookupResult:
    """Primary plus replica ownership for a key."""

    primary_node: str
    replicas: List[str]

    def get_all_nodes(self) -> List[str]:
        return [self.primary_node] + self.replicas


@dataclass
class Metrics:
    """Simple counters for observability."""

    lookups: int = 0
    rebalance_count: int = 0

    def record_lookup(self) -> None:
        self.lookups += 1

    def record_rebalance(self) -> None:
        self.rebalance_count += 1


class ProductionConsistentHash:
    """
    Production-style consistent hash ring.

    Backward compatibility:
    - Accepts both `default_vnodes` and `num_replicas` for vnode count.
    - Supports both `lookup(key)` and `get_nodes(key)` styles.
    """

    def __init__(
        self,
        default_vnodes: int = 100,
        replication_factor: int = 1,
        load_factor: float = 1.0,
        num_replicas: Optional[int] = None,
    ):
        if num_replicas is not None:
            default_vnodes = num_replicas

        self._default_vnodes = default_vnodes
        self._replication_factor = replication_factor
        self._load_factor = load_factor

        self._ring_keys: List[int] = []
        self._ring_map: Dict[int, str] = {}
        self._nodes: Dict[str, NodeInfo] = {}
        self._metrics = Metrics()
        self._lock = threading.Lock()

    def add_node(self, node_id: str, weight: int = 1) -> None:
        """Add a node to the ring."""
        with self._lock:
            if node_id in self._nodes:
                return

            self._nodes[node_id] = NodeInfo(node_id=node_id, weight=weight)
            vnodes = self._default_vnodes * weight

            for i in range(vnodes):
                h = self._hash(f"{node_id}#{i}")
                idx = bisect.bisect_left(self._ring_keys, h)
                self._ring_keys.insert(idx, h)
                self._ring_map[h] = node_id

            self._metrics.record_rebalance()

    def remove_node(self, node_id: str) -> None:
        """Remove a node from the ring."""
        with self._lock:
            info = self._nodes.pop(node_id, None)
            if info is None:
                return

            vnodes = self._default_vnodes * info.weight
            for i in range(vnodes):
                h = self._hash(f"{node_id}#{i}")
                if h in self._ring_map:
                    del self._ring_map[h]
                    self._ring_keys.remove(h)

            self._metrics.record_rebalance()

    def set_node_health(self, node_id: str, healthy: bool) -> None:
        """Set node health status."""
        info = self._nodes.get(node_id)
        if info is not None:
            info.healthy = healthy

    def lookup(self, key: str) -> Optional[LookupResult]:
        """Return primary and replicas for key."""
        self._metrics.record_lookup()

        if not self._ring_keys:
            return None

        node_list = self._get_nodes_for_key(key, self._replication_factor)
        if not node_list:
            return None

        return LookupResult(primary_node=node_list[0], replicas=node_list[1:])

    def get_nodes(self, key: str) -> List[str]:
        """Backward-compatible helper returning node list only."""
        result = self.lookup(key)
        return result.get_all_nodes() if result else []

    def _get_nodes_for_key(self, key: str, count: int) -> List[str]:
        result: List[str] = []
        seen: Set[str] = set()

        h = self._hash(key)
        idx = bisect.bisect_left(self._ring_keys, h)
        attempts = 0
        max_attempts = len(self._ring_keys)

        while len(result) < count and len(result) < len(self._nodes) and attempts < max_attempts:
            if idx >= len(self._ring_keys):
                idx = 0

            ring_h = self._ring_keys[idx]
            node_id = self._ring_map[ring_h]
            info = self._nodes.get(node_id)

            if node_id not in seen and info and info.healthy:
                if self._load_factor <= 1.0 or self._within_bounded_load(info):
                    seen.add(node_id)
                    result.append(node_id)
                    info.request_count += 1

            idx += 1
            attempts += 1

        return result

    def _within_bounded_load(self, node: NodeInfo) -> bool:
        if self._load_factor <= 1.0:
            return True

        total = sum(n.request_count for n in self._nodes.values())
        if total == 0:
            return True

        avg = total / len(self._nodes)
        return node.request_count < (avg * self._load_factor)

    def _hash(self, key: str) -> int:
        digest = hashlib.md5(key.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big")

    def get_distribution(self) -> Dict[str, int]:
        return {node_id: info.request_count for node_id, info in self._nodes.items()}

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def virtual_node_count(self) -> int:
        return len(self._ring_keys)

    @property
    def metrics(self) -> Metrics:
        return self._metrics


def remap_comparison_demo() -> None:
    total_keys = 10000
    keys = [f"key-{i}" for i in range(total_keys)]

    modulo_moved = 0
    for key in keys:
        before = hash(key) % 3
        after = hash(key) % 4
        if before != after:
            modulo_moved += 1

    ring = ProductionConsistentHash(default_vnodes=100, replication_factor=1)
    ring.add_node("node-a")
    ring.add_node("node-b")
    ring.add_node("node-c")

    before_map = {key: ring.lookup(key).primary_node for key in keys}
    ring.add_node("node-d")

    consistent_moved = sum(
        1
        for key in keys
        if before_map[key] != ring.lookup(key).primary_node
    )

    print("   Modulo (3 -> 4 nodes): moved "
          f"{modulo_moved}/{total_keys} ({modulo_moved * 100 / total_keys:.1f}%)")
    print("   Consistent hash (3 -> 4 nodes): moved "
          f"{consistent_moved}/{total_keys} ({consistent_moved * 100 / total_keys:.1f}%)")


def replication_and_failure_demo() -> None:
    ring = ProductionConsistentHash(default_vnodes=100, replication_factor=3)
    ring.add_node("node-a")
    ring.add_node("node-b")
    ring.add_node("node-c")
    ring.add_node("node-d")

    key = "critical:data"
    print(f"   Healthy replicas for {key}: {ring.get_nodes(key)}")

    ring.set_node_health("node-a", False)
    print(f"   After node-a failure: {ring.get_nodes(key)}")

    ring.set_node_health("node-a", True)
    print(f"   After recovery: {ring.get_nodes(key)}")


def hotspot_demo() -> None:
    ring = ProductionConsistentHash(default_vnodes=100, replication_factor=2)
    ring.add_node("node-a")
    ring.add_node("node-b")
    ring.add_node("node-c")

    hot_key = "event:mega-concert"
    ownership: Dict[str, int] = {}
    for _ in range(5000):
        owner = ring.lookup(hot_key).primary_node
        ownership[owner] = ownership.get(owner, 0) + 1

    print(f"   Hot key ownership counts: {ownership}")
    print("   Note: consistent hashing handles remap churn, not traffic popularity skew.")
    print("   Typical mitigations: replica reads, key bucketing, local cache, rate limits.")


def bounded_load_demo() -> None:
    ring = ProductionConsistentHash(default_vnodes=100, replication_factor=1, load_factor=1.25)
    ring.add_node("node-a")
    ring.add_node("node-b")
    ring.add_node("node-c")

    for i in range(10000):
        ring.lookup(f"key-{i}")

    dist = ring.get_distribution()
    print(f"   Distribution: {dist}")

    counts = list(dist.values())
    avg = sum(counts) / len(counts)
    max_dev = max(abs(c - avg) / max(avg, 1.0) * 100 for c in counts)

    print(f"   Max deviation from average: {max_dev:.1f}%")
    print("   Metrics: "
          f"lookups={ring.metrics.lookups} "
          f"rebalance={ring.metrics.rebalance_count} "
          f"nodes={ring.node_count} vnodes={ring.virtual_node_count}")


def main() -> None:
    print("=== Production Consistent Hash Demo ===\n")
    print("1. Remap Comparison: Modulo vs Consistent Hashing")
    remap_comparison_demo()

    print("\n2. Replication and Failure Handling")
    replication_and_failure_demo()

    print("\n3. Hotspot Narrative and Mitigation")
    hotspot_demo()

    print("\n4. Bounded Load and Distribution")
    bounded_load_demo()

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
