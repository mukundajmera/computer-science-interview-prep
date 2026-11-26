// Run with: javac *.java && java -ea Demo

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * v3-production: Coordinate push fanout with replay cursor tracking.
 */
public final class RealtimeUpdateCoordinator {
    public interface PushAdapter {
        void push(String connectionId, String payload) throws Exception;
    }

    private static class Message {
        long offset;
        String payload;
        Message(long offset, String payload) {
            this.offset = offset;
            this.payload = payload;
        }
    }

    private final ConnectionRegistry registry;
    private final PushAdapter pushAdapter;
    private final ConcurrentMap<String, Long> lastDeliveredOffsetByConnection = new ConcurrentHashMap<>();
    
    // Topic -> List of (offset, payload)
    private final ConcurrentMap<String, List<Message>> replayBuffer = new ConcurrentHashMap<>();
    private final int maxBufferSize = 100;
    
    private final Set<String> slowConsumers = ConcurrentHashMap.newKeySet();

    public RealtimeUpdateCoordinator(ConnectionRegistry registry, PushAdapter pushAdapter) {
        this.registry = registry;
        this.pushAdapter = pushAdapter;
    }

    public void publish(String topic, String payload, long eventOffset) {
        replayBuffer.compute(topic, (k, current) -> {
            List<Message> next = current == null ? new ArrayList<>() : new ArrayList<>(current);
            next.add(new Message(eventOffset, payload));
            if (next.size() > maxBufferSize) {
                next.remove(0);
            }
            return next;
        });

        List<String> connections = registry.connectionsForTopic(topic);
        for (String connectionId : connections) {
            if (slowConsumers.contains(connectionId)) continue;
            
            Long lastOffset = lastDeliveredOffsetByConnection.get(connectionId);
            if (lastOffset == null || eventOffset > lastOffset) {
                try {
                    pushAdapter.push(connectionId, payload);
                    lastDeliveredOffsetByConnection.put(connectionId, eventOffset);
                } catch (Exception e) {
                    if ("SlowConsumer".equals(e.getMessage())) {
                        disconnectSlowConsumer(connectionId);
                    }
                }
            }
        }
    }

    public void resumeFrom(String connectionId, long lastClientOffset, String topic) {
        if (slowConsumers.contains(connectionId)) {
            slowConsumers.remove(connectionId);
        }
        
        registry.subscribe(topic, connectionId);
        
        List<Message> messages = replayBuffer.get(topic);
        if (messages != null) {
            for (Message msg : messages) {
                if (msg.offset > lastClientOffset) {
                    try {
                        pushAdapter.push(connectionId, msg.payload);
                        lastDeliveredOffsetByConnection.put(connectionId, msg.offset);
                    } catch (Exception e) {
                        if ("SlowConsumer".equals(e.getMessage())) {
                            disconnectSlowConsumer(connectionId);
                            break;
                        }
                    }
                }
            }
        } else {
            lastDeliveredOffsetByConnection.put(connectionId, lastClientOffset);
        }
    }
    
    public void disconnectSlowConsumer(String connectionId) {
        slowConsumers.add(connectionId);
    }
}

/**
 * Embedded ConnectionRegistry from v2-realistic to make v3 self-contained.
 */
final class ConnectionRegistry {
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

/**
 * Embedded Demo mirroring python/v3-production/distributed_realtime_router.py
 */
class Demo {
    public static void main(String[] args) {
        testBasic();
        testResume();
        testSlowConsumer();
        System.out.println("Demo passed successfully.");
    }
    
    private static void testBasic() {
        ConnectionRegistry registry = new ConnectionRegistry();
        
        List<String> delivered = new ArrayList<>();
        RealtimeUpdateCoordinator.PushAdapter adapter = (connId, payload) -> {
            delivered.add(connId + ":" + payload);
        };
        
        RealtimeUpdateCoordinator coordinator = new RealtimeUpdateCoordinator(registry, adapter);
        
        registry.subscribe("news", "conn1");
        registry.subscribe("news", "conn2");
        
        coordinator.publish("news", "msg1", 100);
        
        if (delivered.size() != 2) throw new AssertionError("Expected 2 deliveries, got " + delivered.size());
        
        coordinator.publish("news", "msg2", 50); // should not be delivered
        
        if (delivered.size() != 2) throw new AssertionError("Expected 2 deliveries after older offset, got " + delivered.size());
        
        coordinator.publish("news", "msg3", 101);
        
        if (delivered.size() != 4) throw new AssertionError("Expected 4 deliveries, got " + delivered.size());
    }
    
    private static void testResume() {
        ConnectionRegistry registry = new ConnectionRegistry();
        
        List<String> delivered = new ArrayList<>();
        RealtimeUpdateCoordinator.PushAdapter adapter = (connId, payload) -> {
            delivered.add(connId + ":" + payload);
        };
        
        RealtimeUpdateCoordinator coordinator = new RealtimeUpdateCoordinator(registry, adapter);
        
        coordinator.publish("news", "msg1", 1);
        coordinator.publish("news", "msg2", 2);
        coordinator.publish("news", "msg3", 3);
        
        coordinator.resumeFrom("conn1", 1, "news");
        
        if (delivered.size() != 2) throw new AssertionError("Expected 2 deliveries on resume, got " + delivered.size());
        if (!delivered.get(0).equals("conn1:msg2")) throw new AssertionError("Expected msg2");
        if (!delivered.get(1).equals("conn1:msg3")) throw new AssertionError("Expected msg3");
        
        coordinator.publish("news", "msg4", 4);
        if (delivered.size() != 3) throw new AssertionError("Expected 3 deliveries total, got " + delivered.size());
    }
    
    private static void testSlowConsumer() {
        ConnectionRegistry registry = new ConnectionRegistry();
        registry.subscribe("news", "conn1");
        
        List<String> delivered = new ArrayList<>();
        class SlowAdapter implements RealtimeUpdateCoordinator.PushAdapter {
            boolean fail = true;
            @Override
            public void push(String connId, String payload) throws Exception {
                if (fail && payload.equals("msg2")) {
                    throw new Exception("SlowConsumer");
                }
                delivered.add(connId + ":" + payload);
            }
        }
        
        SlowAdapter adapter = new SlowAdapter();
        RealtimeUpdateCoordinator coordinator = new RealtimeUpdateCoordinator(registry, adapter);
        
        coordinator.publish("news", "msg1", 1);
        if (delivered.size() != 1) throw new AssertionError("Expected 1 delivery");
        
        coordinator.publish("news", "msg2", 2); // fail
        if (delivered.size() != 1) throw new AssertionError("Expected still 1 delivery");
        
        coordinator.publish("news", "msg3", 3); // skipped
        if (delivered.size() != 1) throw new AssertionError("Expected still 1 delivery");
        
        adapter.fail = false;
        delivered.clear();
        
        coordinator.resumeFrom("conn1", 1, "news");
        if (delivered.size() != 2) throw new AssertionError("Expected 2 deliveries on resume");
        if (!delivered.get(0).equals("conn1:msg2")) throw new AssertionError("Expected msg2");
        if (!delivered.get(1).equals("conn1:msg3")) throw new AssertionError("Expected msg3");
    }
}
