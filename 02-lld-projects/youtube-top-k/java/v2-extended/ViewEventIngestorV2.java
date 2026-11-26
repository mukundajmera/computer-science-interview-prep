import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

class CountMinSketch {
    private final int width;
    private final int depth;
    private final int[][] table;
    
    public int[][] getTable() {
        return table;
    }
    
    public CountMinSketch(int width, int depth) {
        this.width = width;
        this.depth = depth;
        this.table = new int[depth][width];
    }
    
    private int hash(String item, int seed) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            String data = seed + "_" + item;
            byte[] hashBytes = md.digest(data.getBytes(StandardCharsets.UTF_8));
            return new java.math.BigInteger(1, hashBytes).mod(java.math.BigInteger.valueOf(width)).intValue();
        } catch (NoSuchAlgorithmException e) {
            return Math.abs(item.hashCode() % width);
        }
    }
    
    public void add(String item, int count) {
        if (count < 0) return;
        for (int i = 0; i < depth; i++) {
            int idx = hash(item, i);
            table[i][idx] += count;
        }
    }
    
    public int estimate(String item) {
        int minCount = Integer.MAX_VALUE;
        for (int i = 0; i < depth; i++) {
            int idx = hash(item, i);
            minCount = Math.min(minCount, table[i][idx]);
        }
        return minCount;
    }
}

class HeapItem implements Comparable<HeapItem> {
    int count;
    String videoId;
    
    public HeapItem(int count, String videoId) {
        this.count = count;
        this.videoId = videoId;
    }
    
    @Override
    public int compareTo(HeapItem other) {
        if (this.count != other.count) {
            return Integer.compare(this.count, other.count);
        }
        return other.videoId.compareTo(this.videoId);
    }
}

class WindowState {
    final CountMinSketch cms;
    final PriorityQueue<HeapItem> topKHeap;
    final Map<String, HeapItem> topKMap;
    
    public WindowState(int sketchWidth, int sketchDepth) {
        this.cms = new CountMinSketch(sketchWidth, sketchDepth);
        this.topKHeap = new PriorityQueue<>();
        this.topKMap = new HashMap<>();
    }
    
    public String toPayload() {
        StringBuilder sb = new StringBuilder();
        int[][] table = cms.getTable();
        for (int i = 0; i < table.length; i++) {
            for (int j = 0; j < table[i].length; j++) {
                sb.append(table[i][j]).append(",");
            }
        }
        sb.append("|");
        for (HeapItem item : topKHeap) {
            sb.append(item.videoId).append(":").append(item.count).append(";");
        }
        return sb.toString();
    }
    
    public static WindowState fromPayload(String payload, int sketchWidth, int sketchDepth) {
        WindowState ws = new WindowState(sketchWidth, sketchDepth);
        if (payload == null || payload.isEmpty()) return ws;
        
        try {
            String[] parts = payload.split("\\|");
            if (parts.length > 0 && !parts[0].isEmpty()) {
                String[] counts = parts[0].split(",");
                int[][] table = ws.cms.getTable();
                int idx = 0;
                for (int i = 0; i < table.length; i++) {
                    for (int j = 0; j < table[i].length; j++) {
                        if (idx < counts.length && !counts[idx].isEmpty()) {
                            table[i][j] = Integer.parseInt(counts[idx]);
                        }
                        idx++;
                    }
                }
            }
            if (parts.length > 1 && !parts[1].isEmpty()) {
                String[] items = parts[1].split(";");
                for (String itemStr : items) {
                    if (itemStr.isEmpty()) continue;
                    String[] kv = itemStr.split(":");
                    if (kv.length == 2) {
                        String vId = kv[0];
                        int c = Integer.parseInt(kv[1]);
                        HeapItem hItem = new HeapItem(c, vId);
                        ws.topKHeap.offer(hItem);
                        ws.topKMap.put(vId, hItem);
                    }
                }
            }
        } catch (Exception e) {
            // ignore malformed payloads and return empty state
        }
        return ws;
    }

    public void update(String videoId, int k) {
        cms.add(videoId, 1);
        int estCount = cms.estimate(videoId);
        
        if (topKMap.containsKey(videoId)) {
            HeapItem item = topKMap.get(videoId);
            topKHeap.remove(item);
            item.count = estCount;
            topKHeap.offer(item);
        } else {
            HeapItem item = new HeapItem(estCount, videoId);
            if (topKHeap.size() < k) {
                topKHeap.offer(item);
                topKMap.put(videoId, item);
            } else if (estCount > topKHeap.peek().count) {
                HeapItem removed = topKHeap.poll();
                topKMap.remove(removed.videoId);
                topKHeap.offer(item);
                topKMap.put(videoId, item);
            }
        }
    }
}

public class ViewEventIngestorV2 implements WindowedTopKAggregator, TopKQueryService {
    private final WindowStateStore windowStateStore;
    private final int k;
    private final int sketchWidth;
    private final int sketchDepth;
    private final Map<String, WindowState> windows;
    private final ReentrantLock lock;
    private final long windowSizeMs = 60 * 60 * 1000L;
    private final int maxWindows = 5;
    private final Queue<String> windowKeys = new LinkedList<>();

    public ViewEventIngestorV2(WindowStateStore windowStateStore, int k) {
        this.windowStateStore = windowStateStore;
        this.k = k;
        this.sketchWidth = 1000;
        this.sketchDepth = 5;
        this.windows = new ConcurrentHashMap<>();
        this.lock = new ReentrantLock();
    }
    
    private String getWindowKey(long eventTimeMs) {
        long windowStart = (eventTimeMs / windowSizeMs) * windowSizeMs;
        return "window_" + windowStart;
    }

    @Override
    public void ingest(String videoId, long eventTimeMs) {
        String windowKey = getWindowKey(eventTimeMs);
        
        lock.lock();
        try {
            WindowState window = windows.get(windowKey);
            if (window == null) {
                String payload = windowStateStore.load(windowKey);
                if (payload != null) {
                    window = WindowState.fromPayload(payload, sketchWidth, sketchDepth);
                } else {
                    window = new WindowState(sketchWidth, sketchDepth);
                }
                windows.put(windowKey, window);
                windowKeys.offer(windowKey);
                if (windowKeys.size() > maxWindows) {
                    String oldest = windowKeys.poll();
                    windows.remove(oldest);
                }
            }
                
            window.update(videoId, k);
            
            windowStateStore.save(windowKey, window.toPayload());
        } finally {
            lock.unlock();
        }
    }

    @Override
    public List<String> topK(String windowKey, int k) {
        lock.lock();
        try {
            WindowState window = windows.get(windowKey);
            if (window == null) {
                String payload = windowStateStore.load(windowKey);
                if (payload == null) {
                    return Collections.emptyList();
                }
                window = WindowState.fromPayload(payload, sketchWidth, sketchDepth);
            }
            
            List<HeapItem> items = new ArrayList<>(window.topKHeap);
            items.sort((a, b) -> {
                if (a.count != b.count) {
                    return Integer.compare(b.count, a.count);
                }
                return a.videoId.compareTo(b.videoId);
            });
            
            List<String> result = new ArrayList<>();
            int limit = Math.min(k, items.size());
            for (int i = 0; i < limit; i++) {
                result.add(items.get(i).videoId);
            }
            return result;
        } finally {
            lock.unlock();
        }
    }
}
