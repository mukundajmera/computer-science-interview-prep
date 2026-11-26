package brokerage.v1;

import java.time.Instant;
import java.util.Optional;

public interface BrokerageService {
    Order submitOrder(SubmitOrderCommand command, String idempotencyKey);
    Order cancelOrder(String orderId, String userId, String idempotencyKey);
    Optional<Order> getOrder(String orderId, String userId);
    Quote getQuote(String symbol);
}

enum OrderSide { BUY, SELL }
enum OrderType { MARKET, LIMIT }
enum OrderState { PENDING_SUBMIT, OPEN, PARTIAL_FILLED, FILLED, CANCELLED, REJECTED }

final class SubmitOrderCommand {
    public final String userId;
    public final String symbol;
    public final OrderSide side;
    public final OrderType type;
    public final long quantity;
    public final Double limitPrice;

    SubmitOrderCommand(String userId, String symbol, OrderSide side, OrderType type,
                       long quantity, Double limitPrice) {
        this.userId = userId;
        this.symbol = symbol;
        this.side = side;
        this.type = type;
        this.quantity = quantity;
        this.limitPrice = limitPrice;
    }
}

final class Order {
    public final String orderId;
    public final String userId;
    public final String symbol;
    public final OrderState state;
    public final Instant updatedAt;

    Order(String orderId, String userId, String symbol, OrderState state, Instant updatedAt) {
        this.orderId = orderId;
        this.userId = userId;
        this.symbol = symbol;
        this.state = state;
        this.updatedAt = updatedAt;
    }
}

final class Quote {
    public final String symbol;
    public final double price;
    public final Instant timestamp;

    Quote(String symbol, double price, Instant timestamp) {
        this.symbol = symbol;
        this.price = price;
        this.timestamp = timestamp;
    }
}
