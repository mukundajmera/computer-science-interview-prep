/**
 * Ticketing Platform - V2 Scaled
 * Skeleton for distributed seat hold coordination and release.
 */

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public class SeatHoldCoordinator {

    public static class HoldToken {
        private final String holdId;
        private final String eventId;
        private final String userId;
        private final List<String> seatIds;
        private final Instant expiresAt;

        public HoldToken(String holdId, String eventId, String userId, List<String> seatIds, Instant expiresAt) {
            this.holdId = holdId;
            this.eventId = eventId;
            this.userId = userId;
            this.seatIds = seatIds;
            this.expiresAt = expiresAt;
        }

        public String getHoldId() { return holdId; }
        public String getEventId() { return eventId; }
        public String getUserId() { return userId; }
        public List<String> getSeatIds() { return seatIds; }
        public Instant getExpiresAt() { return expiresAt; }
    }

    public interface LockStore {
        boolean tryLockSeat(String eventId, String seatId, String holdId, Instant expiresAt);
        void unlockSeat(String eventId, String seatId, String holdId);
        Optional<String> currentOwner(String eventId, String seatId);
    }

    public interface HoldLedger {
        HoldToken save(HoldToken token);
        Optional<HoldToken> find(String holdId);
        void markExpired(String holdId);
    }

    private final LockStore lockStore;
    private final HoldLedger ledger;

    public SeatHoldCoordinator(LockStore lockStore, HoldLedger ledger) {
        this.lockStore = lockStore;
        this.ledger = ledger;
    }

    public HoldToken reserveSeats(String userId, String eventId, List<String> seatIds, int ttlSeconds) {
        String holdId = UUID.randomUUID().toString();
        Instant expiresAt = Instant.now().plusSeconds(ttlSeconds);

        List<String> acquired = new ArrayList<>();
        try {
            for (String seatId : seatIds) {
                if (lockStore.tryLockSeat(eventId, seatId, holdId, expiresAt)) {
                    acquired.add(seatId);
                } else {
                    throw new RuntimeException("Seat " + seatId + " is already held or booked");
                }
            }

            HoldToken token = new HoldToken(
                holdId,
                eventId,
                userId,
                seatIds,
                expiresAt
            );
            return ledger.save(token);
        } catch (Exception e) {
            for (String seatId : acquired) {
                lockStore.unlockSeat(eventId, seatId, holdId);
            }
            throw e;
        }
    }

    public boolean releaseSeats(String holdId, String reason) {
        Optional<HoldToken> tokenOpt = ledger.find(holdId);
        if (tokenOpt.isEmpty()) {
            return false;
        }

        HoldToken token = tokenOpt.get();
        for (String seatId : token.getSeatIds()) {
            lockStore.unlockSeat(token.getEventId(), seatId, holdId);
        }

        ledger.markExpired(holdId);
        return true;
    }

    public int expireStaleHolds(Instant now) {
        // Handled by Redis TTL usually. Can be mocked.
        return 0;
    }
}
