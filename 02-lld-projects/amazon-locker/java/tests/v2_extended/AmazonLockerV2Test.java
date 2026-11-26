import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.*;

public class AmazonLockerV2Test {

    private static final class MutableClock extends java.time.Clock {
        private Instant now;

        private MutableClock(Instant now) {
            this.now = now;
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
    void fallbackPolicyCanUseLargerCompartment() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(0, 0, 1, clock, Duration.ofDays(1), new ExactSizePolicy());

        assertNull(locker.depositPackage(PackageSize.SMALL));
        locker.setAllocationPolicy(new FallbackSizePolicy());

        String token = locker.depositPackage(PackageSize.SMALL);
        assertNotNull(token);
        assertTrue(locker.pickup(token));
    }

    @Test
    void outOfServiceCompartmentIsSkipped() {
        MutableClock clock = new MutableClock(Instant.parse("2026-01-01T00:00:00Z"));
        Locker locker = new Locker(1, 0, 0, clock, Duration.ofDays(1), new ExactSizePolicy());

        assertTrue(locker.markCompartmentOutOfService("S-1"));
        assertNull(locker.depositPackage(PackageSize.SMALL));
    }
}
