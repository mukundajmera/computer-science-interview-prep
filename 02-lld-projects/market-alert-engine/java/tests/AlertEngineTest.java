import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.junit.jupiter.api.Assertions.assertEquals;

class MockSink implements Sink {
    private final AtomicInteger alertCount = new AtomicInteger(0);

    @Override
    public void send(AlertRule rule, Tick tick) {
        alertCount.incrementAndGet();
    }

    public int getAlertCount() {
        return alertCount.get();
    }
}


public class AlertEngineTest {

    @Test
    void testPriceThresholdCrossing() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        AlertRule rule = new AlertRule("rule1", "AAPL", condition, 0, Collections.singletonList(sink));
        engine.addRule(rule);

        engine.processTick(new Tick("AAPL", 90.0, 100, 1000));
        assertEquals(0, sink.getAlertCount());

        engine.processTick(new Tick("AAPL", 110.0, 100, 2000));
        assertEquals(1, sink.getAlertCount());
    }

    @Test
    void testCompositeAndOrCondition() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        
        Condition priceCond = new PriceCondition(100.0, Operator.GREATER_THAN);
        Condition volCond = new VolumeCondition(500, Operator.GREATER_THAN);
        Condition andCond = new AndCondition(priceCond, volCond);
        
        AlertRule rule = new AlertRule("rule2", "GOOGL", andCond, 0, Collections.singletonList(sink));
        engine.addRule(rule);

        // Price > 100, but Vol < 500 (No alert)
        engine.processTick(new Tick("GOOGL", 150.0, 100, 1000));
        assertEquals(0, sink.getAlertCount());

        // Price > 100 and Vol > 500 (Alert!)
        engine.processTick(new Tick("GOOGL", 150.0, 600, 2000));
        assertEquals(1, sink.getAlertCount());
    }

    @Test
    void testAlertCooldownSuppression() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        // 5000ms cooldown
        AlertRule rule = new AlertRule("rule3", "MSFT", condition, 5000, Collections.singletonList(sink));
        engine.addRule(rule);

        // Initial breach at t=1000 -> Alert!
        engine.processTick(new Tick("MSFT", 110.0, 100, 1000));
        assertEquals(1, sink.getAlertCount());

        // Second breach at t=2000 (within 5000ms cooldown) -> Suppressed!
        engine.processTick(new Tick("MSFT", 115.0, 100, 2000));
        assertEquals(1, sink.getAlertCount());

        // Third breach at t=6000 (cooldown expired: 6000 - 1000 >= 5000) -> Alert!
        engine.processTick(new Tick("MSFT", 120.0, 100, 6000));
        assertEquals(2, sink.getAlertCount());
    }

    @Test
    void testThreadSafeStreaming() throws InterruptedException {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        // Cooldown long enough to suppress all subsequent alerts from other threads
        AlertRule rule = new AlertRule("rule4", "AMZN", condition, 10000, Collections.singletonList(sink));
        engine.addRule(rule);

        int numThreads = 100;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);

        for (int i = 0; i < numThreads; i++) {
            executor.submit(() -> {
                // All threads process the tick at exactly the same timestamp (t=1000)
                engine.processTick(new Tick("AMZN", 150.0, 100, 1000));
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();

        // Despite 100 threads evaluating the condition concurrently, the atomic compute 
        // in AlertEngine should ensure exactly one alert is dispatched because of the cooldown.
        assertEquals(1, sink.getAlertCount());
    }

    @Test
    void testMultipleSinks() {
        AlertEngine engine = new AlertEngine();
        MockSink sink1 = new MockSink();
        MockSink sink2 = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        List<Sink> sinks = new ArrayList<>();
        sinks.add(sink1);
        sinks.add(sink2);
        
        AlertRule rule = new AlertRule("rule5", "NVDA", condition, 5000, sinks);
        engine.addRule(rule);

        engine.processTick(new Tick("NVDA", 110.0, 100, 1000));
        assertEquals(1, sink1.getAlertCount());
        assertEquals(1, sink2.getAlertCount());
    }


    @Test
    void testPercentChangeCondition() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PercentChangeCondition(10.0, 5000);
        
        AlertRule rule = new AlertRule("rule6", "TSLA", condition, 0, Collections.singletonList(sink));
        engine.addRule(rule);

        engine.processTick(new Tick("TSLA", 100.0, 100, 1000));
        assertEquals(0, sink.getAlertCount());

        engine.processTick(new Tick("TSLA", 105.0, 100, 2000));
        assertEquals(0, sink.getAlertCount());

        engine.processTick(new Tick("TSLA", 115.0, 100, 3000));
        assertEquals(1, sink.getAlertCount());

        engine.processTick(new Tick("TSLA", 118.0, 100, 8001));
        assertEquals(1, sink.getAlertCount());
    }
}
