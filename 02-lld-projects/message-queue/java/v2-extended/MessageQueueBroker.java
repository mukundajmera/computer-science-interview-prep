
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;

public class MessageQueueBroker {
    private final Map<String, Topic> topics;
    private final Map<String, ConsumerGroup> consumerGroups;

    public MessageQueueBroker() {
        this.topics = new ConcurrentHashMap<>();
        this.consumerGroups = new ConcurrentHashMap<>();
    }

    public void createTopic(String name, int partitions) {
        topics.putIfAbsent(name, new Topic(name, partitions));
    }

    public Topic getTopic(String name) {
        return topics.get(name);
    }

    public List<Topic> getTopicsMatching(String regex) {
        List<Topic> matched = new ArrayList<>();
        Pattern pattern = Pattern.compile(regex);
        for (String topicName : topics.keySet()) {
            if (pattern.matcher(topicName).matches()) {
                matched.add(topics.get(topicName));
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
}
