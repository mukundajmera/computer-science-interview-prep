package v1_basic;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class CommentIngressService {
    
    private static class RingBuffer {
        private final LiveComment[] buffer;
        private final int capacity;
        private final AtomicLong sequenceGenerator;
        
        public RingBuffer(int capacity) {
            this.capacity = capacity;
            this.buffer = new LiveComment[capacity];
            this.sequenceGenerator = new AtomicLong(0);
        }
        
        public LiveComment publish(String videoId, String userId, String message) {
            long seq = sequenceGenerator.incrementAndGet();
            LiveComment comment = new LiveComment(
                UUID.randomUUID().toString(),
                videoId,
                userId,
                message,
                System.currentTimeMillis(),
                seq
            );
            
            // Volatile write essentially by array? No, simple array is not volatile.
            // But we can synchronize or use AtomicReferenceArray for strict thread-safety
            // on publish since multiple threads might write concurrently. 
            // The prompt allows ConcurrentHashMap and AtomicLong. Let's use synchronization
            // for the actual array write to make sure get/put are consistent.
            
            // A simple implementation for high throughput:
            synchronized (this) {
                int index = (int) (seq % capacity);
                buffer[index] = comment;
            }
            return comment;
        }
        
        public synchronized List<LiveComment> getRecent(int limit) {
            long maxSeq = sequenceGenerator.get();
            int count = (int) Math.min(limit, Math.min(maxSeq, capacity));
            List<LiveComment> result = new ArrayList<>(count);
            
            for (int i = 0; i < count; i++) {
                long currentSeq = maxSeq - i;
                int index = (int) (currentSeq % capacity);
                LiveComment comment = buffer[index];
                if (comment != null && comment.getSequenceNumber() == currentSeq) {
                    result.add(comment);
                }
            }
            return result;
        }
        
        public synchronized List<LiveComment> getSince(long lastSeq) {
            long maxSeq = sequenceGenerator.get();
            if (lastSeq >= maxSeq) {
                return new ArrayList<>();
            }
            
            // Limit to capacity elements
            long startSeq = Math.max(lastSeq + 1, maxSeq - capacity + 1);
            int count = (int) (maxSeq - startSeq + 1);
            
            List<LiveComment> result = new ArrayList<>(count);
            for (long seq = startSeq; seq <= maxSeq; seq++) {
                int index = (int) (seq % capacity);
                LiveComment comment = buffer[index];
                if (comment != null && comment.getSequenceNumber() == seq) {
                    result.add(comment);
                }
            }
            return result;
        }
    }

    private final ConcurrentHashMap<String, RingBuffer> videoRooms = new ConcurrentHashMap<>();
    private final int bufferCapacity;

    public CommentIngressService() {
        this(1000);
    }
    
    public CommentIngressService(int bufferCapacity) {
        this.bufferCapacity = bufferCapacity;
    }

    public LiveComment publishComment(String videoId, String userId, String message) {
        RingBuffer buffer = videoRooms.computeIfAbsent(videoId, k -> new RingBuffer(bufferCapacity));
        return buffer.publish(videoId, userId, message);
    }

    public List<LiveComment> getRecentComments(String videoId, int limit) {
        RingBuffer buffer = videoRooms.get(videoId);
        if (buffer == null) {
            return new ArrayList<>();
        }
        return buffer.getRecent(limit);
    }

    public List<LiveComment> getCommentsSince(String videoId, long sequenceNumber) {
        RingBuffer buffer = videoRooms.get(videoId);
        if (buffer == null) {
            return new ArrayList<>();
        }
        return buffer.getSince(sequenceNumber);
    }
}
