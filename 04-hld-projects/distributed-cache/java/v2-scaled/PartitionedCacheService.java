package dcache.v2;

public interface PartitionedCacheService {
    String resolveNodeForKey(String key);
    void replicateWrite(String key, String value, long ttlSeconds);
    void rebalanceRange(String tokenRange, String targetNodeId);
}

interface MembershipService {
    RingSnapshot currentRing();
}

final class RingSnapshot {
    public final long version;
    public final String serializedAssignments;

    RingSnapshot(long version, String serializedAssignments) {
        this.version = version;
        this.serializedAssignments = serializedAssignments;
    }
}
