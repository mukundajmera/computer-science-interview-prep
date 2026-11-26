package v3_optimized;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;
import java.net.URI;
import java.net.URISyntaxException;
import v1_basic.CrawlRequest;

public class ShardQueue {
    private final Map<String, Queue<CrawlRequest>> shards = new HashMap<>();

    public synchronized void enqueue(CrawlRequest request) {
        try {
            URI uri = new URI(request.getUrl());
            String host = uri.getHost();
            if (host == null) host = "";
            shards.computeIfAbsent(host, k -> new LinkedList<>()).offer(request);
        } catch (URISyntaxException e) {
            // Ignore
        }
    }

    public synchronized CrawlRequest dequeue(String host) {
        Queue<CrawlRequest> queue = shards.get(host);
        if (queue != null && !queue.isEmpty()) {
            return queue.poll();
        }
        return null;
    }
}
