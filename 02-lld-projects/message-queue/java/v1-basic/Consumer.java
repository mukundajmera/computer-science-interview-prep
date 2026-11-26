import java.util.ArrayList;
import java.util.List;

public class Consumer {
    private final MessageQueueBroker broker;
    private final ConsumerGroup group;
    private final String topicRegex;

    public Consumer(MessageQueueBroker broker, String groupId, String topicRegex) {
        this.broker = broker;
        this.group = broker.getOrCreateConsumerGroup(groupId);
        this.topicRegex = topicRegex;
    }

    public List<Message> poll() {
        List<Message> messages = new ArrayList<>();
        List<Topic> topics = broker.getTopicsMatching(topicRegex);
        for (Topic topic : topics) {
            for (Partition partition : topic.getPartitions()) {
                int offset = group.getOffset(topic.getName(), partition.getId());
                Message msg = partition.read(offset);
                if (msg != null) {
                    messages.add(msg);
                    // At-most-once semantics logic or at-least-once.
                    // For demo, we just increment. Proper implementation commits after processing.
                    // Let's not commit here automatically, provide a commit method.
                }
            }
        }
        return messages;
    }
    
    // Polls 1 message per topic-partition and auto-increments for the simple case
    public List<Message> pollAndCommit() {
        List<Message> messages = new ArrayList<>();
        List<Topic> topics = broker.getTopicsMatching(topicRegex);
        for (Topic topic : topics) {
            for (Partition partition : topic.getPartitions()) {
                int offset = group.getOffset(topic.getName(), partition.getId());
                Message msg = partition.read(offset);
                if (msg != null) {
                    messages.add(msg);
                    group.commitOffset(topic.getName(), partition.getId(), offset + 1);
                }
            }
        }
        return messages;
    }

    public void commit(String topicName, int partitionId, int newOffset) {
        group.commitOffset(topicName, partitionId, newOffset);
    }
}
