public interface BidService {
    boolean placeBid(String auctionId, String bidderId, long amount, String idempotencyKey, double currentTime);
}
