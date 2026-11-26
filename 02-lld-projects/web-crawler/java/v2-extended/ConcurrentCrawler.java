package v2_extended;

import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.Collections;
import java.net.URI;
import java.net.URISyntaxException;

import v1_basic.CrawlRequest;
import v1_basic.CrawlResult;
import v1_basic.UrlFetcher;
import v1_basic.HtmlParser;

public class ConcurrentCrawler {
    private final UrlCanonicalizer canonicalizer;
    private final RobotsPolicy robots;
    private final PolitenessPolicy politeness;
    private final HostRateLimiter rateLimiter;
    private final ContentDeduplicator deduplicator;
    private final UrlFetcher fetcher;
    private final HtmlParser parser;
    private final List<CrawlResult> results = Collections.synchronizedList(new ArrayList<>());
    private final Set<String> visited = Collections.synchronizedSet(new HashSet<>());
    private final Queue<CrawlRequest> queue = new ConcurrentLinkedQueue<>();
    private final AtomicInteger activeTasks = new AtomicInteger(0);
    private final AtomicInteger queueSize = new AtomicInteger(0);

    public ConcurrentCrawler(UrlCanonicalizer canonicalizer, RobotsPolicy robots, PolitenessPolicy politeness, HostRateLimiter rateLimiter, ContentDeduplicator deduplicator, UrlFetcher fetcher, HtmlParser parser) {
        this.canonicalizer = canonicalizer;
        this.robots = robots;
        this.politeness = politeness;
        this.rateLimiter = rateLimiter;
        this.deduplicator = deduplicator;
        this.fetcher = fetcher;
        this.parser = parser;
    }

    public void start(List<String> seedUrls, int maxDepth, int numThreads) throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        
        for (String url : seedUrls) {
            String canonUrl = canonicalizer.canonicalize(url);
            if (!canonUrl.startsWith("http")) continue;
            if (visited.add(canonUrl)) {
                queue.offer(new CrawlRequest(canonUrl, 0));
                queueSize.incrementAndGet();
            }
        }
        
        while (!queue.isEmpty() || activeTasks.get() > 0) {
            CrawlRequest request = queue.poll();
            if (request == null) {
                Thread.sleep(10);
                continue;
            }
            queueSize.decrementAndGet();
            
            if (request.getDepth() > maxDepth) continue;
            
            String host = getHost(request.getUrl());
            if (host == null || !robots.isAllowed(request.getUrl())) continue;
            
            if (!rateLimiter.tryAcquire(host)) {
                queue.offer(request);
                queueSize.incrementAndGet();
                continue; // Yields processing to next task in queue without sleeping
            }
            
            activeTasks.incrementAndGet();
            executor.submit(() -> {
                try {
                    politeness.waitForHost(request.getUrl());
                    
                    String content = "";
                    List<String> links = new ArrayList<>();
                    int status = 200;
                    
                    try {
                        content = fetcher.fetch(request);
                        if (!deduplicator.isDuplicate(content)) {
                            links = parser.extractLinks(content);
                        }
                    } catch (RuntimeException e) {
                        status = 404;
                    }
                    
                    results.add(new CrawlResult(request.getUrl(), status, content, links, "", System.currentTimeMillis()));
                    
                    if (status == 200 && request.getDepth() < maxDepth) {
                        for (String link : links) {
                            String canonLink = canonicalizer.canonicalize(link);
                            if (canonLink.startsWith("http") && queueSize.get() < 10000) {
                                if (visited.add(canonLink)) {
                                    queue.offer(new CrawlRequest(canonLink, request.getDepth() + 1));
                                    queueSize.incrementAndGet();
                                }
                            }
                        }
                    }
                } finally {
                    rateLimiter.release(host);
                    activeTasks.decrementAndGet();
                }
            });
        }
        
        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);
    }
    
    private String getHost(String urlStr) {
        try {
            return new URI(urlStr).getHost();
        } catch (URISyntaxException e) {
            return null;
        }
    }
    
    public List<CrawlResult> getResults() {
        return results;
    }
}
