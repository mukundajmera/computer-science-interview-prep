import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

public class WebCrawlerService {

    public interface Fetcher {
        String fetch(String url);
    }

    public interface Extractor {
        List<String> extract(String url, String content);
    }

    public static class MockFetcher implements Fetcher {
        @Override
        public String fetch(String url) {
            return "Content of " + url;
        }
    }

    public static class MockExtractor implements Extractor {
        @Override
        public List<String> extract(String url, String content) {
            return new ArrayList<>();
        }
    }

    public static class CrawledResult {
        public final String url;
        public final String content;

        public CrawledResult(String url, String content) {
            this.url = url;
            this.content = content;
        }
    }

    private static class QueueItem {
        public final String url;
        public final int depth;

        public QueueItem(String url, int depth) {
            this.url = url;
            this.depth = depth;
        }
    }

    private final Fetcher fetcher;
    private final Extractor extractor;
    private final long politenessDelayMs;
    private final int maxDepth;
    private final Set<String> seenUrls;
    private final Queue<QueueItem> frontier;
    private final Map<String, Long> lastFetchTimePerDomain;
    private final List<CrawledResult> crawledResults;
    private final Set<String> disallowedUrls;

    public WebCrawlerService(Fetcher fetcher, Extractor extractor, long politenessDelayMs, int maxDepth) {
        this.fetcher = fetcher != null ? fetcher : new MockFetcher();
        this.extractor = extractor != null ? extractor : new MockExtractor();
        this.politenessDelayMs = politenessDelayMs;
        this.maxDepth = maxDepth;
        this.seenUrls = new HashSet<>();
        this.frontier = new ArrayDeque<>();
        this.lastFetchTimePerDomain = new HashMap<>();
        this.crawledResults = new ArrayList<>();
        this.disallowedUrls = new HashSet<>();
    }

    public WebCrawlerService(long politenessDelayMs, int maxDepth) {
        this(null, null, politenessDelayMs, maxDepth);
    }

    public void addDisallowedRule(String url) {
        this.disallowedUrls.add(url);
    }

    public boolean isAllowed(String url) {
        return !this.disallowedUrls.contains(url);
    }

    private String getDomain(String url) {
        try {
            URI uri = new URI(url);
            String domain = uri.getHost();
            return domain != null ? domain : url;
        } catch (URISyntaxException e) {
            return url;
        }
    }

    public void crawl(List<String> seedUrls) {
        for (String url : seedUrls) {
            this.frontier.offer(new QueueItem(url, 0));
        }

        while (!this.frontier.isEmpty()) {
            QueueItem item = this.frontier.poll();
            String url = item.url;
            int depth = item.depth;

            if (this.seenUrls.contains(url)) {
                continue;
            }

            if (!isAllowed(url)) {
                this.seenUrls.add(url);
                continue;
            }

            String domain = getDomain(url);
            long lastFetchTime = this.lastFetchTimePerDomain.getOrDefault(domain, 0L);
            long currentTime = System.currentTimeMillis();

            if (currentTime - lastFetchTime < this.politenessDelayMs) {
                try {
                    Thread.sleep(this.politenessDelayMs - (currentTime - lastFetchTime));
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }

            try {
                String content = this.fetcher.fetch(url);
                this.crawledResults.add(new CrawledResult(url, content));
                this.seenUrls.add(url);
                this.lastFetchTimePerDomain.put(domain, System.currentTimeMillis());

                if (depth < this.maxDepth) {
                    List<String> links = this.extractor.extract(url, content);
                    for (String link : links) {
                        if (!this.seenUrls.contains(link)) {
                            this.frontier.offer(new QueueItem(link, depth + 1));
                        }
                    }
                }
            } catch (Exception e) {
                // Mark as seen to avoid infinite retry loops on failure
                this.seenUrls.add(url);
            }
        }
    }

    public Set<String> getSeenUrls() {
        return this.seenUrls;
    }

    public List<CrawledResult> getCrawledResults() {
        return this.crawledResults;
    }
}
