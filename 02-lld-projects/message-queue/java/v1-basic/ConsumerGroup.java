import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class ConsumerGroup {
    private final String groupId;
    // Map of topic name to partition offsets
    // Map<TopicName, Map<PartitionId, Offset>>
    private final Map<String, Map<Integer, AtomicInteger>> offsets;

    public ConsumerGroup(String groupId) {
        this.groupId = groupId;
        this.offsets = new ConcurrentHashMap<>();
    }

    public String getGroupId() { return groupId; }

    public int getOffset(String topicName, int partitionId) {
        offsets.putIfAbsent(topicName, new ConcurrentHashMap<>());
        offsets.get(topicName).putIfAbsent(partitionId, new AtomicInteger(0));
        return offsets.get(topicName).get(partitionId).get();
    }

    public void commitOffset(String topicName, int partitionId, int newOffset) {
        offsets.putIfAbsent(topicName, new ConcurrentHashMap<>());
        offsets.get(topicName).putIfAbsent(partitionId, new AtomicInteger(0));
        AtomicInteger current = offsets.get(topicName).get(partitionId);
        // Simple monotonically increasing offset commit
        int currentVal;
        do {
            currentVal = current.get();
            if (newOffset <= currentVal) break;
        } while (!current.compareAndSet(currentVal, newOffset));
    }
}
