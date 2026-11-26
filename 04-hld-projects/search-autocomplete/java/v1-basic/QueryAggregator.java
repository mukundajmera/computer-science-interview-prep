import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

public class QueryAggregator {
    private final ConcurrentHashMap<String, LongAdder> queryCounts;

    public QueryAggregator() {
        this.queryCounts = new ConcurrentHashMap<>();
    }

    public void addQuery(String query) {
        if (query == null || query.trim().isEmpty()) {
            return;
        }
        queryCounts.computeIfAbsent(query.toLowerCase(), k -> new LongAdder()).increment();
    }

    public Map<String, Long> getAggregatedFrequencies() {
        Map<String, Long> result = new HashMap<>();
        for (Map.Entry<String, LongAdder> entry : queryCounts.entrySet()) {
            result.put(entry.getKey(), entry.getValue().sum());
        }
        return result;
    }
}
