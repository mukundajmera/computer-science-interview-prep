import typing

if typing.TYPE_CHECKING:
    from price_service import PriceService
from domain import PriceRecord

class Transport(typing.Protocol):
    def fetch_price(self, product_id: str, merchant_id: str) -> typing.Optional[int]: ...

class Clock(typing.Protocol):
    def now_sec(self) -> int: ...

class PriceCollector:
    def __init__(self, price_service: 'PriceService', product_ids: typing.List[str], merchant_ids: typing.List[str], transport: Transport, clock: Clock):
        self.price_service = price_service
        self.product_ids = product_ids
        self.merchant_ids = merchant_ids
        self.transport = transport
        self.clock = clock

    def poll(self):
        for product_id in self.product_ids:
            for merchant_id in self.merchant_ids:
                price_cents = self.transport.fetch_price(product_id, merchant_id)
                if price_cents is not None:
                    record = PriceRecord(timestamp=self.clock.now_sec(), price_cents=price_cents, in_stock=True)
                    self.price_service.on_price_update(product_id, merchant_id, record)
