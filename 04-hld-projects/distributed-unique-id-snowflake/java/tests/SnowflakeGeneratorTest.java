package tests;

import v1_basic.Clock;
import v1_basic.ClockMovedBackwardsException;
import v1_basic.SnowflakeGenerator;

public class SnowflakeGeneratorTest {

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
        testNextId();
        testSequenceRollover();
        testClockMovedBackwards();
        System.out.println("All Java tests passed.");
    }

    private static void testNextId() {
        MockClock clock = new MockClock();
        long epoch = 0L;
        SnowflakeGenerator generator = new SnowflakeGenerator(1, epoch, clock);

        long id1 = generator.nextId();
        long id2 = generator.nextId();

        // 1000 << 22 = 4194304000
        // 1 << 12 = 4096
        // seq = 0 for id1, 1 for id2
        assert id1 == ((1000L << 22) | (1L << 12) | 0L) : "Unexpected id1";
        assert id2 == ((1000L << 22) | (1L << 12) | 1L) : "Unexpected id2";

        clock.advanceMillis(1);
        long id3 = generator.nextId();
        assert id3 == ((1001L << 22) | (1L << 12) | 0L) : "Unexpected id3";
        
        System.out.println("testNextId passed.");
    }

    private static void testSequenceRollover() {
        MockClock clock = new MockClock() {
            int calls = 0;
            @Override
            public long currentTimeMillis() {
                // Return 1000 for the first 4096 calls, then advance to 1001
                if (calls <= 4096) {
                    calls++;
                    return 1000L;
                }
                return 1001L;
            }
        };
        long epoch = 0L;
        SnowflakeGenerator generator = new SnowflakeGenerator(1, epoch, clock);

        for (int i = 0; i < 4096; i++) {
            long id = generator.nextId();
            assert id == ((1000L << 22) | (1L << 12) | i) : "Unexpected id during loop";
        }

        // 4097th call should rollover sequence and wait for next ms (1001)
        long id = generator.nextId();
        assert id == ((1001L << 22) | (1L << 12) | 0L) : "Unexpected id after rollover";
        
        System.out.println("testSequenceRollover passed.");
    }

    private static void testClockMovedBackwards() {
        MockClock clock = new MockClock();
        long epoch = 0L;
        SnowflakeGenerator generator = new SnowflakeGenerator(1, epoch, clock);

        generator.nextId(); // time = 1000
        clock.setTime(999); // clock moved backward
        
        try {
            generator.nextId();
            assert false : "Expected ClockMovedBackwardsException to be thrown";
        } catch (ClockMovedBackwardsException e) {
            // Expected
        }
        
        System.out.println("testClockMovedBackwards passed.");
    }
}
