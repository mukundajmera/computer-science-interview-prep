package v2_extended;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import v1_basic.HtmlParser;
import v1_basic.UrlFetcher;
import v1_basic.CrawlResult;

public class WebCrawlerV2Test {
    @Test
    void testCanonicalizer() {
        UrlCanonicalizer canon = new UrlCanonicalizer();
        String res = canon.canonicalize("HTTP://Example.COM:80/path#frag");
        assertEquals("http://example.com:80/path", res);
    }
    
    @Test
    void testRobotsPolicy() {
        RobotsPolicy robots = new RobotsPolicy();
        robots.addRule("example.com", "/private");
        assertTrue(robots.isAllowed("http://example.com/public"));
        assertFalse(robots.isAllowed("http://example.com/private/data"));
    }
    
    @Test
    void testCrawlerFlowWithOfflineGraphCycles() {
        UrlCanonicalizer canon = new UrlCanonicalizer();
        RobotsPolicy robots = new RobotsPolicy();
        PolitenessPolicy politeness = new PolitenessPolicy(0); // 0 delay
        ContentDeduplicator dedup = new ContentDeduplicator();
        
        Map<String, String> offlineGraph = new HashMap<>();
        offlineGraph.put("http://example.com/a", "<html><a href='http://example.com/b'>B</a></html>");
        offlineGraph.put("http://example.com/b", "<html><a href='http://example.com/a'>A</a><a href='http://example.com/c'>C</a></html>");
        offlineGraph.put("http://example.com/c", "<html><a href='http://example.com/a'>A</a></html>");
        
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        
        Crawler crawler = new Crawler(canon, robots, politeness, dedup, fetcher, parser);
        crawler.start(Arrays.asList("http://example.com/a"), 5);
        
        assertEquals(3, crawler.getResults().size());
        
        java.util.Set<String> visitedUrls = new java.util.HashSet<>();
        for (CrawlResult r : crawler.getResults()) {
            visitedUrls.add(r.getUrl());
        }
        assertTrue(visitedUrls.contains("http://example.com/a"));
        assertTrue(visitedUrls.contains("http://example.com/b"));
        assertTrue(visitedUrls.contains("http://example.com/c"));
    }

    @Test
    void testConcurrentCrawler() throws InterruptedException {
        UrlCanonicalizer canon = new UrlCanonicalizer();
        RobotsPolicy robots = new RobotsPolicy();
        PolitenessPolicy politeness = new PolitenessPolicy(0);
        HostRateLimiter rateLimiter = new HostRateLimiter(2);
        ContentDeduplicator dedup = new ContentDeduplicator();
        
        Map<String, String> offlineGraph = new HashMap<>();
        offlineGraph.put("http://example.com/1", "<html><a href='http://example.com/2'>2</a></html>");
        offlineGraph.put("http://example.com/2", "<html><a href='http://example.com/3'>3</a></html>");
        offlineGraph.put("http://example.com/3", "<html><a href='http://example.com/1'>1</a></html>");
        
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        
        ConcurrentCrawler crawler = new ConcurrentCrawler(canon, robots, politeness, rateLimiter, dedup, fetcher, parser);
        crawler.start(Arrays.asList("http://example.com/1"), 5, 2);
        
        assertEquals(3, crawler.getResults().size());
    }
}
