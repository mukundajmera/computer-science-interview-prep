import java.util.*;
import java.util.concurrent.locks.*;

class ReplicatedPartition {
    int id;
    Integer leaderId;
    List<Integer> followers;
    Set<Integer> isr = new HashSet<>();
    List<String> log = new ArrayList<>();
    int highWatermark = 0;
    Lock lock = new ReentrantLock();

    ReplicatedPartition(int id, int leaderId, List<Integer> followers) {
        this.id = id;
        this.leaderId = leaderId;
        this.followers = followers;
        this.isr.add(leaderId);
        this.isr.addAll(followers);
    }

    int append(String message, String acks, int minInsyncReplicas) throws Exception {
        lock.lock();
        try {
            if (isr.size() < minInsyncReplicas) {
                throw new Exception("NotEnoughReplicas");
            }
            int offset = log.size();
            log.add(message);

            if ("all".equals(acks)) {
                highWatermark++;
            }
            return offset;
        } finally {
            lock.unlock();
        }
    }

    void failNode(int nodeId) {
        lock.lock();
        try {
            if (isr.contains(nodeId)) {
                isr.remove(nodeId);
                if (leaderId != null && leaderId == nodeId) {
                    electLeader();
                }
            }
        } finally {
            lock.unlock();
        }
    }

    private void electLeader() {
        if (!isr.isEmpty()) {
            leaderId = isr.iterator().next();
        } else {
            leaderId = null;
        }
    }
}
