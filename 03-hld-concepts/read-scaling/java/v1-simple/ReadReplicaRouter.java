package v1_simple;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ReadReplicaRouter {
    private final String primary;
    private final List<Replica> replicas;
    private final long maxLagMs;
    private final Map<String, Long> userLastWrite;
    private final AtomicInteger rrIndex = new AtomicInteger(0);
    private long mockTimeMs = -1;

    public static class Replica {
        private final String id;
        private volatile boolean healthy = true;
        private volatile long lagMs = 0;

        public Replica(String id) {
            this.id = id;
        }

        public String getId() { return id; }
        public boolean isHealthy() { return healthy; }
        public void setHealthy(boolean healthy) { this.healthy = healthy; }
        public long getLagMs() { return lagMs; }
        public void setLagMs(long lagMs) { this.lagMs = lagMs; }
    }

    public ReadReplicaRouter(String primary, List<String> replicaIds, long maxLagMs) {
        this.primary = primary;
        this.replicas = new CopyOnWriteArrayList<>();
        for (String id : replicaIds) {
            this.replicas.add(new Replica(id));
        }
        this.maxLagMs = maxLagMs;
        this.userLastWrite = new ConcurrentHashMap<>();
    }

    protected long now() {
        return mockTimeMs != -1 ? mockTimeMs : System.currentTimeMillis();
    }

    public void setMockTime(long mockTimeMs) {
        this.mockTimeMs = mockTimeMs;
    }

    public String routeWrite(String userId) {
        userLastWrite.put(userId, now());
        return primary;
    }

    public String routeRead(String userId) {
        long now = now();
        Long lastWrite = userLastWrite.get(userId);

        List<Replica> eligible = new ArrayList<>();
        for (Replica r : replicas) {
            if (!r.isHealthy()) {
                continue;
            }
            if (r.getLagMs() > maxLagMs) {
                continue;
            }
            // Read-your-own-writes: if user wrote recently, we need a replica
            // that is fresh enough to have seen the write.
            // We ensure lag is strictly less than elapsed time since write.
            if (lastWrite != null) {
                long elapsed = now - lastWrite;
                if (r.getLagMs() >= elapsed) {
                    continue;
                }
            }
            eligible.add(r);
        }

        // Fallback to primary if no eligible replicas (or if maxLagMs threshold or RYOW forces it)
        if (eligible.isEmpty()) {
            return primary;
        }

        int index = Math.abs(rrIndex.getAndIncrement()) % eligible.size();
        return eligible.get(index).getId();
    }

    public void updateReplicaHealth(String id, boolean healthy) {
        for (Replica r : replicas) {
            if (r.getId().equals(id)) {
                r.setHealthy(healthy);
                break;
            }
        }
    }

    public void updateReplicaLag(String id, long lagMs) {
        for (Replica r : replicas) {
            if (r.getId().equals(id)) {
                r.setLagMs(lagMs);
                break;
            }
        }
    }

    public List<Replica> getReplicas() {
        return Collections.unmodifiableList(replicas);
    }
}
