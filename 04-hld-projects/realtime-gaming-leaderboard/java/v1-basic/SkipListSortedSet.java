// no package here because requirements typically use default package for tests if source uses default package
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentSkipListSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class SkipListSortedSet {
    public static class Entry implements Comparable<Entry> {
        public final String userId;
        public final int score;
        public final long timestamp;

        public Entry(String userId, int score, long timestamp) {
            this.userId = userId;
            this.score = score;
            this.timestamp = timestamp;
        }

        @Override
        public int compareTo(Entry other) {
            if (this.score != other.score) {
                return Integer.compare(other.score, this.score);
            }
            if (this.timestamp != other.timestamp) {
                return Long.compare(this.timestamp, other.timestamp);
            }
            return this.userId.compareTo(other.userId);
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            Entry entry = (Entry) obj;
            return score == entry.score &&
                   timestamp == entry.timestamp &&
                   Objects.equals(userId, entry.userId);
        }

        @Override
        public int hashCode() {
            return Objects.hash(userId, score, timestamp);
        }
    }

    private final Set<Entry> sortedSet;
    private final Map<String, Entry> userMap;

    public SkipListSortedSet() {
        this.sortedSet = new ConcurrentSkipListSet<>();
        this.userMap = new ConcurrentHashMap<>();
    }

    public synchronized void updateScore(String userId, int newScore, long timestamp) {
        Entry oldEntry = userMap.get(userId);
        if (oldEntry != null) {
            sortedSet.remove(oldEntry);
        }
        Entry newEntry = new Entry(userId, newScore, timestamp);
        sortedSet.add(newEntry);
        userMap.put(userId, newEntry);
    }
    
    public synchronized void removeUser(String userId) {
        Entry oldEntry = userMap.remove(userId);
        if (oldEntry != null) {
            sortedSet.remove(oldEntry);
        }
    }

    public synchronized List<Entry> getTopK(int k) {
        List<Entry> topK = new ArrayList<>();
        for (Entry entry : sortedSet) {
            if (topK.size() >= k) {
                break;
            }
            topK.add(entry);
        }
        return topK;
    }

    public synchronized int getRank(String userId) {
        Entry userEntry = userMap.get(userId);
        if (userEntry == null) {
            return -1;
        }
        int rank = 1;
        for (Entry entry : sortedSet) {
            if (entry.equals(userEntry)) {
                return rank;
            }
            rank++;
        }
        return -1;
    }
    
    public synchronized Integer getScore(String userId) {
        Entry userEntry = userMap.get(userId);
        return userEntry != null ? userEntry.score : null;
    }

    public synchronized List<Entry> getRelativeWindow(String userId, int radius) {
        int rank = getRank(userId);
        if (rank == -1) return new ArrayList<>();

        List<Entry> window = new ArrayList<>();
        int currentRank = 1;
        int minRank = Math.max(1, rank - radius);
        int maxRank = rank + radius;

        for (Entry entry : sortedSet) {
            if (currentRank >= minRank && currentRank <= maxRank) {
                window.add(entry);
            }
            if (currentRank > maxRank) {
                break;
            }
            currentRank++;
        }
        return window;
    }
    
    public int size() {
        return userMap.size();
    }
    
    public Iterable<Entry> entries() {
        return sortedSet;
    }
}
