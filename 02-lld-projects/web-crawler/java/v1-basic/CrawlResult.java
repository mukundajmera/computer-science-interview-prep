package v1_basic;

import java.util.List;

public class CrawlResult {
    private final String url;
    private final int statusCode;
    private final String content;
    private final List<String> links;
    private final String contentHash;
    private final long fetchedAt;

    public CrawlResult(String url, int statusCode, String content, List<String> links) {
        this(url, statusCode, content, links, "", 0L);
    }
    
    public CrawlResult(String url, int statusCode, String content, List<String> links, String contentHash, long fetchedAt) {
        this.url = url;
        this.statusCode = statusCode;
        this.content = content;
        this.links = links;
        this.contentHash = contentHash;
        this.fetchedAt = fetchedAt;
    }

    public String getUrl() { return url; }
    public int getStatusCode() { return statusCode; }
    public String getContent() { return content; }
    public List<String> getLinks() { return links; }
    public String getContentHash() { return contentHash; }
    public long getFetchedAt() { return fetchedAt; }
}
