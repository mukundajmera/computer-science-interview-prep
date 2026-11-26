"""Simple hash and range partitioning helpers."""

from typing import List, Tuple
import zlib


class DataPartitioner:
    def __init__(self, partition_count: int):
        if partition_count <= 0:
            raise ValueError("partition_count must be > 0")
        self._partition_count = partition_count

    def hash_partition(self, key: str) -> int:
        if key is None:
            raise ValueError("key must not be None")
        return zlib.crc32(key.encode("utf-8")) % self._partition_count

    def range_partition(self, value: int, ranges: List[Tuple[int, int]]) -> int:
        if not ranges:
            raise ValueError("ranges must not be empty")
        previous_end = 0
        has_previous = False
        for start, end in ranges:
            if start > end:
                raise ValueError("range boundaries are invalid")
            if has_previous and start <= previous_end:
                raise ValueError("ranges must be ordered and non-overlapping")
            previous_end = end
            has_previous = True
        for index, (start, end) in enumerate(ranges):
            if start <= value <= end:
                return index
        raise ValueError("value outside configured ranges")


if __name__ == "__main__":
    p = DataPartitioner(4)
    print(p.hash_partition("user-123"))
    print(p.range_partition(450, [(0, 99), (100, 499), (500, 999)]))
