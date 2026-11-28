package v2_extended;

/**
 * v2-extended Snowflake ID generator.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Configurable backwards-clock policy (FOLLOW-UPS.md #4, PITFALLS.md
 *    mitigation #1): v1 always throws when the clock moves backwards. v2
 *    adds a WAIT policy that tolerates an NTP correction of up to
 *    maxWaitMillis by blocking until the physical clock catches up to the
 *    last recorded timestamp, exactly the availability-for-consistency
 *    trade the follow-up describes; larger jumps still throw. THROW
 *    remains the default, so v1 behavior is unchanged unless opted in.
 *
 * 2. Dynamic worker-ID leasing (FOLLOW-UPS.md #3, PITFALLS.md #2): see
 *    WorkerIdPool for the ZooKeeper-style ephemeral lease pool.
 *
 * 3. Timestamp-overflow guard (FOLLOW-UPS.md #1): v1 silently emits
 *    negative/invalid IDs once the timestamp delta outgrows the 41-bit
 *    field. v2 raises TimestampOverflowException instead, so the failure
 *    is loud and operators can migrate the epoch or format before
 *    collisions happen.
 */
public class SnowflakeGenerator {

    public enum BackwardsClockPolicy { THROW, WAIT }

    // 41 bits for timestamp, 10 bits for workerId, 12 bits for sequence
    private static final long WORKER_ID_BITS = 10L;
    private static final long SEQUENCE_BITS = 12L;

    private static final long MAX_WORKER_ID = -1L ^ (-1L << WORKER_ID_BITS);
    private static final long SEQUENCE_MASK = -1L ^ (-1L << SEQUENCE_BITS);
    private static final long MAX_TIMESTAMP_DELTA = (1L << 41) - 1L;

    private static final long WORKER_ID_SHIFT = SEQUENCE_BITS;
    private static final long TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS;

    private final long workerId;
    private final long epoch;
    private final Clock clock;
    private final BackwardsClockPolicy backwardsPolicy;
    private final long maxWaitMillis;

    private long sequence = 0L;
    private long lastTimestamp = -1L;

    public SnowflakeGenerator(long workerId, long epoch, Clock clock) {
        this(workerId, epoch, clock, BackwardsClockPolicy.THROW, 10L);
    }

    public SnowflakeGenerator(long workerId, long epoch, Clock clock,
                              BackwardsClockPolicy backwardsPolicy, long maxWaitMillis) {
        if (workerId > MAX_WORKER_ID || workerId < 0) {
            throw new IllegalArgumentException(
                    "worker Id can't be greater than " + MAX_WORKER_ID + " or less than 0");
        }
        if (backwardsPolicy == null) {
            throw new IllegalArgumentException("backwardsPolicy can't be null");
        }
        if (maxWaitMillis < 0) {
            throw new IllegalArgumentException("maxWaitMillis can't be less than 0");
        }
        this.workerId = workerId;
        this.epoch = epoch;
        this.clock = clock;
        this.backwardsPolicy = backwardsPolicy;
        this.maxWaitMillis = maxWaitMillis;
    }

    public synchronized long nextId() {
        long timestamp = clock.currentTimeMillis();

        if (timestamp < lastTimestamp) {
            // Improvement #1: tolerate small NTP corrections under WAIT.
            if (backwardsPolicy == BackwardsClockPolicy.WAIT) {
                timestamp = waitForCatchup(lastTimestamp);
            } else {
                throw new ClockMovedBackwardsException(
                        "Clock moved backwards. Refusing to generate id for "
                                + (lastTimestamp - timestamp) + " milliseconds");
            }
        }

        if (lastTimestamp == timestamp) {
            sequence = (sequence + 1) & SEQUENCE_MASK;
            if (sequence == 0) {
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0;
        }

        // Improvement #3: fail loudly at the 69-year boundary instead of
        // emitting negative or colliding IDs.
        long delta = timestamp - epoch;
        if (delta < 0 || delta > MAX_TIMESTAMP_DELTA) {
            throw new TimestampOverflowException(
                    "Timestamp delta " + delta + "ms does not fit the 41-bit field; "
                            + "migrate the epoch or ID format");
        }

        lastTimestamp = timestamp;

        return (delta << TIMESTAMP_LEFT_SHIFT)
                | (workerId << WORKER_ID_SHIFT)
                | sequence;
    }

    private long waitForCatchup(long targetTimestamp) {
        long timestamp = clock.currentTimeMillis();
        if (targetTimestamp - timestamp > maxWaitMillis) {
            throw new ClockMovedBackwardsException(
                    "Clock moved backwards by " + (targetTimestamp - timestamp)
                            + "ms, beyond the tolerated " + maxWaitMillis + "ms");
        }
        while (timestamp < targetTimestamp) {
            timestamp = clock.currentTimeMillis();
        }
        return timestamp;
    }

    private long waitNextMillis(long targetTimestamp) {
        long timestamp = clock.currentTimeMillis();
        while (timestamp <= targetTimestamp) {
            timestamp = clock.currentTimeMillis();
        }
        return timestamp;
    }
}
