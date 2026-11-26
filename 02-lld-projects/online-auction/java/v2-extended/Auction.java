import java.util.ArrayList;
import java.util.List;

public class Auction {
    public final String auctionId;
    public final String sellerId;
    public final long startPrice;
    public final long minIncrement;
    public double endTime;
    public AuctionState state;
    public final BidPolicy policy;
    
    public final List<Bid> bids = new ArrayList<>();
    public String winnerId = null;
    public Long winningPrice = null;
    
    public final int extensionLimit;
    public int extensionCount = 0;
    public final double extensionWindow;
    public final double extensionDuration;

    public Auction(String auctionId, String sellerId, long startPrice, long minIncrement, double endTime, BidPolicy policy, int extensionLimit, double extensionWindow, double extensionDuration) {
        this.auctionId = auctionId;
        this.sellerId = sellerId;
        this.startPrice = startPrice;
        this.minIncrement = minIncrement;
        this.endTime = endTime;
        this.policy = policy;
        this.state = AuctionState.DRAFT;
        this.extensionLimit = extensionLimit;
        this.extensionWindow = extensionWindow;
        this.extensionDuration = extensionDuration;
    }
}
