package v3_optimized;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import v1_basic.AggregationKey;
import v1_basic.AggregationStore;

public class ShardedStateStore implements AggregationStore {
    private final PartitionRouter router;
    private final Map<AggregationKey, Integer>[] stores;

    @SuppressWarnings("unchecked")
    public ShardedStateStore(int numPartitions) {
        this.router = new PartitionRouter(numPartitions);
        this.stores = new ConcurrentHashMap[numPartitions];
        for (int i = 0; i < numPartitions; i++) {
            this.stores[i] = new ConcurrentHashMap<>();
        }
    }

    @Override
    public void increment(AggregationKey key, int count) {
        int partition = router.getPartition(key.getAdId());
        stores[partition].merge(key, count, Integer::sum);
    }

    @Override
    public int getCount(AggregationKey key) {
        int partition = router.getPartition(key.getAdId());
        return stores[partition].getOrDefault(key, 0);
    }
    
    @Override
    public Map<AggregationKey, Integer> getAll() {
        Map<AggregationKey, Integer> all = new ConcurrentHashMap<>();
        for (Map<AggregationKey, Integer> store : stores) {
            all.putAll(store);
        }
        return all;
    }

    }
