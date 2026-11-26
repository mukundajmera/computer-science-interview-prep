package v3_optimized;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import v1_basic.CrawlRequest;
import v1_basic.HtmlParser;
import v1_basic.UrlFetcher;
import v2_extended.PolitenessPolicy;
import v2_extended.RobotsPolicy;
import v2_extended.UrlCanonicalizer;

public class Crawler {
    private final ShardQueue queue;
    private final FingerprintStore store;
    private final BackpressureController backpressure;
    private final UrlFetcher fetcher;
    private final HtmlParser parser;
    private final UrlCanonicalizer canonicalizer;
    private final PolitenessPolicy politeness;
    private final RobotsPolicy robots;
    private final List<String> completed = Collections.synchronizedList(new ArrayList<>());
    private volatile boolean running = true;
    
    public void cancel() {
        this.running = false;
    }
    
    public Crawler(ShardQueue queue, FingerprintStore store, BackpressureController backpressure,
                   UrlFetcher fetcher, HtmlParser parser, UrlCanonicalizer canonicalizer,
                   PolitenessPolicy politeness, RobotsPolicy robots) {
        this.queue = queue;
        this.store = store;
        this.backpressure = backpressure;
        this.fetcher = fetcher;
        this.parser = parser;
        this.canonicalizer = canonicalizer;
        this.politeness = politeness;
        this.robots = robots;
    }
    
    public void start(List<String> seeds, String host, int numTasks, int numThreads) {
        start(seeds, host, numTasks, numThreads, 2);
    }
    
    public void start(List<String> seeds, String host, int numTasks, int numThreads, int maxDepth) {
        for (String url : seeds) {
            queue.enqueue(new CrawlRequest(url, 0));
        }
        
        List<Thread> threads = new ArrayList<>();
        int tasksPerThread = numTasks / numThreads;
        
        for (int i = 0; i < numThreads; i++) {
            Thread t = new Thread(() -> {
                int tasksDone = 0;
                while (tasksDone < tasksPerThread && running) {
                    if (backpressure.acquire()) {
                        try {
                            CrawlRequest req = queue.dequeue(host);
                            if (req != null && req.getDepth() <= maxDepth) {
                                String canonicalUrl = canonicalizer.canonicalize(req.getUrl());
                                if (robots.isAllowed(canonicalUrl) && store.add(canonicalUrl)) {
                                    politeness.waitForHost(canonicalUrl);
                                    try {
                                        String content = fetcher.fetch(new CrawlRequest(canonicalUrl, req.getDepth()));
                                        List<String> links = parser.extractLinks(content);
                                        if (req.getDepth() < maxDepth) {
                                            for (String link : links) {
                                                queue.enqueue(new CrawlRequest(link, req.getDepth() + 1));
                                            }
                                        }
                                    } catch (Exception e) {
                                        // Ignore fetch errors
                                    }
                                }
                                completed.add(req.getUrl());
                                tasksDone++;
                            } else {
                                try { Thread.sleep(10); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                            }
                        } finally {
                            backpressure.release();
                        }
                    } else {
                        try { Thread.sleep(10); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                    }
                }
            });
            threads.add(t);
            t.start();
        }
        
        for (Thread t : threads) {
            try {
                t.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    public List<String> getCompleted() {
        return completed;
    }
}
