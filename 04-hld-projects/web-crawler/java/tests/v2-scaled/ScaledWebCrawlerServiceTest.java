package v2;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class ScaledWebCrawlerServiceTest {

    private ScaledWebCrawlerService crawler;

    @BeforeEach
    void setUp() {
        crawler = new ScaledWebCrawlerService();
    }

    @Test
    void testPriorityFrontierAndDomainScope() {
        List<String> seeds = Arrays.asList("http://example.com/seed1", "http://example.com/seed2");
        crawler.createJob("job1", seeds, "example.com");

        crawler.addUrlToFrontier("http://example.com/high-priority", 1, "example.com");
        crawler.addUrlToFrontier("http://example.com/low-priority", 100, "example.com");
        crawler.addUrlToFrontier("http://outside.com/ignore", 1, "example.com");

        assertEquals(4, crawler.getFrontierSize()); // 2 seeds + 2 valid additions (outside.com is ignored)

        Object highestPriority = crawler.pollFrontier();
        assertNotNull(highestPriority);
        assertEquals("http://example.com/high-priority", getUrlFromFrontierItem(highestPriority));

        Object nextItem = crawler.pollFrontier();
        assertNotNull(nextItem); // It will be one of the seeds (priority 10)
    }

    @Test
    void testHostPolitenessTokenBucket() throws InterruptedException {
        String url = "http://slowhost.com/page";

        // Assume default bucket is 5, refill is 1/sec
        // Try fetching 5 times, should succeed
        for (int i = 0; i < 5; i++) {
            assertTrue(crawler.tryFetch(url), "Fetch " + i + " should succeed");
        }

        // 6th time should fail as bucket is empty
        assertFalse(crawler.tryFetch(url), "Fetch 6 should fail");

        // Wait 1.1 second for refill
        Thread.sleep(1100);

        // Should succeed again
        assertTrue(crawler.tryFetch(url), "Fetch after refill should succeed");
    }

    @Test
    void testDuplicateContentFingerprinting() {
        String content1 = "This is some unique content.";
        String content2 = "This is some unique content."; // Exact match
        String content3 = "This is completely different.";

        assertFalse(crawler.isDuplicateContent(content1), "First time seeing content1 should not be duplicate");
        assertTrue(crawler.isDuplicateContent(content2), "Second time seeing content1 should be duplicate");
        assertFalse(crawler.isDuplicateContent(content3), "First time seeing content3 should not be duplicate");
    }

    @Test
    void testCrawlJobPauseResume() {
        List<String> seeds = Arrays.asList("http://example.com");
        crawler.createJob("job2", seeds, "example.com");

        assertEquals(ScaledWebCrawlerService.JobStatus.RUNNING, crawler.getJobStatus("job2"));

        crawler.pauseJob("job2");
        assertEquals(ScaledWebCrawlerService.JobStatus.PAUSED, crawler.getJobStatus("job2"));

        crawler.resumeJob("job2");
        assertEquals(ScaledWebCrawlerService.JobStatus.RUNNING, crawler.getJobStatus("job2"));

        assertNull(crawler.getJobStatus("nonexistent"));
    }

    private String getUrlFromFrontierItem(Object item) {
        try {
            return (String) item.getClass().getMethod("getUrl").invoke(item);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
