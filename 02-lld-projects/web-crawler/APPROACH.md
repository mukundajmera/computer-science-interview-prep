# Approach for Web Crawler

## Overview and Core Strategy
A distributed Web Crawler is designed to systematically browse the World Wide Web to index content. The core engineering challenges are managing a massive, ever-growing frontier of URLs, preventing infinite loops (spider traps), obeying site politeness rules (robots.txt), and aggressively scaling network I/O across thousands of worker nodes.

Our approach centers on a highly distributed, loosely coupled architecture utilizing a central URL Frontier, stateless fetcher nodes, and robust deduplication mechanisms. We prioritize breadth-first traversal and strict rate limiting to ensure we are a "good citizen" of the web.

## The URL Frontier and Prioritization
The URL Frontier is the brain of the crawler. It is not a simple FIFO queue. We approach this using a prioritized, multi-queue system.
- URLs are categorized by domain. To ensure we don't hammer a single website with thousands of concurrent requests, the Frontier maintains separate queues for each domain.
- A worker requests a URL from the Frontier. The Frontier selects a domain that has not been fetched recently (enforcing a politeness delay, e.g., 5 seconds between requests to `example.com`), and pops a URL from that domain's queue.
- We prioritize URLs based on page rank estimates, update frequency, and domain authority to ensure we index the most important parts of the web first.
- In `v1-basic`, we implement an intuitive minimum single-threaded frontier, focusing on the core crawler loop, fetching, and visited set logic.
- In `v2-extended`, we introduce pluggable URL canonicalization, robots.txt policies, politeness delays, and handling duplicate content.
- In `v3-optimized`, we implement advanced concurrency, bounded distributed queues, partition handling, backpressure, and handling of spider traps and malformed components using an injected offline graph with cycles.

## Deduplication (Seen URL Set)
Before adding a newly discovered link to the URL Frontier, the system must definitively check if it has already been crawled or is already in the queue.
- Storing billions of URLs in memory is impossible. Storing them in a database and querying before every insert is too slow.
- We approach this using a distributed Bloom Filter. A Bloom Filter uses a fraction of the memory (e.g., 1 byte per URL) and provides an O(1) check if a URL has *definitely not* been seen. If the filter says it *might* have been seen, we perform a slower check against a persistent Key-Value store or simply drop it to avoid the disk I/O, accepting a small number of missed pages in exchange for massive throughput.
- To prevent false-positive link loss, we implement exact visited confirmation using exact sets coupled with Bloom Filters.

**Java FingerprintStore (v3-optimized)**
```java
package v3_optimized;

import java.util.HashSet;
import java.util.Set;

public class FingerprintStore {
    private final Set<String> fingerprints = new HashSet<>();
    private final Set<String> bloomFilter = new HashSet<>();

    public synchronized boolean add(String fingerprint) {
        String bloomHash = String.valueOf(Math.abs(fingerprint.hashCode()));
        if (bloomFilter.contains(bloomHash)) {
            if (fingerprints.contains(fingerprint)) {
                return false;
            }
            fingerprints.add(fingerprint);
            return true;
        }
        
        bloomFilter.add(bloomHash);
        fingerprints.add(fingerprint);
        return true;
    }
}
```

**Python FingerprintStore (v3-optimized)**
```python
import threading
import hashlib
from typing import Set

class FingerprintStore:
    def __init__(self) -> None:
        self.fingerprints: Set[str] = set()
        self.bloom_filter: Set[str] = set()
        self.lock = threading.Lock()

    def add(self, fingerprint: str) -> bool:
        with self.lock:
            bloom_hash = hashlib.md5(fingerprint.encode('utf-8')).hexdigest()[:4]
            if bloom_hash in self.bloom_filter:
                if fingerprint in self.fingerprints:
                    return False
                self.fingerprints.add(fingerprint)
                return True
            
            self.bloom_filter.add(bloom_hash)
            self.fingerprints.add(fingerprint)
            return True
```

## Distributed Fetching and Parsing
The heavy lifting is performed by a fleet of stateless Worker Nodes.
- They fetch the HTML, but network timeouts are the biggest bottleneck. Workers use asynchronous, non-blocking HTTP clients to manage thousands of concurrent connections on a single thread.
- Parsing HTML to extract links and text is CPU-intensive. Workers utilize fast stream parsers rather than loading massive DOM trees into memory, protecting against out-of-memory crashes on maliciously large web pages.
- robots/politeness policy, per-host concurrency, redirect depth, malformed URLs and cancellation enforce bounded queues and no real outbound requests.

**Python Crawler Cancellation Test (v3-optimized)**
```python
    def test_crawler_flow_edges_and_cancellation(self) -> None:
        offline_graph = {
            "http://example.com/start": "<html><a href='http://example.com/cycle1'>Cycle 1</a><a href='bad://url'>Bad</a><a href='http://example.com/notfound'>Not Found</a></html>",
            "http://example.com/cycle1": "<html><a href='http://example.com/start'>Start</a><a href='http://example.com/deep'>Deep</a></html>",
            "http://example.com/deep": "<html><a href='http://example.com/deeper'>Deeper</a></html>"
        }
        fetcher = UrlFetcher(offline_graph)
        parser = HtmlParser()
        canonicalizer = UrlCanonicalizer()
        robots = RobotsPolicy()
        politeness = PolitenessPolicy(delay_ms=0)
        
        queue = ShardQueue()
        store = FingerprintStore()
        backpressure = BackpressureController(max_concurrent=5)
        
        crawler = Crawler(queue, store, backpressure, fetcher, parser, canonicalizer, politeness, robots)
        crawler.start(["http://example.com/start"], "example.com", 10, 1, max_depth=1)
        
        completed_urls = set(crawler.completed)
        self.assertIn("http://example.com/start", completed_urls)
        self.assertIn("http://example.com/cycle1", completed_urls)
        
        crawler.cancel()
        self.assertFalse(crawler.running)
```

**Java Crawler Cancellation Test (v3-optimized)**
```java
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
```
