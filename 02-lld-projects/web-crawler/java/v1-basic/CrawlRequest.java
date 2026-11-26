package v1_basic;

public class CrawlRequest {
    private final String url;
    private final int depth;

    public CrawlRequest(String url, int depth) {
        this.url = url;
        this.depth = depth;
    }

    public String getUrl() {
        return url;
    }

    public int getDepth() {
        return depth;
    }
}
