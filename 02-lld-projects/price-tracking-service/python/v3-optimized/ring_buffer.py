import threading
import typing
from domain import PriceRecord

class OptimizedPriceTracker:
    def __init__(self, window_size: int = 100) -> None:
        self.window_size = window_size
        self._lock = threading.RLock()
        
        # product_id -> merchant_id -> ring_buffer
        self._buffers: typing.Dict[str, typing.Dict[str, 'PriceRingBuffer']] = {}

    def _get_or_create_buffer(self, product_id: str, merchant_id: str) -> 'PriceRingBuffer':
        with self._lock:
            if product_id not in self._buffers:
                self._buffers[product_id] = {}
            if merchant_id not in self._buffers[product_id]:
                self._buffers[product_id][merchant_id] = PriceRingBuffer(self.window_size)
            return self._buffers[product_id][merchant_id]

    def add_tick(self, product_id: str, merchant_id: str, record: PriceRecord) -> bool:
        buffer = self._get_or_create_buffer(product_id, merchant_id)
        return buffer.add(record)
        
    def get_stats(self, product_id: str, merchant_id: str) -> typing.Dict[str, typing.Any]:
        with self._lock:
            if product_id not in self._buffers or merchant_id not in self._buffers[product_id]:
                return {"moving_average": None, "all_time_low": None, "current_price": None}
            buffer = self._buffers[product_id][merchant_id]
            return {
                "moving_average": buffer.get_moving_average(),
                "all_time_low": buffer.get_all_time_low(),
                "current_price": buffer.get_current_price()
            }


class PriceRingBuffer:
    def __init__(self, size: int) -> None:
        self.size = size
        self.buffer: typing.List[typing.Optional[PriceRecord]] = [None] * size
        self.head = 0
        self.count = 0
        
        self.running_sum = 0
        self.all_time_low: typing.Optional[int] = None
        self.last_record: typing.Optional[PriceRecord] = None
        
        self._lock = threading.RLock()

    def add(self, record: PriceRecord) -> bool:
        with self._lock:
            # Deduplication: ignore if same price and same timestamp or if it's identical to last seen
            if self.last_record and self.last_record.timestamp == record.timestamp and self.last_record.price_cents == record.price_cents:
                return False
                
            self.last_record = record

            # Update all-time low
            if self.all_time_low is None or record.price_cents < self.all_time_low:
                self.all_time_low = record.price_cents

            # If buffer is full, subtract the oldest item from running sum
            if self.count == self.size:
                oldest = self.buffer[self.head]
                if oldest:
                    self.running_sum -= oldest.price_cents
            else:
                self.count += 1

            # Add new item
            self.buffer[self.head] = record
            self.running_sum += record.price_cents
            
            # Advance head
            self.head = (self.head + 1) % self.size
            return True

    def get_moving_average(self) -> typing.Optional[float]:
        with self._lock:
            if self.count == 0:
                return None
            return self.running_sum / self.count

    def get_all_time_low(self) -> typing.Optional[int]:
        with self._lock:
            return self.all_time_low
            
    def get_current_price(self) -> typing.Optional[int]:
        with self._lock:
            if not self.last_record:
                return None
            return self.last_record.price_cents

