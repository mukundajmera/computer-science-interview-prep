/**
 * Observer Pattern - Unit Tests
 */

import java.util.*;

public class ObserverTest {

    public static void main(String[] args) {
        ObserverTest test = new ObserverTest();
        test.stockTickerNotifiesAndDetachesObservers();
        test.eventBusRoutesTopicAndWildcardSubscribers();
        System.out.println("All tests passed.");
    }

    private void assertEquals(Object expected, Object actual, double delta) {
        if (expected instanceof Double && actual instanceof Double) {
            if (Math.abs((Double) expected - (Double) actual) > delta) {
                throw new AssertionError("Expected " + expected + " but got " + actual);
            }
        } else if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }

    private void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }

    private void stockTickerNotifiesAndDetachesObservers() {
        StockTicker ticker = new StockTicker();
        PortfolioDisplay portfolio = new PortfolioDisplay(Map.of("ORCL", 4));
        PriceAlert alert = new PriceAlert("ORCL", 120.0);

        ticker.attach(portfolio);
        ticker.attach(alert);
        ticker.updatePrice("ORCL", 125.50);

        assertEquals(125.50, portfolio.getLastPrices().get("ORCL"), 0.01);
        assertEquals(502.0, portfolio.getTotalValue(), 0.01);
        assertEquals(List.of("ORCL crossed 120.00 at 125.50"), alert.getMessages());

        ticker.detach(portfolio);
        ticker.updatePrice("ORCL", 130.0);
        assertEquals(125.50, portfolio.getLastPrices().get("ORCL"), 0.01);
    }

    private void eventBusRoutesTopicAndWildcardSubscribers() {
        EventBus bus = new EventBus();
        List<String> orders = new ArrayList<>();
        List<String> audit = new ArrayList<>();

        bus.subscribe("order.created", event -> orders.add((String) event.getPayload().get("id")));
        bus.subscribe("*", event -> audit.add(event.getTopic()));

        bus.publish("order.created", Map.of("id", "ord-1"));
        bus.publish("payment.failed", Map.of("id", "pay-1"));

        assertEquals(List.of("ord-1"), orders);
        assertEquals(List.of("order.created", "payment.failed"), audit);
    }
}
