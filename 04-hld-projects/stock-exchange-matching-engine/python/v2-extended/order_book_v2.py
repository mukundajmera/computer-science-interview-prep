"""v2 order book. Matching logic is byte-for-byte v1 behavior (price-time
priority, fixed-point integer prices per PITFALLS.md #4); the only change
is that MatchResult carries a status and reject reason so the engine can
report validation failures without touching the book."""
from collections import OrderedDict
from typing import Dict, List, Optional

class Order:
    __slots__ = ['order_id', 'symbol', 'is_buy', 'price', 'quantity', 'sequence_number', 'prev', 'next']

    def __init__(self, order_id: str, symbol: str, is_buy: bool, price: int, quantity: int, sequence_number: int):
        self.order_id = order_id
        self.symbol = symbol
        self.is_buy = is_buy
        self.price = price
        self.quantity = quantity
        self.sequence_number = sequence_number
        self.prev: Optional['Order'] = None
        self.next: Optional['Order'] = None

class Trade:
    __slots__ = ['maker_order_id', 'taker_order_id', 'price', 'quantity']

    def __init__(self, maker_order_id: str, taker_order_id: str, price: int, quantity: int):
        self.maker_order_id = maker_order_id
        self.taker_order_id = taker_order_id
        self.price = price
        self.quantity = quantity

class MatchResult:
    __slots__ = ['trades', 'residual_order', 'status', 'reject_reason']

    def __init__(self):
        self.trades: List[Trade] = []
        self.residual_order: Optional[Order] = None
        # "filled" | "resting" | "rejected"; set by the engine/book.
        self.status: str = "resting"
        self.reject_reason: Optional[str] = None

class OrderQueue:
    __slots__ = ['head', 'tail', 'total_quantity']

    def __init__(self):
        self.head: Optional[Order] = None
        self.tail: Optional[Order] = None
        self.total_quantity: int = 0

    def add(self, order: Order) -> None:
        if self.tail is None:
            self.head = order
            self.tail = order
        else:
            self.tail.next = order
            order.prev = self.tail
            self.tail = order
        self.total_quantity += order.quantity

    def remove(self, order: Order) -> None:
        if order.prev is not None:
            order.prev.next = order.next
        else:
            self.head = order.next

        if order.next is not None:
            order.next.prev = order.prev
        else:
            self.tail = order.prev

        order.prev = None
        order.next = None
        self.total_quantity -= order.quantity

    def is_empty(self) -> bool:
        return self.head is None

class OrderBook:
    def __init__(self):
        self.bids: Dict[int, OrderQueue] = {}
        self.asks: Dict[int, OrderQueue] = {}
        self.order_map: Dict[str, Order] = {}
        # Keep track of sorted keys to simulate TreeMap
        self._bid_prices: List[int] = [] # descending
        self._ask_prices: List[int] = [] # ascending

    def _insert_bid_price(self, price: int) -> None:
        import bisect
        idx = bisect.bisect_left([-p for p in self._bid_prices], -price)
        if idx == len(self._bid_prices) or self._bid_prices[idx] != price:
            self._bid_prices.insert(idx, price)

    def _remove_bid_price(self, price: int) -> None:
        if price in self._bid_prices:
            self._bid_prices.remove(price)

    def _insert_ask_price(self, price: int) -> None:
        import bisect
        idx = bisect.bisect_left(self._ask_prices, price)
        if idx == len(self._ask_prices) or self._ask_prices[idx] != price:
            self._ask_prices.insert(idx, price)

    def _remove_ask_price(self, price: int) -> None:
        if price in self._ask_prices:
            self._ask_prices.remove(price)

    def process_order(self, order: Order) -> MatchResult:
        result = MatchResult()
        remaining_quantity = order.quantity

        if order.is_buy:
            while remaining_quantity > 0 and self._ask_prices:
                best_ask_price = self._ask_prices[0]
                if order.price < best_ask_price:
                    break

                queue = self.asks[best_ask_price]
                while remaining_quantity > 0 and not queue.is_empty():
                    maker_order = queue.head
                    trade_quantity = min(remaining_quantity, maker_order.quantity)
                    result.trades.append(Trade(maker_order.order_id, order.order_id, maker_order.price, trade_quantity))

                    remaining_quantity -= trade_quantity
                    maker_order.quantity -= trade_quantity
                    queue.total_quantity -= trade_quantity

                    if maker_order.quantity == 0:
                        queue.remove(maker_order)
                        del self.order_map[maker_order.order_id]

                if queue.is_empty():
                    del self.asks[best_ask_price]
                    self._remove_ask_price(best_ask_price)
        else:
            while remaining_quantity > 0 and self._bid_prices:
                best_bid_price = self._bid_prices[0]
                if order.price > best_bid_price:
                    break

                queue = self.bids[best_bid_price]
                while remaining_quantity > 0 and not queue.is_empty():
                    maker_order = queue.head
                    trade_quantity = min(remaining_quantity, maker_order.quantity)
                    result.trades.append(Trade(maker_order.order_id, order.order_id, maker_order.price, trade_quantity))

                    remaining_quantity -= trade_quantity
                    maker_order.quantity -= trade_quantity
                    queue.total_quantity -= trade_quantity

                    if maker_order.quantity == 0:
                        queue.remove(maker_order)
                        del self.order_map[maker_order.order_id]

                if queue.is_empty():
                    del self.bids[best_bid_price]
                    self._remove_bid_price(best_bid_price)

        if remaining_quantity > 0:
            order.quantity = remaining_quantity
            self.order_map[order.order_id] = order
            if order.is_buy:
                if order.price not in self.bids:
                    self.bids[order.price] = OrderQueue()
                    self._insert_bid_price(order.price)
                self.bids[order.price].add(order)
            else:
                if order.price not in self.asks:
                    self.asks[order.price] = OrderQueue()
                    self._insert_ask_price(order.price)
                self.asks[order.price].add(order)
            result.residual_order = order
            result.status = "resting"
        else:
            result.status = "filled"

        return result

    def cancel_order(self, order_id: str) -> bool:
        order = self.order_map.pop(order_id, None)
        if order is None:
            return False

        if order.is_buy:
            queue = self.bids.get(order.price)
            if queue is not None:
                queue.remove(order)
                if queue.is_empty():
                    del self.bids[order.price]
                    self._remove_bid_price(order.price)
        else:
            queue = self.asks.get(order.price)
            if queue is not None:
                queue.remove(order)
                if queue.is_empty():
                    del self.asks[order.price]
                    self._remove_ask_price(order.price)
        return True

    def get_bids_depth(self) -> Dict[int, int]:
        depth = OrderedDict()
        for p in self._bid_prices:
            depth[p] = self.bids[p].total_quantity
        return depth

    def get_asks_depth(self) -> Dict[int, int]:
        depth = OrderedDict()
        for p in self._ask_prices:
            depth[p] = self.asks[p].total_quantity
        return depth
