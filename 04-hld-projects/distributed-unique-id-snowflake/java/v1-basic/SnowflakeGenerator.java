package v1_basic;

public class SnowflakeGenerator {

    // 41 bits for timestamp
    // 10 bits for workerId
    // 12 bits for sequence
    private static final long WORKER_ID_BITS = 10L;
    private static final long SEQUENCE_BITS = 12L;

    private static final long MAX_WORKER_ID = -1L ^ (-1L << WORKER_ID_BITS);
    private static final long SEQUENCE_MASK = -1L ^ (-1L << SEQUENCE_BITS);

    private static final long WORKER_ID_SHIFT = SEQUENCE_BITS;
    private static final long TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS;

    // Custom epoch (e.g., 2023-10-25)
    private final long epoch;
    private final long workerId;
    private final Clock clock;

    private long sequence = 0L;
    private long lastTimestamp = -1L;

    public SnowflakeGenerator(long workerId, long epoch, Clock clock) {
        if (workerId > MAX_WORKER_ID || workerId < 0) {
            throw new IllegalArgumentException(String.format("worker Id can't be greater than %d or less than 0", MAX_WORKER_ID));
        }
        this.workerId = workerId;
        this.epoch = epoch;
        this.clock = clock;
    }

    public synchronized long nextId() {
        long timestamp = clock.currentTimeMillis();

        if (timestamp < lastTimestamp) {
            throw new ClockMovedBackwardsException(
                    String.format("Clock moved backwards. Refusing to generate id for %d milliseconds", lastTimestamp - timestamp));
        }

        if (lastTimestamp == timestamp) {
            sequence = (sequence + 1) & SEQUENCE_MASK;
            if (sequence == 0) {
                // Sequence exhausted, wait for next millisecond
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0L;
        }

        lastTimestamp = timestamp;

        return ((timestamp - epoch) << TIMESTAMP_LEFT_SHIFT)
                | (workerId << WORKER_ID_SHIFT)
                | sequence;
    }

    private long waitNextMillis(long lastTimestamp) {
        long timestamp = clock.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = clock.currentTimeMillis();
        }
        return timestamp;
    }
}
