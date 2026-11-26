from typing import Protocol, List
from auction_state import AuctionState, Bid, Auction

class BidValidationPolicy(Protocol):
    def is_valid_bid(self, current_highest_bid: int, candidate_bid: int, state: AuctionState, auction: Auction) -> bool: ...

class EnglishProxyBidPolicy:
    def is_valid_bid(self, current_highest_bid: int, candidate_bid: int, state: AuctionState, auction: Auction) -> bool:
        if state != AuctionState.OPEN:
            return False
        # Proxy bid logic: Users can submit a proxy bid that is lower or equal to current highest
        # IF they are outbidding the *current winning price*, but the current logic just accepts it
        # and lets the system resolve who wins. However, a new proxy bid usually has to beat the *current*
        # winning price by the increment. 
        # But for tie order / proxy, can you submit a bid lower than max proxy? Yes, you can submit any bid
        # as long as it's >= current starting price (or effectively, you just check against start price + increment).
        # Actually, standard proxy bid just requires the bid to be >= start_price (or current effective price).
        # We will allow any bid >= start_price and let settle_auction handle it, or we require candidate_bid >= start_price.
        return candidate_bid >= auction.start_price

class VickreySealedBidPolicy:
    def is_valid_bid(self, current_highest_bid: int, candidate_bid: int, state: AuctionState, auction: Auction) -> bool:
        if state != AuctionState.OPEN:
            return False
        return candidate_bid >= auction.start_price
