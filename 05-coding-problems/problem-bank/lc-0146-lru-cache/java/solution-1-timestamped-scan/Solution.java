import java.util.HashMap;
import java.util.Map;

class LRUCache {
    private final int capacity;
    private final Map<Integer, Entry> entries = new HashMap<>();
    private long clock = 0L;

    public LRUCache(int capacity) {
        this.capacity = capacity;
    }

    public int get(int key) {
        Entry entry = entries.get(key);
        if (entry == null) {
            return -1;
        }
        entry.lastUsed = nextTick();
        return entry.value;
    }

    public void put(int key, int value) {
        Entry existing = entries.get(key);
        if (existing != null) {
            existing.value = value;
            existing.lastUsed = nextTick();
            return;
        }
        if (entries.size() == capacity) {
            evictOldest();
        }
        entries.put(key, new Entry(value, nextTick()));
    }

    private long nextTick() {
        clock += 1;
        return clock;
    }

    private void evictOldest() {
        int oldestKey = 0;
        long oldestTick = Long.MAX_VALUE;
        for (Map.Entry<Integer, Entry> item : entries.entrySet()) {
            if (item.getValue().lastUsed < oldestTick) {
                oldestTick = item.getValue().lastUsed;
                oldestKey = item.getKey();
            }
        }
        entries.remove(oldestKey);
    }

    private static class Entry {
        private int value;
        private long lastUsed;

        private Entry(int value, long lastUsed) {
            this.value = value;
            this.lastUsed = lastUsed;
        }
    }
}
