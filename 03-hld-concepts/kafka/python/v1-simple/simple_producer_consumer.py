"""Interview-scale topic model with partitions and offsets."""

from collections import deque
from typing import Deque, Dict, Optional


class SimpleProducerConsumer:
    def __init__(self, partition_count: int) -> None:
        if partition_count <= 0:
            raise ValueError("partition_count must be > 0")
        self._partitions: Dict[int, Deque[str]] = {
            index: deque() for index in range(partition_count)
        }
        self._offsets: Dict[int, int] = {index: 0 for index in range(partition_count)}

    def partition_for_key(self, key: str) -> int:
        return hash(key) % len(self._partitions)

    def produce(self, key: str, message: str) -> int:
        partition = self.partition_for_key(key)
        self._partitions[partition].append(message)
        return partition

    def consume(self, partition: int) -> Optional[str]:
        queue = self._partitions.get(partition)
        if not queue:
            return None
        self._offsets[partition] += 1
        return queue.popleft()

    def current_offset(self, partition: int) -> int:
        return self._offsets.get(partition, 0)


if __name__ == "__main__":
    stream = SimpleProducerConsumer(partition_count=3)
    partition = stream.produce("order-1001", "order-created")
    print("partition ->", partition)
    print("consume ->", stream.consume(partition))
    print("offset ->", stream.current_offset(partition))
