import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SnowflakeIdGeneratorTest {

    private final long CUSTOM_EPOCH = 1609459200000L;

    @Test
    public void testMonotonicity() {
        SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5);
        long id1 = generator.nextId();
        long id2 = generator.nextId();
        long id3 = generator.nextId();
        
        assertTrue(id1 < id2);
        assertTrue(id2 < id3);
    }

    @Test
    public void testMultiThreadedConcurrency() throws InterruptedException {
        SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5);
        int threadCount = 10;
        int iterations = 1000;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);
        ConcurrentHashMap<Long, Boolean> generatedIds = new ConcurrentHashMap<>();

        for (int i = 0; i < threadCount; i++) {
            executor.submit(() -> {
                for (int j = 0; j < iterations; j++) {
                    long id = generator.nextId();
                    assertNull(generatedIds.putIfAbsent(id, true), "Duplicate ID found: " + id);
                }
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();
        assertEquals(threadCount * iterations, generatedIds.size());
    }

    @Test
    public void testSequenceRollover() {
        SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5) {
            @Override
            protected long timeGen() {
                return CUSTOM_EPOCH + 1000; // Fixed timestamp
            }
            
            @Override
            protected long tilNextMillis(long lastTimestamp) {
                return lastTimestamp + 1;
            }
        };

        for (int i = 0; i < 4096; i++) {
            generator.nextId();
        }
        
        long nextId = generator.nextId(); // Should trigger wait for next millis
        IdComponents components = generator.parse(nextId);
        
        assertEquals(0, components.sequence);
        assertEquals(CUSTOM_EPOCH + 1001, components.timestamp);
    }

    @Test
    public void testClockMovedBackwardsException() {
        SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5) {
            private long currentTime = CUSTOM_EPOCH + 1000;
            
            @Override
            protected long timeGen() {
                return currentTime;
            }

            public void moveClockBackwards() {
                currentTime -= 10; // Move back more than maxClockDriftMs (5)
            }
        };

        generator.nextId();
        
        try {
            // Use reflection or an exposed method in the anonymous subclass to trigger backward time
            generator.getClass().getMethod("moveClockBackwards").invoke(generator);
        } catch (Exception e) {
            fail("Failed to setup backward clock drift test");
        }

        assertThrows(ClockMovedBackwardsException.class, generator::nextId);
    }
    
    @Test
    public void testClockMovedBackwardsSpinWait() {
        SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5) {
            private long currentTime = CUSTOM_EPOCH + 1000;
            
            @Override
            protected long timeGen() {
                return currentTime;
            }
            
            @Override
            protected long tilNextMillis(long lastTimestamp) {
                return lastTimestamp + 1; // Mock next millis resolution
            }

            public void moveClockBackwardsSlightly() {
                currentTime -= 3; // Move back less than maxClockDriftMs (5)
            }
        };

        generator.nextId(); // Sets lastTimestamp to CUSTOM_EPOCH + 1000
        
        try {
            generator.getClass().getMethod("moveClockBackwardsSlightly").invoke(generator);
        } catch (Exception e) {
            fail("Failed to setup backward clock drift test");
        }

        long id = generator.nextId();
        IdComponents components = generator.parse(id);
        assertTrue(components.timestamp > CUSTOM_EPOCH + 1000); // Because it spin-waits
    }
}
