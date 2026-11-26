package brokerage.v2;

import java.util.List;

public interface MarketDataFanoutService {
    void publishQuote(QuoteUpdate update);
    void subscribe(String clientId, List<String> symbols);
    void unsubscribe(String clientId, List<String> symbols);
}

interface OrderCommandStore {
    void savePending(OrderCommandRecord record);
    void markFinal(String orderId, String finalState);
}

final class QuoteUpdate {
    public final String symbol;
    public final double price;
    public final long sequence;

    QuoteUpdate(String symbol, double price, long sequence) {
        this.symbol = symbol;
        this.price = price;
        this.sequence = sequence;
    }
}

final class OrderCommandRecord {
    public final String orderId;
    public final String idempotencyKey;
    public final String payload;

    OrderCommandRecord(String orderId, String idempotencyKey, String payload) {
        this.orderId = orderId;
        this.idempotencyKey = idempotencyKey;
        this.payload = payload;
    }
}
