"""Responsibility-first helpers for DynamoDB key design examples."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Key:
    partition_key: str
    sort_key: Optional[str] = None


@dataclass(frozen=True)
class Item:
    key: Key
    attributes: Dict[str, str]


class DynamoAccessPatterns:
    """Builds keys/items for common access patterns."""

    def message_key(self, chat_id: str, message_ordinal: int) -> Key:
        return Key(partition_key=f"CHAT#{chat_id}", sort_key=f"MSG#{message_ordinal:020d}")

    def user_preference_key(self, user_id: str) -> Key:
        return Key(partition_key=f"USER#{user_id}")

    def build_item(self, key: Key, attributes: Dict[str, str]) -> Item:
        return Item(key=key, attributes=dict(attributes))
