"""v3-production: fanout + replay offset coordination."""

from typing import Callable, Dict, List, Tuple
from collections import deque

from connection_registry import ConnectionRegistry


class RealtimeUpdateCoordinator:
    def __init__(self, registry: ConnectionRegistry, push_adapter: Callable[[str, str], None], max_buffer_size: int = 100) -> None:
        self._registry = registry
        self._push_adapter = push_adapter
        self._last_delivered_offset_by_connection: Dict[str, int] = {}
        # Topic -> Deque of (offset, payload)
        self._replay_buffer: Dict[str, deque] = {}
        self._max_buffer_size = max_buffer_size
        self._slow_consumers: set[str] = set()

    def publish(self, topic: str, payload: str, event_offset: int) -> None:
        if topic not in self._replay_buffer:
            self._replay_buffer[topic] = deque(maxlen=self._max_buffer_size)
        self._replay_buffer[topic].append((event_offset, payload))

        for connection_id in self._registry.connections_for_topic(topic):
            if connection_id in self._slow_consumers:
                continue
                
            last_offset = self._last_delivered_offset_by_connection.get(connection_id, 0)
            if event_offset > last_offset:
                try:
                    self._push_adapter(connection_id, payload)
                    self._last_delivered_offset_by_connection[connection_id] = event_offset
                except Exception as e:
                    # In a real system, we'd check the exception type
                    if str(e) == "SlowConsumer":
                        self.disconnect_slow_consumer(connection_id)

    def resume_from(self, connection_id: str, last_client_offset: int, topic: str) -> None:
        if connection_id in self._slow_consumers:
            self._slow_consumers.remove(connection_id)
            
        self._registry.subscribe(topic, connection_id)
        
        if topic in self._replay_buffer:
            for offset, payload in self._replay_buffer[topic]:
                if offset > last_client_offset:
                    try:
                        self._push_adapter(connection_id, payload)
                        self._last_delivered_offset_by_connection[connection_id] = offset
                    except Exception as e:
                        if str(e) == "SlowConsumer":
                            self.disconnect_slow_consumer(connection_id)
                            break
        else:
            self._last_delivered_offset_by_connection[connection_id] = last_client_offset


    def disconnect_slow_consumer(self, connection_id: str) -> None:
        self._slow_consumers.add(connection_id)
        # We could unsubscribe them from registry here, but we keep it simple for now
