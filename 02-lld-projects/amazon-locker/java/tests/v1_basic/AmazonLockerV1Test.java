import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.*;

public class AmazonLockerV1Test {

    private static final class MutableClock extends java.time.Clock {
        private Instant now;

        private MutableClock(Instant now) {
            this.now = now;
        }

        void advance(Duration duration) {
            this.now = this.now.plus(duration);
        }

        @Override
        public ZoneId getZone() {
            return ZoneOffset.UTC;
        }

        @Override
        public java.time.Clock withZone(ZoneId zone) {
            return this;
        }

        @Override
        public Instant instant() {
            return now;
        }
    }

    @Test
    void exactDepositAndPickupFlow() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(1, 0, 0, clock, Duration.ofDays(1));

        String token = locker.depositPackage(PackageSize.SMALL);
        assertNotNull(token);
        assertNull(locker.depositPackage(PackageSize.SMALL));

        assertTrue(locker.pickup(token));
        assertFalse(locker.pickup(token));
    }

    @Test
    void clearExpiredDepositsReleasesCompartment() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(0, 1, 0, clock, Duration.ofMinutes(5));

        String token = locker.depositPackage(PackageSize.MEDIUM);
        assertNotNull(token);
        clock.advance(Duration.ofMinutes(6));

        assertEquals(1, locker.clearExpiredDeposits());
        assertFalse(locker.pickup(token));
    }
}
