import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class WriteBatcherTest {

    @Test
    public void testFlushByBatchSize() throws Exception {
        List<List<String>> committedBatches = Collections.synchronizedList(new ArrayList<>());
        CountDownLatch latch = new CountDownLatch(1);

        try (WriteBatcher<String> batcher = new WriteBatcher<>(10, 3, 5000, batch -> {
            committedBatches.add(new ArrayList<>(batch));
            latch.countDown();
        })) {
            assertTrue(batcher.write("item1"));
            assertTrue(batcher.write("item2"));

            // Should not have flushed yet
            assertEquals(0, committedBatches.size());

            assertTrue(batcher.write("item3"));

            // Wait for flush
            assertTrue(latch.await(2, TimeUnit.SECONDS));
            assertEquals(1, committedBatches.size());
            assertEquals(3, committedBatches.get(0).size());
            assertTrue(committedBatches.get(0).contains("item1"));
            assertTrue(committedBatches.get(0).contains("item2"));
            assertTrue(committedBatches.get(0).contains("item3"));
        }
    }

    @Test
    public void testFlushByWaitDuration() throws Exception {
        List<List<String>> committedBatches = Collections.synchronizedList(new ArrayList<>());
        CountDownLatch latch = new CountDownLatch(1);

        try (WriteBatcher<String> batcher = new WriteBatcher<>(10, 5, 200, batch -> {
            committedBatches.add(new ArrayList<>(batch));
            latch.countDown();
        })) {
            assertTrue(batcher.write("item1"));
            assertTrue(batcher.write("item2"));

            // Should not have flushed yet immediately
            assertEquals(0, committedBatches.size());

            // Wait for duration to pass
            assertTrue(latch.await(2, TimeUnit.SECONDS));

            assertEquals(1, committedBatches.size());
            assertEquals(2, committedBatches.get(0).size());
        }
    }

    @Test
    public void testBackpressureRejection() throws Exception {
        AtomicInteger commitCount = new AtomicInteger(0);
        // Small capacity (equals batch threshold), long wait to simulate slow consumer
        try (WriteBatcher<String> batcher = new WriteBatcher<>(2, 2, 5000, batch -> {
            try {
                Thread.sleep(100); // Slow down consumer to force buffer full
            } catch (InterruptedException e) {}
            commitCount.incrementAndGet();
        })) {
            assertTrue(batcher.write("item1"));
            assertTrue(batcher.write("item2"));

            // At this point buffer might be polled but let's send more fast
            batcher.write("item3");
            boolean rejected = !batcher.write("item4") || !batcher.write("item5") || !batcher.write("item6");

            // At least one should have failed
            assertTrue(rejected);
        }
    }

    @Test
    public void testFlushOnClose() throws Exception {
        List<List<String>> committedBatches = Collections.synchronizedList(new ArrayList<>());

        WriteBatcher<String> batcher = new WriteBatcher<>(10, 5, 5000, batch -> {
            committedBatches.add(new ArrayList<>(batch));
        });

        assertTrue(batcher.write("item1"));
        assertTrue(batcher.write("item2"));

        batcher.close(); // Should trigger flush of remaining items

        assertEquals(1, committedBatches.size());
        assertEquals(2, committedBatches.get(0).size());

        assertThrows(IllegalStateException.class, () -> batcher.write("item3"), "Should throw on write after close");
    }
}
