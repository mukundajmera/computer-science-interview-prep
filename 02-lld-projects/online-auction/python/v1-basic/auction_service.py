import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading


class AuctionState(Enum):
    PENDING = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELLED = 4


@dataclass
class Bid:
    bidder_id: str
    amount: float
    timestamp: float = field(default_factory=time.time)


class Auction:
    def __init__(self, auction_id: str, item_id: str, seller_id: str, 
                 reserve_price: float, duration_sec: float, min_increment: float):
        self.auction_id = auction_id
        self.item_id = item_id
        self.seller_id = seller_id
        self.reserve_price = reserve_price
        self.min_increment = min_increment
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_sec = duration_sec
        self.state = AuctionState.PENDING
        
        self.bids: List[Bid] = []
        self.highest_bid: Optional[Bid] = None
        self.lock = threading.RLock()

    def start(self, current_time: float):
        with self.lock:
            if self.state == AuctionState.PENDING:
                self.state = AuctionState.ACTIVE
                self.start_time = current_time
                self.end_time = current_time + self.duration_sec

    def is_active(self, current_time: float) -> bool:
        with self.lock:
            if self.state != AuctionState.ACTIVE:
                return False
            if self.end_time and current_time >= self.end_time:
                self.complete()
                return False
            return True

    def place_bid(self, bidder_id: str, amount: float, current_time: float) -> bool:
        with self.lock:
            if not self.is_active(current_time):
                return False

            if bidder_id == self.seller_id:
                return False

            # Atomic bid increment validation
            current_highest = self.highest_bid.amount if self.highest_bid else 0
            if amount >= current_highest + self.min_increment:
                new_bid = Bid(bidder_id, amount, current_time)
                self.bids.append(new_bid)
                self.highest_bid = new_bid
                return True
            return False

    def complete(self):
        with self.lock:
            if self.state == AuctionState.ACTIVE:
                self.state = AuctionState.COMPLETED

    def get_winner(self) -> Optional[Bid]:
        with self.lock:
            if self.state != AuctionState.COMPLETED:
                return None
            # Reserve price evaluation
            if self.highest_bid and self.highest_bid.amount >= self.reserve_price:
                return self.highest_bid
            return None


class AuctionService:
    def __init__(self):
        self.auctions: Dict[str, Auction] = {}
        self.lock = threading.Lock()
        self._auction_counter = 0

    def create_auction(self, item_id: str, seller_id: str, 
                       reserve_price: float, duration_sec: float, min_increment: float) -> str:
        with self.lock:
            self._auction_counter += 1
            auction_id = f"auction_{self._auction_counter}"
            auction = Auction(auction_id, item_id, seller_id, reserve_price, duration_sec, min_increment)
            self.auctions[auction_id] = auction
            return auction_id

    def start_auction(self, auction_id: str):
        auction = self.auctions.get(auction_id)
        if auction:
            auction.start(time.time())

    def place_bid(self, auction_id: str, bidder_id: str, amount: float) -> bool:
        auction = self.auctions.get(auction_id)
        if auction:
            return auction.place_bid(bidder_id, amount, time.time())
        return False

    def get_auction(self, auction_id: str) -> Optional[Auction]:
        return self.auctions.get(auction_id)

    def evaluate_auction(self, auction_id: str, current_time: Optional[float] = None) -> Optional[Bid]:
        auction = self.auctions.get(auction_id)
        if auction:
            curr = current_time or time.time()
            if auction.is_active(curr):
                # Still active, check if time passed
                if auction.end_time and curr >= auction.end_time:
                    auction.complete()
            elif auction.state == AuctionState.ACTIVE:
                # Active but is_active returned False means it just completed
                pass
            return auction.get_winner()
        return None

