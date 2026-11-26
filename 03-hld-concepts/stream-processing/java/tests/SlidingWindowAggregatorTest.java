package tests;

import org.junit.jupiter.api.Test;
import v1_simple.SlidingWindowAggregator;
import v1_simple.SlidingWindowAggregator.WindowResult;
import v1_simple.SlidingWindowAggregator.AggregateFunction;

import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

public class SlidingWindowAggregatorTest {

    static class SimpleEvent {
        long timestamp;
        double value;
        SimpleEvent(long t, double v) { timestamp = t; value = v; }
    }

    private final SlidingWindowAggregator.TimestampExtractor<SimpleEvent> extractor = e -> e.timestamp;
    private final AggregateFunction<Object, double[], Double> sumAgg = SlidingWindowAggregator.sumAggregation();

    @Test
    public void testTumblingWindows() {
        // windowSize=10, slideSize=10 (tumbling window)
        SlidingWindowAggregator<SimpleEvent, double[], Double> agg =
            new SlidingWindowAggregator<>(10, 10, 0, extractor, sumAgg);

        agg.processEvent(new SimpleEvent(2, 5.0));
        agg.processEvent(new SimpleEvent(7, 10.0));
        agg.processEvent(new SimpleEvent(12, 2.0));

        // Advance to 10 (window 0-10 complete)
        List<WindowResult<Double>> res = agg.advanceWatermark(10);
        assertEquals(1, res.size());
        assertEquals(0, res.get(0).start);
        assertEquals(10, res.get(0).end);
        assertEquals(15.0, res.get(0).result);

        // Advance to 20 (window 10-20 complete)
        res = agg.advanceWatermark(20);
        assertEquals(1, res.size());
        assertEquals(10, res.get(0).start);
        assertEquals(20, res.get(0).end);
        assertEquals(2.0, res.get(0).result);
    }

    @Test
    public void testSlidingWindows() {
        // windowSize=10, slideSize=5
        SlidingWindowAggregator<SimpleEvent, double[], Double> agg =
            new SlidingWindowAggregator<>(10, 5, 0, extractor, sumAgg);

        // An event at t=7 falls into windows [0, 10) and [5, 15)
        agg.processEvent(new SimpleEvent(7, 5.0));

        List<WindowResult<Double>> res = agg.advanceWatermark(11);
        assertEquals(1, res.size());
        assertEquals(0, res.get(0).start);
        assertEquals(10, res.get(0).end);
        assertEquals(5.0, res.get(0).result);

        res = agg.advanceWatermark(16);
        assertEquals(1, res.size());
        assertEquals(5, res.get(0).start);
        assertEquals(15, res.get(0).end);
        assertEquals(5.0, res.get(0).result);
    }

    @Test
    public void testLateEventHandling() {
        // windowSize=10, slideSize=10, allowedLateness=5
        SlidingWindowAggregator<SimpleEvent, double[], Double> agg =
            new SlidingWindowAggregator<>(10, 10, 5, extractor, sumAgg);

        agg.processEvent(new SimpleEvent(2, 10.0));
        agg.advanceWatermark(11); // Window 0-10 not closed yet because lateness = 5 (watermark < 10 + 5)

        // Event t=7, watermark=11, lateness=5 -> 7 < 11-5 is False, so it's accepted.
        agg.processEvent(new SimpleEvent(7, 5.0)); // Late but accepted

        List<WindowResult<Double>> res = agg.advanceWatermark(15); // Watermark is 15 >= 10+5, so 0-10 is closed
        assertEquals(1, res.size());
        assertEquals(0, res.get(0).start);
        assertEquals(10, res.get(0).end);
        assertEquals(15.0, res.get(0).result);

        // This event is too late for 0-10, will be discarded
        agg.processEvent(new SimpleEvent(3, 20.0));

        // Nothing more triggered
        res = agg.advanceWatermark(20);
        assertEquals(0, res.size()); // Window 10-20 has no events
    }

    @Test
    public void testCountAggregation() {
        SlidingWindowAggregator<SimpleEvent, long[], Long> agg =
            new SlidingWindowAggregator<>(10, 10, 0, extractor, SlidingWindowAggregator.countAggregation());

        agg.processEvent(new SimpleEvent(1, 100));
        agg.processEvent(new SimpleEvent(2, 200));
        agg.processEvent(new SimpleEvent(5, 300));

        List<WindowResult<Long>> res = agg.advanceWatermark(10);
        assertEquals(1, res.size());
        assertEquals(3L, res.get(0).result);
    }
}
