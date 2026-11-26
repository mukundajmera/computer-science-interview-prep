import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v2-realistic: Track active connections and topic subscriptions.
 */
public final class ConnectionRegistry {
    private final Map<String, List<String>> topicToConnections = new ConcurrentHashMap<>();

    public void subscribe(String topic, String connectionId) {
        topicToConnections.compute(topic, (k, current) -> {
            List<String> next = current == null ? new ArrayList<>() : new ArrayList<>(current);
            if (!next.contains(connectionId)) {
                next.add(connectionId);
            }
            return next;
        });
    }

    public void unsubscribe(String topic, String connectionId) {
        topicToConnections.computeIfPresent(topic, (k, current) -> {
            List<String> next = new ArrayList<>(current);
            next.remove(connectionId);
            return next;
        });
    }

    public List<String> connectionsForTopic(String topic) {
        List<String> current = topicToConnections.get(topic);
        if (current == null) {
            return Collections.emptyList();
        }
        return List.copyOf(current);
    }
}
