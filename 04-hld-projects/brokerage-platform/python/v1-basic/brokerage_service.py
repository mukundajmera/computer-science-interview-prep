from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderState(str, Enum):
    PENDING_SUBMIT = "pending_submit"
    OPEN = "open"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SubmitOrderCommand:
    user_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    limit_price: Optional[float] = None


@dataclass(frozen=True)
class Order:
    order_id: str
    user_id: str
    symbol: str
    state: OrderState
    updated_at: datetime


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    timestamp: datetime


class BrokerageService(Protocol):
    def submit_order(self, command: SubmitOrderCommand, idempotency_key: str) -> Order: ...
    def cancel_order(self, order_id: str, user_id: str, idempotency_key: str) -> Order: ...
    def get_order(self, order_id: str, user_id: str) -> Optional[Order]: ...
    def get_quote(self, symbol: str) -> Quote: ...
