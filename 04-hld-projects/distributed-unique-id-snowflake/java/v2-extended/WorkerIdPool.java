package v2_extended;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Dynamic worker-ID lease pool (v2 improvement #2).
 *
 * Simulates the ZooKeeper ephemeral sequential node lease design from
 * FOLLOW-UPS.md #3: a node claims an available worker ID at startup, the ID
 * stays leased while the node lives, and releasing it (session expiry in
 * the real design) returns the ID to the available pool so a replacement
 * node can pick it up. Acquisition is collision-proof by construction and
 * exhaustion is loud instead of a silent collision (PITFALLS.md #2).
 */
public class WorkerIdPool {
    private final int maxWorkerId;
    private final List<Integer> available = new ArrayList<>();
    private final Set<Integer> leased = new HashSet<>();

    public WorkerIdPool() {
        this(1023);
    }

    public WorkerIdPool(int maxWorkerId) {
        if (maxWorkerId < 0) {
            throw new IllegalArgumentException("maxWorkerId can't be less than 0");
        }
        this.maxWorkerId = maxWorkerId;
        for (int i = 0; i <= maxWorkerId; i++) {
            available.add(i);
        }
    }

    /**
     * Claims the lowest available worker ID. Throws
     * WorkerIdPoolExhaustedException when every ID is leased.
     */
    public synchronized int acquire() {
        if (available.isEmpty()) {
            throw new WorkerIdPoolExhaustedException(
                    "All " + (maxWorkerId + 1) + " worker IDs are leased");
        }
        int workerId = available.remove(0);
        leased.add(workerId);
        return workerId;
    }

    /** Returns a leased ID to the pool (the ephemeral node dropped). */
    public synchronized void release(int workerId) {
        if (!leased.remove(workerId)) {
            throw new IllegalArgumentException("Worker ID " + workerId + " is not leased");
        }
        int index = 0;
        while (index < available.size() && available.get(index) < workerId) {
            index++;
        }
        available.add(index, workerId);
    }

    public synchronized boolean isLeased(int workerId) {
        return leased.contains(workerId);
    }

    public synchronized int leasedCount() {
        return leased.size();
    }
}
