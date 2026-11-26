package v4_xfetch;

import java.util.concurrent.*;
import java.util.function.Supplier;

/**
 * Singleflight deduplicates concurrent function calls for the same key.
 * When multiple threads ask for the same key simultaneously, only the first
 * one evaluates the function, while others wait for and share the result.
 */
public class SingleflightMutex {
    private final ConcurrentHashMap<Object, CompletableFuture<Result>> calls = new ConcurrentHashMap<>();

    public static class Result {
        public final Object value;
        public final Exception error;
        public final boolean shared;

        public Result(Object value, Exception error, boolean shared) {
            this.value = value;
            this.error = error;
            this.shared = shared;
        }
    }

    /**
     * Executes the supplier function if it's the first time for this key.
     * Otherwise waits for the existing computation to complete.
     */
    public Result doCall(Object key, Supplier<Object> fn) {
        CompletableFuture<Result> newFuture = new CompletableFuture<>();
        CompletableFuture<Result> existingFuture = calls.putIfAbsent(key, newFuture);

        if (existingFuture != null) {
            // Already in flight, wait for result
            try {
                Result r = existingFuture.join();
                return new Result(r.value, r.error, true); // Mark as shared
            } catch (Exception e) {
                return new Result(null, e, true);
            }
        }

        // We are the first, evaluate
        try {
            Object value = fn.get();
            Result res = new Result(value, null, false);
            newFuture.complete(res);
            return res;
        } catch (Exception e) {
            Result res = new Result(null, e, false);
            newFuture.complete(res);
            return res;
        } finally {
            // Ensure we remove it so subsequent calls re-evaluate if needed
            calls.remove(key, newFuture);
        }
    }
}
