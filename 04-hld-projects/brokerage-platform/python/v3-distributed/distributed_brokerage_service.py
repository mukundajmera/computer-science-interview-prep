from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExchangeOrder:
    order_id: str
    symbol: str


@dataclass(frozen=True)
class ExchangeAck:
    accepted: bool
    reason: str


@dataclass(frozen=True)
class OrderEvent:
    order_id: str
    event_type: str


class ExchangeAdapter(Protocol):
    def place(self, order: ExchangeOrder) -> ExchangeAck: ...
    def cancel(self, external_order_id: str) -> ExchangeAck: ...


class DistributedBrokerageService(Protocol):
    def route_order_region(self, user_id: str, symbol: str) -> str: ...
    def replicate_order_event(self, event: OrderEvent) -> None: ...
    def reconcile_region(self, region: str) -> None: ...
