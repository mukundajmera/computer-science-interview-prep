import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class CircularRingBufferReplayStore implements CommentReplayStore {
    
    private static class RingBuffer {
        private final String[] buffer;
        private final int capacity;
        private final AtomicLong sequenceGenerator;
        
        public RingBuffer(int capacity) {
            this.capacity = capacity;
            this.buffer = new String[capacity];
            this.sequenceGenerator = new AtomicLong(0);
        }
        
        public void add(String message) {
            long seq = sequenceGenerator.incrementAndGet();
            synchronized (this) {
                int index = (int) (seq % capacity);
                buffer[index] = message;
            }
        }
        
        public synchronized List<String> replay(String cursorStr, int limit) {
            long cursor = 0;
            boolean hasCursor = cursorStr != null && !cursorStr.isEmpty();
            if (hasCursor) {
                try { cursor = Long.parseLong(cursorStr); } catch (NumberFormatException e) {}
            }
            
            long maxSeq = sequenceGenerator.get();
            long oldestAvailable = Math.max(1, maxSeq - capacity + 1);
            
            List<String> result = new ArrayList<>();
            
            // A bounded replay ring emits a documented sequence gap on overflow
            boolean isGap = hasCursor && cursor < oldestAvailable - 1;
            if (isGap) {
                result.add("[GAP] Sequence gap detected on overflow");
                cursor = oldestAvailable - 1;
            }
            
            long startSeq;
            if (hasCursor) {
                startSeq = Math.max(cursor + 1, oldestAvailable);
            } else {
                startSeq = Math.max(oldestAvailable, maxSeq - limit + 1);
            }
            
            long endSeq = maxSeq;
            
            for (long seq = startSeq; seq <= endSeq; seq++) {
                int index = (int) (seq % capacity);
                String comment = buffer[index];
                if (comment != null) {
                    result.add(comment);
                }
            }
            
            if (hasCursor && result.size() > limit) {
                return result.subList(0, limit);
            }
            return result;
        }
    }

    private final Map<String, RingBuffer> streamBuffers = new ConcurrentHashMap<>();
    private final int bufferCapacity;

    public CircularRingBufferReplayStore(int bufferCapacity) {
        this.bufferCapacity = bufferCapacity;
    }
    
    public void addComment(String streamId, String commentPayload) {
        streamBuffers.computeIfAbsent(streamId, k -> new RingBuffer(bufferCapacity)).add(commentPayload);
    }

    @Override
    public List<String> replay(String streamId, String cursor, int limit) {
        RingBuffer buffer = streamBuffers.get(streamId);
        if (buffer == null) {
            return new ArrayList<>();
        }
        return buffer.replay(cursor, limit);
    }
}
