package v2_extended;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.LinkedList;
import java.util.Set;
import java.util.HashSet;
import java.net.URI;
import java.net.URISyntaxException;

import v1_basic.CrawlRequest;
import v1_basic.CrawlResult;
import v1_basic.UrlFetcher;
import v1_basic.HtmlParser;

public class Crawler {
    private final UrlCanonicalizer canonicalizer;
    private final RobotsPolicy robots;
    private final PolitenessPolicy politeness;
    private final ContentDeduplicator deduplicator;
    private final UrlFetcher fetcher;
    private final HtmlParser parser;
    private final List<String> crawled = new ArrayList<>();
    private final List<CrawlResult> results = new ArrayList<>();
    private final Set<String> visited = new HashSet<>();

    public Crawler(UrlCanonicalizer canonicalizer, RobotsPolicy robots, PolitenessPolicy politeness, ContentDeduplicator deduplicator, UrlFetcher fetcher, HtmlParser parser) {
        this.canonicalizer = canonicalizer;
        this.robots = robots;
        this.politeness = politeness;
        this.deduplicator = deduplicator;
        this.fetcher = fetcher;
        this.parser = parser;
    }

    public Crawler(UrlCanonicalizer canonicalizer, RobotsPolicy robots, PolitenessPolicy politeness, ContentDeduplicator deduplicator) {
        this(canonicalizer, robots, politeness, deduplicator, null, null);
    }

    public void start(List<String> seedUrls, int maxDepth) {
        Queue<CrawlRequest> queue = new LinkedList<>();
        
        for (String url : seedUrls) {
            String canonUrl = canonicalizer.canonicalize(url);
            if (!canonUrl.startsWith("http")) continue;
            if (!visited.contains(canonUrl)) {
                visited.add(canonUrl);
                queue.offer(new CrawlRequest(canonUrl, 0));
            }
        }
        
        while (!queue.isEmpty()) {
            CrawlRequest request = queue.poll();
            if (request == null || request.getDepth() > maxDepth) continue;
            
            String url = request.getUrl();
            
            try {
                URI uri = new URI(url);
                if (uri.getHost() == null) continue;
            } catch (URISyntaxException e) {
                continue;
            }
            
            if (!robots.isAllowed(url)) continue;
            
            politeness.waitForHost(url);
            
            String content = "";
            List<String> links = new ArrayList<>();
            int status = 200;
            
            try {
                if (fetcher != null) {
                    content = fetcher.fetch(request);
                    if (deduplicator.isDuplicate(content)) {
                        continue;
                    }
                    if (parser != null) {
                        links = parser.extractLinks(content);
                    }
                }
            } catch (RuntimeException e) {
                status = 404;
            }
            
            long fetchedAt = System.currentTimeMillis();
            crawled.add(url);
            results.add(new CrawlResult(url, status, content, links, "", fetchedAt));
            
            if (status == 200 && request.getDepth() < maxDepth) {
                for (String link : links) {
                    String canonLink = canonicalizer.canonicalize(link);
                    if (!canonLink.startsWith("http")) continue;
                    if (!visited.contains(canonLink)) {
                        visited.add(canonLink);
                        if (queue.size() < 10000) {
                            queue.offer(new CrawlRequest(canonLink, request.getDepth() + 1));
                        }
                    }
                }
            }
        }
    }
    
    public boolean crawl(String url, String content) {
        String canonicalUrl = canonicalizer.canonicalize(url);
        if (!robots.isAllowed(canonicalUrl)) return false;
        politeness.waitForHost(canonicalUrl);
        if (deduplicator.isDuplicate(content)) return false;
        crawled.add(canonicalUrl);
        return true;
    }
    
    public List<String> getCrawled() { return crawled; }
    public List<CrawlResult> getResults() { return results; }
}
