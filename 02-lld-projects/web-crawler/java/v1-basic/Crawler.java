package v1_basic;

import java.util.ArrayList;
import java.util.List;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

public class Crawler {
    private final UrlFrontier frontier;
    private final UrlFetcher fetcher;
    private final HtmlParser parser;
    private final List<CrawlResult> results = new ArrayList<>();

    public Crawler(UrlFrontier frontier, UrlFetcher fetcher, HtmlParser parser) {
        this.frontier = frontier;
        this.fetcher = fetcher;
        this.parser = parser;
    }
    
    public Crawler() {
        this(new UrlFrontier(), new UrlFetcher(), new HtmlParser());
    }

    public void start(List<String> seedUrls, int maxDepth) {
        for (String url : seedUrls) {
            frontier.enqueue(new CrawlRequest(url, 0));
        }

        while (frontier.hasNext()) {
            CrawlRequest request = frontier.dequeue();
            if (request == null || request.getDepth() > maxDepth) continue;

            String content = "";
            List<String> links = new ArrayList<>();
            int status = 200;
            
            try {
                content = fetcher.fetch(request);
                links = parser.extractLinks(content);
            } catch (RuntimeException e) {
                status = 404;
            }
            
            String contentHash = computeHash(content);
            long fetchedAt = System.currentTimeMillis();
            
            results.add(new CrawlResult(request.getUrl(), status, content, links, contentHash, fetchedAt));

            if (status == 200 && request.getDepth() < maxDepth) {
                for (String link : links) {
                    frontier.enqueue(new CrawlRequest(link, request.getDepth() + 1));
                }
            }
        }
    }
    
    private String computeHash(String input) {
        if (input == null || input.isEmpty()) return "";
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * hash.length);
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            return "";
        }
    }
    
    public List<CrawlResult> getResults() {
        return results;
    }
}
