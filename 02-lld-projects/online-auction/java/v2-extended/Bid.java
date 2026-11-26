public class Bid {
    public final String bidderId;
    public final long amount;
    public final double timestamp;
    public final String idempotencyKey;

    public Bid(String bidderId, long amount, double timestamp, String idempotencyKey) {
        this.bidderId = bidderId;
        this.amount = amount;
        this.timestamp = timestamp;
        this.idempotencyKey = idempotencyKey;
    }
}
