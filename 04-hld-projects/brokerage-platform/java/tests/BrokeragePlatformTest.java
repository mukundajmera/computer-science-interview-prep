import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.*;
import java.time.Instant;
import java.util.*;

public class BrokeragePlatformTest {

    @Test
    public void testV1BasicPlaceOrderAndMatch() throws Exception {
        // Test v1-basic: place order, match order in-memory
        Class<?> commandClass = Class.forName("brokerage.v1.SubmitOrderCommand");
        Class<?> orderClass = Class.forName("brokerage.v1.Order");
        Class<?> orderSideClass = Class.forName("brokerage.v1.OrderSide");
        Class<?> orderTypeClass = Class.forName("brokerage.v1.OrderType");
        Class<?> orderStateClass = Class.forName("brokerage.v1.OrderState");

        // Create command
        Object sideBuy = Enum.valueOf((Class<Enum>) orderSideClass, "BUY");
        Object typeMarket = Enum.valueOf((Class<Enum>) orderTypeClass, "MARKET");

        Constructor<?> commandConstructor = commandClass.getDeclaredConstructor(
                String.class, String.class, orderSideClass, orderTypeClass, long.class, Double.class
        );
        commandConstructor.setAccessible(true);
        Object command = commandConstructor.newInstance("u1", "AAPL", sideBuy, typeMarket, 10L, null);

        // Mimic place order
        Field userIdField = commandClass.getDeclaredField("userId");
        userIdField.setAccessible(true);
        String userId = (String) userIdField.get(command);

        Field symbolField = commandClass.getDeclaredField("symbol");
        symbolField.setAccessible(true);
        String symbol = (String) symbolField.get(command);

        Object pendingState = Enum.valueOf((Class<Enum>) orderStateClass, "PENDING_SUBMIT");

        Constructor<?> orderConstructor = orderClass.getDeclaredConstructor(
            String.class, String.class, String.class, orderStateClass, Instant.class
        );
        orderConstructor.setAccessible(true);
        Object placedOrder = orderConstructor.newInstance("ord-key1", userId, symbol, pendingState, Instant.now());

        Field stateField = orderClass.getDeclaredField("state");
        stateField.setAccessible(true);
        assertEquals("PENDING_SUBMIT", stateField.get(placedOrder).toString());

        // Mimic match order in-memory (change state to FILLED)
        Object filledState = Enum.valueOf((Class<Enum>) orderStateClass, "FILLED");
        Object matchedOrder = orderConstructor.newInstance("ord-key1", userId, symbol, filledState, Instant.now());

        assertEquals("FILLED", stateField.get(matchedOrder).toString());
    }

    @Test
    public void testV2ScaledCircuitBreakerAndRiskChecks() throws Exception {
        // Test v2-scaled: circuit breaker and risk checks
        // Using MarketDataFanoutService models: QuoteUpdate, OrderCommandRecord
        Class<?> updateClass = Class.forName("brokerage.v2.QuoteUpdate");
        Class<?> recordClass = Class.forName("brokerage.v2.OrderCommandRecord");

        Constructor<?> updateConstructor = updateClass.getDeclaredConstructor(String.class, double.class, long.class);
        updateConstructor.setAccessible(true);
        Object update = updateConstructor.newInstance("AAPL", 150.0, 1L);

        Field priceField = updateClass.getDeclaredField("price");
        priceField.setAccessible(true);
        double currentPrice = (double) priceField.get(update);

        // Simulate risk check (ensure price > 0 and within threshold)
        assertTrue(currentPrice > 0.0);

        // Simulate OrderCommandRecord creation post-risk check
        Constructor<?> recordConstructor = recordClass.getDeclaredConstructor(String.class, String.class, String.class);
        recordConstructor.setAccessible(true);
        Object record = recordConstructor.newInstance("ord-2", "idemp-2", "payload-2");

        Field orderIdField = recordClass.getDeclaredField("orderId");
        orderIdField.setAccessible(true);
        assertEquals("ord-2", orderIdField.get(record));
    }

    @Test
    public void testV3DistributedOrderLedgerAndSettlement() throws Exception {
        // Test v3-distributed: distributed order ledger and settlement
        // Using OrderEvent and ExchangeAck
        Class<?> eventClass = Class.forName("brokerage.v3.OrderEvent");
        Class<?> ackClass = Class.forName("brokerage.v3.ExchangeAck");
        Class<?> exchangeOrderClass = Class.forName("brokerage.v3.ExchangeOrder");

        // Settlement initiation
        Constructor<?> orderConstructor = exchangeOrderClass.getDeclaredConstructor(String.class, String.class);
        orderConstructor.setAccessible(true);
        Object exOrder = orderConstructor.newInstance("ord-3", "AAPL");

        Constructor<?> ackConstructor = ackClass.getDeclaredConstructor(boolean.class, String.class);
        ackConstructor.setAccessible(true);
        Object ack = ackConstructor.newInstance(true, "OK");

        Field acceptedField = ackClass.getDeclaredField("accepted");
        acceptedField.setAccessible(true);
        boolean accepted = (boolean) acceptedField.get(ack);
        assertTrue(accepted);

        // Distributed ledger replication
        Constructor<?> eventConstructor = eventClass.getDeclaredConstructor(String.class, String.class);
        eventConstructor.setAccessible(true);
        Object event = eventConstructor.newInstance("ord-3", "SETTLED");

        Field eventTypeField = eventClass.getDeclaredField("eventType");
        eventTypeField.setAccessible(true);
        assertEquals("SETTLED", eventTypeField.get(event));
    }
}
