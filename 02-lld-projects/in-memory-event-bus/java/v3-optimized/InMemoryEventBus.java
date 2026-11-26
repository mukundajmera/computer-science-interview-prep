package v3_optimized;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.function.Consumer;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class InMemoryEventBus {

    public static class Partition {
        private final int id;
        private final List<Object> events = new ArrayList<>();
        private final ReadWriteLock lock = new ReentrantReadWriteLock();

        public Partition(int id) { this.id = id; }
        public int getId() { return id; }

        public int append(Object event) {
            lock.writeLock().lock();
            try {
                events.add(event);
                return events.size() - 1;
            } finally { lock.writeLock().unlock(); }
        }

        public Object read(int offset) {
            lock.readLock().lock();
            try {
                if (offset < events.size()) return events.get(offset);
                return null;
            } finally { lock.readLock().unlock(); }
        }

        public int size() {
            lock.readLock().lock();
            try {
                return events.size();
            } finally { lock.readLock().unlock(); }
        }
    }

    public static class Topic {
        private final String name;
        private final List<Partition> partitions;

        public Topic(String name, int numPartitions) {
            this.name = name;
            this.partitions = new ArrayList<>(numPartitions);
            for (int i = 0; i < numPartitions; i++) this.partitions.add(new Partition(i));
        }
        
        public String getName() { return name; }
        public List<Partition> getPartitions() { return partitions; }

        public int publish(Object event, int partitionKey) {
            int idx = Math.abs(partitionKey) % partitions.size();
            return partitions.get(idx).append(event);
        }
    }

    public enum QueuePolicy { BLOCK, DROP, REJECT }
    
    private static class Subscriber {
        Consumer<Object> handler;
        BlockingQueue<Object> queue;
        QueuePolicy policy;
        Thread worker;
        volatile boolean active = true;
        
        Subscriber(Consumer<Object> handler, int capacity, QueuePolicy policy) {
            this.handler = handler;
            this.queue = new ArrayBlockingQueue<>(capacity);
            this.policy = policy;
            this.worker = new Thread(() -> {
                while (active || !queue.isEmpty()) {
                    try {
                        Object event = queue.poll(100, java.util.concurrent.TimeUnit.MILLISECONDS);
                        if (event != null) handler.accept(event);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    } catch (Exception e) {}
                }
            });
            this.worker.start();
        }
        
        void push(Object event) {
            if (!active) return;
            switch(policy) {
                case BLOCK:
                    try { queue.put(event); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                    break;
                case DROP: queue.offer(event); break;
                case REJECT: if (!queue.offer(event)) throw new RuntimeException("Queue is full"); break;
            }
        }
        
        void shutdown() {
            active = false;
            try { worker.join(2000); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        }
    }

    private final Map<String, Topic> topics = new ConcurrentHashMap<>();
    private final Map<String, Map<String, Map<Integer, Integer>>> offsets = new ConcurrentHashMap<>();
    private final Map<String, List<Subscriber>> subscribers = new ConcurrentHashMap<>();
    private final Map<String, List<Object>> retryQueues = new ConcurrentHashMap<>();
    private final Map<String, List<Object>> dlq = new ConcurrentHashMap<>();
    private final Map<String, Map<Object, Integer>> retryCounts = new ConcurrentHashMap<>();

    public void createTopic(String name, int numPartitions) {
        topics.putIfAbsent(name, new Topic(name, numPartitions));
        subscribers.putIfAbsent(name, new CopyOnWriteArrayList<>());
    }

    public void publish(String topicName, Object event, int partitionKey) {
        Topic topic = topics.computeIfAbsent(topicName, k -> new Topic(topicName, 1));
        topic.publish(event, partitionKey);
        List<Subscriber> subs = subscribers.getOrDefault(topicName, new ArrayList<>());
        for (Subscriber sub : subs) sub.push(event);
    }

    public synchronized void subscribe(String topicName, Consumer<Object> handler, int capacity, QueuePolicy policy) {
        subscribers.computeIfAbsent(topicName, k -> new CopyOnWriteArrayList<>()).add(new Subscriber(handler, capacity, policy));
    }
    
    public synchronized void unsubscribeAll() {
        for (List<Subscriber> subs : subscribers.values()) {
            for (Subscriber sub : subs) sub.shutdown();
        }
        subscribers.clear();
    }

    public void subscribe(String group, String topicName) {
        offsets.putIfAbsent(group, new ConcurrentHashMap<>());
        Map<String, Map<Integer, Integer>> groupOffsets = offsets.get(group);
        groupOffsets.putIfAbsent(topicName, new ConcurrentHashMap<>());
        
        Topic topic = topics.get(topicName);
        if (topic != null) {
            Map<Integer, Integer> topicOffsets = groupOffsets.get(topicName);
            for (Partition p : topic.getPartitions()) topicOffsets.putIfAbsent(p.getId(), 0);
        }
    }

    public Object poll(String group, String topicName, int partitionId) {
        String key = group + "_" + topicName;
        List<Object> retries = retryQueues.get(key);
        if (retries != null && !retries.isEmpty()) {
            synchronized (retries) {
                if (!retries.isEmpty()) {
                    return retries.remove(0);
                }
            }
        }

        Map<String, Map<Integer, Integer>> groupOffsets = offsets.get(group);
        if (groupOffsets == null) return null;
        Map<Integer, Integer> topicOffsets = groupOffsets.get(topicName);
        if (topicOffsets == null) return null;
        Topic topic = topics.get(topicName);
        if (topic == null) return null;
        
        int offset = topicOffsets.getOrDefault(partitionId, 0);
        return topic.getPartitions().get(partitionId).read(offset);
    }

    public void commitOffset(String group, String topicName, int partitionId, int offset) {
        Map<String, Map<Integer, Integer>> groupOffsets = offsets.get(group);
        if (groupOffsets != null) {
            Map<Integer, Integer> topicOffsets = groupOffsets.get(topicName);
            if (topicOffsets != null) topicOffsets.merge(partitionId, offset, Math::max);
        }
    }

    public void failEvent(String group, String topicName, Object msg) {
        String key = group + "_" + topicName;
        retryCounts.putIfAbsent(key, new ConcurrentHashMap<>());
        int count = retryCounts.get(key).merge(msg, 1, Integer::sum);
        if (count > 3) {
            dlq.computeIfAbsent(key, k -> new CopyOnWriteArrayList<>()).add(msg);
            List<Object> retries = retryQueues.get(key);
            if (retries != null) {
                synchronized (retries) {
                    retries.remove(msg);
                }
            }
        } else {
            retryQueues.computeIfAbsent(key, k -> new CopyOnWriteArrayList<>()).add(msg);
        }
    }

    public Map<String, List<Object>> getDlq() {
        return dlq;
    }

    public Map<String, Topic> getTopics() {
        return topics;
    }
}
