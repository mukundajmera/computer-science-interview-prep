
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;

public class MessageQueueBroker {
    private final Map<String, Topic> topics;
    private final Map<String, ConsumerGroup> consumerGroups;
    private final Map<String, SubscriberDAG> dags;

    public MessageQueueBroker() {
        this.topics = new ConcurrentHashMap<>();
        this.consumerGroups = new ConcurrentHashMap<>();
        this.dags = new ConcurrentHashMap<>();
    }

    public void createTopic(String name, int partitions) {
        if (!topics.containsKey(name)) {
            topics.put(name, new Topic(name, partitions));
            dags.put(name, new SubscriberDAG(name));
        }
    }

    public Topic getTopic(String name) {
        return topics.get(name);
    }

    public List<Topic> getTopicsMatching(String regex) {
        List<Topic> matched = new ArrayList<>();
        Pattern pattern = Pattern.compile(regex);
        for (Map.Entry<String, Topic> entry : topics.entrySet()) {
            if (pattern.matcher(entry.getKey()).matches()) {
                matched.add(entry.getValue());
            }
        }
        return matched;
    }

    public void publish(String topicName, Message message) {
        Topic topic = topics.get(topicName);
        if (topic != null) {
            topic.publish(message);
        } else {
            throw new IllegalArgumentException("Topic does not exist: " + topicName);
        }
    }

    public ConsumerGroup getOrCreateConsumerGroup(String groupId) {
        return consumerGroups.computeIfAbsent(groupId, ConsumerGroup::new);
    }
    
    public SubscriberDAG getDag(String topicName) {
        return dags.get(topicName);
    }
}
