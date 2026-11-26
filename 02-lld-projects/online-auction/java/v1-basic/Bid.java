public class Bid {
    private final String bidId;
    private final String auctionId;
    private final String bidderId;
    private final double amount;
    private final long timestamp;

    public Bid(String bidId, String auctionId, String bidderId, double amount, long timestamp) {
        this.bidId = bidId;
        this.auctionId = auctionId;
        this.bidderId = bidderId;
        this.amount = amount;
        this.timestamp = timestamp;
    }

    public String getBidId() {
        return bidId;
    }

    public String getAuctionId() {
        return auctionId;
    }

    public String getBidderId() {
        return bidderId;
    }

    public double getAmount() {
        return amount;
    }

    public long getTimestamp() {
        return timestamp;
    }
}
