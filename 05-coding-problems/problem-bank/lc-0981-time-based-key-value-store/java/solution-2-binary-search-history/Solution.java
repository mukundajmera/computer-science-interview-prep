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
        int left = 0;
        int right = history.size() - 1;
        String answer = "";
        while (left <= right) {
            int mid = left + (right - left) / 2;
            Entry entry = history.get(mid);
            if (entry.timestamp <= timestamp) {
                answer = entry.value;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return answer;
    }
}
