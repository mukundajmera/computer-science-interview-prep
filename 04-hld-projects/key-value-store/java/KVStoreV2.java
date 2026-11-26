package keyvaluestore;

import java.util.*;
import java.security.MessageDigest;

class HashRing {
    int replicas;
    TreeMap<Long, String> ring = new TreeMap<>();
    Set<String> nodes = new HashSet<>();
    
    HashRing(int replicas) { this.replicas = replicas; }
    
    void addNode(String node) {
        nodes.add(node);
        for (int i=0; i<replicas; i++) {
            ring.put(hash(node + ":" + i), node);
        }
    }
    
    void removeNode(String node) {
        nodes.remove(node);
        ring.values().removeIf(n -> n.equals(node));
    }
    
    String getNode(String key) {
        if (ring.isEmpty()) return null;
        Long hash = hash(key);
        Map.Entry<Long, String> entry = ring.ceilingEntry(hash);
        if (entry == null) entry = ring.firstEntry();
        return entry.getValue();
    }
    
    long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes());
            return ((long)(digest[3]&0xFF) << 24) | ((long)(digest[2]&0xFF) << 16) | ((long)(digest[1]&0xFF) << 8) | (long)(digest[0]&0xFF);
        } catch (Exception e) {
            return key.hashCode();
        }
    }
}

public class KVStoreV2 {
    public static void main(String[] args) {
        testAddNode();
        testGetNode();
        testMultipleNodes();
        testRemoveNode();
        testVNodes();
        testEmptyRing();
        System.out.println("V2 Tests passed");
    }
    
    static void testAddNode() {
        HashRing ring = new HashRing(3);
        ring.addNode("n1");
        assert ring.nodes.size() == 1;
    }
    
    static void testGetNode() {
        HashRing ring = new HashRing(3);
        ring.addNode("n1");
        assert "n1".equals(ring.getNode("k1"));
    }
    
    static void testMultipleNodes() {
        HashRing ring = new HashRing(3);
        ring.addNode("n1"); ring.addNode("n2"); ring.addNode("n3");
        Set<String> seen = new HashSet<>();
        for (int i=0; i<100; i++) seen.add(ring.getNode("k"+i));
        assert seen.size() > 1;
    }
    
    static void testRemoveNode() {
        HashRing ring = new HashRing(3);
        ring.addNode("n1"); ring.addNode("n2");
        ring.removeNode("n1");
        assert "n2".equals(ring.getNode("k1"));
    }
    
    static void testVNodes() {
        HashRing ring = new HashRing(5);
        ring.addNode("n1");
        assert ring.ring.size() == 5;
    }
    
    static void testEmptyRing() {
        HashRing ring = new HashRing(3);
        assert ring.getNode("k1") == null;
    }
}
