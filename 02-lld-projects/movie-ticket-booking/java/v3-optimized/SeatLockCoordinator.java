import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Coordinates short-lived seat lock ownership tokens for a show.
 */
public class SeatLockCoordinator {
    private final Map<String, SeatLockToken> activeLocks;

    public SeatLockCoordinator() {
        this.activeLocks = new ConcurrentHashMap<String, SeatLockToken>();
    }

    public SeatLockToken acquire(String showId, List<String> seatIds, String userId, long ttlMs) {
        if (showId == null || seatIds == null || seatIds.isEmpty() || userId == null) {
            return null;
        }

        cleanupExpired();

        String tokenId = UUID.randomUUID().toString();
        long expiresAt = System.currentTimeMillis() + Math.max(1000L, ttlMs);
        SeatLockToken token = new SeatLockToken(tokenId, showId, seatIds, userId, expiresAt);
        activeLocks.put(tokenId, token);
        return token;
    }

    public boolean isActive(String tokenId) {
        SeatLockToken token = activeLocks.get(tokenId);
        if (token == null) {
            return false;
        }
        if (token.isExpired()) {
            activeLocks.remove(tokenId);
            return false;
        }
        return true;
    }

    public boolean release(String tokenId) {
        return activeLocks.remove(tokenId) != null;
    }

    public int cleanupExpired() {
        int removed = 0;
        for (Map.Entry<String, SeatLockToken> entry : activeLocks.entrySet()) {
            if (entry.getValue().isExpired() && activeLocks.remove(entry.getKey(), entry.getValue())) {
                removed++;
            }
        }
        return removed;
    }

    public int activeLockCount() {
        cleanupExpired();
        return activeLocks.size();
    }

    public static final class SeatLockToken {
        private final String tokenId;
        private final String showId;
        private final List<String> seatIds;
        private final String userId;
        private final long expiresAtMs;

        private SeatLockToken(String tokenId, String showId, List<String> seatIds, String userId, long expiresAtMs) {
            this.tokenId = tokenId;
            this.showId = showId;
            this.seatIds = Collections.unmodifiableList(new ArrayList<String>(seatIds));
            this.userId = userId;
            this.expiresAtMs = expiresAtMs;
        }

        public String getTokenId() { return tokenId; }
        public String getShowId() { return showId; }
        public List<String> getSeatIds() { return seatIds; }
        public String getUserId() { return userId; }
        public long getExpiresAtMs() { return expiresAtMs; }

        public boolean isExpired() {
            return System.currentTimeMillis() >= expiresAtMs;
        }
    }
}
