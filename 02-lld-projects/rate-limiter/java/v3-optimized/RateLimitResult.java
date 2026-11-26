import java.util.HashMap;
import java.util.Map;

/**
 * Rate Limiter - V3 Optimized
 * 
 * Enhanced RateLimitResult with rich information.
 */
public class RateLimitResult {
    private final boolean allowed;
    private final int remainingRequests;
    private final long resetTimeMs;
    private final long retryAfterMs;
    private final String algorithmUsed;

    /**
     * Compatibility constructor used by simpler token-bucket style call sites.
     */
    public RateLimitResult(boolean allowed, int remainingRequests, long resetTimeMs) {
        this.allowed = allowed;
        this.remainingRequests = remainingRequests;
        this.resetTimeMs = resetTimeMs;
        this.retryAfterMs = 0;
        this.algorithmUsed = "token-bucket";
    }

    private RateLimitResult(Builder builder) {
        this.allowed = builder.allowed;
        this.remainingRequests = builder.remainingRequests;
        this.resetTimeMs = builder.resetTimeMs;
        this.retryAfterMs = builder.retryAfterMs;
        this.algorithmUsed = builder.algorithmUsed;
    }

    public boolean isAllowed() {
        return allowed;
    }

    public int getRemainingRequests() {
        return remainingRequests;
    }

    public long getResetTimeMs() {
        return resetTimeMs;
    }

    public long getRetryAfterMs() {
        return retryAfterMs;
    }

    public String getAlgorithmUsed() {
        return algorithmUsed;
    }

    /**
     * Get rate limit headers for HTTP response.
     */
    public Map<String, String> getHeaders() {
        Map<String, String> headers = new HashMap<>();
        headers.put("X-RateLimit-Remaining", String.valueOf(remainingRequests));
        headers.put("X-RateLimit-Reset", String.valueOf(resetTimeMs / 1000));
        if (!allowed) {
            headers.put("Retry-After", String.valueOf(retryAfterMs / 1000));
        }
        return headers;
    }

    @Override
    public String toString() {
        return String.format(
            "RateLimitResult{allowed=%s, remaining=%d, resetMs=%d, retryAfterMs=%d, algorithm=%s}",
            allowed, remainingRequests, resetTimeMs, retryAfterMs, algorithmUsed
        );
    }

    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private boolean allowed;
        private int remainingRequests;
        private long resetTimeMs;
        private long retryAfterMs;
        private String algorithmUsed = "unknown";

        public Builder allowed(boolean allowed) {
            this.allowed = allowed;
            return this;
        }

        public Builder remainingRequests(int remaining) {
            this.remainingRequests = remaining;
            return this;
        }

        public Builder resetTimeMs(long resetTimeMs) {
            this.resetTimeMs = resetTimeMs;
            return this;
        }

        public Builder retryAfterMs(long retryAfterMs) {
            this.retryAfterMs = retryAfterMs;
            return this;
        }

        public Builder algorithmUsed(String algorithm) {
            this.algorithmUsed = algorithm;
            return this;
        }

        public RateLimitResult build() {
            return new RateLimitResult(this);
        }
    }
}
