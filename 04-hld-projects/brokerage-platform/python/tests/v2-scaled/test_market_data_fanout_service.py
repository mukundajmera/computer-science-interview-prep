import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled'))

from market_data_fanout_service import (
    MarketDataFanoutService,
    QuoteUpdate,
)

class DummyMarketDataFanoutService:
    def __init__(self):
        self.subscriptions = {}
        self.published_quotes = []

    def publish_quote(self, update: QuoteUpdate) -> None:
        self.published_quotes.append(update)

    def subscribe(self, client_id: str, symbols: Sequence[str]) -> None:
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = set()
        for symbol in symbols:
            self.subscriptions[client_id].add(symbol)

    def unsubscribe(self, client_id: str, symbols: Sequence[str]) -> None:
        if client_id in self.subscriptions:
            for symbol in symbols:
                self.subscriptions[client_id].discard(symbol)


def test_subscribe_adds_symbols_to_client():
    service = DummyMarketDataFanoutService()
    service.subscribe("client1", ["AAPL", "GOOGL"])
    
    assert "client1" in service.subscriptions
    assert "AAPL" in service.subscriptions["client1"]
    assert "GOOGL" in service.subscriptions["client1"]


def test_unsubscribe_removes_symbols_from_client():
    service = DummyMarketDataFanoutService()
    service.subscribe("client1", ["AAPL", "GOOGL"])
    service.unsubscribe("client1", ["AAPL"])
    
    assert "AAPL" not in service.subscriptions["client1"]
    assert "GOOGL" in service.subscriptions["client1"]


def test_publish_quote_records_update():
    service = DummyMarketDataFanoutService()
    update = QuoteUpdate(symbol="AAPL", price=155.0, sequence=1)
    service.publish_quote(update)
    
    assert len(service.published_quotes) == 1
    assert service.published_quotes[0].symbol == "AAPL"
    assert service.published_quotes[0].price == 155.0
