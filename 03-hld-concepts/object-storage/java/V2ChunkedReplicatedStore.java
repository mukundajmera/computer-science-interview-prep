import java.util.*;

public class V2ChunkedReplicatedStore {
    private final int chunkSize;
    private final int replicationFactor;
    
    // key -> list of chunk IDs
    private final Map<String, List<String>> metadataIndex = new HashMap<>();
    
    // node_id -> { chunk_id -> data }
    private final Map<Integer, Map<String, byte[]>> storageNodes = new HashMap<>();
    
    // chunk_id -> list of node_ids
    private final Map<String, List<Integer>> placementMap = new HashMap<>();

    public V2ChunkedReplicatedStore(int chunkSize, int replicationFactor) {
        this.chunkSize = chunkSize;
        this.replicationFactor = replicationFactor;
        for (int i = 0; i < 5; i++) {
            storageNodes.put(i, new HashMap<>());
        }
    }

    public void put(String key, byte[] data) {
        List<String> chunkIds = new ArrayList<>();
        for (int i = 0; i < data.length; i += chunkSize) {
            int length = Math.min(chunkSize, data.length - i);
            byte[] chunk = new byte[length];
            System.arraycopy(data, i, chunk, 0, length);
            
            String chunkId = key + "_p" + (i / chunkSize);
            chunkIds.add(chunkId);
            
            List<Integer> nodes = new ArrayList<>();
            for (int r = 0; r < replicationFactor; r++) {
                int nodeId = ((i / chunkSize) + r) % storageNodes.size();
                storageNodes.get(nodeId).put(chunkId, chunk);
                nodes.add(nodeId);
            }
            placementMap.put(chunkId, nodes);
        }
        metadataIndex.put(key, chunkIds);
    }

    public byte[] get(String key) {
        List<String> chunkIds = metadataIndex.get(key);
        if (chunkIds == null) throw new RuntimeException("Not found");
        
        List<Byte> assembled = new ArrayList<>();
        for (String chunkId : chunkIds) {
            byte[] chunkData = null;
            for (int nodeId : placementMap.getOrDefault(chunkId, Collections.emptyList())) {
                if (storageNodes.containsKey(nodeId) && storageNodes.get(nodeId).containsKey(chunkId)) {
                    chunkData = storageNodes.get(nodeId).get(chunkId);
                    break;
                }
            }
            if (chunkData == null) throw new RuntimeException("Data loss for " + chunkId);
            for (byte b : chunkData) assembled.add(b);
        }
        
        byte[] result = new byte[assembled.size()];
        for (int i = 0; i < assembled.size(); i++) result[i] = assembled.get(i);
        return result;
    }

    public void simulateNodeFailure(int nodeId) {
        storageNodes.remove(nodeId);
    }

    public static void main(String[] args) {
        V2ChunkedReplicatedStore store = new V2ChunkedReplicatedStore(4, 3);
        String key = "test.txt";
        byte[] data = "ReplicatedDataChunk".getBytes();
        
        store.put(key, data);
        assert new String(store.get(key)).equals("ReplicatedDataChunk") : "Get failed";
        
        store.simulateNodeFailure(0);
        store.simulateNodeFailure(1);
        
        assert new String(store.get(key)).equals("ReplicatedDataChunk") : "Did not survive node failure";
        
        System.out.println("V2 Tests Passed!");
    }
}
