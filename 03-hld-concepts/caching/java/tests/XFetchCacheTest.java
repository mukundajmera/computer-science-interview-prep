package tests;

import v4_xfetch.SingleflightMutex;
import v4_xfetch.XFetchCache;
import org.junit.jupiter.api.Test;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class XFetchCacheTest {

    @Test
    public void testSingleflightDeduplication() throws Exception {
        SingleflightMutex sf = new SingleflightMutex();
        AtomicInteger callCount = new AtomicInteger(0);

        Callable<SingleflightMutex.Result> worker = () -> sf.doCall("key1", () -> {
            callCount.incrementAndGet();
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "result";
        });

        ExecutorService executor = Executors.newFixedThreadPool(5);
        Future<SingleflightMutex.Result>[] futures = new Future[5];
        for (int i = 0; i < 5; i++) {
            futures[i] = executor.submit(worker);
        }

        int sharedCount = 0;
        for (int i = 0; i < 5; i++) {
            SingleflightMutex.Result res = futures[i].get();
            assertEquals("result", res.value);
            if (res.shared) {
                sharedCount++;
            }
        }

        assertEquals(1, callCount.get(), "Loader should only be executed once");
        assertEquals(4, sharedCount, "4 requests should have shared the result");
        executor.shutdown();
    }

    @Test
    public void testXFetchProbabilisticRefresh() throws Exception {
        long[] clockVal = {1000L};
        double[] rngVal = {0.5};

        XFetchCache cache = new XFetchCache(
                1.0,
                () -> clockVal[0],
                () -> rngVal[0],
                2
        );

        // Delta will be 200ms
        AtomicInteger loaderCalls = new AtomicInteger(0);

        // Initial get
        Object val = cache.get("key", () -> {
            loaderCalls.incrementAndGet();
            clockVal[0] += 200L;
            return "data";
        }, 1000L); // 1000ms TTL

        assertEquals("data", val);
        assertEquals(1, loaderCalls.get());
        
        // Initial get happens at 1000L. Loader finishes at 1200L.
        // Created at = 1200L. Expires at = 2200L. Delta = 200L.

        // Fast forward to 1700L. Remaining TTL = 2200L - 1700L = 500L.
        clockVal[0] = 1700L;

        // threshold = -beta * delta * ln(u) = -1.0 * 200 * ln(u)
        // Refresh if threshold >= 500 => ln(u) <= -2.5 => u <= e^-2.5 (~0.082)

        // Try with u = 0.5 (should not refresh)
        rngVal[0] = 0.5;
        cache.get("key", () -> {
            loaderCalls.incrementAndGet();
            clockVal[0] += 200L;
            return "newdata";
        }, 1000L);

        Thread.sleep(100); // Give background thread a chance if it were to run
        assertEquals(1, loaderCalls.get(), "Should not have refreshed");

        // Try with u = 0.05 (should refresh)
        rngVal[0] = 0.05;
        cache.get("key", () -> {
            loaderCalls.incrementAndGet();
            clockVal[0] += 200L;
            return "newdata";
        }, 1000L);

        // The background thread should now run the loader
        Thread.sleep(150);
        
        assertEquals(2, loaderCalls.get(), "Should have refreshed in background");

        cache.shutdown();
    }
}
