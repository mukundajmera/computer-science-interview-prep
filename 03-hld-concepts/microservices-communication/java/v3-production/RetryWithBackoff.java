/**
 * V3: Retry with Exponential Backoff and Jitter
 * 
 * Production-grade retry mechanism for transient failures.
 */

import java.util.Random;
import java.util.concurrent.Callable;

public class RetryWithBackoff {
    
    private final int maxRetries;
    private final long initialDelayMs;
    private final double multiplier;
    private final long maxDelayMs;
    private final double jitterFactor;
    private final Random random = new Random();
    
    public RetryWithBackoff(int maxRetries, long initialDelayMs, 
                           double multiplier, long maxDelayMs, double jitterFactor) {
        this.maxRetries = maxRetries;
        this.initialDelayMs = initialDelayMs;
        this.multiplier = multiplier;
        this.maxDelayMs = maxDelayMs;
        this.jitterFactor = jitterFactor;
    }
    
    public <T> T execute(Callable<T> action) throws Exception {
        Exception lastException = null;
        long delay = initialDelayMs;
        
        for (int attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                System.out.printf("Attempt %d/%d%n", attempt, maxRetries);
                return action.call();
            } catch (Exception e) {
                lastException = e;
                System.out.printf("Attempt %d failed: %s%n", attempt, e.getMessage());
                
                if (attempt < maxRetries) {
                    long jitter = (long)(delay * jitterFactor * random.nextDouble());
                    long sleepTime = Math.min(delay + jitter, maxDelayMs);
                    System.out.printf("Waiting %dms before retry%n", sleepTime);
                    Thread.sleep(sleepTime);
                    delay = (long)(delay * multiplier);
                }
            }
        }
        
        throw new RuntimeException("All retries failed", lastException);
    }
    
    public static RetryWithBackoff defaultConfig() {
        return new RetryWithBackoff(
            3,      // max retries
            100,    // initial delay 100ms
            2.0,    // double each time
            5000,   // max 5 seconds
            0.3     // 30% jitter
        );
    }
    
    public static void main(String[] args) {
        RetryWithBackoff retry = RetryWithBackoff.defaultConfig();
        
        int[] attemptCounter = {0};
        
        try {
            String result = retry.execute(() -> {
                attemptCounter[0]++;
                if (attemptCounter[0] < 3) {
                    throw new RuntimeException("Transient failure");
                }
                return "Success on attempt " + attemptCounter[0];
            });
            System.out.println("\nFinal result: " + result);
        } catch (Exception e) {
            System.out.println("Failed: " + e.getMessage());
        }
    }
}
