import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class PastebinServiceTest {

    private PastebinService service;

    @BeforeEach
    public void setUp() {
        // Default service with plenty of capacity
        service = new PastebinService(10, 1.0);
    }

    @Test
    public void testBase62DeterministicEncoding() {
        assertEquals("0", Base62Encoder.encode(0));
        assertEquals("1", Base62Encoder.encode(1));
        assertEquals("a", Base62Encoder.encode(10));
        assertEquals("A", Base62Encoder.encode(36));
        assertEquals("Z", Base62Encoder.encode(61));
        assertEquals("10", Base62Encoder.encode(62));

        long[] testNums = {0, 1, 62, 1000, 1000000000L};
        for (long num : testNums) {
            assertEquals(num, Base62Encoder.decode(Base62Encoder.encode(num)));
        }
    }

    @Test
    public void testCreateAndRetrievePasteSuccess() {
        String content = "Hello, Java Pastebin!";
        String ip = "127.0.0.1";

        String shortLink = service.createPaste(content, ip);
        assertNotNull(shortLink);
        assertTrue(shortLink.length() >= 7);

        String retrieved = service.getPaste(shortLink);
        assertEquals(content, retrieved);
    }

    @Test
    public void testExpiredPasteReturns404() throws InterruptedException {
        String content = "Ephemeral content";
        String ip = "127.0.0.2";

        String shortLink = service.createPaste(content, ip, 1L);
        assertNotNull(shortLink);

        // Immediately accessible
        assertEquals(content, service.getPaste(shortLink));

        // Wait for expiration
        Thread.sleep(1100);

        // Passive expiration on read
        assertNull(service.getPaste(shortLink));
    }

    @Test
    public void testRateLimitingThrottlesSpam() {
        // Capacity 2, fill rate 0.5 tokens/sec
        PastebinService strictService = new PastebinService(2, 0.5);
        String ip = "127.0.0.3";

        String link1 = strictService.createPaste("1", ip);
        String link2 = strictService.createPaste("2", ip);
        String link3 = strictService.createPaste("3", ip);

        assertNotNull(link1);
        assertNotNull(link2);
        assertNull(link3); // Should be rate limited
    }

    @Test
    public void testTtlCleanerDeletesExpiredEntries() throws InterruptedException {
        String ip = "127.0.0.4";

        String link1 = service.createPaste("Persist", ip);
        String link2 = service.createPaste("Die1", ip, 1L);
        String link3 = service.createPaste("Die2", ip, 1L);

        assertNotNull(link1);
        assertNotNull(link2);
        assertNotNull(link3);

        // Before expiration
        assertEquals(0, service.sweepExpiredPastes());

        // Wait for expiration
        Thread.sleep(1100);

        // Sweeper should clean up expired pastes
        assertEquals(2, service.sweepExpiredPastes());

        // Links should be gone
        assertNull(service.getPaste(link2));
        assertNull(service.getPaste(link3));
        // Persistent link remains
        assertEquals("Persist", service.getPaste(link1));
    }
}