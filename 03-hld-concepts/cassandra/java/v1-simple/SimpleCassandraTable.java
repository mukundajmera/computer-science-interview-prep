import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Interview-scale Cassandra table model using partition + clustering keys.
 */
public class SimpleCassandraTable {
    public enum ConsistencyLevel {
        ONE,
        QUORUM,
        ALL
    }

    public static final class Row {
        public final String partitionKey;
        public final long clusteringKey;
        public final Map<String, Object> columns;

        public Row(String partitionKey, long clusteringKey, Map<String, Object> columns) {
            this.partitionKey = partitionKey;
            this.clusteringKey = clusteringKey;
            this.columns = columns;
        }
    }

    private final Map<String, Map<Long, Row>> partitions = new HashMap<>();
    private ConsistencyLevel readConsistency = ConsistencyLevel.QUORUM;
    private ConsistencyLevel writeConsistency = ConsistencyLevel.QUORUM;

    public void setReadConsistency(ConsistencyLevel level) {
        this.readConsistency = level;
    }

    public void setWriteConsistency(ConsistencyLevel level) {
        this.writeConsistency = level;
    }

    public ConsistencyLevel getReadConsistency() {
        return readConsistency;
    }

    public ConsistencyLevel getWriteConsistency() {
        return writeConsistency;
    }

    public void upsert(String partitionKey, long clusteringKey, Map<String, Object> columns) {
        Map<Long, Row> partition = partitions.computeIfAbsent(partitionKey, ignored -> new HashMap<>());
        partition.put(clusteringKey, new Row(partitionKey, clusteringKey, new HashMap<>(columns)));
    }

    public Row get(String partitionKey, long clusteringKey) {
        Map<Long, Row> partition = partitions.get(partitionKey);
        if (partition == null) {
            return null;
        }
        return partition.get(clusteringKey);
    }

    public List<Row> queryPartition(String partitionKey) {
        Map<Long, Row> partition = partitions.get(partitionKey);
        List<Row> results = new ArrayList<>();
        if (partition == null) {
            return results;
        }
        partition.keySet().stream().sorted().forEach(key -> results.add(partition.get(key)));
        return results;
    }

    public List<Row> queryRange(String partitionKey, long fromInclusive, long toInclusive) {
        List<Row> results = new ArrayList<>();
        for (Row row : queryPartition(partitionKey)) {
            if (row.clusteringKey >= fromInclusive && row.clusteringKey <= toInclusive) {
                results.add(row);
            }
        }
        return results;
    }

    public boolean delete(String partitionKey, long clusteringKey) {
        Map<Long, Row> partition = partitions.get(partitionKey);
        if (partition == null) {
            return false;
        }
        return partition.remove(clusteringKey) != null;
    }

    public int partitionSize(String partitionKey) {
        Map<Long, Row> partition = partitions.get(partitionKey);
        return partition == null ? 0 : partition.size();
    }
}
