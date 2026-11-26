import typing
from typing import Dict, List, Optional
from domain import PriceRecord

class PriceHistoryStore:
    def __init__(self) -> None:
        # store history per product and merchant
        # dict structure: product_id -> merchant_id -> list of PriceRecord
        self._history: typing.Dict[str, typing.Dict[str, typing.List[PriceRecord]]] = {}

    def add_price_tick(self, product_id: str, merchant_id: str, record: PriceRecord) -> None:
        if product_id not in self._history:
            self._history[product_id] = {}
        if merchant_id not in self._history[product_id]:
            self._history[product_id][merchant_id] = []
        self._history[product_id][merchant_id].append(record)

    def get_history(self, product_id: str, merchant_id: str) -> typing.List[PriceRecord]:
        return self._history.get(product_id, {}).get(merchant_id, [])

    def get_current_price(self, product_id: str, merchant_id: str) -> Optional[int]:
        history = self.get_history(product_id, merchant_id)
        if not history:
            return None
        # Sort by timestamp to get the latest
        latest = max(history, key=lambda r: r.timestamp)
        return latest.price_cents

    def get_min_price(self, product_id: str, merchant_id: str) -> Optional[int]:
        history = self.get_history(product_id, merchant_id)
        if not history:
            return None
        return min(r.price_cents for r in history)

    def get_max_price(self, product_id: str, merchant_id: str) -> Optional[int]:
        history = self.get_history(product_id, merchant_id)
        if not history:
            return None
        return max(r.price_cents for r in history)

    def get_percentage_change(self, product_id: str, merchant_id: str, start_time: int, end_time: int) -> Optional[float]:
        history = self.get_history(product_id, merchant_id)
        if not history:
            return None
        
        # Get records strictly before or equal to start_time
        start_records = [r for r in history if r.timestamp <= start_time]
        if not start_records:
            return None
        start_price = max(start_records, key=lambda r: r.timestamp).price_cents
        
        # Get records strictly before or equal to end_time
        end_records = [r for r in history if r.timestamp <= end_time]
        if not end_records:
            return None
        end_price = max(end_records, key=lambda r: r.timestamp).price_cents
        
        if start_price == 0:
            return 0.0 # handle div by zero gracefully
            
        return ((end_price - start_price) / start_price) * 100.0

