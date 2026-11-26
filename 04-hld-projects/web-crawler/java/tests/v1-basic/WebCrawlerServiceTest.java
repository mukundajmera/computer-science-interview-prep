import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;

public class WebCrawlerServiceTest {

    private static class MockExtractorWithMapping implements WebCrawlerService.Extractor {
        private final Map<String, List<String>> mapping;

        public MockExtractorWithMapping(Map<String, List<String>> mapping) {
            this.mapping = mapping;
        }

        @Override
        public List<String> extract(String url, String content) {
            return mapping.getOrDefault(url, Collections.emptyList());
        }
    }

    @Test
    public void testBasicCrawling() {
        WebCrawlerService crawler = new WebCrawlerService(0, 1);
        crawler.crawl(Arrays.asList("http://example.com/1", "http://example.com/2"));

        Set<String> seenUrls = crawler.getSeenUrls();
        assertEquals(2, seenUrls.size());
        assertTrue(seenUrls.contains("http://example.com/1"));
        assertTrue(seenUrls.contains("http://example.com/2"));
    }

    @Test
    public void testDeduplication() {
        WebCrawlerService crawler = new WebCrawlerService(0, 1);
        crawler.crawl(Arrays.asList("http://example.com/1", "http://example.com/1"));

        Set<String> seenUrls = crawler.getSeenUrls();
        assertEquals(1, seenUrls.size());
        assertEquals(1, crawler.getCrawledResults().size());
    }

    @Test
    public void testDepthLimiter() {
        Map<String, List<String>> mapping = new HashMap<>();
        mapping.put("http://example.com/1", Arrays.asList("http://example.com/2"));
        mapping.put("http://example.com/2", Arrays.asList("http://example.com/3"));
        mapping.put("http://example.com/3", Arrays.asList("http://example.com/4"));

        WebCrawlerService.Extractor extractor = new MockExtractorWithMapping(mapping);
        WebCrawlerService crawler = new WebCrawlerService(null, extractor, 0, 1);

        crawler.crawl(Arrays.asList("http://example.com/1"));

        Set<String> seenUrls = crawler.getSeenUrls();
        assertEquals(2, seenUrls.size());
        assertTrue(seenUrls.contains("http://example.com/1"));
        assertTrue(seenUrls.contains("http://example.com/2"));
        assertFalse(seenUrls.contains("http://example.com/3"));
    }

    @Test
    public void testPolitenessDelay() {
        WebCrawlerService crawler = new WebCrawlerService(200, 1);
        long startTime = System.currentTimeMillis();
        crawler.crawl(Arrays.asList("http://example.com/1", "http://example.com/2"));
        long endTime = System.currentTimeMillis();

        assertTrue((endTime - startTime) >= 200, "Politeness delay should enforce at least 200ms wait between requests to same domain");
    }

    @Test
    public void testRobotsTxtDisallowed() {
        WebCrawlerService crawler = new WebCrawlerService(0, 1);
        crawler.addDisallowedRule("http://example.com/secret");

        crawler.crawl(Arrays.asList("http://example.com/public", "http://example.com/secret"));

        Set<String> seenUrls = crawler.getSeenUrls();
        assertTrue(seenUrls.contains("http://example.com/public"));
        assertTrue(seenUrls.contains("http://example.com/secret"));

        boolean foundSecretInResults = false;
        boolean foundPublicInResults = false;

        for (WebCrawlerService.CrawledResult result : crawler.getCrawledResults()) {
            if (result.url.equals("http://example.com/secret")) {
                foundSecretInResults = true;
            }
            if (result.url.equals("http://example.com/public")) {
                foundPublicInResults = true;
            }
        }

        assertTrue(foundPublicInResults);
        assertFalse(foundSecretInResults, "Secret URL should not be crawled and present in results");
    }
}
