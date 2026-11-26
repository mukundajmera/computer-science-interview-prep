import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

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

public class AlertEngineV2Test {

    @Test
    void testV2CompositeDag() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        
        Condition c1 = new PriceCondition(100.0, Operator.GREATER_THAN);
        Condition c2 = new VolumeCondition(500, Operator.GREATER_THAN);
        Condition c3 = new PriceCondition(150.0, Operator.EQUAL);
        
        Condition orCond = new OrCondition(c1, c2);
        Condition notCond = new NotCondition(c3);
        Condition finalCond = new AndCondition(orCond, notCond);
        
        AlertRule rule = new AlertRule("dag_rule", "AAPL", finalCond, 0, Collections.singletonList(sink));
        engine.addRule(rule);
        
        engine.processTick(new Tick("AAPL", 120.0, 100, 1000));
        assertEquals(1, sink.getAlertCount());
        
        engine.processTick(new Tick("AAPL", 90.0, 600, 2000));
        assertEquals(2, sink.getAlertCount());
        
        engine.processTick(new Tick("AAPL", 150.0, 600, 3000));
        assertEquals(2, sink.getAlertCount());
    }

    @Test
    void testV2SlidingPercentage() {
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        
        Condition condition = new PercentChangeCondition(5.0, 10000);
        AlertRule rule = new AlertRule("pct_rule", "GOOG", condition, 0, Collections.singletonList(sink));
        engine.addRule(rule);
        
        engine.processTick(new Tick("GOOG", 100.0, 100, 1000));
        assertEquals(0, sink.getAlertCount());
        
        engine.processTick(new Tick("GOOG", 102.0, 100, 2000));
        assertEquals(0, sink.getAlertCount());
        
        engine.processTick(new Tick("GOOG", 106.0, 100, 3000));
        assertEquals(1, sink.getAlertCount());
        
        engine.processTick(new Tick("GOOG", 107.0, 100, 13000));
        assertEquals(1, sink.getAlertCount());
    }

    @Test
    void testV2ShortCircuitAnd() {
        class SideEffectCondition extends PriceCondition {
            boolean evaluated = false;
            SideEffectCondition() {
                super(100.0, Operator.GREATER_THAN);
            }
            @Override
            public boolean evaluate(Tick tick) {
                evaluated = true;
                return true;
            }
        }
        
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        
        Condition c1 = new PriceCondition(100.0, Operator.LESS_THAN); // false for 150
        SideEffectCondition c2 = new SideEffectCondition();
        
        Condition andCond = new AndCondition(c1, c2);
        AlertRule rule = new AlertRule("sc_and", "MSFT", andCond, 0, Collections.singletonList(sink));
        engine.addRule(rule);
        
        engine.processTick(new Tick("MSFT", 150.0, 100, 1000));
        assertEquals(0, sink.getAlertCount());
        assertFalse(c2.evaluated);
    }
    
    @Test
    void testV2ShortCircuitOr() {
        class SideEffectCondition extends PriceCondition {
            boolean evaluated = false;
            SideEffectCondition() {
                super(100.0, Operator.GREATER_THAN);
            }
            @Override
            public boolean evaluate(Tick tick) {
                evaluated = true;
                return true;
            }
        }
        
        AlertEngine engine = new AlertEngine();
        MockSink sink = new MockSink();
        
        Condition c1 = new PriceCondition(50.0, Operator.LESS_THAN); // true for 40
        SideEffectCondition c2 = new SideEffectCondition();
        
        Condition orCond = new OrCondition(c1, c2);
        AlertRule rule = new AlertRule("sc_or", "AMZN", orCond, 0, Collections.singletonList(sink));
        engine.addRule(rule);
        
        engine.processTick(new Tick("AMZN", 40.0, 100, 1000));
        assertEquals(1, sink.getAlertCount());
        assertFalse(c2.evaluated);
    }
}
