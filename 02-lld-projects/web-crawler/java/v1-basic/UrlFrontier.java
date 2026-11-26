package v1_basic;

import java.util.LinkedList;
import java.util.Queue;
import java.util.Set;
import java.util.HashSet;

public class UrlFrontier {
    private final Queue<CrawlRequest> queue = new LinkedList<>();
    private final Set<String> visited = new HashSet<>();

    private String normalizeUrl(String url) {
        String norm = url.trim().toLowerCase();
        if (norm.endsWith("/")) {
            norm = norm.substring(0, norm.length() - 1);
        }
        return norm;
    }

    public void enqueue(CrawlRequest request) {
        if (!request.getUrl().startsWith("http")) {
            return;
        }
        
        if (queue.size() >= 10000) {
            return;
        }

        String normalizedUrl = normalizeUrl(request.getUrl());
        if (!visited.contains(normalizedUrl)) {
            visited.add(normalizedUrl);
            queue.offer(new CrawlRequest(normalizedUrl, request.getDepth()));
        }
    }

    public CrawlRequest dequeue() {
        return queue.poll();
    }

    public boolean hasNext() {
        return !queue.isEmpty();
    }
    
    public int size() {
        return queue.size();
    }
}
