import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Optional;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Collections;

import v1_basic.*;
import v2_extended.*;
import v3_optimized.*;

public class PriceTrackingServiceTest {

    private PriceTrackingService service;

    @Before
    public void setUp() {
        service = new PriceTrackingService();
    }

    @Test
    public void testPriceRecordingAndBasicSummary() {
        Instant now = Instant.now();
        service.recordPrice(new PriceObservation("p1", now.minusSeconds(3600), 100.0, "RetailerA"));
        service.recordPrice(new PriceObservation("p1", now, 90.0, "RetailerA"));

        Optional<ProductPriceSummary> summaryOpt = service.getPriceSummary("p1");
        Assert.assertTrue(summaryOpt.isPresent());
        ProductPriceSummary summary = summaryOpt.get();

        Assert.assertEquals("p1", summary.getProductId());
        Assert.assertEquals(90.0, summary.getMinPrice());
        Assert.assertEquals(100.0, summary.getMaxPrice());
        Assert.assertEquals(90.0, summary.getCurrentPrice());
        Assert.assertEquals(now, summary.getLastUpdated());
    }

    @Test
    public void testGetPriceHistory() {
        Instant now = Instant.now();
        Instant t1 = now.minus(2, ChronoUnit.DAYS);
        Instant t2 = now.minus(1, ChronoUnit.DAYS);
        Instant t3 = now;

        service.recordPrice(new PriceObservation("p2", t1, 20.0, "RetailerB"));
        service.recordPrice(new PriceObservation("p2", t2, 18.0, "RetailerB"));
        service.recordPrice(new PriceObservation("p2", t3, 19.0, "RetailerC"));

        // Query between t1 and t2
        List<PriceObservation> history = service.getPriceHistory("p2", t1, t2);
        Assert.assertEquals(2, history.size());
        Assert.assertEquals(t1, history.get(0).getTimestamp());
        Assert.assertEquals(t2, history.get(1).getTimestamp());

        // Query exact match for t3
        List<PriceObservation> historyT3 = service.getPriceHistory("p2", t3, t3);
        Assert.assertEquals(1, historyT3.size());
        Assert.assertEquals("RetailerC", historyT3.get(0).getRetailer());
    }

    @Test
    void testSummaryMetricsWithMultipleRetailers() {
        Instant now = Instant.now();
        service.recordPrice(new PriceObservation("p3", now.minusSeconds(100), 50.0, "RetailerA"));
        service.recordPrice(new PriceObservation("p3", now.minusSeconds(50), 45.0, "RetailerA"));
        
        service.recordPrice(new PriceObservation("p3", now.minusSeconds(80), 55.0, "RetailerB"));
        service.recordPrice(new PriceObservation("p3", now, 48.0, "RetailerB"));

        Optional<ProductPriceSummary> summaryOpt = service.getPriceSummary("p3");
        Assert.assertTrue(summaryOpt.isPresent());
        ProductPriceSummary summary = summaryOpt.get();

        Assert.assertEquals(45.0, summary.getMinPrice());
        Assert.assertEquals(55.0, summary.getMaxPrice());
        Assert.assertEquals(48.0, summary.getCurrentPrice()); // RetailerB has the most recent update
        Assert.assertEquals(now, summary.getLastUpdated());
    }

    @Test
    void testMultiRetailerLowestPrice() {
        Instant now = Instant.now();
        
        // Retailer A has an older lower price, but its current price is higher
        service.recordPrice(new PriceObservation("p4", now.minusSeconds(1000), 10.0, "RetailerA"));
        service.recordPrice(new PriceObservation("p4", now, 30.0, "RetailerA"));
        
        // Retailer B has a lower current price
        service.recordPrice(new PriceObservation("p4", now.minusSeconds(500), 35.0, "RetailerB"));
        service.recordPrice(new PriceObservation("p4", now.minusSeconds(10), 20.0, "RetailerB"));

        Optional<String> lowestRetailerOpt = service.getLowestPriceRetailer("p4");
        Assert.assertTrue(lowestRetailerOpt.isPresent());
        Assert.assertEquals("RetailerB", lowestRetailerOpt.get());
    }

    @Test
    void testEmptyHistoryEdgeCases() {
        Assert.assertFalse(service.getPriceSummary("unknown_product").isPresent());
        Assert.assertFalse(service.getLowestPriceRetailer("unknown_product").isPresent());
        Assert.assertTrue(service.getPriceHistory("unknown_product", Instant.MIN, Instant.MAX).isEmpty());
    }

    static class MockClock extends java.time.Clock {
        private Instant instant;
        
        public MockClock(Instant instant) {
            this.instant = instant;
        }

        public void setInstant(Instant instant) {
            this.instant = instant;
        }

        @Override
        public java.time.ZoneId getZone() {
            return java.time.ZoneId.of("UTC");
        }

        @Override
        public java.time.Clock withZone(java.time.ZoneId zone) {
            return this;
        }

        @Override
        public Instant instant() {
            return instant;
        }
    }

    @Test
    public void testV2ThresholdAlertAndUnsubscribe() {
        MockClock clock = new MockClock(Instant.ofEpochSecond(1000000));
        v2_extended.InMemoryPriceHistoryStore store = new v2_extended.InMemoryPriceHistoryStore(3600, clock);
        
        Map<v2_extended.Channel, v2_extended.ChannelAdapter> adapters = new HashMap<>();
        List<String> sentMessages = new ArrayList<>();
        adapters.put(v2_extended.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v2_extended.RateLimitedDispatcher dispatcher = new v2_extended.RateLimitedDispatcher(adapters, 60, clock);
        v2_extended.SubscriptionService service2 = new v2_extended.SubscriptionService(store, dispatcher);
        
        v2_extended.PriceAlertSubscription sub = new v2_extended.PriceAlertSubscription(
            "sub1", "u1", "p1", Optional.of(1000), Optional.empty(), v2_extended.Channel.EMAIL
        );
        service2.subscribe(sub);
        
        // Initial price above threshold
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 1200, true));
        Assert.assertEquals(0, sentMessages.size());
        
        // Price drops below threshold - triggers alert
        clock.setInstant(clock.instant().plusSeconds(10));
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 900, true));
        Assert.assertEquals(1, sentMessages.size());
        
        // Price stays below threshold - should NOT trigger alert again (only crossing)
        clock.setInstant(clock.instant().plusSeconds(70)); // past rate limit just in case
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 800, true));
        Assert.assertEquals(1, sentMessages.size()); // Still 1
        
        // Price goes above threshold
        clock.setInstant(clock.instant().plusSeconds(10));
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 1100, true));
        Assert.assertEquals(1, sentMessages.size());
        
        // Price drops below threshold again - triggers alert
        clock.setInstant(clock.instant().plusSeconds(10));
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 950, true));
        Assert.assertEquals(2, sentMessages.size());
        
        // Unsubscribe
        service2.unsubscribe("sub1");
        
        // Price drops - should NOT trigger since unsubscribed
        clock.setInstant(clock.instant().plusSeconds(10));
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 850, true));
        Assert.assertEquals(2, sentMessages.size());
    }
    
    @Test
    public void testV2OutOfOrderTimestampsAndRetention() {
        MockClock clock = new MockClock(Instant.ofEpochSecond(1000000));
        v2_extended.InMemoryPriceHistoryStore store = new v2_extended.InMemoryPriceHistoryStore(3600, clock); // 1 hour retention
        
        Map<v2_extended.Channel, v2_extended.ChannelAdapter> adapters = new HashMap<>();
        List<String> sentMessages = new ArrayList<>();
        adapters.put(v2_extended.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v2_extended.RateLimitedDispatcher dispatcher = new v2_extended.RateLimitedDispatcher(adapters, 60, clock);
        v2_extended.SubscriptionService service2 = new v2_extended.SubscriptionService(store, dispatcher);
        
        v2_extended.PriceAlertSubscription sub = new v2_extended.PriceAlertSubscription(
            "sub1", "u1", "p1", Optional.of(1000), Optional.empty(), v2_extended.Channel.EMAIL
        );
        service2.subscribe(sub);
        
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 1200, true));
        
        // Out of order: earlier timestamp, lower price
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond() - 100, 900, true));
        
        // Should be ignored
        Assert.assertEquals(0, sentMessages.size());
        Assert.assertEquals(1200, store.getCurrentPrice("p1", "m1"));
        
        // Fast forward 2 hours
        clock.setInstant(clock.instant().plusSeconds(7200));
        
        // New update
        service2.onPriceUpdate("p1", "m1", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 1100, true));
        
        // The old 1200 record should be cleared due to retention policy
        Assert.assertEquals(1, store.getHistory("p1", "m1").size());
        Assert.assertEquals(1100, store.getCurrentPrice("p1", "m1"));
    }
    
    @Test
    public void testV2PriceCollectorFailedPollingAndMissingProduct() {
        MockClock clock = new MockClock(Instant.ofEpochSecond(1000000));
        v2_extended.InMemoryPriceHistoryStore store = new v2_extended.InMemoryPriceHistoryStore(3600, clock);
        Map<v2_extended.Channel, v2_extended.ChannelAdapter> adapters = new HashMap<>();
        v2_extended.RateLimitedDispatcher dispatcher = new v2_extended.RateLimitedDispatcher(adapters, 60, clock);
        v2_extended.SubscriptionService service2 = new v2_extended.SubscriptionService(store, dispatcher);
        
        // Transport that returns empty for missing/failed
        v2_extended.Transport transport = new v2_extended.Transport() {
            @Override
            public Optional<Integer> fetchPrice(String productId, String merchantId) {
                if (productId.equals("missing")) return Optional.empty();
                return Optional.of(1500);
            }
        };
        
        List<String> products = new ArrayList<>();
        products.add("p1");
        products.add("missing");
        
        List<String> merchants = new ArrayList<>();
        merchants.add("m1");
        
        v2_extended.PriceCollectorV2 collector = new v2_extended.PriceCollectorV2(service2, products, merchants, transport, clock);
        
        collector.poll();
        
        Assert.assertEquals(1500, store.getCurrentPrice("p1", "m1"));
        Assert.assertNull(store.getCurrentPrice("missing", "m1"));
    }
    
    @Test
    public void testV2PercentageDropAlert() {
        MockClock clock = new MockClock(Instant.ofEpochSecond(1000000));
        v2_extended.InMemoryPriceHistoryStore store = new v2_extended.InMemoryPriceHistoryStore(48 * 3600, clock);
        
        Map<v2_extended.Channel, v2_extended.ChannelAdapter> adapters = new HashMap<>();
        List<String> sentMessages = new ArrayList<>();
        adapters.put(v2_extended.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v2_extended.RateLimitedDispatcher dispatcher = new v2_extended.RateLimitedDispatcher(adapters, 60, clock);
        v2_extended.SubscriptionService service2 = new v2_extended.SubscriptionService(store, dispatcher);
        
        v2_extended.PriceAlertSubscription sub = new v2_extended.PriceAlertSubscription(
            "sub2", "u2", "p2", Optional.empty(), Optional.of(20.0), v2_extended.Channel.EMAIL
        );
        service2.subscribe(sub);
        
        long oldTime = clock.instant().getEpochSecond() - (25 * 60 * 60);
        service2.onPriceUpdate("p2", "m2", new v2_extended.PriceRecord(oldTime, 1000, true));
        
        // 10% drop, should not trigger
        service2.onPriceUpdate("p2", "m2", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 900, true));
        Assert.assertEquals(0, sentMessages.size());
        
        // 30% drop, should trigger
        clock.setInstant(clock.instant().plusSeconds(1));
        service2.onPriceUpdate("p2", "m2", new v2_extended.PriceRecord(clock.instant().getEpochSecond(), 700, true));
        Assert.assertEquals(1, sentMessages.size());
    }
    
    @Test
    public void testV2RateLimiting() {
        MockClock clock = new MockClock(Instant.ofEpochSecond(1000000));
        Map<v2_extended.Channel, v2_extended.ChannelAdapter> adapters = new HashMap<>();
        List<String> sentMessages = new ArrayList<>();
        adapters.put(v2_extended.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v2_extended.RateLimitedDispatcher dispatcher = new v2_extended.RateLimitedDispatcher(adapters, 60, clock);
        
        Assert.assertTrue(dispatcher.dispatch("sub3", "u3", v2_extended.Channel.EMAIL, "msg1"));
        Assert.assertEquals(1, sentMessages.size());
        
        // Should be rate limited
        Assert.assertFalse(dispatcher.dispatch("sub3", "u3", v2_extended.Channel.EMAIL, "msg2"));
        Assert.assertEquals(1, sentMessages.size());
    }
    
    @Test
    public void testV2UnsupportedChannel() {
        MockClock clock = new MockClock(Instant.ofEpochSecond(1000000));
        Map<v2_extended.Channel, v2_extended.ChannelAdapter> adapters = new HashMap<>();
        v2_extended.RateLimitedDispatcher dispatcher = new v2_extended.RateLimitedDispatcher(adapters, 60, clock);
        
        // Send via SMS but no SMS adapter registered
        Assert.assertFalse(dispatcher.dispatch("sub4", "u4", v2_extended.Channel.SMS, "msg"));
    }

@Test
    public void testV3IntegratedThresholdAlertAndUnsubscribe() {
        MockClock clock = new MockClock(java.time.Instant.ofEpochSecond(1000000));
        v3_optimized.InMemoryPriceHistoryStore store = new v3_optimized.InMemoryPriceHistoryStore(3600, clock);
        
        java.util.Map<v3_optimized.Channel, v3_optimized.ChannelAdapter> adapters = new java.util.HashMap<>();
        java.util.List<String> sentMessages = new java.util.ArrayList<>();
        adapters.put(v3_optimized.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v3_optimized.RateLimitedDispatcher dispatcher = new v3_optimized.RateLimitedDispatcher(adapters, 60, clock);
        v3_optimized.SubscriptionService service3 = new v3_optimized.SubscriptionService(store, dispatcher);
        
        v3_optimized.PriceAlertSubscription sub = new v3_optimized.PriceAlertSubscription(
            "sub1", "u1", "p1", java.util.Optional.of(1000), java.util.Optional.empty(), v3_optimized.Channel.EMAIL
        );
        service3.subscribe(sub);
        
        // Initial price above threshold
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 1200, true));
        Assert.assertEquals(0, sentMessages.size());
        
        // Price drops below threshold - triggers alert
        clock.setInstant(clock.instant().plusSeconds(10));
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 900, true));
        Assert.assertEquals(1, sentMessages.size());
    }

    @Test
    public void testV3IntegratedOutOfOrderTimestampsAndRetention() {
        MockClock clock = new MockClock(java.time.Instant.ofEpochSecond(1000000));
        v3_optimized.InMemoryPriceHistoryStore store = new v3_optimized.InMemoryPriceHistoryStore(3600, clock); // 1 hour retention
        
        java.util.Map<v3_optimized.Channel, v3_optimized.ChannelAdapter> adapters = new java.util.HashMap<>();
        java.util.List<String> sentMessages = new java.util.ArrayList<>();
        adapters.put(v3_optimized.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v3_optimized.RateLimitedDispatcher dispatcher = new v3_optimized.RateLimitedDispatcher(adapters, 60, clock);
        v3_optimized.SubscriptionService service3 = new v3_optimized.SubscriptionService(store, dispatcher);
        
        v3_optimized.PriceAlertSubscription sub = new v3_optimized.PriceAlertSubscription(
            "sub1", "u1", "p1", java.util.Optional.of(1000), java.util.Optional.empty(), v3_optimized.Channel.EMAIL
        );
        service3.subscribe(sub);
        
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 1200, true));
        
        // Out of order: earlier timestamp, lower price
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond() - 100, 900, true));
        
        // Should be ignored
        Assert.assertEquals(0, sentMessages.size());
        Assert.assertEquals(1200, store.getCurrentPrice("p1", "m1"));
        
        // Fast forward 2 hours
        clock.setInstant(clock.instant().plusSeconds(7200));
        
        // New update
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 1100, true));
        
        // The old 1200 record should be cleared due to retention policy
        Assert.assertEquals(1, store.getHistory("p1", "m1").size());
        Assert.assertEquals(1100, store.getCurrentPrice("p1", "m1"));
    }
    
    @Test
    public void testV3IntegratedPriceCollectorFailedPollingAndMissingProduct() {
        MockClock clock = new MockClock(java.time.Instant.ofEpochSecond(1000000));
        v3_optimized.InMemoryPriceHistoryStore store = new v3_optimized.InMemoryPriceHistoryStore(3600, clock);
        java.util.Map<v3_optimized.Channel, v3_optimized.ChannelAdapter> adapters = new java.util.HashMap<>();
        v3_optimized.RateLimitedDispatcher dispatcher = new v3_optimized.RateLimitedDispatcher(adapters, 60, clock);
        v3_optimized.SubscriptionService service3 = new v3_optimized.SubscriptionService(store, dispatcher);
        
        // Transport that returns empty for missing/failed
        v3_optimized.Transport transport = new v3_optimized.Transport() {
            @Override
            public java.util.Optional<Integer> fetchPrice(String productId, String merchantId) {
                if (productId.equals("missing")) return java.util.Optional.empty();
                return java.util.Optional.of(1500);
            }
        };
        
        java.util.List<String> products = new java.util.ArrayList<>();
        products.add("p1");
        products.add("missing");
        
        java.util.List<String> merchants = new java.util.ArrayList<>();
        merchants.add("m1");
        
        v3_optimized.PriceCollectorV3 collector = new v3_optimized.PriceCollectorV3(service3, products, merchants, transport, clock);
        
        collector.poll();
        
        Assert.assertEquals(1500, store.getCurrentPrice("p1", "m1"));
        Assert.assertNull(store.getCurrentPrice("missing", "m1"));
    }

    @Test
    public void testV3IntegratedThresholdAlertAndUnsubscribe() {
        MockClock clock = new MockClock(java.time.Instant.ofEpochSecond(1000000));
        v3_optimized.RingBuffer.OptimizedPriceHistoryStore store = new v3_optimized.RingBuffer.OptimizedPriceHistoryStore(3600, clock);
        
        java.util.Map<v3_optimized.Channel, v3_optimized.ChannelAdapter> adapters = new java.util.HashMap<>();
        java.util.List<String> sentMessages = new java.util.ArrayList<>();
        adapters.put(v3_optimized.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v3_optimized.RateLimitedDispatcher dispatcher = new v3_optimized.RateLimitedDispatcher(adapters, 60, clock);
        v3_optimized.SubscriptionService service3 = new v3_optimized.SubscriptionService(store, dispatcher);
        
        v3_optimized.PriceAlertSubscription sub = new v3_optimized.PriceAlertSubscription(
            "sub1", "u1", "p1", java.util.Optional.of(1000), java.util.Optional.empty(), v3_optimized.Channel.EMAIL
        );
        service3.subscribe(sub);
        
        // Initial price above threshold
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 1200, true));
        Assert.assertEquals(0, sentMessages.size());
        
        // Price drops below threshold - triggers alert
        clock.setInstant(clock.instant().plusSeconds(10));
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 900, true));
        Assert.assertEquals(1, sentMessages.size());
    }

    @Test
    public void testV3IntegratedOutOfOrderTimestampsAndRetention() {
        MockClock clock = new MockClock(java.time.Instant.ofEpochSecond(1000000));
        v3_optimized.RingBuffer.OptimizedPriceHistoryStore store = new v3_optimized.RingBuffer.OptimizedPriceHistoryStore(3600, clock);
        
        java.util.Map<v3_optimized.Channel, v3_optimized.ChannelAdapter> adapters = new java.util.HashMap<>();
        java.util.List<String> sentMessages = new java.util.ArrayList<>();
        adapters.put(v3_optimized.Channel.EMAIL, (userId, message) -> sentMessages.add(message));
        
        v3_optimized.RateLimitedDispatcher dispatcher = new v3_optimized.RateLimitedDispatcher(adapters, 60, clock);
        v3_optimized.SubscriptionService service3 = new v3_optimized.SubscriptionService(store, dispatcher);
        
        v3_optimized.PriceAlertSubscription sub = new v3_optimized.PriceAlertSubscription(
            "sub1", "u1", "p1", java.util.Optional.of(1000), java.util.Optional.empty(), v3_optimized.Channel.EMAIL
        );
        service3.subscribe(sub);
        
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 1200, true));
        
        // Out of order: earlier timestamp, lower price
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond() - 100, 900, true));
        
        // Should be ignored
        Assert.assertEquals(0, sentMessages.size());
        Assert.assertEquals(1200, store.getCurrentPrice("p1", "m1"));
        
        // Fast forward 2 hours
        clock.setInstant(clock.instant().plusSeconds(7200));
        
        // New update
        service3.onPriceUpdate("p1", "m1", new v3_optimized.PriceRecord(clock.instant().getEpochSecond(), 1100, true));
        
        // The old 1200 record should be cleared due to retention policy
        Assert.assertEquals(1, store.getHistory("p1", "m1").size());
        Assert.assertEquals(1100, store.getCurrentPrice("p1", "m1"));
    }
    
    @Test
    public void testV3IntegratedPriceCollectorFailedPollingAndMissingProduct() {
        MockClock clock = new MockClock(java.time.Instant.ofEpochSecond(1000000));
        v3_optimized.RingBuffer.OptimizedPriceHistoryStore store = new v3_optimized.RingBuffer.OptimizedPriceHistoryStore(3600, clock);
        java.util.Map<v3_optimized.Channel, v3_optimized.ChannelAdapter> adapters = new java.util.HashMap<>();
        v3_optimized.RateLimitedDispatcher dispatcher = new v3_optimized.RateLimitedDispatcher(adapters, 60, clock);
        v3_optimized.SubscriptionService service3 = new v3_optimized.SubscriptionService(store, dispatcher);
        
        v3_optimized.Transport transport = new v3_optimized.Transport() {
            @Override
            public java.util.Optional<Integer> fetchPrice(String productId, String merchantId) {
                if (productId.equals("missing")) return java.util.Optional.empty();
                return java.util.Optional.of(1500);
            }
        };
        
        java.util.List<String> products = new java.util.ArrayList<>();
        products.add("p1");
        products.add("missing");
        
        java.util.List<String> merchants = new java.util.ArrayList<>();
        merchants.add("m1");
        
        v3_optimized.PriceCollectorV3 collector = new v3_optimized.PriceCollectorV3(service3, products, merchants, transport, clock);
        
        collector.poll();
        
        Assert.assertEquals(1500, store.getCurrentPrice("p1", "m1"));
        Assert.assertNull(store.getCurrentPrice("missing", "m1"));
    }

    @Test
    public void testV3RingBuffer() {
        v3_optimized.RingBuffer.OptimizedPriceTracker tracker = new v3_optimized.RingBuffer.OptimizedPriceTracker(2);
        
        Assert.assertTrue(tracker.addTick("p1", "m1", new v3_optimized.PriceRecord(1000, 100, true)));
        Assert.assertTrue(tracker.addTick("p1", "m1", new v3_optimized.PriceRecord(1001, 200, true)));
        
        Map<String, Object> stats = tracker.getStats("p1", "m1");
        Assert.assertEquals(150.0, (Double) stats.get("moving_average"), 0.01);
        
        // Add third, pushes out the first
        Assert.assertTrue(tracker.addTick("p1", "m1", new v3_optimized.PriceRecord(1002, 300, true)));
        stats = tracker.getStats("p1", "m1");
        Assert.assertEquals(250.0, (Double) stats.get("moving_average"), 0.01);
        Assert.assertEquals(100, (Integer) stats.get("all_time_low"));
    }
}


