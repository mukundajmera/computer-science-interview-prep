package v1_basic;
import java.util.Map;

public interface AggregationStore {
    void increment(AggregationKey key, int count);
    int getCount(AggregationKey key);
    Map<AggregationKey, Integer> getAll();
}
