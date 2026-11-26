"""
Observer Pattern - V3 Advanced: Topic Event Bus

Demonstrates topic subscriptions, wildcard observers, and resilient dispatch.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass(frozen=True)
class Event:
    """Message delivered to event bus subscribers."""
    topic: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


EventHandler = Callable[[Event], None]


class EventBus:
    """Synchronous event bus with topic-specific and wildcard observers."""

    WILDCARD_TOPIC = "*"

    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self.dead_letters: List[Event] = []

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        handlers = self._subscribers.setdefault(topic, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)
        if not handlers and topic in self._subscribers:
            del self._subscribers[topic]

    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        metadata: Dict[str, Any] = None,
    ) -> Event:
        event = Event(topic=topic, payload=dict(payload), metadata=dict(metadata or {}))
        handlers = self._handlers_for(topic)
        if not handlers:
            self.dead_letters.append(event)
            return event

        for handler in handlers:
            handler(event)
        return event

    def _handlers_for(self, topic: str) -> List[EventHandler]:
        return (
            list(self._subscribers.get(topic, []))
            + list(self._subscribers.get(self.WILDCARD_TOPIC, []))
        )


if __name__ == "__main__":
    bus = EventBus()

    bus.subscribe("order.created", lambda event: print(f"Order: {event.payload['id']}"))
    bus.subscribe("*", lambda event: print(f"Audit topic: {event.topic}"))

    bus.publish("order.created", {"id": "ord-100"})
    bus.publish("payment.failed", {"id": "pay-200"})
    print(f"Dead letters: {len(bus.dead_letters)}")
