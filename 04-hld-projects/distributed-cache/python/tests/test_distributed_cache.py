import sys
import os
from typing import Optional, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-scaled'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-distributed'))

from cache_service import CacheService
from partitioned_cache_service import PartitionedCacheService
from distributed_cache_cluster_service import DistributedCacheClusterService

class InMemoryCache(CacheService):
    def __init__(self):
        self.store: Dict[str, str] = {}
        
    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.store[key] = value
        
    def get(self, key: str) -> Optional[str]:
        return self.store.get(key)
        
    def delete(self, key: str) -> bool:
        if key in self.store:
            del self.store[key]
            return True
        return False

class DummyPartitionedCache(PartitionedCacheService):
    def __init__(self):
        self.replicas = []
        self.rebalanced = False
        
    def resolve_node_for_key(self, key: str) -> str:
        return f"node-{len(key)}"
        
    def replicate_write(self, key: str, value: str, ttl_seconds: int) -> None:
        self.replicas.append((key, value))
        
    def rebalance_range(self, token_range: str, target_node_id: str) -> None:
        self.rebalanced = True

class DummyClusterService(DistributedCacheClusterService):
    def __init__(self):
        self.failed_nodes = []
        self.promoted = []
        self.mitigated_keys = []
        
    def handle_node_failure(self, node_id: str) -> None:
        self.failed_nodes.append(node_id)
        
    def promote_replica(self, key_range: str) -> None:
        self.promoted.append(key_range)
        
    def mitigate_hot_key(self, key: str) -> None:
        self.mitigated_keys.append(key)


def test_v1_basic_cache():
    cache = InMemoryCache()
    cache.set("foo", "bar", 60)
    assert cache.get("foo") == "bar"
    
    assert cache.delete("foo") is True
    assert cache.get("foo") is None
    assert cache.delete("foo") is False

def test_v2_scaled_cache():
    pcache = DummyPartitionedCache()
    assert pcache.resolve_node_for_key("key1") == "node-4"
    
    pcache.replicate_write("key2", "val2", 120)
    assert len(pcache.replicas) == 1
    assert pcache.replicas[0] == ("key2", "val2")
    
    pcache.rebalance_range("0-100", "node-2")
    assert pcache.rebalanced is True

def test_v3_distributed_cluster():
    cluster = DummyClusterService()
    
    cluster.handle_node_failure("node-fail")
    assert "node-fail" in cluster.failed_nodes
    
    cluster.promote_replica("100-200")
    assert "100-200" in cluster.promoted
    
    cluster.mitigate_hot_key("hot_key_1")
    assert "hot_key_1" in cluster.mitigated_keys

