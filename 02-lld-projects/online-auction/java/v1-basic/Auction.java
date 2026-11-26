import java.time.Instant;

public class Auction {
    private final String auctionId;
    private final String itemId;
    private final String sellerId;
    private final double startingPrice;
    private final double reservePrice;
    private final Instant startTime;
    private final Instant endTime;
    private volatile AuctionStatus status;

    public Auction(String auctionId, String itemId, String sellerId, double startingPrice, double reservePrice, Instant startTime, Instant endTime, AuctionStatus status) {
        this.auctionId = auctionId;
        this.itemId = itemId;
        this.sellerId = sellerId;
        this.startingPrice = startingPrice;
        this.reservePrice = reservePrice;
        this.startTime = startTime;
        this.endTime = endTime;
        this.status = status;
    }

    public String getAuctionId() {
        return auctionId;
    }

    public String getItemId() {
        return itemId;
    }

    public String getSellerId() {
        return sellerId;
    }

    public double getStartingPrice() {
        return startingPrice;
    }

    public double getReservePrice() {
        return reservePrice;
    }

    public Instant getStartTime() {
        return startTime;
    }

    public Instant getEndTime() {
        return endTime;
    }

    public AuctionStatus getStatus() {
        return status;
    }

    public void setStatus(AuctionStatus status) {
        this.status = status;
    }
}
