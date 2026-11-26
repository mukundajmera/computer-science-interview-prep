import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.zip.CRC32;

/** Simple hash and range partitioning helpers. */
public class DataPartitioner {
    private final int partitionCount;

    public DataPartitioner(int partitionCount) {
        if (partitionCount <= 0) {
            throw new IllegalArgumentException("partitionCount must be > 0");
        }
        this.partitionCount = partitionCount;
    }

    public int hashPartition(String key) {
        if (key == null) {
            throw new IllegalArgumentException("key must not be null");
        }
        CRC32 checksum = new CRC32();
        checksum.update(key.getBytes(StandardCharsets.UTF_8));
        return (int) (checksum.getValue() % partitionCount);
    }

    public int rangePartition(int value, List<IntRange> ranges) {
        if (ranges == null || ranges.isEmpty()) {
            throw new IllegalArgumentException("ranges must not be empty");
        }
        int previousEnd = 0;
        boolean hasPrevious = false;
        for (IntRange range : ranges) {
            if (range == null || range.start() > range.end()) {
                throw new IllegalArgumentException("range boundaries are invalid");
            }
            if (hasPrevious && range.start() <= previousEnd) {
                throw new IllegalArgumentException("ranges must be ordered and non-overlapping");
            }
            previousEnd = range.end();
            hasPrevious = true;
        }
        for (int i = 0; i < ranges.size(); i++) {
            IntRange range = ranges.get(i);
            if (value >= range.start() && value <= range.end()) {
                return i;
            }
        }
        throw new IllegalArgumentException("value outside configured ranges");
    }

    public static final class IntRange {
        private final int start;
        private final int end;

        public IntRange(int start, int end) {
            this.start = start;
            this.end = end;
        }

        public int start() {
            return start;
        }

        public int end() {
            return end;
        }
    }
}
