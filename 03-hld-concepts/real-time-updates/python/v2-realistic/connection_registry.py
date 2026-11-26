"""v2-realistic: topic subscription registry for active connections."""

from collections import defaultdict
from typing import DefaultDict, List, Set


class ConnectionRegistry:
    def __init__(self) -> None:
        self._topic_to_connections: DefaultDict[str, Set[str]] = defaultdict(set)

    def subscribe(self, topic: str, connection_id: str) -> None:
        self._topic_to_connections[topic].add(connection_id)

    def unsubscribe(self, topic: str, connection_id: str) -> None:
        if topic in self._topic_to_connections:
            self._topic_to_connections[topic].discard(connection_id)

    def connections_for_topic(self, topic: str) -> List[str]:
        return sorted(self._topic_to_connections.get(topic, set()))
