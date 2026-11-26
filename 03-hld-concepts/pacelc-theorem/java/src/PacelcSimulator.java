import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class PacelcSimulator {
    private static final Set<String> VALID_POLICIES = Set.of("PC_EC", "PC_EL", "PA_EL", "PA_EC");
    private final String policy;
    private final Map<Integer, String> nodes = new HashMap<>();
    private Set<Integer> isolatedNodes = new HashSet<>();

    public PacelcSimulator(String policy) {
        if (!VALID_POLICIES.contains(policy)) {
            throw new IllegalArgumentException("Invalid policy");
        }
        this.policy = policy;
        nodes.put(1, null);
        nodes.put(2, null);
        nodes.put(3, null);
    }

    public static class Result {
        public String status;
        public String message;
        public long latencyMs;
        public String value;
        public boolean stale;

        public Result(String status, String message, long latencyMs, String value, boolean stale) {
            this.status = status;
            this.message = message;
            this.latencyMs = latencyMs;
            this.value = value;
            this.stale = stale;
        }
    }

    public Result write(String key, String value) {
        long startTime = System.currentTimeMillis();

        Set<Integer> activeNodes = new HashSet<>(nodes.keySet());
        activeNodes.removeAll(isolatedNodes);

        boolean hasMajority = activeNodes.size() > nodes.size() / 2;
        boolean isPartitioned = !isolatedNodes.isEmpty();

        if (isPartitioned) {
            if (policy.equals("PC_EC") || policy.equals("PC_EL")) {
                if (!hasMajority) {
                    return new Result("error", "Consistency rejected write: Minority partition", System.currentTimeMillis() - startTime, null, false);
                }
            }
            if (activeNodes.isEmpty()) {
                return new Result("error", "No active nodes", System.currentTimeMillis() - startTime, null, false);
            }
        } else {
            if (policy.equals("PC_EC") || policy.equals("PA_EC")) {
                try {
                    Thread.sleep(50);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }

        for (Integer node : activeNodes) {
            nodes.put(node, value);
        }

        return new Result("success", null, System.currentTimeMillis() - startTime, null, false);
    }

    public Result read(String key) {
        long startTime = System.currentTimeMillis();

        Set<Integer> activeNodes = new HashSet<>(nodes.keySet());
        activeNodes.removeAll(isolatedNodes);

        boolean hasMajority = activeNodes.size() > nodes.size() / 2;
        boolean isPartitioned = !isolatedNodes.isEmpty();

        if (isPartitioned) {
            if (policy.equals("PC_EC") || policy.equals("PC_EL")) {
                if (!hasMajority) {
                    return new Result("error", "Consistency rejected read: Minority partition", System.currentTimeMillis() - startTime, null, false);
                }
            }
            if (activeNodes.isEmpty()) {
                return new Result("error", "No active nodes", System.currentTimeMillis() - startTime, null, false);
            }
        } else {
            if (policy.equals("PC_EC") || policy.equals("PA_EC")) {
                try {
                    Thread.sleep(50);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        }
        
        if (activeNodes.isEmpty()) {
            return new Result("error", "No active nodes", System.currentTimeMillis() - startTime, null, false);
        }

        Integer firstActiveNode = activeNodes.iterator().next();
        String val = nodes.get(firstActiveNode);

        Set<String> uniqueValues = new HashSet<>(nodes.values());
        boolean stale = uniqueValues.size() > 1;

        return new Result("success", null, System.currentTimeMillis() - startTime, val, stale);
    }

    public void injectPartition(Set<Integer> isolatedNodes) {
        this.isolatedNodes = new HashSet<>(isolatedNodes);
    }

    public void healPartition() {
        this.isolatedNodes = new HashSet<>();
        String lastNonNullValue = null;
        for (String val : nodes.values()) {
            if (val != null) {
                lastNonNullValue = val;
            }
        }
        if (lastNonNullValue != null) {
            for (Integer n : nodes.keySet()) {
                nodes.put(n, lastNonNullValue);
            }
        }
    }
    
    public Map<Integer, String> getNodes() {
        return nodes;
    }
}
