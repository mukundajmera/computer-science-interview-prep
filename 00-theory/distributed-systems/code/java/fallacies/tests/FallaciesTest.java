package fallacies.tests;

import fallacies.FallaciesDemo;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;

public class FallaciesTest {

    public static void main(String[] args) {
        System.out.println("Starting FallaciesTest...");
        int passed = 0;
        int failed = 0;

        try {
            testRetrySuccess();
            System.out.println("testRetrySuccess: PASSED");
            passed++;
        } catch (Throwable t) {
            System.err.println("testRetrySuccess: FAILED - " + t.getMessage());
            failed++;
        }

        try {
            testRetryFailure();
            System.out.println("testRetryFailure: PASSED");
            passed++;
        } catch (Throwable t) {
            System.err.println("testRetryFailure: FAILED - " + t.getMessage());
            failed++;
        }
        
        try {
            testTimeout();
            System.out.println("testTimeout: PASSED");
            passed++;
        } catch (Throwable t) {
            System.err.println("testTimeout: FAILED - " + t.getMessage());
            failed++;
        }

        try {
            testChunking();
            System.out.println("testChunking: PASSED");
            passed++;
        } catch (Throwable t) {
            System.err.println("testChunking: FAILED - " + t.getMessage());
            failed++;
        }

        System.out.println("-----------------------------------");
        System.out.println("Tests passed: " + passed);
        System.out.println("Tests failed: " + failed);

        if (failed > 0) {
            System.exit(1);
        }
    }

    private static void assertEquals(Object expected, Object actual, String message) {
        if (expected == null && actual == null) return;
        if (expected != null && expected.equals(actual)) return;
        throw new AssertionError(message + " - Expected: " + expected + ", Actual: " + actual);
    }
    
    private static void assertTrue(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    // Simulates a network call that fails a specific number of times before succeeding
    static class FlakyNetworkCall implements Callable<String> {
        private int attempts = 0;
        private final int failuresBeforeSuccess;

        public FlakyNetworkCall(int failuresBeforeSuccess) {
            this.failuresBeforeSuccess = failuresBeforeSuccess;
        }

        @Override
        public String call() throws Exception {
            attempts++;
            if (attempts <= failuresBeforeSuccess) {
                throw new FallaciesDemo.NetworkException("Network error on attempt " + attempts);
            }
            return "Success!";
        }
    }

    private static void testRetrySuccess() throws Exception {
        // Will fail 2 times, then succeed. We allow 3 retries (4 attempts total).
        FlakyNetworkCall call = new FlakyNetworkCall(2);
        String result = FallaciesDemo.callWithRetryAndTimeout(call, 3, 1000);
        assertEquals("Success!", result, "Result should be success after retries");
    }

    private static void testRetryFailure() {
        // Will fail 4 times before success, but we only allow 2 retries (3 attempts).
        FlakyNetworkCall call = new FlakyNetworkCall(4);
        try {
            FallaciesDemo.callWithRetryAndTimeout(call, 2, 1000);
            throw new AssertionError("Expected to fail after exceeding retries");
        } catch (Exception e) {
            assertTrue(e.getMessage().contains("Operation failed after 2 retries"), "Exception message should indicate max retries reached");
        }
    }

    private static void testTimeout() {
        // Simulating a call that always times out
        Callable<String> timeoutCall = () -> {
            throw new FallaciesDemo.TimeoutException("Connection timed out");
        };

        try {
            FallaciesDemo.callWithRetryAndTimeout(timeoutCall, 1, 100);
            throw new AssertionError("Expected to fail due to timeout");
        } catch (Exception e) {
            assertTrue(e.getMessage().contains("Connection timed out"), "Exception should wrap the timeout error");
        }
    }

    private static void testChunking() {
        List<Integer> data = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        List<List<Integer>> chunks = FallaciesDemo.chunkData(data, 3);
        
        assertEquals(4, chunks.size(), "Should be 4 chunks for 10 items with chunk size 3");
        assertEquals(Arrays.asList(1, 2, 3), chunks.get(0), "First chunk mismatch");
        assertEquals(Arrays.asList(4, 5, 6), chunks.get(1), "Second chunk mismatch");
        assertEquals(Arrays.asList(7, 8, 9), chunks.get(2), "Third chunk mismatch");
        assertEquals(Arrays.asList(10), chunks.get(3), "Fourth chunk mismatch");
    }
}
