import dcache.v1.CacheService;
import dcache.v2.PartitionedCacheService;
import dcache.v3.DistributedCacheClusterService;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.ArrayList;
import java.util.List;

class InMemoryCache implements CacheService {
    private final Map<String, String> store = new HashMap<>();

    @Override
    public void set(String key, String value, long ttlSeconds) {
        store.put(key, value);
    }

    @Override
    public Optional<String> get(String key) {
        return Optional.ofNullable(store.get(key));
    }

    @Override
    public boolean delete(String key) {
        if (store.containsKey(key)) {
            store.remove(key);
            return true;
        }
        return false;
    }
}

class DummyPartitionedCache implements PartitionedCacheService {
    public final List<String> replicatedKeys = new ArrayList<>();
    public boolean rebalanced = false;

    @Override
    public String resolveNodeForKey(String key) {
        return "node-" + key.length();
    }

    @Override
    public void replicateWrite(String key, String value, long ttlSeconds) {
        replicatedKeys.add(key);
    }

    @Override
    public void rebalanceRange(String tokenRange, String targetNodeId) {
        rebalanced = true;
    }
}

class DummyClusterService implements DistributedCacheClusterService {
    public final List<String> failedNodes = new ArrayList<>();
    public final List<String> promotedRanges = new ArrayList<>();
    public final List<String> mitigatedKeys = new ArrayList<>();

    @Override
    public void handleNodeFailure(String nodeId) {
        failedNodes.add(nodeId);
    }

    @Override
    public void promoteReplica(String keyRange) {
        promotedRanges.add(keyRange);
    }

    @Override
    public void mitigateHotKey(String key) {
        mitigatedKeys.add(key);
    }
}

public class DistributedCacheTest {

    @Test
    void testV1BasicCache() {
        CacheService cache = new InMemoryCache();
        cache.set("foo", "bar", 60);
        assertTrue(cache.get("foo").isPresent());
        assertEquals("bar", cache.get("foo").get());

        assertTrue(cache.delete("foo"));
        assertFalse(cache.get("foo").isPresent());
        assertFalse(cache.delete("foo"));
    }

    @Test
    void testV2ScaledCache() {
        DummyPartitionedCache pcache = new DummyPartitionedCache();
        assertEquals("node-4", pcache.resolveNodeForKey("key1"));

        pcache.replicateWrite("key2", "val2", 120);
        assertEquals(1, pcache.replicatedKeys.size());
        assertEquals("key2", pcache.replicatedKeys.get(0));

        pcache.rebalanceRange("0-100", "node-2");
        assertTrue(pcache.rebalanced);
    }

    @Test
    void testV3DistributedCluster() {
        DummyClusterService cluster = new DummyClusterService();

        cluster.handleNodeFailure("node-fail");
        assertTrue(cluster.failedNodes.contains("node-fail"));

        cluster.promoteReplica("100-200");
        assertTrue(cluster.promotedRanges.contains("100-200"));

        cluster.mitigateHotKey("hot_key_1");
        assertTrue(cluster.mitigatedKeys.contains("hot_key_1"));
    }
}
