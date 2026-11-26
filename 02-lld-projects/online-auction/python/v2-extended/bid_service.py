from typing import Protocol
from auction_state import AuctionState, Bid, BidPolicy
import time

class BidService(Protocol):
    def place_bid(self, auction_id: str, bidder_id: str, amount: int, idempotency_key: str, current_time: float) -> bool: ...
