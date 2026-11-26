package v3_optimized;

public class PartitionRouter {
    private final int numPartitions;

    public PartitionRouter(int numPartitions) {
        this.numPartitions = numPartitions;
    }

    public int getPartition(String key) {
        return (key.hashCode() & 0x7fffffff) % numPartitions;
    }
}
