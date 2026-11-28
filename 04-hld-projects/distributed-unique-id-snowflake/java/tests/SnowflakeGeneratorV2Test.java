package tests;

import v2_extended.Clock;
import v2_extended.ClockMovedBackwardsException;
import v2_extended.SnowflakeGenerator;
import v2_extended.TimestampOverflowException;
import v2_extended.WorkerIdPool;
import v2_extended.WorkerIdPoolExhaustedException;

public class SnowflakeGeneratorV2Test {

    static class MockClock implements Clock {
        long time = 1000L;

        @Override
        public long currentTimeMillis() {
            return time;
        }

        public void advanceMillis(long millis) {
            time += millis;
        }

        public void setTime(long time) {
            this.time = time;
        }
    }

    public static void main(String[] args) {
        // Parity with the v1 scenarios
        testNextId();
        testSequenceRollover();
        testClockMovedBackwardsThrowsByDefault();
        // Improvement #1: configurable backwards-clock policy
        testWaitPolicyToleratesSmallBackwardsJump();
        testWaitPolicyRejectsJumpBeyondTolerance();
        // Improvement #3: timestamp-overflow guard
        testOverflowGuardRaisesBeyond41Bits();
        testOverflowGuardAllowsMaxDelta();
        // Improvement #2: dynamic worker-ID leasing
        testPoolAcquireIsCollisionProof();
        testPoolReleaseReturnsIdToPool();
        testPoolExhaustionIsLoud();
        testPoolReleaseUnleasedIdRaises();
        System.out.println("All SnowflakeGeneratorV2 Java tests passed.");
    }

    // --- Parity ---

    static void testNextId() {
        MockClock clk = new MockClock();
        SnowflakeGenerator generator = new SnowflakeGenerator(1, 0, clk);

        assertEquals((1000L << 22) | (1L << 12) | 0, generator.nextId(), "first id");
        assertEquals((1000L << 22) | (1L << 12) | 1, generator.nextId(), "second id");

        clk.advanceMillis(1);
        assertEquals((1001L << 22) | (1L << 12) | 0, generator.nextId(), "id after tick");
    }

    static void testSequenceRollover() {
        Clock rolloverClock = new Clock() {
            long calls = 0;

            @Override
            public long currentTimeMillis() {
                if (calls <= 4096) {
                    calls++;
                    return 1000L;
                }
                return 1001L;
            }
        };
        SnowflakeGenerator generator = new SnowflakeGenerator(1, 0, rolloverClock);
        for (long i = 0; i < 4096; i++) {
            assertEquals((1000L << 22) | (1L << 12) | i, generator.nextId(), "sequence " + i);
        }
        assertEquals((1001L << 22) | (1L << 12) | 0, generator.nextId(), "rollover id");
    }

    static void testClockMovedBackwardsThrowsByDefault() {
        MockClock clk = new MockClock();
        SnowflakeGenerator generator = new SnowflakeGenerator(1, 0, clk);
        generator.nextId(); // time = 1000
        clk.setTime(999);
        expectThrows(ClockMovedBackwardsException.class, generator::nextId, "default THROW policy");
    }

    // --- Improvement #1: backwards-clock policy ---

    static void testWaitPolicyToleratesSmallBackwardsJump() {
        Clock recoveringClock = new Clock() {
            long reads = 0;

            @Override
            public long currentTimeMillis() {
                reads++;
                if (reads == 1) {
                    return 1000L;
                }
                if (reads <= 6) {
                    return 995L + (reads - 2); // 995..999, then 1000
                }
                return 1000L;
            }
        };
        SnowflakeGenerator generator = new SnowflakeGenerator(
                1, 0, recoveringClock, SnowflakeGenerator.BackwardsClockPolicy.WAIT, 5);

        assertEquals((1000L << 22) | (1L << 12) | 0, generator.nextId(), "first id");
        // Clock dipped to 995, then recovered; the generator blocked until
        // it caught up to 1000 and continued the same-millisecond sequence.
        assertEquals((1000L << 22) | (1L << 12) | 1, generator.nextId(), "id after catchup");
    }

    static void testWaitPolicyRejectsJumpBeyondTolerance() {
        MockClock clk = new MockClock();
        SnowflakeGenerator generator = new SnowflakeGenerator(
                1, 0, clk, SnowflakeGenerator.BackwardsClockPolicy.WAIT, 10);
        generator.nextId(); // time = 1000
        clk.setTime(900); // 100ms backwards, beyond the 10ms tolerance
        expectThrows(ClockMovedBackwardsException.class, generator::nextId, "large backwards jump");
    }

    // --- Improvement #3: timestamp-overflow guard ---

    static void testOverflowGuardRaisesBeyond41Bits() {
        MockClock clk = new MockClock();
        SnowflakeGenerator generator = new SnowflakeGenerator(1, 0, clk);
        clk.setTime(1L << 41); // one millisecond past the 41-bit delta field
        expectThrows(TimestampOverflowException.class, generator::nextId, "overflow");
    }

    static void testOverflowGuardAllowsMaxDelta() {
        MockClock clk = new MockClock();
        SnowflakeGenerator generator = new SnowflakeGenerator(1, 0, clk);
        clk.setTime((1L << 41) - 1);
        long expected = (((1L << 41) - 1) << 22) | (1L << 12) | 0;
        assertEquals(expected, generator.nextId(), "max delta id");
    }

    // --- Improvement #2: worker-ID leasing ---

    static void testPoolAcquireIsCollisionProof() {
        WorkerIdPool pool = new WorkerIdPool();
        int first = pool.acquire();
        int second = pool.acquire();
        if (first == second) {
            throw new AssertionError("Leased IDs must be unique");
        }
        if (first != 0 || second != 1) {
            throw new AssertionError("Expected lowest free IDs to be leased first");
        }
        if (!pool.isLeased(first) || !pool.isLeased(second)) {
            throw new AssertionError("Both IDs should show as leased");
        }
    }

    static void testPoolReleaseReturnsIdToPool() {
        WorkerIdPool pool = new WorkerIdPool();
        int workerId = pool.acquire();
        pool.release(workerId);
        if (pool.isLeased(workerId)) {
            throw new AssertionError("Released ID should no longer be leased");
        }
        if (pool.acquire() != workerId) {
            throw new AssertionError("A replacement node should pick the freed ID up again");
        }
    }

    static void testPoolExhaustionIsLoud() {
        WorkerIdPool pool = new WorkerIdPool(1);
        pool.acquire();
        pool.acquire();
        if (pool.leasedCount() != 2) {
            throw new AssertionError("Expected 2 leased IDs");
        }
        expectThrows(WorkerIdPoolExhaustedException.class, pool::acquire, "exhaustion");
    }

    static void testPoolReleaseUnleasedIdRaises() {
        WorkerIdPool pool = new WorkerIdPool();
        expectThrows(IllegalArgumentException.class, () -> pool.release(7), "unleased release");
    }

    // --- Helpers ---

    static void assertEquals(long expected, long actual, String label) {
        if (expected != actual) {
            throw new AssertionError(label + ": expected " + expected + " but got " + actual);
        }
    }

    static void expectThrows(Class<? extends RuntimeException> type, Runnable action, String label) {
        try {
            action.run();
        } catch (RuntimeException e) {
            if (type.isInstance(e)) {
                return;
            }
            throw new AssertionError(label + ": expected " + type.getSimpleName()
                    + " but got " + e.getClass().getSimpleName());
        }
        throw new AssertionError(label + ": expected " + type.getSimpleName() + " but nothing was thrown");
    }
}
