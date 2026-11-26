import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

public class IdempotencyStoreTest {
    @Test
    void shouldReturnOriginalResponseForRetry() {
        IdempotencyStore store = new IdempotencyStore();
        String first = store.processCreateRequest("k1", "order-1");
        String retry = store.processCreateRequest("k1", "order-2");
        assertEquals("order-1", first);
        assertEquals(first, retry);
    }

    @Test
    void concurrentRetriesShouldShareOneResponse() throws Exception {
        int requestCount = 8;
        IdempotencyStore store = new IdempotencyStore();
        ExecutorService executor = Executors.newFixedThreadPool(requestCount);
        CountDownLatch ready = new CountDownLatch(requestCount);
        CountDownLatch start = new CountDownLatch(1);
        List<Future<String>> futures = new ArrayList<>();

        try {
            for (int i = 0; i < requestCount; i++) {
                String generatedId = "order-" + i;
                futures.add(executor.submit(() -> {
                    ready.countDown();
                    if (!start.await(2, TimeUnit.SECONDS)) {
                        throw new IllegalStateException("start signal timed out");
                    }
                    return store.processCreateRequest("same-key", generatedId);
                }));
            }

            assertTrue(ready.await(2, TimeUnit.SECONDS), "workers did not become ready");
            start.countDown();
            Set<String> responses = new HashSet<>();
            for (Future<String> future : futures) {
                responses.add(future.get(2, TimeUnit.SECONDS));
            }
            assertEquals(1, responses.size());
        } finally {
            start.countDown();
            executor.shutdownNow();
            assertTrue(executor.awaitTermination(2, TimeUnit.SECONDS));
        }
    }
}
