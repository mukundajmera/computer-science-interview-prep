"""v3-advanced: Service Broker Event Mediator Pattern.

Decouples services/components by routing and mediating business domain events
(Order, Inventory, Payment, Notification) through a central broker with
full event auditing and subscription routing.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Set, Optional
import time


class Event:
    def __init__(self, event_type: str, source: str, payload: Optional[Dict[str, Any]] = None) -> None:
        self.type = event_type
        self.source = source
        self.payload = dict(payload) if payload else {}
        self.timestamp = time.time()

    def __repr__(self) -> str:
        return f"Event(type='{self.type}', source='{self.source}', payload={self.payload})"


class ServiceParticipant(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def on_event(self, event: Event, broker: "ServiceBroker") -> None:
        pass


class ServiceBroker:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[ServiceParticipant]] = {}
        self._history: List[Event] = []

    def subscribe(self, event_type: str, participant: ServiceParticipant) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(participant)

    def publish(self, event: Event) -> None:
        self._history.append(event)
        for sub in list(self._subscribers.get(event.type, [])):
            sub.on_event(event, self)

    @property
    def history(self) -> List[Event]:
        return list(self._history)

    def count_events_by_type(self, event_type: str) -> int:
        return sum(1 for e in self._history if e.type == event_type)


class OrderService(ServiceParticipant):
    def __init__(self) -> None:
        self.created_orders: List[str] = []

    @property
    def name(self) -> str:
        return "OrderService"

    def create_order(self, broker: ServiceBroker, order_id: str, amount: float) -> None:
        self.created_orders.append(order_id)
        broker.publish(Event("ORDER_CREATED", self.name, {"order_id": order_id, "amount": amount}))

    def on_event(self, event: Event, broker: ServiceBroker) -> None:
        pass


class InventoryService(ServiceParticipant):
    def __init__(self) -> None:
        self.reserved_orders: Set[str] = set()

    @property
    def name(self) -> str:
        return "InventoryService"

    def on_event(self, event: Event, broker: ServiceBroker) -> None:
        if event.type == "ORDER_CREATED":
            order_id = str(event.payload.get("order_id"))
            self.reserved_orders.add(order_id)
            broker.publish(Event("INVENTORY_RESERVED", self.name, {"order_id": order_id, "status": "RESERVED"}))


class PaymentService(ServiceParticipant):
    def __init__(self) -> None:
        self.processed_payments: Set[str] = set()

    @property
    def name(self) -> str:
        return "PaymentService"

    def on_event(self, event: Event, broker: ServiceBroker) -> None:
        if event.type == "INVENTORY_RESERVED":
            order_id = str(event.payload.get("order_id"))
            self.processed_payments.add(order_id)
            broker.publish(Event("PAYMENT_COMPLETED", self.name, {"order_id": order_id, "status": "CHARGED"}))


class NotificationService(ServiceParticipant):
    def __init__(self) -> None:
        self.notifications: List[str] = []

    @property
    def name(self) -> str:
        return "NotificationService"

    def on_event(self, event: Event, broker: ServiceBroker) -> None:
        if event.type == "PAYMENT_COMPLETED":
            order_id = str(event.payload.get("order_id"))
            self.notifications.append(f"Receipt sent for order: {order_id}")
