package kafka_broker_v2;

import java.util.function.LongSupplier;

/**
 * v2 ConsumerGroupCoordinator: injectable clock and lag metrics
 * (improvement #3).
 *
 * Identical range-assignment and offset behavior to v1, but the heartbeat
 * clock is injectable so health checks are deterministic in tests, and
 * consumerLag() reports how far a group's committed offset is behind a
 * partition's log end, the standard consumer-state metric. See
 * BrokerCluster for the full v2 list.
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class ConsumerGroupCoordinator {
    private final long heartbeatTimeoutMs;
    private final LongSupplier clockMillis;
    private final Map<String, Map<String, Long>> members = new ConcurrentHashMap<>();
    private final Map<String, Map<String, String>> assignments = new ConcurrentHashMap<>();
    private final Map<String, List<String>> groupPartitions = new ConcurrentHashMap<>();
    private final Map<String, Map<String, Integer>> committedOffsets = new ConcurrentHashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public ConsumerGroupCoordinator(long heartbeatTimeoutMs) {
        this(heartbeatTimeoutMs, System::currentTimeMillis);
    }

    public ConsumerGroupCoordinator(long heartbeatTimeoutMs, LongSupplier clockMillis) {
        this.heartbeatTimeoutMs = heartbeatTimeoutMs;
        this.clockMillis = clockMillis;
    }

    public void registerGroup(String groupId, List<String> partitions) {
        lock.lock();
        try {
            if (!members.containsKey(groupId)) {
                members.put(groupId, new ConcurrentHashMap<>());
                assignments.put(groupId, new ConcurrentHashMap<>());
                groupPartitions.put(groupId, new ArrayList<>(partitions));
                committedOffsets.put(groupId, new ConcurrentHashMap<>());
            }
        } finally {
            lock.unlock();
        }
    }

    public void joinGroup(String groupId, String memberId) {
        lock.lock();
        try {
            members.computeIfAbsent(groupId, k -> new ConcurrentHashMap<>())
                   .put(memberId, clockMillis.getAsLong());
            rebalance(groupId);
        } finally {
            lock.unlock();
        }
    }

    public void heartbeat(String groupId, String memberId) {
        lock.lock();
        try {
            if (members.containsKey(groupId) && members.get(groupId).containsKey(memberId)) {
                members.get(groupId).put(memberId, clockMillis.getAsLong());
            }
        } finally {
            lock.unlock();
        }
    }

    public void checkHealth() {
        lock.lock();
        try {
            long now = clockMillis.getAsLong();
            for (String groupId : new ArrayList<>(members.keySet())) {
                Map<String, Long> groupMembers = members.get(groupId);
                List<String> deadMembers = new ArrayList<>();
                for (Map.Entry<String, Long> entry : groupMembers.entrySet()) {
                    if (now - entry.getValue() > heartbeatTimeoutMs) {
                        deadMembers.add(entry.getKey());
                    }
                }
                if (!deadMembers.isEmpty()) {
                    for (String memberId : deadMembers) {
                        groupMembers.remove(memberId);
                    }
                    rebalance(groupId);
                }
            }
        } finally {
            lock.unlock();
        }
    }

    private void rebalance(String groupId) {
        Map<String, Long> groupMembers = members.get(groupId);
        if (groupMembers == null) return;
        List<String> memberList = new ArrayList<>(groupMembers.keySet());
        Collections.sort(memberList);

        List<String> partitions = groupPartitions.getOrDefault(groupId, new ArrayList<>());
        Collections.sort(partitions);

        Map<String, String> newAssignment = new ConcurrentHashMap<>();

        if (memberList.isEmpty() || partitions.isEmpty()) {
            assignments.put(groupId, newAssignment);
            return;
        }

        int partitionsPerMember = partitions.size() / memberList.size();
        int extra = partitions.size() % memberList.size();

        int pIdx = 0;
        for (int i = 0; i < memberList.size(); i++) {
            String mId = memberList.get(i);
            int count = partitionsPerMember + (i < extra ? 1 : 0);
            for (int j = 0; j < count; j++) {
                newAssignment.put(partitions.get(pIdx), mId);
                pIdx++;
            }
        }

        assignments.put(groupId, newAssignment);
    }

    public List<String> getAssignment(String groupId, String memberId) {
        lock.lock();
        try {
            Map<String, String> assignment = assignments.getOrDefault(groupId, new HashMap<>());
            List<String> result = new ArrayList<>();
            for (Map.Entry<String, String> entry : assignment.entrySet()) {
                if (entry.getValue().equals(memberId)) {
                    result.add(entry.getKey());
                }
            }
            return result;
        } finally {
            lock.unlock();
        }
    }

    public void commitOffset(String groupId, String partitionId, int offset) {
        lock.lock();
        try {
            committedOffsets.computeIfAbsent(groupId, k -> new ConcurrentHashMap<>())
                    .put(partitionId, offset);
        } finally {
            lock.unlock();
        }
    }

    public int fetchOffset(String groupId, String partitionId) {
        lock.lock();
        try {
            Map<String, Integer> groupOffsets = committedOffsets.get(groupId);
            if (groupOffsets != null) {
                return groupOffsets.getOrDefault(partitionId, 0);
            }
            return 0;
        } finally {
            lock.unlock();
        }
    }

    /**
     * Messages between the group's committed offset and the partition's
     * log end offset: the lag a monitoring dashboard would chart.
     */
    public int consumerLag(String groupId, String partitionId, int logEndOffset) {
        return logEndOffset - fetchOffset(groupId, partitionId);
    }
}
