/**
 * Observer Pattern - V3 Advanced: Topic Event Bus
 */

import java.util.*;

final class Event {
    private final String topic;
    private final Map<String, Object> payload;
    private final Map<String, Object> metadata;

    Event(String topic, Map<String, Object> payload, Map<String, Object> metadata) {
        this.topic = topic;
        this.payload = new HashMap<>(payload);
        this.metadata = new HashMap<>(metadata);
    }

    public String getTopic() { return topic; }
    public Map<String, Object> getPayload() { return Collections.unmodifiableMap(payload); }
    public Map<String, Object> getMetadata() { return Collections.unmodifiableMap(metadata); }
}

interface EventHandler {
    void handle(Event event);
}

class EventBus {
    static final String WILDCARD_TOPIC = "*";

    private final Map<String, List<EventHandler>> subscribers = new HashMap<>();
    private final List<Event> deadLetters = new ArrayList<>();

    public void subscribe(String topic, EventHandler handler) {
        List<EventHandler> handlers = subscribers.computeIfAbsent(topic, key -> new ArrayList<>());
        if (!handlers.contains(handler)) {
            handlers.add(handler);
        }
    }

    public void unsubscribe(String topic, EventHandler handler) {
        List<EventHandler> handlers = subscribers.get(topic);
        if (handlers == null) {
            return;
        }
        handlers.remove(handler);
        if (handlers.isEmpty()) {
            subscribers.remove(topic);
        }
    }

    public Event publish(String topic, Map<String, Object> payload) {
        return publish(topic, payload, Collections.emptyMap());
    }

    public Event publish(String topic, Map<String, Object> payload, Map<String, Object> metadata) {
        Event event = new Event(topic, payload, metadata);
        List<EventHandler> handlers = handlersFor(topic);
        if (handlers.isEmpty()) {
            deadLetters.add(event);
            return event;
        }
        for (EventHandler handler : handlers) {
            handler.handle(event);
        }
        return event;
    }

    public List<Event> getDeadLetters() {
        return Collections.unmodifiableList(deadLetters);
    }

    private List<EventHandler> handlersFor(String topic) {
        List<EventHandler> handlers = new ArrayList<>();
        handlers.addAll(subscribers.getOrDefault(topic, Collections.emptyList()));
        handlers.addAll(subscribers.getOrDefault(WILDCARD_TOPIC, Collections.emptyList()));
        return handlers;
    }
}

public class EventBusDemo {
    public static void main(String[] args) {
        EventBus bus = new EventBus();

        bus.subscribe("order.created", event -> System.out.println("Order: " + event.getPayload().get("id")));
        bus.subscribe("*", event -> System.out.println("Audit topic: " + event.getTopic()));

        bus.publish("order.created", Map.of("id", "ord-100"));
        bus.publish("payment.failed", Map.of("id", "pay-200"));
        System.out.println("Dead letters: " + bus.getDeadLetters().size());
    }
}
