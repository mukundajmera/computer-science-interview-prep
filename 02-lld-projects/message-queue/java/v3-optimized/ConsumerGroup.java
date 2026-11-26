
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.concurrent.locks.ReentrantLock;

public class ConsumerGroup {
    private final String groupId;
    private final Set<String> consumers = new CopyOnWriteArraySet<>();
    private final ReentrantLock lock = new ReentrantLock();

    // TopicName -> PartitionId -> Object
    private final Map<String, Map<Integer, Integer>> readOffsets = new ConcurrentHashMap<>();
    private final Map<String, Map<Integer, Set<Integer>>> unackedMessages = new ConcurrentHashMap<>();
    private final Map<String, Map<Integer, Set<Integer>>> redeliveryOffsets = new ConcurrentHashMap<>();
    private final Map<String, Map<Integer, Integer>> committedOffsets = new ConcurrentHashMap<>();
    
    // Maintain messages for DAG check
    private final Map<String, Map<Integer, Map<Integer, Message>>> offsetToMessage = new ConcurrentHashMap<>();

    public ConsumerGroup(String groupId) {
        this.groupId = groupId;
    }

    public String getGroupId() { return groupId; }

    public void registerConsumer(String consumerId) {
        consumers.add(consumerId);
    }

    public void deregisterConsumer(String consumerId) {
        consumers.remove(consumerId);
    }

    public static class Assignment {
        public final Topic topic;
        public final Partition partition;
        public Assignment(Topic topic, Partition partition) {
            this.topic = topic;
            this.partition = partition;
        }
    }

    public List<Assignment> getAssignedPartitions(String consumerId, List<Topic> topics) {
        List<String> sortedConsumers = new ArrayList<>(consumers);
        Collections.sort(sortedConsumers);
        
        int idx = sortedConsumers.indexOf(consumerId);
        if (idx == -1) return Collections.emptyList();
        
        int numConsumers = sortedConsumers.size();
        
        List<Assignment> allParts = new ArrayList<>();
        List<Topic> sortedTopics = new ArrayList<>(topics);
        sortedTopics.sort(Comparator.comparing(Topic::getName));
        
        for (Topic t : sortedTopics) {
            List<Partition> sortedPartitions = new ArrayList<>(t.getPartitions());
            sortedPartitions.sort(Comparator.comparing(Partition::getId));
            for (Partition p : sortedPartitions) {
                allParts.add(new Assignment(t, p));
            }
        }
        
        List<Assignment> assigned = new ArrayList<>();
        for (int i = 0; i < allParts.size(); i++) {
            if (i % numConsumers == idx) {
                assigned.add(allParts.get(i));
            }
        }
        return assigned;
    }

    public static class ReadResult {
        public final Message message;
        public final int offset;
        public ReadResult(Message message, int offset) {
            this.message = message;
            this.offset = offset;
        }
    }

    public ReadResult readMessage(Topic topic, Partition partition, SubscriberDAG dag) {
        lock.lock();
        try {
            String tName = topic.getName();
            int pId = partition.getId();

            readOffsets.putIfAbsent(tName, new ConcurrentHashMap<>());
            unackedMessages.putIfAbsent(tName, new ConcurrentHashMap<>());
            redeliveryOffsets.putIfAbsent(tName, new ConcurrentHashMap<>());
            committedOffsets.putIfAbsent(tName, new ConcurrentHashMap<>());
            offsetToMessage.putIfAbsent(tName, new ConcurrentHashMap<>());

            readOffsets.get(tName).putIfAbsent(pId, 0);
            unackedMessages.get(tName).putIfAbsent(pId, new HashSet<>());
            redeliveryOffsets.get(tName).putIfAbsent(pId, new TreeSet<>());
            committedOffsets.get(tName).putIfAbsent(pId, 0);
            offsetToMessage.get(tName).putIfAbsent(pId, new ConcurrentHashMap<>());

            Set<Integer> redeliveries = redeliveryOffsets.get(tName).get(pId);
            if (!redeliveries.isEmpty()) {
                List<Integer> redeliverList = new ArrayList<>(redeliveries);
                Collections.sort(redeliverList);
                for (int offset : redeliverList) {
                    Message msg = offsetToMessage.get(tName).get(pId).get(offset);
                    if (msg == null) {
                        msg = partition.read(offset);
                        if (msg != null) {
                            offsetToMessage.get(tName).get(pId).put(offset, msg);
                        }
                    }
                    if (msg != null) {
                        if (dag == null || dag.isEligible(groupId, msg)) {
                            redeliveries.remove(offset);
                            unackedMessages.get(tName).get(pId).add(offset);
                            return new ReadResult(msg, offset);
                        }
                    }
                }
            }

            int offset = readOffsets.get(tName).get(pId);
            while (true) {
                Message msg = partition.read(offset);
                if (msg == null) {
                    break;
                }
                offsetToMessage.get(tName).get(pId).put(offset, msg);
                
                if (dag == null || dag.isEligible(groupId, msg)) {
                    unackedMessages.get(tName).get(pId).add(offset);
                    readOffsets.get(tName).put(pId, offset + 1);
                    return new ReadResult(msg, offset);
                } else {
                    break; // stop reading forward if blocked
                }
            }
            
            return null;
        } finally {
            lock.unlock();
        }
    }

    public void ack(String topicName, int partitionId, int offset, SubscriberDAG dag) {
        lock.lock();
        try {
            if (unackedMessages.containsKey(topicName) && unackedMessages.get(topicName).containsKey(partitionId)) {
                unackedMessages.get(topicName).get(partitionId).remove(offset);
                
                Set<Integer> unacked = unackedMessages.get(topicName).get(partitionId);
                int readOff = readOffsets.get(topicName).get(partitionId);
                if (unacked.isEmpty()) {
                    committedOffsets.get(topicName).put(partitionId, readOff);
                } else {
                    int minUnacked = Collections.min(unacked);
                    committedOffsets.get(topicName).put(partitionId, minUnacked);
                }
                
                if (dag != null && offsetToMessage.containsKey(topicName) && offsetToMessage.get(topicName).containsKey(partitionId)) {
                    Message msg = offsetToMessage.get(topicName).get(partitionId).get(offset);
                    if (msg != null) {
                        dag.recordAck(groupId, msg);
                    }
                }
            }
        } finally {
            lock.unlock();
        }
    }

    public void nack(String topicName, int partitionId, int offset) {
        lock.lock();
        try {
            if (unackedMessages.containsKey(topicName) && unackedMessages.get(topicName).containsKey(partitionId)) {
                if (unackedMessages.get(topicName).get(partitionId).contains(offset)) {
                    unackedMessages.get(topicName).get(partitionId).remove(offset);
                    redeliveryOffsets.get(topicName).get(partitionId).add(offset);
                }
            }
        } finally {
            lock.unlock();
        }
    }
}
