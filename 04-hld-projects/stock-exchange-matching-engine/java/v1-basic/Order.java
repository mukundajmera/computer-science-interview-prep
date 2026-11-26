package v1_basic;

public class Order {
    public final String orderId;
    public final String symbol;
    public final boolean isBuy;
    public final long price;
    public long quantity;
    public final long sequenceNumber;
    
    public Order prev;
    public Order next;

    public Order(String orderId, String symbol, boolean isBuy, long price, long quantity, long sequenceNumber) {
        this.orderId = orderId;
        this.symbol = symbol;
        this.isBuy = isBuy;
        this.price = price;
        this.quantity = quantity;
        this.sequenceNumber = sequenceNumber;
    }
}