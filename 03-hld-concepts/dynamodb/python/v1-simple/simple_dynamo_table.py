"""Interview-scale DynamoDB table model with PK/SK and a lightweight GSI."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Item:
    partition_key: str
    sort_key: str
    attributes: Dict[str, Any]


@dataclass(frozen=True)
class GsiDefinition:
    name: str
    partition_attr: str
    sort_attr: Optional[str] = None


class SimpleDynamoTable:
    def __init__(self) -> None:
        self._table: Dict[str, Dict[str, Item]] = {}
        self._indexes: Dict[str, GsiDefinition] = {}

    def define_gsi(self, name: str, partition_attr: str, sort_attr: Optional[str] = None) -> None:
        self._indexes[name] = GsiDefinition(name=name, partition_attr=partition_attr, sort_attr=sort_attr)

    def put_item(self, partition_key: str, sort_key: str, attributes: Dict[str, Any]) -> None:
        partition = self._table.setdefault(partition_key, {})
        partition[sort_key] = Item(partition_key=partition_key, sort_key=sort_key, attributes=dict(attributes))

    def get_item(self, partition_key: str, sort_key: str) -> Optional[Item]:
        partition = self._table.get(partition_key)
        if partition is None:
            return None
        return partition.get(sort_key)

    def delete_item(self, partition_key: str, sort_key: str) -> bool:
        partition = self._table.get(partition_key)
        if partition is None:
            return False
        return partition.pop(sort_key, None) is not None

    def query(self, partition_key: str) -> List[Item]:
        partition = self._table.get(partition_key, {})
        return [partition[key] for key in sorted(partition.keys())]

    def query_range(self, partition_key: str, start_sort_key: str, end_sort_key: str) -> List[Item]:
        return [
            item
            for item in self.query(partition_key)
            if start_sort_key <= item.sort_key <= end_sort_key
        ]

    def query_gsi(self, index_name: str, gsi_partition_value: str) -> List[Item]:
        definition = self._indexes.get(index_name)
        if definition is None:
            return []

        results: List[Item] = []
        for partition in self._table.values():
            for item in partition.values():
                if item.attributes.get(definition.partition_attr) == gsi_partition_value:
                    results.append(item)

        if definition.sort_attr is not None:
            results.sort(key=lambda item: str(item.attributes.get(definition.sort_attr, "")))
        return results

    def scan(self, limit: int, offset: int = 0) -> List[Item]:
        all_items: List[Item] = []
        for partition in self._table.values():
            all_items.extend(partition.values())
        all_items.sort(key=lambda item: item.sort_key)

        start = min(offset, len(all_items))
        end = min(start + limit, len(all_items))
        return all_items[start:end]
