package v1_simple;

import java.util.List;

public class Demo {
    static class Event {
        String id;
        long timestamp;
        double value;

        public Event(String id, long timestamp, double value) {
            this.id = id;
            this.timestamp = timestamp;
            this.value = value;
        }

        @Override
        public String toString() {
            return String.format("Event(t=%d, v=%.1f)", timestamp, value);
        }
    }

    public static void main(String[] args) {
        System.out.println("--- Stream Processing Demo ---");

        // Tumbling window (size = slide) of 5 units, 2 units allowed lateness, summing values
        SlidingWindowAggregator<Event, double[], Double> aggregator = new SlidingWindowAggregator<>(
            5, 5, 2,
            e -> e.timestamp,
            SlidingWindowAggregator.sumAggregation()
        );

        Event[] stream = {
            new Event("1", 1, 10),
            new Event("2", 3, 20),
            new Event("3", 2, 5),   // Slightly out of order
            new Event("4", 8, 15),
            new Event("5", 4, 30),  // Late but within allowed lateness for window 0-5
            new Event("6", 1, 50),  // Too late for window 0-5, should be discarded
            new Event("7", 12, 5)
        };

        for (Event e : stream) {
            System.out.println("Processing " + e);
            aggregator.processEvent(e);

            // Advance watermark to timestamp - 1 (simple watermark heuristic)
            List<SlidingWindowAggregator.WindowResult<Double>> results = aggregator.advanceWatermark(e.timestamp - 1);
            for (SlidingWindowAggregator.WindowResult<Double> res : results) {
                System.out.println("  Triggered: " + res);
            }
        }

        // Final watermark advancement to flush remaining windows
        System.out.println("Advancing watermark to infinity...");
        List<SlidingWindowAggregator.WindowResult<Double>> finalResults = aggregator.advanceWatermark(Long.MAX_VALUE);
        for (SlidingWindowAggregator.WindowResult<Double> res : finalResults) {
            System.out.println("  Triggered: " + res);
        }
    }
}
