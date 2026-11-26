import threading
from typing import Dict
from order_book import OrderBook, MatchResult, Order

class Sequencer:
    def __init__(self):
        self._sequence = 0
        self._lock = threading.Lock()

    def next(self) -> int:
        with self._lock:
            self._sequence += 1
            return self._sequence

class MatchingEngine:
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.symbol_locks: Dict[str, threading.RLock] = {}
        self._books_lock = threading.Lock()
        self.sequencer = Sequencer()

    def _get_lock(self, symbol: str) -> threading.RLock:
        with self._books_lock:
            if symbol not in self.symbol_locks:
                self.symbol_locks[symbol] = threading.RLock()
            return self.symbol_locks[symbol]

    def _get_order_book(self, symbol: str) -> OrderBook:
        with self._books_lock:
            if symbol not in self.order_books:
                self.order_books[symbol] = OrderBook()
            return self.order_books[symbol]

    def place_order(self, order_id: str, symbol: str, is_buy: bool, price: int, quantity: int) -> MatchResult:
        order = Order(order_id, symbol, is_buy, price, quantity, self.sequencer.next())
        lock = self._get_lock(symbol)
        with lock:
            book = self._get_order_book(symbol)
            return book.process_order(order)

    def cancel_order(self, symbol: str, order_id: str) -> bool:
        lock = self._get_lock(symbol)
        with lock:
            book = self.order_books.get(symbol)
            if book is not None:
                return book.cancel_order(order_id)
            return False

    def get_bids_depth(self, symbol: str) -> Dict[int, int]:
        lock = self._get_lock(symbol)
        with lock:
            book = self.order_books.get(symbol)
            if book is not None:
                return book.get_bids_depth()
            return {}

    def get_asks_depth(self, symbol: str) -> Dict[int, int]:
        lock = self._get_lock(symbol)
        with lock:
            book = self.order_books.get(symbol)
            if book is not None:
                return book.get_asks_depth()
            return {}
