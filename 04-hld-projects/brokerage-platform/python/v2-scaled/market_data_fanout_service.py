from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class QuoteUpdate:
    symbol: str
    price: float
    sequence: int


@dataclass(frozen=True)
class OrderCommandRecord:
    order_id: str
    idempotency_key: str
    payload: str


class MarketDataFanoutService(Protocol):
    def publish_quote(self, update: QuoteUpdate) -> None: ...
    def subscribe(self, client_id: str, symbols: Sequence[str]) -> None: ...
    def unsubscribe(self, client_id: str, symbols: Sequence[str]) -> None: ...


class OrderCommandStore(Protocol):
    def save_pending(self, record: OrderCommandRecord) -> None: ...
    def mark_final(self, order_id: str, final_state: str) -> None: ...
