"""Observer pattern tests backed by the example source files."""
import importlib.util
from pathlib import Path
import unittest


PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


stock_ticker = load_module("stock_ticker", "python/v2-variant/stock_ticker.py")
event_bus = load_module("event_bus", "python/v3-advanced/event_bus.py")


class TestObserverPattern(unittest.TestCase):
    def test_stock_ticker_notifies_attached_observers(self):
        """Stock observers receive source-backed price updates."""
        ticker = stock_ticker.StockTicker()
        portfolio = stock_ticker.PortfolioDisplay({"ORCL": 4, "MSFT": 2})
        alert = stock_ticker.PriceAlert("ORCL", threshold=120.0)

        ticker.attach(portfolio)
        ticker.attach(alert)
        ticker.update_price("ORCL", 125.50)

        self.assertEqual(portfolio.last_prices["ORCL"], 125.50)
        self.assertEqual(portfolio.total_value, 502.0)
        self.assertEqual(alert.messages, ["ORCL crossed 120.00 at 125.50"])

    def test_stock_ticker_detaches_observers(self):
        """Detached observers stop receiving updates."""
        ticker = stock_ticker.StockTicker()
        portfolio = stock_ticker.PortfolioDisplay({"ORCL": 1})

        ticker.attach(portfolio)
        ticker.update_price("ORCL", 100.0)
        ticker.detach(portfolio)
        ticker.update_price("ORCL", 110.0)

        self.assertEqual(portfolio.last_prices["ORCL"], 100.0)

    def test_event_bus_routes_topic_and_wildcard_subscribers(self):
        """The event bus supports topic-specific and audit-style observers."""
        bus = event_bus.EventBus()
        orders = []
        audit = []

        bus.subscribe("order.created", lambda event: orders.append(event.payload["id"]))
        bus.subscribe("*", lambda event: audit.append(event.topic))

        bus.publish("order.created", {"id": "ord-1"})
        bus.publish("payment.failed", {"id": "pay-1"})

        self.assertEqual(orders, ["ord-1"])
        self.assertEqual(audit, ["order.created", "payment.failed"])

    def test_event_bus_unsubscribe_prevents_future_notifications(self):
        """Unsubscribed handlers are no longer invoked."""
        bus = event_bus.EventBus()
        received = []

        def handler(event):
            received.append(event.payload)

        bus.subscribe("inventory.low", handler)
        bus.publish("inventory.low", {"sku": "BOOK"})
        bus.unsubscribe("inventory.low", handler)
        bus.publish("inventory.low", {"sku": "LAPTOP"})

        self.assertEqual(received, [{"sku": "BOOK"}])


if __name__ == "__main__":
    unittest.main()
