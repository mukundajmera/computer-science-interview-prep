package v1_basic;

import java.util.ArrayList;
import java.util.Deque;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class LiveManifestManager {
    private final int windowSize;
    private final Map<String, Deque<Segment>> manifests = new ConcurrentHashMap<>();
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
            Deque<Segment> deque = manifests.get(streamId);
            if (deque.size() == windowSize) {
                deque.pollFirst();
            }
            deque.addLast(new Segment(rendition, segmentUrl));
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
}
