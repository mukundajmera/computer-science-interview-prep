package brokerage.v3;

public interface DistributedBrokerageService {
    String routeOrderRegion(String userId, String symbol);
    void replicateOrderEvent(OrderEvent event);
    void reconcileRegion(String region);
}

interface ExchangeAdapter {
    ExchangeAck place(ExchangeOrder order);
    ExchangeAck cancel(String externalOrderId);
}

final class ExchangeOrder {
    public final String orderId;
    public final String symbol;

    ExchangeOrder(String orderId, String symbol) {
        this.orderId = orderId;
        this.symbol = symbol;
    }
}

final class ExchangeAck {
    public final boolean accepted;
    public final String reason;

    ExchangeAck(boolean accepted, String reason) {
        this.accepted = accepted;
        this.reason = reason;
    }
}

final class OrderEvent {
    public final String orderId;
    public final String eventType;

    OrderEvent(String orderId, String eventType) {
        this.orderId = orderId;
        this.eventType = eventType;
    }
}
