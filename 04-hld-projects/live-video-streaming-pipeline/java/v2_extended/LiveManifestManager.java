package v2_extended;

import java.util.ArrayList;
import java.util.Deque;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * v2 LiveManifestManager: v1 sliding window plus improvement #3,
 * live-to-VOD archival (FOLLOW-UPS.md #4). The sliding window keeps
 * serving the live manifest while a complete segment history lets a
 * finished stream become a permanent VOD playlist.
 * See OriginShieldTree for the full v2 list.
 */
public class LiveManifestManager {
    private final int windowSize;
    private final Map<String, Deque<Segment>> manifests = new ConcurrentHashMap<>();
    private final Map<String, List<Segment>> history = new ConcurrentHashMap<>();
    private final Map<String, Lock> streamLocks = new ConcurrentHashMap<>();

    public LiveManifestManager(int windowSize) {
        this.windowSize = windowSize;
    }

    public LiveManifestManager() {
        this(5);
    }

    public static class Segment {
        public final String rendition;
        public final String url;

        public Segment(String rendition, String url) {
            this.rendition = rendition;
            this.url = url;
        }
    }

    public void appendSegment(String streamId, String rendition, String segmentUrl) {
        streamLocks.putIfAbsent(streamId, new ReentrantLock());
        Lock lock = streamLocks.get(streamId);
        lock.lock();
        try {
            manifests.putIfAbsent(streamId, new LinkedList<>());
            history.putIfAbsent(streamId, new ArrayList<>());
            Deque<Segment> deque = manifests.get(streamId);
            if (deque.size() == windowSize) {
                deque.pollFirst();
            }
            Segment segment = new Segment(rendition, segmentUrl);
            deque.addLast(segment);
            history.get(streamId).add(segment);
        } finally {
            lock.unlock();
        }
    }

    public List<Segment> getManifest(String streamId) {
        streamLocks.putIfAbsent(streamId, new ReentrantLock());
        Lock lock = streamLocks.get(streamId);
        lock.lock();
        try {
            if (manifests.containsKey(streamId)) {
                return new ArrayList<>(manifests.get(streamId));
            }
            return new ArrayList<>();
        } finally {
            lock.unlock();
        }
    }

    /**
     * Convert the stream's full history into a permanent VOD playlist.
     * The sliding live window drops old segments; the VOD asset must
     * contain every segment in broadcast order (FOLLOW-UPS.md #4).
     * Idempotent: archiving twice returns the same playlist.
     */
    public List<Segment> archiveVod(String streamId) {
        streamLocks.putIfAbsent(streamId, new ReentrantLock());
        Lock lock = streamLocks.get(streamId);
        lock.lock();
        try {
            if (history.containsKey(streamId)) {
                return new ArrayList<>(history.get(streamId));
            }
            return new ArrayList<>();
        } finally {
            lock.unlock();
        }
    }
}
