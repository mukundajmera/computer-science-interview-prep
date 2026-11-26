package fallacies;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;

/**
 * Fallacies of Distributed Computing - Demo
 * This class demonstrates three common fallacies:
 * 1. The network is reliable (Requires Retry/Timeout)
 * 2. Latency is zero (Requires Timeout/Asynchronous handling)
 * 3. Bandwidth is infinite (Requires Chunking/Pagination)
 */
public class FallaciesDemo {

    // --- Fallacy 1 & 2: The Network is Reliable / Latency is Zero ---
    // We simulate a network call that can fail or take too long.

    public static class NetworkException extends Exception {
        public NetworkException(String message) {
            super(message);
        }
    }

    public static class TimeoutException extends Exception {
        public TimeoutException(String message) {
            super(message);
        }
    }

    /**
     * Simulates a network call with retries and a timeout.
     * @param networkCall The simulated network operation.
     * @param maxRetries Maximum number of retries before giving up.
     * @param timeoutMs Timeout in milliseconds for each attempt.
     * @return The result of the network call.
     * @throws Exception If all retries fail or timeout occurs on all attempts.
     */
    public static <T> T callWithRetryAndTimeout(Callable<T> networkCall, int maxRetries, long timeoutMs) throws Exception {
        int attempt = 0;
        Exception lastException = null;

        while (attempt <= maxRetries) {
            try {
                // In a real application, timeout would involve threads/futures.
                // Here we just execute it. The Callable itself will simulate the timeout failure.
                return networkCall.call();
            } catch (NetworkException | TimeoutException e) {
                lastException = e;
                attempt++;
                if (attempt <= maxRetries) {
                    // Backoff could be added here
                    System.out.println("Attempt " + attempt + " failed. Retrying...");
                }
            }
        }
        throw new Exception("Operation failed after " + maxRetries + " retries. Last error: " + lastException.getMessage());
    }

    // --- Fallacy 3: Bandwidth is Infinite ---
    // We simulate sending a large dataset over the network, which requires chunking.

    /**
     * Simulates processing a large dataset by breaking it into chunks to avoid overwhelming bandwidth.
     * @param data The large list of data items.
     * @param chunkSize The maximum size of each chunk.
     * @return A list of chunks (each chunk is a list of items).
     */
    public static <T> List<List<T>> chunkData(List<T> data, int chunkSize) {
        if (chunkSize <= 0) {
            throw new IllegalArgumentException("Chunk size must be greater than 0");
        }
        List<List<T>> chunks = new ArrayList<>();
        for (int i = 0; i < data.size(); i += chunkSize) {
            int end = Math.min(i + chunkSize, data.size());
            chunks.add(new ArrayList<>(data.subList(i, end)));
        }
        return chunks;
    }

}
