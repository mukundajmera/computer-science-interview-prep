import java.util.*;

public class V3XorParityStore {
    private final int k; // Data chunks
    
    private static class Meta {
        int originalLength;
        int chunkSize;
        List<String> chunkIds = new ArrayList<>();
    }
    
    private final Map<String, Meta> metadataIndex = new HashMap<>();
    private final Map<Integer, Map<String, byte[]>> nodes = new HashMap<>();

    public V3XorParityStore(int k) {
        this.k = k;
        for (int i = 0; i <= k; i++) {
            nodes.put(i, new HashMap<>());
        }
    }

    private byte[] xorBytes(byte[] b1, byte[] b2) {
        byte[] res = new byte[b1.length];
        for (int i = 0; i < b1.length; i++) {
            res[i] = (byte) (b1[i] ^ b2[i]);
        }
        return res;
    }

    public void put(String key, byte[] data) {
        int remainder = data.length % k;
        int padding = remainder == 0 ? 0 : k - remainder;
        
        byte[] paddedData = new byte[data.length + padding];
        System.arraycopy(data, 0, paddedData, 0, data.length);
        
        int chunkSize = paddedData.length / k;
        byte[][] chunks = new byte[k + 1][chunkSize];
        
        for (int i = 0; i < k; i++) {
            System.arraycopy(paddedData, i * chunkSize, chunks[i], 0, chunkSize);
        }
        
        // Calculate parity
        chunks[k] = chunks[0].clone();
        for (int i = 1; i < k; i++) {
            chunks[k] = xorBytes(chunks[k], chunks[i]);
        }
        
        Meta meta = new Meta();
        meta.originalLength = data.length;
        meta.chunkSize = chunkSize;
        
        for (int i = 0; i <= k; i++) {
            String chunkId = key + "_c" + i;
            meta.chunkIds.add(chunkId);
            nodes.get(i).put(chunkId, chunks[i]);
        }
        metadataIndex.put(key, meta);
    }

    private byte[] readChunk(int nodeId, String chunkId) {
        Map<String, byte[]> node = nodes.get(nodeId);
        if (node == null) return null;
        return node.get(chunkId);
    }

    public byte[] get(String key) {
        Meta meta = metadataIndex.get(key);
        if (meta == null) throw new RuntimeException("Not found");
        
        byte[] assembled = new byte[meta.chunkSize * k];
        
        for (int i = 0; i < k; i++) {
            String chunkId = meta.chunkIds.get(i);
            byte[] chunk = readChunk(i, chunkId);
            
            if (chunk == null) {
                // Degraded Read
                System.out.println("Degraded read on node " + i);
                chunk = new byte[meta.chunkSize];
                for (int j = 0; j <= k; j++) {
                    if (i == j) continue;
                    byte[] surviving = readChunk(j, meta.chunkIds.get(j));
                    if (surviving == null) throw new RuntimeException("Double failure!");
                    chunk = xorBytes(chunk, surviving);
                }
            }
            System.arraycopy(chunk, 0, assembled, i * meta.chunkSize, meta.chunkSize);
        }
        
        byte[] original = new byte[meta.originalLength];
        System.arraycopy(assembled, 0, original, 0, meta.originalLength);
        return original;
    }

    public boolean scrubAndRepair(String key) {
        Meta meta = metadataIndex.get(key);
        if (meta == null) return false;
        
        int missingIdx = -1;
        for (int i = 0; i <= k; i++) {
            if (readChunk(i, meta.chunkIds.get(i)) == null) {
                missingIdx = i;
                break;
            }
        }
        
        if (missingIdx != -1) {
            byte[] reconstructed = new byte[meta.chunkSize];
            for (int j = 0; j <= k; j++) {
                if (missingIdx == j) continue;
                byte[] surviving = readChunk(j, meta.chunkIds.get(j));
                reconstructed = xorBytes(reconstructed, surviving);
            }
            nodes.get(missingIdx).put(meta.chunkIds.get(missingIdx), reconstructed);
            return true;
        }
        return false;
    }

    public void simulateNodeFailure(int nodeId) {
        nodes.put(nodeId, new HashMap<>());
    }

    public static void main(String[] args) {
        V3XorParityStore store = new V3XorParityStore(4);
        String key = "test.txt";
        byte[] data = "ErasureCoding123".getBytes(); // 16 bytes
        
        store.put(key, data);
        assert new String(store.get(key)).equals("ErasureCoding123") : "Normal get failed";
        
        store.simulateNodeFailure(1);
        assert new String(store.get(key)).equals("ErasureCoding123") : "Degraded read failed";
        
        assert store.scrubAndRepair(key) : "Repair failed";
        assert store.nodes.get(1).containsKey(key + "_c1") : "Node 1 not repaired";
        
        System.out.println("V3 Tests Passed!");
    }
}
