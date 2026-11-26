
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class SubscriberDAG {
    private final String topicName;
    private final Map<String, Set<String>> dependencies = new ConcurrentHashMap<>();
    private final Map<String, Set<String>> reverseDependencies = new ConcurrentHashMap<>();
    private final ReentrantLock lock = new ReentrantLock();
    
    // MessageId -> (GroupId -> Boolean Ack)
    private final Map<String, Map<String, Boolean>> messageAcks = new ConcurrentHashMap<>();

    public SubscriberDAG(String topicName) {
        this.topicName = topicName;
    }

    public void addDependency(String parentGroup, String childGroup) {
        lock.lock();
        try {
            dependencies.computeIfAbsent(childGroup, k -> new HashSet<>()).add(parentGroup);
            reverseDependencies.computeIfAbsent(parentGroup, k -> new HashSet<>()).add(childGroup);
        } finally {
            lock.unlock();
        }
    }

    public boolean isEligible(String groupId, Message message) {
        lock.lock();
        try {
            Set<String> deps = dependencies.get(groupId);
            if (deps == null || deps.isEmpty()) {
                return true;
            }
            
            String msgId = message.getId();
            Map<String, Boolean> acks = messageAcks.get(msgId);
            if (acks == null) {
                return false;
            }
            
            for (String dep : deps) {
                if (!acks.getOrDefault(dep, false)) {
                    return false;
                }
            }
            return true;
        } finally {
            lock.unlock();
        }
    }

    public void recordAck(String groupId, Message message) {
        lock.lock();
        try {
            messageAcks.computeIfAbsent(message.getId(), k -> new ConcurrentHashMap<>())
                       .put(groupId, true);
        } finally {
            lock.unlock();
        }
    }
}
