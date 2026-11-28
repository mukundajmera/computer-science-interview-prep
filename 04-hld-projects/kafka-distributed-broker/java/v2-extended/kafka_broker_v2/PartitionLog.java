package kafka_broker_v2;

import java.util.function.LongSupplier;

/**
 * v2 PartitionLog: retention policies and disk monitoring (improvement #1).
 *
 * Implements FOLLOW-UPS.md #2: size-based and time-based segment deletion
 * plus a disk usage reading. Retention only ever deletes whole inactive
 * segments from the head, exactly like real Kafka; the active segment is
 * never deleted, and reading a deleted offset still raises the v1
 * OffsetOutOfRange error. See BrokerCluster for the full v2 list.
 */

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class PartitionLog {

    public static class Message {
        public final int offset;
        public final byte[] data;

        public Message(int offset, byte[] data) {
            this.offset = offset;
            this.data = data;
        }
    }

    public static class Segment {
        public final int baseOffset;
        public final int maxBytes;
        public final long createdAtMillis;
        public final List<Message> messages;
        public final List<int[]> sparseIndex; // {offset, physicalByteOffset}
        public int currentByteOffset;
        public int nextOffset;
        private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

        public Segment(int baseOffset, int maxBytes, long createdAtMillis) {
            this.baseOffset = baseOffset;
            this.maxBytes = maxBytes;
            this.createdAtMillis = createdAtMillis;
            this.messages = new ArrayList<>();
            this.sparseIndex = new ArrayList<>();
            this.currentByteOffset = 0;
            this.nextOffset = baseOffset;
        }

        public Integer append(byte[] data) {
            lock.writeLock().lock();
            try {
                int msgSize = data.length;
                if (currentByteOffset + msgSize > maxBytes && !messages.isEmpty()) {
                    return null; // Segment is full
                }
                int offset = nextOffset;
                messages.add(new Message(offset, data));

                if (messages.size() % 2 == 1) {
                    sparseIndex.add(new int[]{offset, currentByteOffset});
                }

                currentByteOffset += msgSize;
                nextOffset++;
                return offset;
            } finally {
                lock.writeLock().unlock();
            }
        }

        public List<Message> read(int startOffset, int maxMessages) {
            lock.readLock().lock();
            try {
                if (startOffset < baseOffset || startOffset > nextOffset) {
                    return new ArrayList<>();
                }

                int low = 0;
                int high = sparseIndex.size() - 1;
                int bestIdx = -1;

                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (sparseIndex.get(mid)[0] <= startOffset) {
                        bestIdx = mid;
                        low = mid + 1;
                    } else {
                        high = mid - 1;
                    }
                }

                int startIdx = 0;
                while (startIdx < messages.size() && messages.get(startIdx).offset < startOffset) {
                    startIdx++;
                }

                List<Message> result = new ArrayList<>();
                for (int i = startIdx; i < Math.min(messages.size(), startIdx + maxMessages); i++) {
                    result.add(messages.get(i));
                }
                return result;
            } finally {
                lock.readLock().unlock();
            }
        }
    }

    private final int maxSegmentBytes;
    private final List<Segment> segments;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    private final LongSupplier clockMillis;

    public PartitionLog(int maxSegmentBytes) {
        this(maxSegmentBytes, System::currentTimeMillis);
    }

    public PartitionLog(int maxSegmentBytes, LongSupplier clockMillis) {
        this.maxSegmentBytes = maxSegmentBytes;
        this.clockMillis = clockMillis;
        this.segments = new ArrayList<>();
        this.segments.add(new Segment(0, maxSegmentBytes, clockMillis.getAsLong()));
    }

    public int append(byte[] data) {
        lock.writeLock().lock();
        try {
            Segment activeSegment = segments.get(segments.size() - 1);
            Integer offset = activeSegment.append(data);
            if (offset == null) {
                int newBaseOffset = activeSegment.nextOffset;
                Segment newSegment = new Segment(newBaseOffset, maxSegmentBytes, clockMillis.getAsLong());
                segments.add(newSegment);
                offset = newSegment.append(data);
                if (offset == null) {
                    throw new RuntimeException("Message too large for a single segment");
                }
            }
            return offset;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void truncateTo(int offset) {
        lock.writeLock().lock();
        try {
            segments.removeIf(seg -> seg.baseOffset > offset);
            if (segments.isEmpty()) {
                Segment seg = new Segment(offset, maxSegmentBytes, clockMillis.getAsLong());
                segments.add(seg);
                return;
            }

            Segment lastSeg = segments.get(segments.size() - 1);
            lastSeg.lock.writeLock().lock();
            try {
                lastSeg.messages.removeIf(m -> m.offset >= offset);
                lastSeg.sparseIndex.removeIf(idx -> idx[0] >= offset);
                lastSeg.nextOffset = offset;
                
                int newByteOffset = 0;
                for (Message m : lastSeg.messages) {
                    newByteOffset += m.data.length;
                }
                lastSeg.currentByteOffset = newByteOffset;
            } finally {
                lastSeg.lock.writeLock().unlock();
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public List<Message> read(int startOffset, int maxMessages) {
        lock.readLock().lock();
        try {
            if (segments.isEmpty()) {
                return new ArrayList<>();
            }
            int earliestOffset = segments.get(0).messages.isEmpty() ? segments.get(0).baseOffset : segments.get(0).messages.get(0).offset;
            if (startOffset < earliestOffset) {
                throw new IllegalArgumentException("OffsetOutOfRange: Retention gap");
            }
            if (startOffset > getLogEndOffset()) {
                throw new IllegalArgumentException("OffsetOutOfRange: Invalid future offset");
            }

            List<Message> results = new ArrayList<>();
            int messagesNeeded = maxMessages;
            int currentOffset = startOffset;

            int segmentIdx = -1;
            int low = 0;
            int high = segments.size() - 1;

            while (low <= high) {
                int mid = low + (high - low) / 2;
                if (segments.get(mid).baseOffset <= currentOffset) {
                    segmentIdx = mid;
                    low = mid + 1;
                } else {
                    high = mid - 1;
                }
            }

            if (segmentIdx == -1) {
                return new ArrayList<>();
            }

            for (int i = segmentIdx; i < segments.size(); i++) {
                Segment segment = segments.get(i);
                List<Message> msgs = segment.read(currentOffset, messagesNeeded);
                results.addAll(msgs);
                messagesNeeded -= msgs.size();
                if (messagesNeeded <= 0) {
                    break;
                }
                if (!msgs.isEmpty()) {
                    currentOffset = msgs.get(msgs.size() - 1).offset + 1;
                } else {
                    break;
                }
            }
            return results;
        } finally {
            lock.readLock().unlock();
        }
    }

    public int getLogEndOffset() {
        lock.readLock().lock();
        try {
            return segments.get(segments.size() - 1).nextOffset;
        } finally {
            lock.readLock().unlock();
        }
    }
    // --- Improvement #1: retention + disk monitoring (FOLLOW-UPS.md #2) ---

    /** Total bytes held across all segments, the number a disk monitor would watch. */
    public long diskUsageBytes() {
        lock.readLock().lock();
        try {
            long total = 0;
            for (Segment seg : segments) {
                total += seg.currentByteOffset;
            }
            return total;
        } finally {
            lock.readLock().unlock();
        }
    }

    /**
     * Deletes whole inactive segments from the head while the total size
     * exceeds maxTotalBytes or the segment is older than maxAgeMillis. The
     * active (last) segment is never deleted. Returns the number of
     * segments deleted. Pass null for a policy dimension you do not want.
     */
    public int enforceRetention(Long maxTotalBytes, Long maxAgeMillis) {
        lock.writeLock().lock();
        try {
            long nowMillis = clockMillis.getAsLong();
            int deleted = 0;
            while (segments.size() > 1) {
                Segment head = segments.get(0);
                boolean overSize = maxTotalBytes != null && diskUsageBytes() > maxTotalBytes;
                boolean overAge = maxAgeMillis != null && nowMillis - head.createdAtMillis > maxAgeMillis;
                if (!overSize && !overAge) {
                    break;
                }
                segments.remove(0);
                deleted++;
            }
            return deleted;
        } finally {
            lock.writeLock().unlock();
        }
    }
}
