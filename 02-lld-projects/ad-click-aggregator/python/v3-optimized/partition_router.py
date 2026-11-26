"""PartitionRouter for ad-click-aggregator (v3-optimized)."""

class PartitionRouter:
    def __init__(self, num_partitions: int = 10) -> None:
        self.num_partitions = num_partitions

    def get_partition(self, key: str) -> int:
        return hash(key) % self.num_partitions
