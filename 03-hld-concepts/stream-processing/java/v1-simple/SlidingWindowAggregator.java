package v1_simple;

import java.util.*;

public class SlidingWindowAggregator<T, A, R> {
    private final long windowSize;
    private final long slideSize;
    private final long allowedLateness;
    private final TimestampExtractor<T> timestampExtractor;
    private final AggregateFunction<? super T, A, R> aggregateFunction;

    private final Map<Long, A> windowStates = new HashMap<>();
    private long currentWatermark = Long.MIN_VALUE;

    public interface TimestampExtractor<T> {
        long extractTimestamp(T event);
    }

    public interface AggregateFunction<T, A, R> {
        A createAccumulator();
        A add(T value, A accumulator);
        R getResult(A accumulator);
    }

    public static class WindowResult<R> {
        public final long start;
        public final long end;
        public final R result;

        public WindowResult(long start, long end, R result) {
            this.start = start;
            this.end = end;
            this.result = result;
        }

        @Override
        public String toString() {
            return String.format("Window[%d-%d]: %s", start, end, result);
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            WindowResult<?> that = (WindowResult<?>) o;
            return start == that.start && end == that.end && Objects.equals(result, that.result);
        }

        @Override
        public int hashCode() {
            return Objects.hash(start, end, result);
        }
    }

    public SlidingWindowAggregator(long windowSize, long slideSize, long allowedLateness,
                                   TimestampExtractor<T> timestampExtractor,
                                   AggregateFunction<? super T, A, R> aggregateFunction) {
        if (windowSize <= 0 || slideSize <= 0) {
            throw new IllegalArgumentException("Window and slide sizes must be positive");
        }
        this.windowSize = windowSize;
        this.slideSize = slideSize;
        this.allowedLateness = allowedLateness;
        this.timestampExtractor = timestampExtractor;
        this.aggregateFunction = aggregateFunction;
    }

    public void processEvent(T event) {
        long timestamp = timestampExtractor.extractTimestamp(event);

        // Prevent underflow of currentWatermark - allowedLateness
        long latenessThreshold = currentWatermark == Long.MIN_VALUE ? Long.MIN_VALUE : currentWatermark - allowedLateness;

        if (timestamp < latenessThreshold) {
            // Event is too late and is discarded
            return;
        }

        long lastWindowStart = Math.floorDiv(timestamp, slideSize) * slideSize;
        for (long start = lastWindowStart; start > timestamp - windowSize; start -= slideSize) {
            long windowEnd = start + windowSize;
            if (currentWatermark < windowEnd + allowedLateness) {
                if (!windowStates.containsKey(start)) {
                    windowStates.put(start, aggregateFunction.createAccumulator());
                }

                A acc = windowStates.get(start);
                windowStates.put(start, aggregateFunction.add(event, acc));
            }
        }
    }

    public List<WindowResult<R>> advanceWatermark(long newWatermark) {
        List<WindowResult<R>> results = new ArrayList<>();
        if (newWatermark > currentWatermark) {
            currentWatermark = newWatermark;

            Iterator<Map.Entry<Long, A>> iter = windowStates.entrySet().iterator();
            while (iter.hasNext()) {
                Map.Entry<Long, A> entry = iter.next();
                long windowStart = entry.getKey();
                long windowEnd = windowStart + windowSize;

                if (currentWatermark >= windowEnd + allowedLateness) {
                    results.add(new WindowResult<>(windowStart, windowEnd, aggregateFunction.getResult(entry.getValue())));
                    iter.remove();
                }
            }
        }
        results.sort(Comparator.comparingLong(w -> w.start));
        return results;
    }

    public long getCurrentWatermark() {
        return currentWatermark;
    }

    // Built-in aggregations
    public static AggregateFunction<Object, long[], Long> countAggregation() {
        return new AggregateFunction<Object, long[], Long>() {
            @Override
            public long[] createAccumulator() { return new long[]{0L}; }
            @Override
            public long[] add(Object value, long[] acc) { acc[0]++; return acc; }
            @Override
            public Long getResult(long[] acc) { return acc[0]; }
        };
    }

    public static AggregateFunction<Object, double[], Double> sumAggregation() {
        return new AggregateFunction<Object, double[], Double>() {
            @Override
            public double[] createAccumulator() { return new double[]{0.0}; }
            @Override
            public double[] add(Object value, double[] acc) {
                try {
                    java.lang.reflect.Field f = value.getClass().getDeclaredField("value");
                    f.setAccessible(true);
                    Object fieldVal = f.get(value);
                    if (fieldVal instanceof Number) {
                        acc[0] += ((Number) fieldVal).doubleValue();
                    } else {
                        throw new RuntimeException("Field 'value' is not a Number");
                    }
                } catch (Exception e) {
                    if (value instanceof Number) {
                        acc[0] += ((Number) value).doubleValue();
                    } else {
                        throw new RuntimeException("Cannot sum object of type " + value.getClass());
                    }
                }
                return acc;
            }
            @Override
            public Double getResult(double[] acc) { return acc[0]; }
        };
    }
}
