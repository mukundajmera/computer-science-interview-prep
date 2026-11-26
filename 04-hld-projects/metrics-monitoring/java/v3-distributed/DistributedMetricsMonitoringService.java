package v3;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class DistributedMetricsMonitoringService {

    public enum MetricType {
        COUNTER, GAUGE, HISTOGRAM
    }

    public static class MetricPoint {
        private final String name;
        private final MetricType type;
        private final Map<String, String> tags;
        private final long timestampMs;
        private final double value;

        public MetricPoint(String name, MetricType type, Map<String, String> tags, long timestampMs, double value) {
            this.name = name;
            this.type = type;
            this.tags = tags != null ? new HashMap<>(tags) : new HashMap<>();
            this.timestampMs = timestampMs;
            this.value = value;
        }

        public String getName() { return name; }
        public MetricType getType() { return type; }
        public Map<String, String> getTags() { return tags; }
        public long getTimestampMs() { return timestampMs; }
        public double getValue() { return value; }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            MetricPoint that = (MetricPoint) o;
            return timestampMs == that.timestampMs &&
                   Double.compare(that.value, value) == 0 &&
                   Objects.equals(name, that.name) &&
                   type == that.type &&
                   Objects.equals(tags, that.tags);
        }

        @Override
        public int hashCode() {
            return Objects.hash(name, type, tags, timestampMs, value);
        }
    }

    public static class ConsistentHashRing {
        private final int virtualNodes;
        private final SortedMap<Integer, String> ring = new TreeMap<>();
        private final Map<String, List<Integer>> nodeMap = new HashMap<>();

        public ConsistentHashRing(int virtualNodes) {
            this.virtualNodes = virtualNodes;
        }

        private int hash(String key) {
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
                // Use first 4 bytes as int
                return ((digest[3] & 0xFF) << 24) |
                       ((digest[2] & 0xFF) << 16) |
                       ((digest[1] & 0xFF) << 8) |
                       (digest[0] & 0xFF);
            } catch (NoSuchAlgorithmException e) {
                throw new RuntimeException(e);
            }
        }

        public synchronized void addNode(String nodeId) {
            List<Integer> hashes = new ArrayList<>();
            for (int i = 0; i < virtualNodes; i++) {
                String vNodeKey = nodeId + "#" + i;
                int h = hash(vNodeKey);
                ring.put(h, nodeId);
                hashes.add(h);
            }
            nodeMap.put(nodeId, hashes);
        }

        public synchronized void removeNode(String nodeId) {
            List<Integer> hashes = nodeMap.remove(nodeId);
            if (hashes != null) {
                for (Integer h : hashes) {
                    ring.remove(h);
                }
            }
        }

        public synchronized List<String> getNodes(String key, int count) {
            if (ring.isEmpty()) {
                return Collections.emptyList();
            }
            int h = hash(key);
            SortedMap<Integer, String> tailMap = ring.tailMap(h);
            Iterator<Map.Entry<Integer, String>> it;

            if (tailMap.isEmpty()) {
                it = ring.entrySet().iterator();
            } else {
                it = tailMap.entrySet().iterator();
            }

            List<String> nodes = new ArrayList<>();
            Set<String> allNodes = new HashSet<>(nodeMap.keySet());
            int limit = Math.min(count, allNodes.size());

            while (nodes.size() < limit) {
                if (!it.hasNext()) {
                    it = ring.entrySet().iterator();
                }
                String node = it.next().getValue();
                if (!nodes.contains(node)) {
                    nodes.add(node);
                }
            }
            return nodes;
        }
    }

    public static class ColdStore {
        private final Map<String, List<MetricPoint>> storage = new ConcurrentHashMap<>();

        public void put(String key, List<MetricPoint> data) {
            storage.compute(key, (k, existing) -> {
                if (existing == null) {
                    return new ArrayList<>(data);
                } else {
                    List<MetricPoint> merged = new ArrayList<>(existing);
                    for (MetricPoint p : data) {
                        if (!merged.contains(p)) {
                            merged.add(p);
                        }
                    }
                    return merged;
                }
            });
        }

        public List<MetricPoint> get(String key) {
            return storage.getOrDefault(key, Collections.emptyList());
        }
    }

    public static class Node {
        private final String nodeId;
        private final ColdStore coldStore;
        private final long chunkSizeMs;
        private volatile boolean isAlive = true;

        private final List<MetricPoint> wal = Collections.synchronizedList(new ArrayList<>());
        private final Map<Long, List<MetricPoint>> localChunks = new ConcurrentHashMap<>();

        public Node(String nodeId, ColdStore coldStore, long chunkSizeMs) {
            this.nodeId = nodeId;
            this.coldStore = coldStore;
            this.chunkSizeMs = chunkSizeMs;
        }

        public void ingest(MetricPoint point) {
            if (!isAlive) throw new RuntimeException("Node is down");
            wal.add(point);
        }

        public synchronized void flushWalToChunks() {
            if (!isAlive) return;
            List<MetricPoint> toFlush;
            synchronized (wal) {
                toFlush = new ArrayList<>(wal);
                wal.clear();
            }

            for (MetricPoint point : toFlush) {
                long chunkIdx = point.getTimestampMs() / chunkSizeMs;
                localChunks.computeIfAbsent(chunkIdx, k -> Collections.synchronizedList(new ArrayList<>())).add(point);
            }
        }

        public synchronized void flushChunksToColdStore(long upToChunkIdx) {
            if (!isAlive) return;
            List<Long> keys = new ArrayList<>(localChunks.keySet());
            for (Long chunkIdx : keys) {
                if (chunkIdx <= upToChunkIdx) {
                    List<MetricPoint> data = localChunks.remove(chunkIdx);
                    if (data != null) {
                        String key = nodeId + "_" + chunkIdx;
                        coldStore.put(key, data);
                    }
                }
            }
        }

        private boolean matchesTags(Map<String, String> pointTags, Map<String, String> queryTags) {
            if (queryTags == null || queryTags.isEmpty()) return true;
            for (Map.Entry<String, String> entry : queryTags.entrySet()) {
                if (!entry.getValue().equals(pointTags.get(entry.getKey()))) {
                    return false;
                }
            }
            return true;
        }

        public List<MetricPoint> query(String metricName, Map<String, String> tags, long startMs, long endMs) {
            if (!isAlive) throw new RuntimeException("Node is down");
            List<MetricPoint> result = new ArrayList<>();

            // 1. Query WAL
            synchronized (wal) {
                for (MetricPoint p : wal) {
                    if (p.getName().equals(metricName) && p.getTimestampMs() >= startMs && p.getTimestampMs() <= endMs && matchesTags(p.getTags(), tags)) {
                        result.add(p);
                    }
                }
            }

            // 2. Query Local Chunks & 3. Cold Store
            long startChunk = startMs / chunkSizeMs;
            long endChunk = endMs / chunkSizeMs;

            for (long chunkIdx = startChunk; chunkIdx <= endChunk; chunkIdx++) {
                List<MetricPoint> localData = localChunks.get(chunkIdx);
                if (localData != null) {
                    synchronized (localData) {
                        for (MetricPoint p : localData) {
                            if (p.getName().equals(metricName) && p.getTimestampMs() >= startMs && p.getTimestampMs() <= endMs && matchesTags(p.getTags(), tags)) {
                                result.add(p);
                            }
                        }
                    }
                } else {
                    String key = nodeId + "_" + chunkIdx;
                    List<MetricPoint> coldData = coldStore.get(key);
                    for (MetricPoint p : coldData) {
                        if (p.getName().equals(metricName) && p.getTimestampMs() >= startMs && p.getTimestampMs() <= endMs && matchesTags(p.getTags(), tags)) {
                            result.add(p);
                        }
                    }
                }
            }

            return result;
        }

        public void setAlive(boolean alive) {
            this.isAlive = alive;
        }

        public boolean isAlive() {
            return isAlive;
        }
    }

    private final ColdStore coldStore = new ColdStore();
    private final Map<String, Node> nodes = new ConcurrentHashMap<>();
    private final ConsistentHashRing ring;
    private final int replicationFactor;

    public DistributedMetricsMonitoringService(int numNodes, int replicationFactor) {
        this.replicationFactor = Math.min(replicationFactor, numNodes);
        this.ring = new ConsistentHashRing(100);
        for (int i = 0; i < numNodes; i++) {
            String nodeId = "node_" + i;
            nodes.put(nodeId, new Node(nodeId, coldStore, 3600000));
            ring.addNode(nodeId);
        }
    }

    // For testing
    public Node getNode(String nodeId) {
        return nodes.get(nodeId);
    }

    public ConsistentHashRing getRing() {
        return ring;
    }

    public String getShardKey(String metricName, Map<String, String> tags) {
        StringBuilder sb = new StringBuilder(metricName).append("|");
        if (tags != null) {
            List<String> sortedKeys = new ArrayList<>(tags.keySet());
            Collections.sort(sortedKeys);
            for (String key : sortedKeys) {
                sb.append(key).append("=").append(tags.get(key)).append(",");
            }
        }
        return sb.toString();
    }

    public void ingest(MetricPoint point) {
        String shardKey = getShardKey(point.getName(), point.getTags());
        List<String> targetNodeIds = ring.getNodes(shardKey, replicationFactor);

        int successCount = 0;
        for (String nodeId : targetNodeIds) {
            Node node = nodes.get(nodeId);
            try {
                if (node != null && node.isAlive()) {
                    node.ingest(point);
                    successCount++;
                }
            } catch (Exception e) {
                // Ignore
            }
        }

        if (successCount == 0) {
            throw new RuntimeException("Failed to ingest on any replica");
        }
    }

    public void setNodeStatus(String nodeId, boolean isAlive) {
        Node node = nodes.get(nodeId);
        if (node != null) {
            node.setAlive(isAlive);
        }
    }

    public void flushAll() {
        for (Node node : nodes.values()) {
            if (node.isAlive()) {
                node.flushWalToChunks();
            }
        }
    }

    public void coldFlushAll(long upToChunkIdx) {
        for (Node node : nodes.values()) {
            if (node.isAlive()) {
                node.flushChunksToColdStore(upToChunkIdx);
            }
        }
    }

    public void reconcileReplicas(String metricName, Map<String, String> tags, long startMs, long endMs) {
        String shardKey = getShardKey(metricName, tags);
        List<String> targetNodeIds = ring.getNodes(shardKey, replicationFactor);

        Set<MetricPoint> allPoints = new HashSet<>();
        for (String nodeId : targetNodeIds) {
            Node node = nodes.get(nodeId);
            if (node != null && node.isAlive()) {
                try {
                    allPoints.addAll(node.query(metricName, tags, startMs, endMs));
                } catch (Exception e) {
                    // Ignore
                }
            }
        }

        for (String nodeId : targetNodeIds) {
            Node node = nodes.get(nodeId);
            if (node != null && node.isAlive()) {
                Set<MetricPoint> currentPoints = new HashSet<>();
                try {
                    currentPoints.addAll(node.query(metricName, tags, startMs, endMs));
                } catch (Exception e) {
                    continue;
                }

                for (MetricPoint p : allPoints) {
                    if (!currentPoints.contains(p)) {
                        try {
                            node.ingest(p);
                        } catch (Exception e) {
                            // Ignore
                        }
                    }
                }
            }
        }
    }

    public List<MetricPoint> query(String metricName, Map<String, String> tags, long startMs, long endMs) {
        String shardKey = getShardKey(metricName, tags);
        List<String> targetNodeIds = ring.getNodes(shardKey, replicationFactor);

        Set<MetricPoint> allPoints = new HashSet<>();
        for (String nodeId : targetNodeIds) {
            Node node = nodes.get(nodeId);
            if (node != null) {
                try {
                    allPoints.addAll(node.query(metricName, tags, startMs, endMs));
                } catch (Exception e) {
                    // Ignore
                }
            }
        }

        return new ArrayList<>(allPoints);
    }

    public double getCounterTotal(String metricName, Map<String, String> tags, long startMs, long endMs) {
        return query(metricName, tags, startMs, endMs).stream()
                .filter(p -> p.getType() == MetricType.COUNTER)
                .mapToDouble(MetricPoint::getValue)
                .sum();
    }

    public double getGaugeLatest(String metricName, Map<String, String> tags, long startMs, long endMs) {
        return query(metricName, tags, startMs, endMs).stream()
                .filter(p -> p.getType() == MetricType.GAUGE)
                .max(Comparator.comparing(MetricPoint::getTimestampMs))
                .map(MetricPoint::getValue)
                .orElse(0.0);
    }

    public double getHistogramPercentile(String metricName, Map<String, String> tags, long startMs, long endMs, double percentile) {
        List<MetricPoint> histPoints = query(metricName, tags, startMs, endMs).stream()
                .filter(p -> p.getType() == MetricType.HISTOGRAM)
                .collect(Collectors.toList());

        if (histPoints.isEmpty()) return 0.0;

        List<Double> values = histPoints.stream()
                .map(MetricPoint::getValue)
                .sorted()
                .collect(Collectors.toList());

        int index = (int) Math.ceil((percentile / 100.0) * values.size()) - 1;
        if (index < 0) index = 0;
        if (index >= values.size()) index = values.size() - 1;
        return values.get(index);
    }
}
