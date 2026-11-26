public class BidResult {
    private final boolean success;
    private final String message;
    private final Bid highestBid;

    public BidResult(boolean success, String message, Bid highestBid) {
        this.success = success;
        this.message = message;
        this.highestBid = highestBid;
    }

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }

    public Bid getHighestBid() {
        return highestBid;
    }
}
