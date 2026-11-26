from typing import Optional, Protocol, Dict
import time
import threading
from auction_state import Auction, AuctionState, Bid, BidPolicy
from policies import EnglishProxyBidPolicy, VickreySealedBidPolicy

class Repository(Protocol):
    def save(self, key: str, value: str) -> None: ...
    def find(self, key: str) -> Optional[str]: ...

class AuctionServiceV2:
    def __init__(self, repository: Repository = None) -> None:
        self.repository = repository
        self.auctions: Dict[str, Auction] = {}
        self.lock = threading.RLock()
        self._policies = {
            BidPolicy.ENGLISH_PROXY: EnglishProxyBidPolicy(),
            BidPolicy.VICKREY: VickreySealedBidPolicy(),
        }

    def upsert(self, key: str, value: str) -> None:
        if self.repository:
            self.repository.save(key, value)

    def get(self, key: str) -> Optional[str]:
        if self.repository:
            return self.repository.find(key)
        return None

    def create_auction(self, auction_id: str, seller_id: str, start_price: int, min_increment: int, end_time: float, policy: BidPolicy = BidPolicy.ENGLISH_PROXY) -> str:
        with self.lock:
            self.auctions[auction_id] = Auction(
                auction_id=auction_id,
                seller_id=seller_id,
                start_price=start_price,
                min_increment=min_increment,
                end_time=end_time,
                policy=policy
            )
            return auction_id

    def open_auction(self, auction_id: str):
        with self.lock:
            auction = self.auctions.get(auction_id)
            if auction and auction.state == AuctionState.DRAFT:
                auction.state = AuctionState.OPEN

    def place_bid(self, auction_id: str, bidder_id: str, amount: int, idempotency_key: str, current_time: float) -> bool:
        if type(amount) is not int or amount <= 0:
            return False

        with self.lock:
            auction = self.auctions.get(auction_id)
            if auction is None or auction.state != AuctionState.OPEN:
                return False
            
            if current_time > auction.end_time or bidder_id == auction.seller_id:
                return False
                
            for bid in auction.bids:
                if idempotency_key and bid.idempotency_key == idempotency_key:
                    return True
                    
            policy_impl = self._policies.get(auction.policy)
            if policy_impl is None:
                return False
                
            highest_bid = auction.start_price - auction.min_increment
            if auction.policy == BidPolicy.ENGLISH_PROXY and auction.bids:
                highest_bid = max(b.amount for b in auction.bids)

            if not policy_impl.is_valid_bid(highest_bid, amount, auction.state, auction):
                return False

            auction.bids.append(Bid(bidder_id=bidder_id, amount=amount, timestamp=current_time, idempotency_key=idempotency_key))
            
            time_left = auction.end_time - current_time
            if time_left <= auction.extension_window and auction.extension_count < auction.extension_limit:
                auction.end_time += auction.extension_duration
                auction.extension_count += 1
            
            return True

    def settle_auction(self, auction_id: str, current_time: float) -> bool:
        with self.lock:
            auction = self.auctions.get(auction_id)
            if auction is None or current_time <= auction.end_time:
                return False

            if auction.state == AuctionState.SETTLED:
                return True

            auction.state = AuctionState.CLOSED
            
            if not auction.bids:
                auction.state = AuctionState.SETTLED
                return True
                
            sorted_bids = sorted(auction.bids, key=lambda b: (-b.amount, b.timestamp))
            winner_bid = sorted_bids[0]
            auction.winner_id = winner_bid.bidder_id
            
            if auction.policy == BidPolicy.ENGLISH_PROXY:
                other_bids = [b.amount for b in auction.bids if b.bidder_id != winner_bid.bidder_id]
                second_highest = max(other_bids) if other_bids else -1
                if second_highest != -1:
                    auction.winning_price = min(winner_bid.amount, second_highest + auction.min_increment)
                else:
                    auction.winning_price = auction.start_price
            
            elif auction.policy == BidPolicy.VICKREY:
                other_bids = [b.amount for b in sorted_bids if b.bidder_id != winner_bid.bidder_id]
                auction.winning_price = other_bids[0] if other_bids else auction.start_price
                    
            auction.state = AuctionState.SETTLED
            return True
