"""
Observer Pattern - V2 Variant: Stock Market Ticker

Demonstrates a subject that broadcasts market data to independent displays.
"""
from dataclasses import dataclass
from typing import Dict, List, Protocol


@dataclass(frozen=True)
class StockQuote:
    """Immutable stock price update sent to observers."""
    symbol: str
    price: float
    previous_price: float

    @property
    def change(self) -> float:
        return self.price - self.previous_price


class StockObserver(Protocol):
    """Observer interface for stock quote updates."""

    def update(self, quote: StockQuote) -> None:
        """Receive a stock quote update."""


class StockTicker:
    """Subject that publishes price changes to subscribed observers."""

    def __init__(self):
        self._observers: List[StockObserver] = []
        self._prices: Dict[str, float] = {}

    def attach(self, observer: StockObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: StockObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def update_price(self, symbol: str, price: float) -> StockQuote:
        previous = self._prices.get(symbol, price)
        self._prices[symbol] = price
        quote = StockQuote(symbol=symbol, price=price, previous_price=previous)
        self._notify(quote)
        return quote

    def _notify(self, quote: StockQuote) -> None:
        for observer in list(self._observers):
            observer.update(quote)


class PortfolioDisplay:
    """Observer that tracks the latest prices for owned positions."""

    def __init__(self, shares: Dict[str, int]):
        self._shares = dict(shares)
        self.last_prices: Dict[str, float] = {}

    @property
    def total_value(self) -> float:
        return sum(
            quantity * self.last_prices.get(symbol, 0.0)
            for symbol, quantity in self._shares.items()
        )

    def update(self, quote: StockQuote) -> None:
        if quote.symbol in self._shares:
            self.last_prices[quote.symbol] = quote.price


class PriceAlert:
    """Observer that records messages when a symbol crosses a threshold."""

    def __init__(self, symbol: str, threshold: float):
        self._symbol = symbol
        self._threshold = threshold
        self.messages: List[str] = []

    def update(self, quote: StockQuote) -> None:
        if quote.symbol == self._symbol and quote.price >= self._threshold:
            self.messages.append(
                f"{quote.symbol} crossed {self._threshold:.2f} at {quote.price:.2f}"
            )


class MovingAverageDisplay:
    """Observer that keeps a rolling average per symbol."""

    def __init__(self, window_size: int):
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self._window_size = window_size
        self._prices_by_symbol: Dict[str, List[float]] = {}

    def update(self, quote: StockQuote) -> None:
        prices = self._prices_by_symbol.setdefault(quote.symbol, [])
        prices.append(quote.price)
        del prices[:-self._window_size]

    def average_for(self, symbol: str) -> float:
        prices = self._prices_by_symbol.get(symbol, [])
        if not prices:
            return 0.0
        return sum(prices) / len(prices)


if __name__ == "__main__":
    ticker = StockTicker()
    portfolio = PortfolioDisplay({"ORCL": 4, "MSFT": 2})
    alert = PriceAlert("ORCL", 120.0)
    moving_average = MovingAverageDisplay(window_size=3)

    ticker.attach(portfolio)
    ticker.attach(alert)
    ticker.attach(moving_average)

    for symbol, price in [("ORCL", 118.0), ("MSFT", 410.0), ("ORCL", 125.5)]:
        quote = ticker.update_price(symbol, price)
        print(f"{quote.symbol}: {quote.price:.2f} ({quote.change:+.2f})")

    print(f"Portfolio value: {portfolio.total_value:.2f}")
    print(f"ORCL moving average: {moving_average.average_for('ORCL'):.2f}")
    print(f"Alerts: {alert.messages}")
