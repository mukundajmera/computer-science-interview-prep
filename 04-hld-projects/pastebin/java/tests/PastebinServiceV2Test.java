import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

public class PastebinServiceV2Test {

    // ------------------------------------------------------------------
    // v1 parity tests: same scenarios as PastebinServiceTest, run against
    // v2.
    // ------------------------------------------------------------------

    @Test
    public void testBase62DeterministicEncoding() {
        assertEquals("0", Base62EncoderV2.encode(0));
        assertEquals("1", Base62EncoderV2.encode(1));
        assertEquals("a", Base62EncoderV2.encode(10));
        assertEquals("A", Base62EncoderV2.encode(36));
        assertEquals("Z", Base62EncoderV2.encode(61));
        assertEquals("10", Base62EncoderV2.encode(62));

        long[] testNums = {0, 1, 62, 1000, 1000000000L};
        for (long num : testNums) {
            assertEquals(num, Base62EncoderV2.decode(Base62EncoderV2.encode(num)));
        }
    }

    @Test
    public void testCreateAndRetrievePasteSuccess() {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
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
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
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
        PastebinServiceV2 strictService = new PastebinServiceV2(2, 0.5);
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
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
        String ip = "127.0.0.4";

        String link1 = service.createPaste("Persist", ip);
        String link2 = service.createPaste("Die1", ip, 1L);
        String link3 = service.createPaste("Die2", ip, 1L);

        assertNotNull(link1);
        assertNotNull(link2);
        assertNotNull(link3);

        // Before expiration
        assertEquals(0, service.sweepExpiredPastes());

        Thread.sleep(1100);

        // Sweeper should clean up expired pastes
        assertEquals(2, service.sweepExpiredPastes());

        // Links should be gone
        assertNull(service.getPaste(link2));
        assertNull(service.getPaste(link3));
        // Persistent link remains
        assertEquals("Persist", service.getPaste(link1));
    }

    // ------------------------------------------------------------------
    // v2-only tests: one or more per improvement.
    // ------------------------------------------------------------------

    // Improvement #1: burn-after-reading (FOLLOW-UPS.md #2).

    @Test
    public void testBurnAfterReadingSingleRead() {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
        String link = service.createPaste("secret", "127.0.0.10", null, true);
        assertNotNull(link);

        assertEquals("secret", service.getPaste(link), "first reader receives the content");
        assertNull(service.getPaste(link), "paste is gone after one read");
    }

    @Test
    public void testBurnAfterReadingConcurrentSingleWinner() throws InterruptedException {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
        String link = service.createPaste("one-time", "127.0.0.11", null, true);

        int readers = 8;
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(readers);
        List<String> results = new ArrayList<>();
        for (int i = 0; i < readers; i++) {
            new Thread(() -> {
                try {
                    start.await();
                    synchronized (results) {
                        results.add(service.getPaste(link));
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    done.countDown();
                }
            }).start();
        }
        start.countDown();
        assertTrue(done.await(5, TimeUnit.SECONDS));

        int winners = 0;
        int losers = 0;
        for (String r : results) {
            if ("one-time".equals(r)) {
                winners++;
            } else if (r == null) {
                losers++;
            }
        }
        assertEquals(1, winners, "exactly one concurrent reader wins");
        assertEquals(readers - 1, losers);
    }

    @Test
    public void testBurnAfterReadingNeverCached() {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
        String link = service.createPaste("no-cache", "127.0.0.12", null, true);
        service.getPaste(link);

        assertFalse(service.readCacheContains(link), "burned pastes must not linger in the cache");
    }

    // Improvement #2: hot-key read cache with metrics (FOLLOW-UPS.md #1).

    @Test
    public void testReadCacheAbsorbsRepeatReads() {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
        String link = service.createPaste("viral", "127.0.0.13");

        assertEquals("viral", service.getPaste(link)); // miss, fills cache
        assertEquals("viral", service.getPaste(link)); // hit
        assertEquals("viral", service.getPaste(link)); // hit

        assertEquals(1, service.getReadCacheMisses());
        assertEquals(2, service.getReadCacheHits());
    }

    @Test
    public void testReadCacheEntriesExpire() throws InterruptedException {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0, new KeyBlockAllocatorV2(), 128, 100L);
        String link = service.createPaste("brief", "127.0.0.14");

        service.getPaste(link); // miss
        Thread.sleep(150);
        service.getPaste(link); // stale cache entry -> miss again

        assertEquals(2, service.getReadCacheMisses());
        assertEquals(0, service.getReadCacheHits());
    }

    @Test
    public void testSweepPurgesReadCache() throws InterruptedException {
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0);
        String link = service.createPaste("cached-die", "127.0.0.15", 1L);
        service.getPaste(link); // fills cache
        assertTrue(service.readCacheContains(link));

        Thread.sleep(1100);
        assertEquals(1, service.sweepExpiredPastes());
        assertFalse(service.readCacheContains(link), "swept pastes leave no cache residue");
    }

    // Improvement #3: KGS-style key block allocation (FOLLOW-UPS.md #3).

    @Test
    public void testKeyBlockAllocatorHandsOutUniqueIds() {
        KeyBlockAllocatorV2 allocator = new KeyBlockAllocatorV2(1000, 4, null);
        Set<Long> ids = new HashSet<>();
        for (int i = 0; i < 9; i++) {
            ids.add(allocator.nextId());
        }

        assertEquals(9, ids.size(), "every id is unique across blocks");
        assertEquals(3, allocator.getBlocksAllocated(), "4+4+1 ids span three blocks");
        for (long id : ids) {
            assertTrue(id >= 1000);
        }
    }

    @Test
    public void testKeyBlockAllocatorExhaustionIsLoud() {
        KeyBlockAllocatorV2 allocator = new KeyBlockAllocatorV2(5000, 2, 1);
        PastebinServiceV2 service = new PastebinServiceV2(10, 1.0, allocator, 128, 5000L);

        String link1 = service.createPaste("a", "127.0.0.16");
        String link2 = service.createPaste("b", "127.0.0.16");
        assertNotNull(link1);
        assertNotNull(link2);
        assertNotEquals(link1, link2);

        IllegalStateException thrown = assertThrows(IllegalStateException.class,
                () -> service.createPaste("c", "127.0.0.16"));
        assertTrue(thrown.getMessage().contains("KeyPoolExhausted"),
                "exhausted key pool must raise, never silently collide");
    }
}
