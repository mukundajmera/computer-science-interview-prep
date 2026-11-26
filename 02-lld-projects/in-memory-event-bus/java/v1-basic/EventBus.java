
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Consumer;

public class EventBus {
    private final Map<String, List<Object>> topics = new ConcurrentHashMap<>();
    private final Map<String, List<Consumer<Object>>> subscribers = new ConcurrentHashMap<>();

    public void createTopic(String topic) {
        topics.putIfAbsent(topic, new CopyOnWriteArrayList<>());
        subscribers.putIfAbsent(topic, new CopyOnWriteArrayList<>());
    }

    public void publish(String topic, Object event) {
        topics.computeIfAbsent(topic, k -> new CopyOnWriteArrayList<>()).add(event);
        List<Consumer<Object>> subs = subscribers.getOrDefault(topic, new ArrayList<>());
        for (Consumer<Object> sub : subs) {
            sub.accept(event);
        }
    }

    public void subscribe(String topic, Consumer<Object> callback) {
        subscribers.computeIfAbsent(topic, k -> new CopyOnWriteArrayList<>()).add(callback);
    }
}
