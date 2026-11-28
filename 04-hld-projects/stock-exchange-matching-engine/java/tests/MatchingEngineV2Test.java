package tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v2_extended.EventLog;
import v2_extended.MarketDataPublisher;
import v2_extended.MatchingEngine;
import v2_extended.OrderBook;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class MatchingEngineV2Test {
    private MatchingEngine engine;

    @BeforeEach
    public void setUp() {
        engine = new MatchingEngine();
    }

    // ---------- v1 parity: every v1 behavior still holds on the v2 track ----------

    @Test
    public void testFullMatchBuyAndSellAtSamePrice() {
        OrderBook.MatchResult result1 = engine.placeOrder("1", "AAPL", false, 150, 100);
        assertTrue(result1.trades.isEmpty());
        assertNotNull(result1.residualOrder);
        assertEquals(100, result1.residualOrder.quantity);
        assertEquals("resting", result1.status);

        OrderBook.MatchResult result2 = engine.placeOrder("2", "AAPL", true, 150, 100);
        assertEquals(1, result2.trades.size());
        assertEquals("1", result2.trades.get(0).makerOrderId);
        assertEquals("2", result2.trades.get(0).takerOrderId);
        assertEquals(150, result2.trades.get(0).price);
        assertEquals(100, result2.trades.get(0).quantity);
        assertNull(result2.residualOrder);
        assertEquals("filled", result2.status);

        assertTrue(engine.getAsksDepth("AAPL").isEmpty());
        assertTrue(engine.getBidsDepth("AAPL").isEmpty());
    }

    @Test
    public void testPartialFillAndResidualQueued() {
        engine.placeOrder("1", "MSFT", false, 300, 50);
        OrderBook.MatchResult result = engine.placeOrder("2", "MSFT", true, 300, 75);

        assertEquals(1, result.trades.size());
        assertEquals(50, result.trades.get(0).quantity);
        assertNotNull(result.residualOrder);
        assertEquals(25, result.residualOrder.quantity);

        Map<Long, Long> bids = engine.getBidsDepth("MSFT");
        assertEquals(1, bids.size());
        assertEquals(25, bids.get(300L));
    }

    @Test
    public void testPriceTimePriorityFifoExecution() {
        engine.placeOrder("1", "GOOG", false, 2800, 10);
        engine.placeOrder("2", "GOOG", false, 2790, 15);
        engine.placeOrder("3", "GOOG", false, 2800, 20);

        OrderBook.MatchResult result = engine.placeOrder("4", "GOOG", true, 2800, 30);

        assertEquals(3, result.trades.size());
        assertEquals("2", result.trades.get(0).makerOrderId);
        assertEquals(15, result.trades.get(0).quantity);
        assertEquals(2790, result.trades.get(0).price);
        assertEquals("1", result.trades.get(1).makerOrderId);
        assertEquals(10, result.trades.get(1).quantity);
        assertEquals(2800, result.trades.get(1).price);
        assertEquals("3", result.trades.get(2).makerOrderId);
        assertEquals(5, result.trades.get(2).quantity);
        assertEquals(2800, result.trades.get(2).price);
        assertNull(result.residualOrder);
    }

    @Test
    public void testCancelOrderRemovesFromBook() {
        engine.placeOrder("1", "TSLA", true, 800, 50);
        engine.placeOrder("2", "TSLA", true, 800, 30);

        Map<Long, Long> depthBefore = engine.getBidsDepth("TSLA");
        assertEquals(80, depthBefore.get(800L));

        assertTrue(engine.cancelOrder("TSLA", "1"));

        Map<Long, Long> depthAfter = engine.getBidsDepth("TSLA");
        assertEquals(30, depthAfter.get(800L));

        assertFalse(engine.cancelOrder("TSLA", "1"));
    }

    @Test
    public void testDeterministicSequencerReplay() {
        OrderBook.MatchResult r1 = engine.placeOrder("1", "AMZN", true, 3300, 10);
        OrderBook.MatchResult r2 = engine.placeOrder("2", "AMZN", true, 3300, 10);

        assertEquals(1, r1.residualOrder.sequenceNumber);
        assertEquals(2, r2.residualOrder.sequenceNumber);
    }

    // ---------- v2 improvement 2: order validation ----------

    @Test
    public void testRejectsNonPositivePrice() {
        OrderBook.MatchResult result = engine.placeOrder("1", "AAPL", true, 0, 100);

        assertEquals("rejected", result.status);
        assertEquals("non-positive price", result.rejectReason);
        assertNull(result.residualOrder);
        assertTrue(engine.getBidsDepth("AAPL").isEmpty());
        // A rejected order never reaches the book, so it cannot be cancelled.
        assertFalse(engine.cancelOrder("AAPL", "1"));
    }

    @Test
    public void testRejectsNonPositiveQuantity() {
        OrderBook.MatchResult result = engine.placeOrder("1", "AAPL", false, 150, -5);

        assertEquals("rejected", result.status);
        assertEquals("non-positive quantity", result.rejectReason);
        assertTrue(engine.getAsksDepth("AAPL").isEmpty());
    }

    @Test
    public void testRejectsDuplicateOrderId() {
        OrderBook.MatchResult first = engine.placeOrder("1", "AAPL", true, 150, 100);
        assertEquals("resting", first.status);

        OrderBook.MatchResult duplicate = engine.placeOrder("1", "AAPL", true, 155, 50);
        assertEquals("rejected", duplicate.status);
        assertEquals("duplicate order id", duplicate.rejectReason);

        // Book still holds exactly the first order.
        Map<Long, Long> bids = engine.getBidsDepth("AAPL");
        assertEquals(1, bids.size());
        assertEquals(100, bids.get(150L));
    }

    @Test
    public void testRejectionsAreLoggedWithReason() {
        engine.placeOrder("1", "AAPL", true, 0, 100);

        assertEquals(1, engine.getEventLog().events().size());
        EventLog.Event event = engine.getEventLog().events().get(0);
        assertEquals("place", event.op);
        assertFalse(event.accepted);
        assertEquals("non-positive price", event.reason);
        assertEquals(1, event.sequence);
    }

    // ---------- v2 improvement 1: sequenced event log + replay ----------

    @Test
    public void testReplayReproducesIdenticalBookState() {
        engine.placeOrder("1", "AAPL", false, 150, 100);
        engine.placeOrder("2", "AAPL", false, 151, 50);
        engine.placeOrder("3", "AAPL", true, 150, 40);  // matches 40 of order 1
        engine.placeOrder("4", "AAPL", true, 149, 200); // rests
        engine.cancelOrder("AAPL", "2");

        MatchingEngine standby = MatchingEngine.replay(engine.getEventLog().events());

        assertEquals(engine.getBidsDepth("AAPL"), standby.getBidsDepth("AAPL"));
        assertEquals(engine.getAsksDepth("AAPL"), standby.getAsksDepth("AAPL"));
        assertEquals(60, standby.getAsksDepth("AAPL").get(150L));
        assertEquals(200, standby.getBidsDepth("AAPL").get(149L));
    }

    @Test
    public void testReplayContinuesSequencingPastLogMaximum() {
        engine.placeOrder("1", "AMZN", true, 3300, 10);
        engine.placeOrder("2", "AMZN", true, 3300, 10);
        long maxLogged = 0;
        for (EventLog.Event event : engine.getEventLog().events()) {
            maxLogged = Math.max(maxLogged, event.sequence);
        }

        MatchingEngine standby = MatchingEngine.replay(engine.getEventLog().events());
        OrderBook.MatchResult fresh = standby.placeOrder("3", "AMZN", true, 3300, 10);

        assertTrue(fresh.residualOrder.sequenceNumber > maxLogged);
        // Same FIFO depth on the standby.
        assertEquals(30, standby.getBidsDepth("AMZN").get(3300L));
    }

    @Test
    public void testReplaySkipsRejectedAndFailedEvents() {
        engine.placeOrder("1", "TSLA", true, 0, 50);     // rejected
        engine.placeOrder("2", "TSLA", true, 800, 50);   // rests
        engine.cancelOrder("TSLA", "nope");              // failed cancel
        engine.cancelOrder("TSLA", "2");                 // successful cancel

        MatchingEngine standby = MatchingEngine.replay(engine.getEventLog().events());

        assertTrue(standby.getBidsDepth("TSLA").isEmpty());
        assertEquals(engine.getBidsDepth("TSLA"), standby.getBidsDepth("TSLA"));
    }

    // ---------- v2 improvement 3: slow-consumer-safe market data ----------

    @Test
    public void testSlowConsumerDropsAreCountedAndIsolated() {
        MarketDataPublisher publisher = new MarketDataPublisher();
        publisher.subscribe("fast", 10);
        publisher.subscribe("slow", 2);
        engine.setMarketDataPublisher(publisher);

        // Three resting asks, then three buys -> 3 trades published.
        engine.placeOrder("s1", "AAPL", false, 150, 10);
        engine.placeOrder("s2", "AAPL", false, 151, 10);
        engine.placeOrder("s3", "AAPL", false, 152, 10);
        engine.placeOrder("b1", "AAPL", true, 152, 10);
        engine.placeOrder("b2", "AAPL", true, 152, 10);
        engine.placeOrder("b3", "AAPL", true, 152, 10);

        // Fast consumer drains everything: 3 trades.
        int received = 0;
        while (publisher.poll("fast") != null) {
            received++;
        }
        assertEquals(3, received);

        // Slow consumer held only its first 2; the third was dropped for it only.
        assertEquals(2, publisher.pending("slow"));
        assertEquals(1, publisher.dropped("slow"));
        assertEquals(0, publisher.dropped("fast"));
    }
}
