import os
import sys
from datetime import datetime

# Setup sys.path for dynamic imports
base_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(base_dir, '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(base_dir, '..', 'v2-scaled')))
sys.path.insert(0, os.path.abspath(os.path.join(base_dir, '..', 'v3-distributed')))

from brokerage_service import (
    BrokerageService,
    Order,
    OrderSide,
    OrderState,
    OrderType,
    Quote,
    SubmitOrderCommand,
)

from market_data_fanout_service import (
    QuoteUpdate,
    MarketDataFanoutService,
)

from distributed_brokerage_service import (
    DistributedBrokerageService,
    OrderEvent,
)

class DummyBrokerageService:
    def __init__(self):
        self.orders = {}

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
        pass

    def get_order(self, order_id: str, user_id: str) -> Order:
        return self.orders.get((order_id, user_id))

    def get_quote(self, symbol: str) -> Quote:
        pass


class DummyMarketDataFanoutService:
    def __init__(self):
        self.published_quotes = []

    def publish_quote(self, update: QuoteUpdate) -> None:
        self.published_quotes.append(update)

    def subscribe(self, client_id: str, symbols: list) -> None:
        pass

    def unsubscribe(self, client_id: str, symbols: list) -> None:
        pass


class DummyDistributedBrokerageService:
    def __init__(self):
        self.replicated_events = []

    def route_order_region(self, user_id: str, symbol: str) -> str:
        if user_id.startswith("eu"):
            return "eu-west-1"
        return "us-east-1"

    def replicate_order_event(self, event: OrderEvent) -> None:
        self.replicated_events.append(event)

    def reconcile_region(self, region: str) -> None:
        pass


def test_v1_submit_order_creates_pending_order():
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


def test_v2_publish_quote():
    service = DummyMarketDataFanoutService()
    update = QuoteUpdate(symbol="AAPL", price=155.0, sequence=1)
    service.publish_quote(update)
    assert len(service.published_quotes) == 1
    assert service.published_quotes[0].price == 155.0


def test_v3_route_order_region():
    service = DummyDistributedBrokerageService()
    assert service.route_order_region("eu_user", "AAPL") == "eu-west-1"
    assert service.route_order_region("us_user", "AAPL") == "us-east-1"
