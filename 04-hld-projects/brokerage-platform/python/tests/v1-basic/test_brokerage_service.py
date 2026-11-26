import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic'))

from brokerage_service import (
    BrokerageService,
    Order,
    OrderSide,
    OrderState,
    OrderType,
    Quote,
    SubmitOrderCommand,
)

class DummyBrokerageService:
    def __init__(self):
        self.orders = {}
        self.quotes = {
            "AAPL": Quote(symbol="AAPL", price=150.0, timestamp=datetime.now())
        }

    def submit_order(self, command: SubmitOrderCommand, idempotency_key: str) -> Order:
        order_id = f"ord-{idempotency_key}"
        order = Order(
            order_id=order_id,
            user_id=command.user_id,
            symbol=command.symbol,
            state=OrderState.PENDING_SUBMIT,
            updated_at=datetime.now(),
        )
        self.orders[(order_id, command.user_id)] = order
        return order

    def cancel_order(self, order_id: str, user_id: str, idempotency_key: str) -> Order:
        order = self.orders.get((order_id, user_id))
        if order:
            cancelled_order = Order(
                order_id=order.order_id,
                user_id=order.user_id,
                symbol=order.symbol,
                state=OrderState.CANCELLED,
                updated_at=datetime.now(),
            )
            self.orders[(order_id, user_id)] = cancelled_order
            return cancelled_order
        raise ValueError("Order not found")

    def get_order(self, order_id: str, user_id: str) -> Order:
        return self.orders.get((order_id, user_id))

    def get_quote(self, symbol: str) -> Quote:
        return self.quotes.get(symbol)


def test_submit_order_creates_pending_order():
    service = DummyBrokerageService()
    command = SubmitOrderCommand(
        user_id="u1",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=10,
    )
    order = service.submit_order(command, "key1")
    assert order.state == OrderState.PENDING_SUBMIT
    assert order.symbol == "AAPL"


def test_cancel_order_updates_state_to_cancelled():
    service = DummyBrokerageService()
    command = SubmitOrderCommand(
        user_id="u1",
        symbol="AAPL",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=10,
    )
    order = service.submit_order(command, "key1")
    cancelled = service.cancel_order(order.order_id, "u1", "cancel_key")
    assert cancelled.state == OrderState.CANCELLED
    
    fetched = service.get_order(order.order_id, "u1")
    assert fetched.state == OrderState.CANCELLED


def test_get_quote_returns_correct_price():
    service = DummyBrokerageService()
    quote = service.get_quote("AAPL")
    assert quote is not None
    assert quote.price == 150.0
