import hashlib
import json
import math
import bisect
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict


class MetricType(Enum):
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"


class MetricPoint:
    def __init__(self, name: str, metric_type: MetricType, tags: Dict[str, str], timestamp_ms: int, value: float):
        self.name = name
        self.metric_type = metric_type
        self.tags = tags.copy() if tags else {}
        self.timestamp_ms = timestamp_ms
        self.value = value

    def to_dict(self):
        return {
            "name": self.name,
            "metric_type": self.metric_type.value,
            "tags": self.tags,
            "timestamp_ms": self.timestamp_ms,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], MetricType(d["metric_type"]), d["tags"], d["timestamp_ms"], d["value"])


class ConsistentHashRing:
    def __init__(self, virtual_nodes: int = 100):
        self.virtual_nodes = virtual_nodes
        self.ring: List[int] = []
        self.node_map: Dict[int, str] = {}

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_id: str):
        for i in range(self.virtual_nodes):
            v_node_key = f"{node_id}#{i}"
            h = self._hash(v_node_key)
            self.ring.append(h)
            self.node_map[h] = node_id
        self.ring.sort()

    def remove_node(self, node_id: str):
        self.ring = [h for h in self.ring if self.node_map[h] != node_id]
        self.node_map = {h: n for h, n in self.node_map.items() if n != node_id}

    def get_nodes(self, key: str, count: int) -> List[str]:
        if not self.ring:
            return []
        h = self._hash(key)
        idx = bisect.bisect(self.ring, h)
        if idx == len(self.ring):
            idx = 0

        nodes = []
        start_idx = idx
        while len(nodes) < count and len(nodes) < len(set(self.node_map.values())):
            node = self.node_map[self.ring[idx]]
            if node not in nodes:
                nodes.append(node)
            idx = (idx + 1) % len(self.ring)
            if idx == start_idx:
                break
        return nodes


class ColdStore:
    def __init__(self):
        self.storage: Dict[str, str] = {}

    def put(self, key: str, data: str):
        self.storage[key] = data

    def get(self, key: str) -> Optional[str]:
        return self.storage.get(key)


class Node:
    def __init__(self, node_id: str, cold_store: ColdStore, chunk_size_ms: int = 3600000):
        self.node_id = node_id
        self.cold_store = cold_store
        self.chunk_size_ms = chunk_size_ms
        self.is_alive = True

        self.wal: List[MetricPoint] = []
        self.local_chunks: Dict[int, List[MetricPoint]] = defaultdict(list)

    def ingest(self, point: MetricPoint):
        if not self.is_alive:
            raise Exception("Node is down")
        self.wal.append(point)

    def flush_wal_to_chunks(self):
        if not self.is_alive:
            return
        for point in self.wal:
            chunk_idx = point.timestamp_ms // self.chunk_size_ms
            self.local_chunks[chunk_idx].append(point)
        self.wal.clear()

    def flush_chunks_to_cold_store(self, up_to_chunk_idx: int):
        if not self.is_alive:
            return
        for chunk_idx in list(self.local_chunks.keys()):
            if chunk_idx <= up_to_chunk_idx:
                data = [p.to_dict() for p in self.local_chunks[chunk_idx]]
                key = f"{self.node_id}_{chunk_idx}"
                existing = self.cold_store.get(key)
                if existing:
                    data.extend(json.loads(existing))
                self.cold_store.put(key, json.dumps(data))
                del self.local_chunks[chunk_idx]

    def _matches_tags(self, point_tags: Dict[str, str], query_tags: Dict[str, str]) -> bool:
        if not query_tags:
            return True
        for k, v in query_tags.items():
            if point_tags.get(k) != v:
                return False
        return True

    def query(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> List[MetricPoint]:
        if not self.is_alive:
            raise Exception("Node is down")

        result = []

        # 1. Query WAL
        for p in self.wal:
            if p.name == metric_name and start_ms <= p.timestamp_ms <= end_ms and self._matches_tags(p.tags, tags):
                result.append(p)

        # 2. Query Local Chunks & 3. Query Cold Store
        start_chunk = start_ms // self.chunk_size_ms
        end_chunk = end_ms // self.chunk_size_ms
        for chunk_idx in range(start_chunk, end_chunk + 1):
            if chunk_idx in self.local_chunks:
                for p in self.local_chunks[chunk_idx]:
                    if p.name == metric_name and start_ms <= p.timestamp_ms <= end_ms and self._matches_tags(p.tags, tags):
                        result.append(p)
            else:
                key = f"{self.node_id}_{chunk_idx}"
                data = self.cold_store.get(key)
                if data:
                    points_data = json.loads(data)
                    for pd in points_data:
                        p = MetricPoint.from_dict(pd)
                        if p.name == metric_name and start_ms <= p.timestamp_ms <= end_ms and self._matches_tags(p.tags, tags):
                            result.append(p)

        return result


class DistributedMetricsMonitoringService:
    def __init__(self, num_nodes: int = 3, replication_factor: int = 2):
        self.cold_store = ColdStore()
        self.nodes: Dict[str, Node] = {
            f"node_{i}": Node(f"node_{i}", self.cold_store) for i in range(num_nodes)
        }
        self.ring = ConsistentHashRing()
        for node_id in self.nodes:
            self.ring.add_node(node_id)
        self.replication_factor = min(replication_factor, num_nodes)

    def _get_shard_key(self, metric_name: str, tags: Dict[str, str]) -> str:
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_name}|{tag_str}"

    def ingest(self, point: MetricPoint):
        shard_key = self._get_shard_key(point.name, point.tags)
        target_node_ids = self.ring.get_nodes(shard_key, self.replication_factor)

        success_count = 0
        for node_id in target_node_ids:
            try:
                self.nodes[node_id].ingest(point)
                success_count += 1
            except Exception:
                pass

        if success_count == 0:
            raise Exception("Failed to ingest on any replica")

    def set_node_status(self, node_id: str, is_alive: bool):
        if node_id in self.nodes:
            self.nodes[node_id].is_alive = is_alive

    def flush_all(self):
        for node in self.nodes.values():
            if node.is_alive:
                node.flush_wal_to_chunks()

    def cold_flush_all(self, up_to_chunk_idx: int):
        for node in self.nodes.values():
            if node.is_alive:
                node.flush_chunks_to_cold_store(up_to_chunk_idx)

    def reconcile_replicas(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int):
        shard_key = self._get_shard_key(metric_name, tags)
        target_node_ids = self.ring.get_nodes(shard_key, self.replication_factor)

        all_points = {}
        for node_id in target_node_ids:
            if self.nodes[node_id].is_alive:
                try:
                    points = self.nodes[node_id].query(metric_name, tags, start_ms, end_ms)
                    for p in points:
                        p_key = (p.name, tuple(sorted(p.tags.items())), p.timestamp_ms, p.value)
                        all_points[p_key] = p
                except Exception:
                    pass

        for node_id in target_node_ids:
            if self.nodes[node_id].is_alive:
                current_points = set()
                try:
                    points = self.nodes[node_id].query(metric_name, tags, start_ms, end_ms)
                    for p in points:
                        current_points.add((p.name, tuple(sorted(p.tags.items())), p.timestamp_ms, p.value))
                except Exception:
                    continue

                for p_key, p in all_points.items():
                    if p_key not in current_points:
                        try:
                            self.nodes[node_id].ingest(p)
                        except Exception:
                            pass

    def query(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> List[MetricPoint]:
        shard_key = self._get_shard_key(metric_name, tags)
        target_node_ids = self.ring.get_nodes(shard_key, self.replication_factor)

        all_points = {}
        for node_id in target_node_ids:
            try:
                points = self.nodes[node_id].query(metric_name, tags, start_ms, end_ms)
                for p in points:
                    p_key = (p.name, tuple(sorted(p.tags.items())), p.timestamp_ms, p.value)
                    all_points[p_key] = p
            except Exception:
                pass

        return list(all_points.values())

    def get_counter_total(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> float:
        points = self.query(metric_name, tags, start_ms, end_ms)
        return sum(p.value for p in points if p.metric_type == MetricType.COUNTER)

    def get_gauge_latest(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int) -> float:
        points = self.query(metric_name, tags, start_ms, end_ms)
        gauges = [p for p in points if p.metric_type == MetricType.GAUGE]
        if not gauges:
            return 0.0
        return max(gauges, key=lambda p: p.timestamp_ms).value

    def get_histogram_percentile(self, metric_name: str, tags: Dict[str, str], start_ms: int, end_ms: int, percentile: float) -> float:
        points = self.query(metric_name, tags, start_ms, end_ms)
        hist_points = [p for p in points if p.metric_type == MetricType.HISTOGRAM]
        if not hist_points:
            return 0.0
        values = sorted(p.value for p in hist_points)
        index = int(math.ceil((percentile / 100.0) * len(values))) - 1
        index = max(0, min(index, len(values) - 1))
        return values[index]
