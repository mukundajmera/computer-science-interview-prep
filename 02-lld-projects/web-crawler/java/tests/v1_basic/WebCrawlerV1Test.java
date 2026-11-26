package v1_basic;

import org.junit.jupiter.api.Test;
import java.util.Arrays;
import static org.junit.jupiter.api.Assertions.*;

public class WebCrawlerV1Test {
    @Test
    void testFrontierDeduplication() {
        UrlFrontier frontier = new UrlFrontier();
        frontier.enqueue(new CrawlRequest("http://example.com", 0));
        frontier.enqueue(new CrawlRequest("http://example.com", 0));
        assertEquals(1, frontier.size());
    }
    
    @Test
    void testHtmlParser() {
        HtmlParser parser = new HtmlParser();
        java.util.List<String> links = parser.extractLinks("<html><a href='http://link1.com'>Link</a></html>");
        assertEquals(1, links.size());
        assertEquals("http://link1.com", links.get(0));
    }
    
    @Test
    void testCrawlerFlow() {
        UrlFrontier frontier = new UrlFrontier();
        java.util.Map<String, String> offlineGraph = new java.util.HashMap<>();
        offlineGraph.put("http://example.com", "<html><a href='http://example.com/next'>Next</a></html>");
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        Crawler crawler = new Crawler(frontier, fetcher, parser);
        
        crawler.start(Arrays.asList("http://example.com"), 1);
        
        assertTrue(crawler.getResults().size() > 0);
        assertEquals("http://example.com", crawler.getResults().get(0).getUrl());
        assertTrue(crawler.getResults().get(0).getLinks().size() > 0);
    }
    
    @Test
    void testOfflineGraphCycles() {
        java.util.Map<String, String> offlineGraph = new java.util.HashMap<>();
        offlineGraph.put("http://example.com/a", "<html><body><a href='http://example.com/b'>B</a></body></html>");
        offlineGraph.put("http://example.com/b", "<html><body><a href='http://example.com/a/'>A</a></body></html>");
        
        UrlFrontier frontier = new UrlFrontier();
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        Crawler crawler = new Crawler(frontier, fetcher, parser);
        
        crawler.start(Arrays.asList("http://example.com/a"), 5);
        
        assertEquals(2, crawler.getResults().size());
        
        java.util.Set<String> urls = new java.util.HashSet<>();
        for (CrawlResult r : crawler.getResults()) {
            urls.add(r.getUrl());
        }
        
        assertTrue(urls.contains("http://example.com/a"));
        assertTrue(urls.contains("http://example.com/b"));
    }
    
    @Test
    void testMalformedUrlAnd404() {
        java.util.Map<String, String> offlineGraph = new java.util.HashMap<>();
        offlineGraph.put("http://start.com", "<html><a href='not_http://bad.com'>Bad</a><a href='http://missing.com'>Missing</a></html>");
        
        UrlFrontier frontier = new UrlFrontier();
        UrlFetcher fetcher = new UrlFetcher(offlineGraph);
        HtmlParser parser = new HtmlParser();
        Crawler crawler = new Crawler(frontier, fetcher, parser);
        
        crawler.start(Arrays.asList("http://start.com"), 2);
        
        assertEquals(2, crawler.getResults().size());
        
        CrawlResult missingResult = null;
        for (CrawlResult r : crawler.getResults()) {
            if ("http://missing.com".equals(r.getUrl())) {
                missingResult = r;
                break;
            }
        }
        
        assertNotNull(missingResult);
        assertEquals(404, missingResult.getStatusCode());
    }
}
