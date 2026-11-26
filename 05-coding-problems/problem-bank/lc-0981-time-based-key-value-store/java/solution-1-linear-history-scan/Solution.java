import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class TimeMap {
    private static class Entry {
        final int timestamp;
        final String value;

        Entry(int timestamp, String value) {
            this.timestamp = timestamp;
            this.value = value;
        }
    }

    private final Map<String, List<Entry>> values = new HashMap<>();

    public void set(String key, String value, int timestamp) {
        values.computeIfAbsent(key, ignored -> new ArrayList<>()).add(new Entry(timestamp, value));
    }

    public String get(String key, int timestamp) {
        List<Entry> history = values.get(key);
        if (history == null) {
            return "";
        }
        for (int i = history.size() - 1; i >= 0; i--) {
            Entry entry = history.get(i);
            if (entry.timestamp <= timestamp) {
                return entry.value;
            }
        }
        return "";
    }
}
