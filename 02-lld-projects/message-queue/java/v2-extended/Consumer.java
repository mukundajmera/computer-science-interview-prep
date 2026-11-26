
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class Consumer {
    private final String id;
    private final MessageQueueBroker broker;
    private final ConsumerGroup group;
    private final String topicRegex;

    private static class InFlight {
        public final String topicName;
        public final int partitionId;
        public final int offset;
        public InFlight(String topicName, int partitionId, int offset) {
            this.topicName = topicName;
            this.partitionId = partitionId;
            this.offset = offset;
        }
    }

    private final Map<String, InFlight> inFlight = new ConcurrentHashMap<>();

    public Consumer(MessageQueueBroker broker, String groupId, String topicRegex) {
        this.id = UUID.randomUUID().toString();
        this.broker = broker;
        this.group = broker.getOrCreateConsumerGroup(groupId);
        this.topicRegex = topicRegex;
        this.group.registerConsumer(this.id);
    }

    public List<Message> poll() {
        List<Message> messages = new ArrayList<>();
        List<Topic> topics = broker.getTopicsMatching(topicRegex);
        List<ConsumerGroup.Assignment> assigned = group.getAssignedPartitions(id, topics);
        
        for (ConsumerGroup.Assignment assignment : assigned) {
            ConsumerGroup.ReadResult result = group.readMessage(assignment.topic, assignment.partition);
            if (result != null) {
                inFlight.put(result.message.getId(), new InFlight(assignment.topic.getName(), assignment.partition.getId(), result.offset));
                messages.add(result.message);
            }
        }
        return messages;
    }

    public void ack(Message message) {
        InFlight info = inFlight.remove(message.getId());
        if (info != null) {
            group.ack(info.topicName, info.partitionId, info.offset);
        }
    }

    public void nack(Message message) {
        InFlight info = inFlight.remove(message.getId());
        if (info != null) {
            group.nack(info.topicName, info.partitionId, info.offset);
        }
    }

    public void close() {
        group.deregisterConsumer(id);
    }
    
    // Retained for backward compatibility
    public List<Message> pollAndCommit() {
        List<Message> messages = poll();
        for (Message msg : messages) {
            ack(msg);
        }
        return messages;
    }
}
