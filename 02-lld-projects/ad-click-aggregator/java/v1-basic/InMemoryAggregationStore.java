package v1_basic;

import java.util.HashMap;
import java.util.Map;

public class InMemoryAggregationStore implements AggregationStore {
    private final Map<AggregationKey, Integer> counts = new HashMap<>();

    @Override
    public void increment(AggregationKey key, int count) {
        counts.put(key, counts.getOrDefault(key, 0) + count);
    }

    @Override
    public int getCount(AggregationKey key) {
        return counts.getOrDefault(key, 0);
    }

    @Override
    public Map<AggregationKey, Integer> getAll() {
        return new HashMap<>(counts);
    }

    }
