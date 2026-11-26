from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Channel(Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"

@dataclass
class Product:
    id: str
    name: str

@dataclass
class Merchant:
    id: str
    name: str

@dataclass
class PriceRecord:
    timestamp: int
    price_cents: int
    in_stock: bool

@dataclass
class PriceAlertSubscription:
    id: str
    user_id: str
    product_id: str
    threshold_price: Optional[int] = None
    percentage_drop: Optional[float] = None
    channel: Channel = Channel.EMAIL
