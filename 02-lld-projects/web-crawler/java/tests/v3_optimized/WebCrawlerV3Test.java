package v3_optimized;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Arrays;

import v1_basic.CrawlRequest;
import v1_basic.HtmlParser;
import v1_basic.UrlFetcher;
import v2_extended.PolitenessPolicy;
import v2_extended.RobotsPolicy;
import v2_extended.UrlCanonicalizer;

public class WebCrawlerV3Test {
    @Test
    void testShardQueue() {
        ShardQueue q = new ShardQueue();
        q.enqueue(new CrawlRequest("http://a.com/1", 0));
        q.enqueue(new CrawlRequest("http://b.com/1", 0));
        assertEquals("http://a.com/1", q.dequeue("a.com").getUrl());
        assertNull(q.dequeue("a.com"));
    }
    
    @Test
    void testFingerprintStore() {
        FingerprintStore store = new FingerprintStore();
        assertTrue(store.add("hash1"));
        assertFalse(store.add("hash1"));
    }
    
    @Test
    void testCoordinator() {
        ShardQueue q = new ShardQueue();
        for (int i = 0; i < 10; i++) {
            q.enqueue(new CrawlRequest("http://example.com/" + i, 0));
        }
        
        BackpressureController bp = new BackpressureController(2);
        CrawlCoordinator coord = new CrawlCoordinator(q, bp);
        coord.runConcurrently("example.com", 10, 2);
        
        assertEquals(10, coord.getCompleted().size());
    }
    
    @Test
    void testCrawlerFlow() {
        Map<String, String> offlineGraph = new HashMap<>();
        offlineGraph.put("http://example.com/a", "<html><a href='http://example.com/b'>B</a></html>");
        offlineGraph.put("http://example.com/b", "<html><a href='http://example.com/a'>A</a></html>");
        
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        UrlCanonicalizer canonicalizer = new UrlCanonicalizer();
        RobotsPolicy robots = new RobotsPolicy();
        PolitenessPolicy politeness = new PolitenessPolicy(0);
        
        ShardQueue queue = new ShardQueue();
        FingerprintStore store = new FingerprintStore();
        BackpressureController backpressure = new BackpressureController(2);
        
        Crawler crawler = new Crawler(queue, store, backpressure, fetcher, parser, canonicalizer, politeness, robots);
        crawler.start(Arrays.asList("http://example.com/a"), "example.com", 2, 1);
        
        assertEquals(2, crawler.getCompleted().size());
        assertTrue(crawler.getCompleted().contains("http://example.com/a"));
    }
    
    @Test
    void testCrawlerFlowEdgesAndCancellation() {
        Map<String, String> offlineGraph = new HashMap<>();
        offlineGraph.put("http://example.com/start", "<html><a href='http://example.com/cycle1'>Cycle 1</a><a href='bad://url'>Bad</a><a href='http://example.com/notfound'>Not Found</a></html>");
        offlineGraph.put("http://example.com/cycle1", "<html><a href='http://example.com/start'>Start</a><a href='http://example.com/deep'>Deep</a></html>");
        offlineGraph.put("http://example.com/deep", "<html><a href='http://example.com/deeper'>Deeper</a></html>");
        
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        UrlCanonicalizer canonicalizer = new UrlCanonicalizer();
        RobotsPolicy robots = new RobotsPolicy();
        PolitenessPolicy politeness = new PolitenessPolicy(0);
        
        ShardQueue queue = new ShardQueue();
        FingerprintStore store = new FingerprintStore();
        BackpressureController backpressure = new BackpressureController(5);
        
        Crawler crawler = new Crawler(queue, store, backpressure, fetcher, parser, canonicalizer, politeness, robots);
        crawler.start(Arrays.asList("http://example.com/start"), "example.com", 10, 1, 1);
        
        assertTrue(crawler.getCompleted().contains("http://example.com/start"));
        assertTrue(crawler.getCompleted().contains("http://example.com/cycle1"));
        
        crawler.cancel();
    }
}
