import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;

/**
 * Interview-scale topic model with per-partition queues and offsets.
 */
public class SimpleProducerConsumer {
    private final Map<Integer, Queue<String>> partitions = new HashMap<>();
    private final Map<Integer, Long> offsets = new HashMap<>();

    public SimpleProducerConsumer(int partitionCount) {
        if (partitionCount <= 0) {
            throw new IllegalArgumentException("partitionCount must be > 0");
        }
        for (int i = 0; i < partitionCount; i++) {
            partitions.put(i, new ArrayDeque<>());
            offsets.put(i, 0L);
        }
    }

    public int partitionForKey(String key) {
        return Math.floorMod(key.hashCode(), partitions.size());
    }

    public void produce(String key, String message) {
        int partition = partitionForKey(key);
        partitions.get(partition).add(message);
    }

    public String consume(int partition) {
        Queue<String> queue = partitions.get(partition);
        if (queue == null || queue.isEmpty()) {
            return null;
        }
        offsets.put(partition, offsets.get(partition) + 1);
        return queue.poll();
    }

    public long currentOffset(int partition) {
        return offsets.getOrDefault(partition, 0L);
    }

    public static void main(String[] args) {
        SimpleProducerConsumer stream = new SimpleProducerConsumer(3);
        stream.produce("order-1001", "order-created");
        int partition = stream.partitionForKey("order-1001");
        System.out.println("partition -> " + partition);
        System.out.println("consume -> " + stream.consume(partition));
        System.out.println("offset -> " + stream.currentOffset(partition));
    }
}
