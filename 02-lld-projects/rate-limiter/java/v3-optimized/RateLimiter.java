import java.util.HashMap;
import java.util.Map;

/**
 * Rate Limiter - V3 Optimized
 *
 * Backward-compatible skeleton that supports:
 * - local token bucket limiting
 * - optional distributed quota delegation
 * - pluggable algorithm constructor signatures expected by factory code
 */
public class RateLimiter {
    private final TokenBucket tokenBucket;
    private final Map<String, TokenBucketState> tokenBucketStates;

    private final RateLimitAlgorithm distributedAlgorithm;
    private final RateLimitConfig distributedConfig;
    private final Map<String, ClientState> distributedStates;
    private final DistributedQuotaStore distributedQuotaStore;

    private final boolean distributedMode;

    public RateLimiter(RateLimitConfig config) {
        this.tokenBucket = new TokenBucket(config);
        this.tokenBucketStates = new HashMap<>();

        this.distributedAlgorithm = null;
        this.distributedConfig = null;
        this.distributedStates = null;
        this.distributedQuotaStore = null;
        this.distributedMode = false;
    }

    public RateLimiter(RateLimitAlgorithm algorithm, RateLimitConfig config) {
        this(algorithm, config, defaultWindowSizeMs(config) * 2L, true, null);
    }

    public RateLimiter(
        RateLimitAlgorithm algorithm,
        RateLimitConfig config,
        long cleanupIntervalMs,
        boolean enableCleanup
    ) {
        this(algorithm, config, cleanupIntervalMs, enableCleanup, null);
    }

    public RateLimiter(
        RateLimitAlgorithm algorithm,
        RateLimitConfig config,
        long cleanupIntervalMs,
        boolean enableCleanup,
        DistributedQuotaStore distributedQuotaStore
    ) {
        this.tokenBucket = null;
        this.tokenBucketStates = null;

        this.distributedAlgorithm = algorithm;
        this.distributedConfig = config;
        this.distributedStates = new HashMap<>();
        this.distributedQuotaStore = distributedQuotaStore;
        this.distributedMode = true;
    }

    public RateLimitResult allowRequest(String clientKey) {
        if (clientKey == null || clientKey.isEmpty()) {
            throw new IllegalArgumentException("Client key cannot be null or empty");
        }

        if (!distributedMode) {
            TokenBucketState state = tokenBucketStates.computeIfAbsent(
                clientKey,
                k -> tokenBucket.createInitialState()
            );
            return tokenBucket.tryAcquire(state);
        }

        if (distributedQuotaStore != null) {
            DistributedQuotaStore.QuotaDecision decision = distributedQuotaStore.consume(
                clientKey,
                distributedConfig.getBucketCapacity(),
                defaultWindowSizeMs(distributedConfig),
                System.currentTimeMillis()
            );
            return new RateLimitResult(
                decision.allowed(),
                decision.remainingRequests(),
                decision.resetTimeMs()
            );
        }

        ClientState state = distributedStates.computeIfAbsent(
            clientKey,
            k -> distributedAlgorithm.createInitialState()
        );
        return distributedAlgorithm.tryAcquire(state, distributedConfig);
    }

    public int getRemainingRequests(String clientKey) {
        if (!distributedMode) {
            TokenBucketState state = tokenBucketStates.get(clientKey);
            if (state == null) {
                return tokenBucket.getRemainingTokens(tokenBucket.createInitialState());
            }
            return tokenBucket.getRemainingTokens(state);
        }

        if (distributedQuotaStore != null) {
            DistributedQuotaStore.QuotaDecision decision = distributedQuotaStore.peek(
                clientKey,
                distributedConfig.getBucketCapacity(),
                defaultWindowSizeMs(distributedConfig),
                System.currentTimeMillis()
            );
            return decision.remainingRequests();
        }

        ClientState state = distributedStates.get(clientKey);
        if (state == null) {
            return distributedConfig.getBucketCapacity();
        }
        return distributedAlgorithm.getRemainingRequests(state, distributedConfig);
    }

    public void resetClient(String clientKey) {
        if (!distributedMode) {
            tokenBucketStates.remove(clientKey);
            return;
        }
        distributedStates.remove(clientKey);
    }

    public int getClientCount() {
        if (!distributedMode) {
            return tokenBucketStates.size();
        }
        return distributedStates.size();
    }

    private static long defaultWindowSizeMs(RateLimitConfig config) {
        double refillRatePerMs = config.getRefillRatePerMs();
        if (refillRatePerMs <= 0.0) {
            return 1000L;
        }
        return Math.max(1L, (long) (config.getBucketCapacity() / refillRatePerMs));
    }
}

/**
 * External quota abstraction for distributed limiting.
 */
interface DistributedQuotaStore {
    QuotaDecision consume(String clientKey, int maxRequests, long windowSizeMs, long nowMs);
    QuotaDecision peek(String clientKey, int maxRequests, long windowSizeMs, long nowMs);

    record QuotaDecision(
        boolean allowed,
        int remainingRequests,
        long resetTimeMs,
        long retryAfterMs
    ) {}
}
