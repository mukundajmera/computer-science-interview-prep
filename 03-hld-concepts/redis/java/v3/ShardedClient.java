package v3;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.CRC32;

public class ShardedClient {
    private final Map<String, Node> nodes;
    private final String[] slots;
    private final Map<String, Object> localCache;
    private final Map<String, Integer> accessCounts;
    private static final int HOT_KEY_THRESHOLD = 5;

    public ShardedClient(List<Node> nodeList) {
        nodes = new HashMap<>();
        for (Node n : nodeList) {
            nodes.put(n.nodeId, n);
        }
        slots = new String[16384];
        assignSlots(nodeList);

        localCache = new HashMap<>();
        accessCounts = new HashMap<>();
    }

    private void assignSlots(List<Node> nodeList) {
        int numNodes = nodeList.size();
        for (int i = 0; i < 16384; i++) {
            String nodeId = nodeList.get(i % numNodes).nodeId;
            slots[i] = nodeId;
            nodes.get(nodeId).assignedSlots.add(i);
        }
    }

    public int getHashSlot(String key) {
        int hashTagStart = key.indexOf('{');
        int hashTagEnd = key.indexOf('}', hashTagStart + 1);
        String keyToHash = key;
        if (hashTagStart != -1 && hashTagEnd != -1) {
            keyToHash = key.substring(hashTagStart + 1, hashTagEnd);
        }

        CRC32 crc = new CRC32();
        crc.update(keyToHash.getBytes());
        return (int) (crc.getValue() % 16384);
    }

    public Result executeCommand(String command, String key, Object value, String initialNodeId) {
        accessCounts.put(key, accessCounts.getOrDefault(key, 0) + 1);

        if ("GET".equals(command) && localCache.containsKey(key)) {
            return new Result(localCache.get(key), null);
        }

        int slot = getHashSlot(key);
        String correctNodeId = slots[slot];
        Node correctNode = nodes.get(correctNodeId);

        String contactedNodeId = (initialNodeId != null) ? initialNodeId : correctNodeId;
        Node contactedNode = nodes.get(contactedNodeId);

        if (!contactedNode.assignedSlots.contains(slot)) {
            return new Result(null, "MOVED " + slot + " " + correctNode.host + ":" + correctNode.port);
        }

        if (accessCounts.get(key) > HOT_KEY_THRESHOLD && "GET".equals(command)) {
            Object val = correctNode.get(key);
            localCache.put(key, val);
            return new Result(val, null);
        }

        if ("GET".equals(command)) {
            return new Result(correctNode.get(key), null);
        } else if ("SET".equals(command)) {
            correctNode.set(key, value);
            if (localCache.containsKey(key)) {
                localCache.put(key, value);
            }
            return new Result("OK", null);
        }

        return new Result(null, "UNKNOWN_COMMAND");
    }

    public static class Result {
        public final Object value;
        public final String error;

        public Result(Object value, String error) {
            this.value = value;
            this.error = error;
        }
    }
}
