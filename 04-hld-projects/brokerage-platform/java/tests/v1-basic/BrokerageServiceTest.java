package brokerage.v1;

import org.junit.jupiter.api.Test;
import java.time.Instant;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class BrokerageServiceTest {

    // Dummy implementation for testing
    static class DummyBrokerageService implements BrokerageService {
        private java.util.Map<String, Order> orders = new java.util.HashMap<>();
        
        @Override
        public Order submitOrder(SubmitOrderCommand command, String idempotencyKey) {
            String orderId = "ord-" + idempotencyKey;
            Order order = new Order(orderId, command.userId, command.symbol, OrderState.PENDING_SUBMIT, Instant.now());
            orders.put(orderId + ":" + command.userId, order);
            return order;
        }

        @Override
        public Order cancelOrder(String orderId, String userId, String idempotencyKey) {
            Order existing = orders.get(orderId + ":" + userId);
            if (existing != null) {
                Order cancelled = new Order(existing.orderId, existing.userId, existing.symbol, OrderState.CANCELLED, Instant.now());
                orders.put(orderId + ":" + userId, cancelled);
                return cancelled;
            }
            return null;
        }

        @Override
        public Optional<Order> getOrder(String orderId, String userId) {
            return Optional.ofNullable(orders.get(orderId + ":" + userId));
        }

        @Override
        public Quote getQuote(String symbol) {
            if ("AAPL".equals(symbol)) {
                return new Quote("AAPL", 150.0, Instant.now());
            }
            return null;
        }
    }

    @Test
    void submitOrderCreatesPendingOrder() {
        BrokerageService service = new DummyBrokerageService();
        SubmitOrderCommand command = new SubmitOrderCommand("u1", "AAPL", OrderSide.BUY, OrderType.MARKET, 10, null);
        Order order = service.submitOrder(command, "key1");
        
        assertNotNull(order);
        assertEquals(OrderState.PENDING_SUBMIT, order.state);
        assertEquals("AAPL", order.symbol);
    }

    @Test
    void cancelOrderUpdatesStateToCancelled() {
        BrokerageService service = new DummyBrokerageService();
        SubmitOrderCommand command = new SubmitOrderCommand("u1", "AAPL", OrderSide.BUY, OrderType.MARKET, 10, null);
        Order order = service.submitOrder(command, "key1");
        
        Order cancelled = service.cancelOrder(order.orderId, "u1", "cancelKey");
        assertNotNull(cancelled);
        assertEquals(OrderState.CANCELLED, cancelled.state);
        
        Optional<Order> fetched = service.getOrder(order.orderId, "u1");
        assertTrue(fetched.isPresent());
        assertEquals(OrderState.CANCELLED, fetched.get().state);
    }

    @Test
    void getQuoteReturnsCorrectPrice() {
        BrokerageService service = new DummyBrokerageService();
        Quote quote = service.getQuote("AAPL");
        
        assertNotNull(quote);
        assertEquals(150.0, quote.price);
    }
}
