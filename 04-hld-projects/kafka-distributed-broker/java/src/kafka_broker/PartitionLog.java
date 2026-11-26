package kafka_broker;

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
        public final List<Message> messages;
        public final List<int[]> sparseIndex; // {offset, physicalByteOffset}
        public int currentByteOffset;
        public int nextOffset;
        private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

        public Segment(int baseOffset, int maxBytes) {
            this.baseOffset = baseOffset;
            this.maxBytes = maxBytes;
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
                if (startOffset < baseOffset || startOffset >= nextOffset) {
                    return new ArrayList<>();
                }

                int low = 0;
                int high = sparseIndex.size() - 1;
                int bestIdx = 0;

                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (sparseIndex.get(mid)[0] <= startOffset) {
                        bestIdx = mid;
                        low = mid + 1;
                    } else {
                        high = mid - 1;
                    }
                }

                int startIdx = startOffset - baseOffset;
                if (startIdx < 0) {
                    startIdx = 0;
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

    public PartitionLog(int maxSegmentBytes) {
        this.maxSegmentBytes = maxSegmentBytes;
        this.segments = new ArrayList<>();
        this.segments.add(new Segment(0, maxSegmentBytes));
    }

    public int append(byte[] data) {
        lock.writeLock().lock();
        try {
            Segment activeSegment = segments.get(segments.size() - 1);
            Integer offset = activeSegment.append(data);
            if (offset == null) {
                int newBaseOffset = activeSegment.nextOffset;
                Segment newSegment = new Segment(newBaseOffset, maxSegmentBytes);
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

    public List<Message> read(int startOffset, int maxMessages) {
        lock.readLock().lock();
        try {
            List<Message> results = new ArrayList<>();
            int messagesNeeded = maxMessages;
            int currentOffset = startOffset;

            int segmentIdx = 0;
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
}
