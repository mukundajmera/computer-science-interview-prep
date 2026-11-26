package brokerage.v2;

import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.HashSet;

import static org.junit.jupiter.api.Assertions.*;

class MarketDataFanoutServiceTest {

    // Dummy implementation for testing
    static class DummyMarketDataFanoutService implements MarketDataFanoutService {
        Map<String, Set<String>> subscriptions = new HashMap<>();
        List<QuoteUpdate> publishedQuotes = new ArrayList<>();

        @Override
        public void publishQuote(QuoteUpdate update) {
            publishedQuotes.add(update);
        }

        @Override
        public void subscribe(String clientId, List<String> symbols) {
            subscriptions.putIfAbsent(clientId, new HashSet<>());
            subscriptions.get(clientId).addAll(symbols);
        }

        @Override
        public void unsubscribe(String clientId, List<String> symbols) {
            if (subscriptions.containsKey(clientId)) {
                subscriptions.get(clientId).removeAll(symbols);
            }
        }
    }

    @Test
    void subscribeAddsSymbolsToClient() {
        DummyMarketDataFanoutService service = new DummyMarketDataFanoutService();
        service.subscribe("client1", List.of("AAPL", "GOOGL"));
        
        assertTrue(service.subscriptions.containsKey("client1"));
        assertTrue(service.subscriptions.get("client1").contains("AAPL"));
        assertTrue(service.subscriptions.get("client1").contains("GOOGL"));
    }

    @Test
    void unsubscribeRemovesSymbolsFromClient() {
        DummyMarketDataFanoutService service = new DummyMarketDataFanoutService();
        service.subscribe("client1", List.of("AAPL", "GOOGL"));
        service.unsubscribe("client1", List.of("AAPL"));
        
        assertFalse(service.subscriptions.get("client1").contains("AAPL"));
        assertTrue(service.subscriptions.get("client1").contains("GOOGL"));
    }

    @Test
    void publishQuoteRecordsUpdate() {
        DummyMarketDataFanoutService service = new DummyMarketDataFanoutService();
        QuoteUpdate update = new QuoteUpdate("AAPL", 155.0, 1L);
        service.publishQuote(update);
        
        assertEquals(1, service.publishedQuotes.size());
        assertEquals("AAPL", service.publishedQuotes.get(0).symbol);
        assertEquals(155.0, service.publishedQuotes.get(0).price);
    }
}
