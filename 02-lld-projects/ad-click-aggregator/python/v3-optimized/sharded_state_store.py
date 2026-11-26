"""ShardedStateStore for ad-click-aggregator (v3-optimized)."""
import threading
from typing import Dict
from aggregation_key import AggregationKey
from partition_router import PartitionRouter

class ShardedStateStore:
    def __init__(self, num_partitions: int = 10) -> None:
        self.router = PartitionRouter(num_partitions)
        self.locks = [threading.Lock() for _ in range(num_partitions)]
        self.stores: list[Dict[AggregationKey, int]] = [{} for _ in range(num_partitions)]

    def increment(self, key: AggregationKey, count: int = 1) -> None:
        partition = self.router.get_partition(key.ad_id)
        with self.locks[partition]:
            self.stores[partition][key] = self.stores[partition].get(key, 0) + count

    def get_count(self, key: AggregationKey) -> int:
        partition = self.router.get_partition(key.ad_id)
        with self.locks[partition]:
            return self.stores[partition].get(key, 0)
