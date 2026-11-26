package v1_basic;

import java.util.Map;
import java.util.HashMap;

public class UrlFetcher {
    private final Map<String, String> offlineGraph;
    
    public UrlFetcher() {
        this(new HashMap<>());
    }
    
    public UrlFetcher(Map<String, String> offlineGraph) {
        this.offlineGraph = offlineGraph;
    }
    
    public String fetch(CrawlRequest request) {
        if (offlineGraph.containsKey(request.getUrl())) {
            return offlineGraph.get(request.getUrl());
        }
        throw new RuntimeException("404 Not Found: " + request.getUrl());
    }
}
