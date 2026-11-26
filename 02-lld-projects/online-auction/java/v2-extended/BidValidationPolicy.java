public interface BidValidationPolicy {
    boolean isValidBid(long currentHighestBid, long candidateBid, AuctionState state, Auction auction);
}
