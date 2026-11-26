from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import time

class AuctionState(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    SETTLED = "settled"

class BidPolicy(str, Enum):
    ENGLISH_PROXY = "english_proxy"
    VICKREY = "vickrey"

@dataclass
class Bid:
    bidder_id: str
    amount: int
    timestamp: float = field(default_factory=time.time)
    idempotency_key: str = ""

@dataclass
class Auction:
    auction_id: str
    seller_id: str
    start_price: int
    min_increment: int
    end_time: float
    state: AuctionState = AuctionState.DRAFT
    policy: BidPolicy = BidPolicy.ENGLISH_PROXY
    bids: List[Bid] = field(default_factory=list)
    winner_id: Optional[str] = None
    winning_price: Optional[int] = None
    extension_limit: int = 5
    extension_count: int = 0
    extension_window: float = 300.0  # seconds (e.g. 5 mins)
    extension_duration: float = 300.0
