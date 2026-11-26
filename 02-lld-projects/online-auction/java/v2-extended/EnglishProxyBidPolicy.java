public class EnglishProxyBidPolicy implements BidValidationPolicy {
    @Override
    public boolean isValidBid(long currentHighestBid, long candidateBid, AuctionState state, Auction auction) {
        if (state != AuctionState.OPEN) {
            return false;
        }
        return candidateBid >= auction.startPrice;
    }
}
