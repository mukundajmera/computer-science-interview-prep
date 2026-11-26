"""Interview-scale Cassandra table model using partition + clustering keys."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Row:
    partition_key: str
    clustering_key: int
    columns: Dict[str, Any]


class SimpleCassandraTable:
    _ALLOWED_LEVELS = {"ONE", "QUORUM", "ALL"}

    def __init__(self) -> None:
        self._partitions: Dict[str, Dict[int, Row]] = {}
        self._read_consistency = "QUORUM"
        self._write_consistency = "QUORUM"

    def set_read_consistency(self, level: str) -> None:
        self._validate_level(level)
        self._read_consistency = level

    def set_write_consistency(self, level: str) -> None:
        self._validate_level(level)
        self._write_consistency = level

    def upsert(self, partition_key: str, clustering_key: int, columns: Dict[str, Any]) -> None:
        partition = self._partitions.setdefault(partition_key, {})
        partition[clustering_key] = Row(
            partition_key=partition_key,
            clustering_key=clustering_key,
            columns=dict(columns),
        )

    def get(self, partition_key: str, clustering_key: int) -> Optional[Row]:
        partition = self._partitions.get(partition_key)
        if partition is None:
            return None
        return partition.get(clustering_key)

    def query_partition(self, partition_key: str) -> List[Row]:
        partition = self._partitions.get(partition_key, {})
        return [partition[key] for key in sorted(partition.keys())]

    def query_range(self, partition_key: str, start: int, end: int) -> List[Row]:
        return [
            row
            for row in self.query_partition(partition_key)
            if start <= row.clustering_key <= end
        ]

    def delete(self, partition_key: str, clustering_key: int) -> bool:
        partition = self._partitions.get(partition_key)
        if partition is None:
            return False
        return partition.pop(clustering_key, None) is not None

    def partition_size(self, partition_key: str) -> int:
        return len(self._partitions.get(partition_key, {}))

    @classmethod
    def _validate_level(cls, level: str) -> None:
        if level not in cls._ALLOWED_LEVELS:
            raise ValueError(f"Unsupported consistency level: {level}")
