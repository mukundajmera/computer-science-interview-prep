package keyvaluestore;

import java.util.*;

class VectorClock {
    Map<String, Integer> clock = new HashMap<>();
    
    void increment(String node) {
        clock.put(node, clock.getOrDefault(node, 0) + 1);
    }
    
    void merge(VectorClock other) {
        for (Map.Entry<String, Integer> e : other.clock.entrySet()) {
            clock.put(e.getKey(), Math.max(clock.getOrDefault(e.getKey(), 0), e.getValue()));
        }
    }
    
    boolean compares(VectorClock other) {
        for (Map.Entry<String, Integer> e : clock.entrySet()) {
            if (other.clock.getOrDefault(e.getKey(), 0) < e.getValue()) return false;
        }
        return true;
    }
}

class Record {
    String value;
    VectorClock vc;
    Record(String v, VectorClock vc) { this.value = v; this.vc = vc; }
}

class Node {
    String name;
    Map<String, Record> store = new HashMap<>();
    List<String> hinted = new ArrayList<>();
    boolean isDown = false;
    
    Node(String name) { this.name = name; }
    
    boolean put(String key, String value, VectorClock vc) {
        if (isDown) throw new RuntimeException("Node down");
        if (!store.containsKey(key) || store.get(key).vc.compares(vc)) {
            store.put(key, new Record(value, vc));
            return true;
        }
        return false;
    }
    
    Record get(String key) {
        if (isDown) throw new RuntimeException("Node down");
        return store.get(key);
    }
}

class QuorumSystem {
    Map<String, Node> nodes = new HashMap<>();
    int n, w, r;
    
    QuorumSystem(List<String> nodeNames, int n, int w, int r) {
        for (String name : nodeNames) nodes.put(name, new Node(name));
        this.n = n; this.w = w; this.r = r;
    }
    
    boolean put(String key, String value, String coordinator) {
        VectorClock vc = new VectorClock();
        if (nodes.get(coordinator).store.containsKey(key)) {
            vc.merge(nodes.get(coordinator).store.get(key).vc);
        }
        vc.increment(coordinator);
        
        int success = 0;
        for (Node node : nodes.values()) {
            try {
                if (node.put(key, value, vc)) success++;
                if (success == w) break;
            } catch (Exception e) {}
        }
        if (success < w) nodes.get(coordinator).hinted.add(key);
        return success >= w;
    }
    
    Record get(String key) {
        List<Record> results = new ArrayList<>();
        for (Node node : nodes.values()) {
            try {
                Record res = node.get(key);
                if (res != null) results.add(res);
            } catch (Exception e) {}
        }
        if (results.size() < r) return null;
        
        Record best = new Record(null, new VectorClock());
        for (Record res : results) {
            if (best.vc.compares(res.vc)) best = res;
        }
        return best;
    }
}

public class KVStoreV3 {
    public static void main(String[] args) {
        testVCIncrement();
        testVCMerge();
        testQuorumPutGet();
        testQuorumNodeDown();
        testConflictResolution();
        testHintedHandoff();
        System.out.println("V3 Tests passed");
    }
    
    static void testVCIncrement() {
        VectorClock vc = new VectorClock();
        vc.increment("n1");
        assert vc.clock.get("n1") == 1;
    }
    
    static void testVCMerge() {
        VectorClock vc1 = new VectorClock(); vc1.increment("n1");
        VectorClock vc2 = new VectorClock(); vc2.increment("n2"); vc2.increment("n2");
        vc1.merge(vc2);
        assert vc1.clock.get("n1") == 1 && vc1.clock.get("n2") == 2;
    }
    
    static void testQuorumPutGet() {
        QuorumSystem qs = new QuorumSystem(Arrays.asList("n1", "n2", "n3"), 3, 2, 2);
        assert qs.put("k1", "v1", "n1");
        assert "v1".equals(qs.get("k1").value);
    }
    
    static void testQuorumNodeDown() {
        QuorumSystem qs = new QuorumSystem(Arrays.asList("n1", "n2", "n3"), 3, 2, 2);
        qs.nodes.get("n3").isDown = true;
        assert qs.put("k1", "v1", "n1");
        assert "v1".equals(qs.get("k1").value);
    }
    
    static void testConflictResolution() {
        QuorumSystem qs = new QuorumSystem(Arrays.asList("n1", "n2", "n3"), 3, 2, 2);
        VectorClock vc1 = new VectorClock(); vc1.increment("n1");
        VectorClock vc2 = new VectorClock(); vc2.increment("n1"); vc2.increment("n2");
        qs.nodes.get("n1").store.put("k1", new Record("v1", vc1));
        qs.nodes.get("n2").store.put("k1", new Record("v2", vc2));
        assert "v2".equals(qs.get("k1").value);
    }
    
    static void testHintedHandoff() {
        QuorumSystem qs = new QuorumSystem(Arrays.asList("n1", "n2", "n3"), 3, 3, 3);
        qs.nodes.get("n2").isDown = true;
        qs.nodes.get("n3").isDown = true;
        qs.put("k1", "v1", "n1");
        assert !qs.nodes.get("n1").hinted.isEmpty();
    }
}
