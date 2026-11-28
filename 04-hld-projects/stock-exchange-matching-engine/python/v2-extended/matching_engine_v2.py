"""v2-extended matching engine. Matching behavior is identical to v1; the
step-ups are the ones the project's own docs call for:

1. Sequenced event log + deterministic replay (FOLLOW-UPS.md #2 and the
   standby interviewer probe): every inbound place/cancel is stamped by
   the sequencer and appended to an in-memory event log with its outcome.
   replay() applies the accepted events to a fresh engine in sequence
   order, reproducing the exact book state, which is the end-of-day
   reconciliation and hot-standby story the docs describe.
2. Order validation (the task brief's input-validation weakness, and
   PITFALLS.md #3's O(1) cancel map only works when ids are unique):
   non-positive price/quantity, missing order ids and duplicate order ids
   are rejected before they reach the book, with the rejection reason on
   the result and in the log. Rejected orders never mutate book state.
3. Market-data publisher with slow-consumer protection (FOLLOW-UPS.md #1):
   subscribers get bounded queues; when a slow consumer's queue is full
   the event is dropped for that consumer only and counted, so a stuck
   consumer can never block the engine.

Threading matches v1: per-symbol locks around the books, a lock around
the log and id registry, an internal lock in the publisher.
"""
import threading
from collections import deque
from typing import Dict, List, Optional

from order_book_v2 import MatchResult, Order, OrderBook, Trade


class Sequencer:
    def __init__(self, seed: int = 0):
        self._sequence = seed
        self._lock = threading.Lock()

    def next(self) -> int:
        with self._lock:
            self._sequence += 1
            return self._sequence


class MarketDataPublisherV2:
    """Bounded per-subscriber queues with drop-and-count protection for
    slow consumers (FOLLOW-UPS.md #1)."""

    def __init__(self):
        self._queues: Dict[str, deque] = {}
        self._limits: Dict[str, int] = {}
        self._dropped: Dict[str, int] = {}
        self._lock = threading.Lock()

    def subscribe(self, name: str, max_queue: int = 1000) -> None:
        with self._lock:
            self._queues[name] = deque()
            self._limits[name] = max_queue
            self._dropped[name] = 0

    def publish_trade(self, trade: Trade) -> None:
        with self._lock:
            for name, queue in self._queues.items():
                if len(queue) >= self._limits[name]:
                    # Non-blocking: drop for this consumer only, keep count.
                    self._dropped[name] += 1
                else:
                    queue.append(trade)

    def poll(self, name: str) -> Optional[Trade]:
        with self._lock:
            queue = self._queues.get(name)
            if not queue:
                return None
            return queue.popleft()

    def dropped(self, name: str) -> int:
        with self._lock:
            return self._dropped.get(name, 0)

    def pending(self, name: str) -> int:
        with self._lock:
            queue = self._queues.get(name)
            return len(queue) if queue is not None else 0


class MatchingEngineV2:
    def __init__(self, publisher: Optional[MarketDataPublisherV2] = None,
                 sequencer_seed: int = 0):
        self.order_books: Dict[str, OrderBook] = {}
        self.symbol_locks: Dict[str, threading.RLock] = {}
        self._books_lock = threading.Lock()
        self.sequencer = Sequencer(sequencer_seed)
        self.publisher = publisher
        self.event_log: List[dict] = []
        self._log_lock = threading.Lock()
        self._seen_order_ids = set()

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

    def _log(self, event: dict) -> None:
        with self._log_lock:
            self.event_log.append(event)

    def _validate(self, order_id: str, price: int, quantity: int) -> Optional[str]:
        if order_id is None or not str(order_id).strip():
            return "missing order id"
        if price <= 0:
            return "non-positive price"
        if quantity <= 0:
            return "non-positive quantity"
        with self._log_lock:
            if order_id in self._seen_order_ids:
                return "duplicate order id"
        return None

    def place_order(self, order_id: str, symbol: str, is_buy: bool, price: int, quantity: int) -> MatchResult:
        # The sequencer stamps every inbound message, accepted or not, so
        # the log and any standby see one gapless stream.
        sequence = self.sequencer.next()

        reason = self._validate(order_id, price, quantity)
        if reason is not None:
            result = MatchResult()
            result.status = "rejected"
            result.reject_reason = reason
            self._log({"sequence": sequence, "op": "place", "order_id": order_id,
                       "symbol": symbol, "is_buy": is_buy, "price": price,
                       "quantity": quantity, "accepted": False, "reason": reason})
            return result

        order = Order(order_id, symbol, is_buy, price, quantity, sequence)
        lock = self._get_lock(symbol)
        with lock:
            book = self._get_order_book(symbol)
            result = book.process_order(order)
            with self._log_lock:
                self._seen_order_ids.add(order_id)
            self._log({"sequence": sequence, "op": "place", "order_id": order_id,
                       "symbol": symbol, "is_buy": is_buy, "price": price,
                       "quantity": quantity, "accepted": True,
                       "trades": len(result.trades)})

        if self.publisher is not None:
            for trade in result.trades:
                self.publisher.publish_trade(trade)
        return result

    def cancel_order(self, symbol: str, order_id: str) -> bool:
        sequence = self.sequencer.next()
        lock = self._get_lock(symbol)
        with lock:
            book = self.order_books.get(symbol)
            success = book.cancel_order(order_id) if book is not None else False
        self._log({"sequence": sequence, "op": "cancel", "order_id": order_id,
                   "symbol": symbol, "accepted": success,
                   "reason": None if success else "unknown order"})
        return success

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

    @classmethod
    def replay(cls, event_log: List[dict]) -> 'MatchingEngineV2':
        """Rebuild an engine from a sequenced log (FOLLOW-UPS.md #2).

        Accepted places and successful cancels are applied in sequence
        order; rejected places and failed cancels never touched the book,
        so they are skipped. The new engine's sequencer continues past the
        log's maximum so fresh orders never reuse a sequence number.
        """
        events = sorted(event_log, key=lambda e: e["sequence"])
        seed = max((e["sequence"] for e in events), default=0)
        engine = cls(sequencer_seed=seed)
        for event in events:
            if event["op"] == "place" and event["accepted"]:
                engine.place_order(event["order_id"], event["symbol"], event["is_buy"],
                                   event["price"], event["quantity"])
            elif event["op"] == "cancel" and event["accepted"]:
                engine.cancel_order(event["symbol"], event["order_id"])
        return engine
