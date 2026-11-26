package v3;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;

public class Node {
    public final String nodeId;
    public final String host;
    public final int port;
    private final Map<String, Object> store;
    public final Set<Integer> assignedSlots;

    public Node(String nodeId, String host, int port) {
        this.nodeId = nodeId;
        this.host = host;
        this.port = port;
        this.store = new HashMap<>();
        this.assignedSlots = new HashSet<>();
    }

    public Object get(String key) {
        return store.get(key);
    }

    public void set(String key, Object value) {
        store.put(key, value);
    }

    public void delete(String key) {
        store.remove(key);
    }
}
