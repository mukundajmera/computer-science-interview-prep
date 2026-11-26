import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

public class AmazonLockerV3Test {

    private static final class MutableClock implements Clock {
        private Instant now;

        private MutableClock(Instant now) {
            this.now = now;
        }

        void advance(Duration duration) {
            this.now = this.now.plus(duration);
        }

        @Override
        public Instant now() {
            return now;
        }
    }

    @Test
    void reservationConfirmAndPickupFlow() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(1, 0, 0, clock, Duration.ofDays(1), Duration.ofMinutes(5), new FallbackSizePolicy());

        String reservationId = locker.reserveCompartment(PackageSize.SMALL);
        assertEquals("R-1", reservationId);

        String token = locker.confirmDeposit(reservationId);
        assertEquals("T-1", token);
        assertTrue(locker.pickup(token));
    }

    @Test
    void expiredReservationCannotBeConfirmed() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(1, 0, 0, clock, Duration.ofDays(1), Duration.ofMinutes(1), new FallbackSizePolicy());

        String reservationId = locker.reserveCompartment(PackageSize.SMALL);
        clock.advance(Duration.ofMinutes(2));

        assertNull(locker.confirmDeposit(reservationId));
        assertEquals(0, locker.expireReservations());
    }

    @Test
    void clearExpiredDepositsRemovesToken() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(1, 0, 0, clock, Duration.ofMinutes(1), Duration.ofMinutes(5), new FallbackSizePolicy());

        String token = locker.depositPackage(PackageSize.SMALL);
        clock.advance(Duration.ofMinutes(2));

        assertEquals(1, locker.clearExpiredDeposits());
        assertFalse(locker.pickup(token));
    }
}
