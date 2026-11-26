package dcache.v3;

public interface DistributedCacheClusterService {
    void handleNodeFailure(String nodeId);
    void promoteReplica(String keyRange);
    void mitigateHotKey(String key);
}
