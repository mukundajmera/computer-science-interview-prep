import java.util.*;
import java.util.concurrent.*;

public class PubSubQueue<T> {

    public static class Message<T> {
        public final String id;
        public final T payload;
        public final long createdAt;
        public int deliveryCount;

        public Message(T payload) {
            this.id = UUID.randomUUID().toString();
            this.payload = payload;
            this.createdAt = System.currentTimeMillis();
            this.deliveryCount = 0;
        }

        private Message(Message<T> other) {
            this.id = other.id;
            this.payload = other.payload;
            this.createdAt = other.createdAt;
            this.deliveryCount = other.deliveryCount;
        }

        public Message<T> copy() {
            return new Message<>(this);
        }
    }

    public static class InFlightRecord<T> {
        public final Message<T> message;
        public final long invisibleUntil;

        public InFlightRecord(Message<T> message, long invisibleUntil) {
            this.message = message;
            this.invisibleUntil = invisibleUntil;
        }
    }

    public static class ConsumerGroup<T> {
        private final String name;
        private final long visibilityTimeoutMs;
        private final int maxDeliveries;
        
        private final LinkedList<Message<T>> messages = new LinkedList<>();
        private final Map<String, InFlightRecord<T>> inFlight = new HashMap<>();
        private final List<Message<T>> deadLetterQueue = new ArrayList<>();

        public ConsumerGroup(String name, long visibilityTimeoutMs, int maxDeliveries) {
            this.name = name;
            this.visibilityTimeoutMs = visibilityTimeoutMs;
            this.maxDeliveries = maxDeliveries;
        }

        public synchronized void push(Message<T> message) {
            messages.add(message);
        }

        public synchronized Message<T> pull() {
            long now = System.currentTimeMillis();
            
            // 1. Check for expired inflight messages (redelivery)
            List<String> expiredIds = new ArrayList<>();
            for (Map.Entry<String, InFlightRecord<T>> entry : inFlight.entrySet()) {
                if (now > entry.getValue().invisibleUntil) {
                    expiredIds.add(entry.getKey());
                }
            }
            
            for (String msgId : expiredIds) {
                InFlightRecord<T> record = inFlight.remove(msgId);
                messages.add(record.message);
            }

            // 2. Get a new message if available
            if (messages.isEmpty()) {
                return null;
            }
            
            Message<T> msg = messages.poll();
            msg.deliveryCount++;
            
            if (msg.deliveryCount >= maxDeliveries) {
                deadLetterQueue.add(msg);
                return null; // Sent to DLQ
            }
            
            inFlight.put(msg.id, new InFlightRecord<>(msg, now + visibilityTimeoutMs));
            return msg;
        }

        public synchronized boolean ack(String msgId) {
            return inFlight.remove(msgId) != null;
        }

        public synchronized List<Message<T>> getDlq() {
            return new ArrayList<>(deadLetterQueue);
        }
    }

    private final Map<String, Map<String, ConsumerGroup<T>>> topics = new HashMap<>();

    public synchronized void createTopic(String topic) {
        topics.putIfAbsent(topic, new HashMap<>());
    }

    public synchronized void subscribe(String topic, String groupName, long visibilityTimeoutMs, int maxDeliveries) {
        topics.putIfAbsent(topic, new HashMap<>());
        Map<String, ConsumerGroup<T>> groups = topics.get(topic);
        groups.putIfAbsent(groupName, new ConsumerGroup<>(groupName, visibilityTimeoutMs, maxDeliveries));
    }

    public synchronized int publish(String topic, T payload) {
        Map<String, ConsumerGroup<T>> groups = topics.get(topic);
        if (groups == null) {
            return 0;
        }
        for (ConsumerGroup<T> group : groups.values()) {
            group.push(new Message<>(payload));
        }
        return groups.size();
    }

    public synchronized Message<T> pull(String topic, String groupName) {
        Map<String, ConsumerGroup<T>> groups = topics.get(topic);
        if (groups != null) {
            ConsumerGroup<T> group = groups.get(groupName);
            if (group != null) {
                return group.pull();
            }
        }
        return null;
    }

    public synchronized boolean ack(String topic, String groupName, String msgId) {
        Map<String, ConsumerGroup<T>> groups = topics.get(topic);
        if (groups != null) {
            ConsumerGroup<T> group = groups.get(groupName);
            if (group != null) {
                return group.ack(msgId);
            }
        }
        return false;
    }

    public synchronized List<Message<T>> getDlq(String topic, String groupName) {
        Map<String, ConsumerGroup<T>> groups = topics.get(topic);
        if (groups != null) {
            ConsumerGroup<T> group = groups.get(groupName);
            if (group != null) {
                return group.getDlq();
            }
        }
        return Collections.emptyList();
    }
}