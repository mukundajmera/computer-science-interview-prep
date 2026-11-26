package tests;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v1_basic.MatchingEngine;
import v1_basic.OrderBook;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class MatchingEngineTest {
    private MatchingEngine engine;

    @BeforeEach
    public void setUp() {
        engine = new MatchingEngine();
    }

    @Test
    public void testFullMatchBuyAndSellAtSamePrice() {
        OrderBook.MatchResult result1 = engine.placeOrder("1", "AAPL", false, 150, 100);
        assertTrue(result1.trades.isEmpty());
        assertNotNull(result1.residualOrder);
        assertEquals(100, result1.residualOrder.quantity);

        OrderBook.MatchResult result2 = engine.placeOrder("2", "AAPL", true, 150, 100);
        assertEquals(1, result2.trades.size());
        assertEquals("1", result2.trades.get(0).makerOrderId);
        assertEquals("2", result2.trades.get(0).takerOrderId);
        assertEquals(150, result2.trades.get(0).price);
        assertEquals(100, result2.trades.get(0).quantity);
        assertNull(result2.residualOrder);
        
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
        
        // Should execute best price first (2790)
        assertEquals("2", result.trades.get(0).makerOrderId);
        assertEquals(15, result.trades.get(0).quantity);
        assertEquals(2790, result.trades.get(0).price);
        
        // Then at 2800, execute in time priority (order 1 before order 3)
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
}
