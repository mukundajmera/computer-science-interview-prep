import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class CausalClockEngine {

    public enum Causality {
        BEFORE, AFTER, CONCURRENT, EQUAL
    }

    public static class LamportClock {
        private final String nodeId;
        private int counter;

        public LamportClock(String nodeId) {
            this.nodeId = nodeId;
            this.counter = 0;
        }

        public int tick() {
            this.counter++;
            return this.counter;
        }

        public int sendEvent() {
            return tick();
        }

        public int receiveEvent(int receivedTime) {
            this.counter = Math.max(this.counter, receivedTime) + 1;
            return this.counter;
        }

        public static Causality compareCausality(int timeA, String nodeA, int timeB, String nodeB) {
            if (timeA < timeB) {
                return Causality.BEFORE;
            } else if (timeA > timeB) {
                return Causality.AFTER;
            } else {
                int cmp = nodeA.compareTo(nodeB);
                if (cmp < 0) {
                    return Causality.BEFORE;
                } else if (cmp > 0) {
                    return Causality.AFTER;
                } else {
                    return Causality.EQUAL;
                }
            }
        }
    }

    public static class VectorClock {
        private final String nodeId;
        private final Map<String, Integer> vector;

        public VectorClock(String nodeId) {
            this.nodeId = nodeId;
            this.vector = new HashMap<>();
            this.vector.put(nodeId, 0);
        }

        public Map<String, Integer> tick() {
            this.vector.put(this.nodeId, this.vector.getOrDefault(this.nodeId, 0) + 1);
            return new HashMap<>(this.vector);
        }

        public Map<String, Integer> sendEvent() {
            return tick();
        }

        public Map<String, Integer> receiveEvent(Map<String, Integer> receivedVector) {
            for (Map.Entry<String, Integer> entry : receivedVector.entrySet()) {
                String node = entry.getKey();
                int count = entry.getValue();
                this.vector.put(node, Math.max(this.vector.getOrDefault(node, 0), count));
            }
            this.vector.put(this.nodeId, this.vector.getOrDefault(this.nodeId, 0) + 1);
            return new HashMap<>(this.vector);
        }

        public static Causality compareCausality(Map<String, Integer> vectorA, Map<String, Integer> vectorB) {
            Set<String> allNodes = new HashSet<>();
            allNodes.addAll(vectorA.keySet());
            allNodes.addAll(vectorB.keySet());

            boolean aIsSmaller = false;
            boolean bIsSmaller = false;

            for (String node : allNodes) {
                int valA = vectorA.getOrDefault(node, 0);
                int valB = vectorB.getOrDefault(node, 0);

                if (valA < valB) {
                    aIsSmaller = true;
                } else if (valA > valB) {
                    bIsSmaller = true;
                }
            }

            if (aIsSmaller && !bIsSmaller) {
                return Causality.BEFORE;
            } else if (bIsSmaller && !aIsSmaller) {
                return Causality.AFTER;
            } else if (!aIsSmaller && !bIsSmaller) {
                return Causality.EQUAL;
            } else {
                return Causality.CONCURRENT;
            }
        }
    }

    public static class TrueTimeSimulator {
        private final long epsilonMs;
        private long currentTimeMs;

        public TrueTimeSimulator(long epsilonMs) {
            this.epsilonMs = epsilonMs;
            this.currentTimeMs = System.currentTimeMillis();
        }

        private void advanceTime(long ms) {
            this.currentTimeMs += ms;
        }

        public long[] now() {
            long earliest = this.currentTimeMs;
            long latest = earliest + this.epsilonMs;
            advanceTime(1);
            return new long[]{earliest, latest};
        }

        public void waitUntil(long targetTime) {
            while (now()[0] <= targetTime) {
                advanceTime(1);
            }
        }

        public long commitTransaction() {
            long[] currentInterval = now();
            long latest = currentInterval[1];
            long commitTimestamp = latest;
            
            waitUntil(commitTimestamp);
            
            return commitTimestamp;
        }
    }
}