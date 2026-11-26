import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

class SlowMockSink implements Sink {
    private final AtomicInteger alertCount = new AtomicInteger(0);
    private final long delayMs;
    
    public SlowMockSink(long delayMs) {
        this.delayMs = delayMs;
    }

    @Override
    public void send(AlertRule rule, Tick tick) {
        try {
            Thread.sleep(delayMs);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        alertCount.incrementAndGet();
    }

    public int getAlertCount() {
        return alertCount.get();
    }
}

public class AlertEngineV3Test {

    @Test
    void testV3ConcurrentIngestion() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        AlertRule rule = new AlertRule("rule1", "AAPL", condition, 0, Collections.singletonList(sink));
        engine.addRule(rule);
        
        int numTicks = 1000;
        for (int i = 0; i < numTicks; i++) {
            engine.processTick(new Tick("AAPL", 110.0, 100, 1000 + i));
        }
        
        engine.stop();
        try { Thread.sleep(500); } catch (InterruptedException e) {}
        
        assertEquals(numTicks, sink.getAlertCount());
    }

    @Test
    void testV3CooldownSuppression() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        AlertRule rule = new AlertRule("rule2", "MSFT", condition, 5000, Collections.singletonList(sink));
        engine.addRule(rule);
        
        engine.processTick(new Tick("MSFT", 110.0, 100, 1000));
        engine.processTick(new Tick("MSFT", 110.0, 100, 2000));
        engine.processTick(new Tick("MSFT", 110.0, 100, 5999));
        engine.processTick(new Tick("MSFT", 110.0, 100, 6000));
        
        engine.stop();
        try { Thread.sleep(500); } catch (InterruptedException e) {}
        
        assertEquals(2, sink.getAlertCount());
    }

    @Test
    void testV3MultisinkDispatchAsync() {
        AlertEngine engine = new AlertEngine();
        SlowMockSink sink1 = new SlowMockSink(100);
        SlowMockSink sink2 = new SlowMockSink(100);
        SlowMockSink sink3 = new SlowMockSink(100);
        
        List<Sink> sinks = new ArrayList<>();
        sinks.add(sink1);
        sinks.add(sink2);
        sinks.add(sink3);
        
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        AlertRule rule = new AlertRule("rule3", "NVDA", condition, 0, sinks);
        engine.addRule(rule);
        
        long startTime = System.currentTimeMillis();
        // Ingestion should be extremely fast, non-blocking
        engine.processTick(new Tick("NVDA", 150.0, 100, 1000));
        long ingestTime = System.currentTimeMillis() - startTime;
        
        assertTrue(ingestTime < 50, "Ingestion should be non-blocking and fast");
        
        engine.stop();
        try { Thread.sleep(500); } catch (InterruptedException e) {}
        
        assertEquals(1, sink1.getAlertCount());
        assertEquals(1, sink2.getAlertCount());
        assertEquals(1, sink3.getAlertCount());
    }

    @Test
    void testV3HighTickVolume() throws InterruptedException {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        Condition condition = new PriceCondition(100.0, Operator.GREATER_THAN);
        // 5 seconds cooldown
        AlertRule rule = new AlertRule("rule4", "AMZN", condition, 5000, Collections.singletonList(sink));
        engine.addRule(rule);
        
        int numThreads = 50;
        int ticksPerThread = 200;
        
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);
        
        for (int i = 0; i < numThreads; i++) {
            executor.submit(() -> {
                for (int j = 0; j < ticksPerThread; j++) {
                    // Same timestamp (1000) for all ticks, so only 1 alert should fire
                    engine.processTick(new Tick("AMZN", 150.0, 100, 1000));
                }
                latch.countDown();
            });
        }
        
        latch.await();
        executor.shutdown();
        
        engine.stop();
        try { Thread.sleep(500); } catch (InterruptedException e) {}
        
        assertEquals(1, sink.getAlertCount());
    }
}
