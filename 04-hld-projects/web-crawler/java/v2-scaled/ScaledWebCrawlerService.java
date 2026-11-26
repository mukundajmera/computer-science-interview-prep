package v2;

import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.PriorityBlockingQueue;

public class ScaledWebCrawlerService {

    public enum JobStatus {
        RUNNING, PAUSED, COMPLETED
    }

    public static class CrawlJob {
        private final String id;
        private final List<String> seeds;
        private final String domainScope;
        private volatile JobStatus status;

        public CrawlJob(String id, List<String> seeds, String domainScope) {
            this.id = id;
            this.seeds = seeds;
            this.domainScope = domainScope;
            this.status = JobStatus.RUNNING;
        }

        public String getId() { return id; }
        public String getDomainScope() { return domainScope; }
        public JobStatus getStatus() { return status; }
        public void setStatus(JobStatus status) { this.status = status; }
    }

    public static class FrontierItem implements Comparable<FrontierItem> {
        private final String url;
        private final int priority;

        public FrontierItem(String url, int priority) {
            this.url = url;
            this.priority = priority;
        }

        public String getUrl() { return url; }
        public int getPriority() { return priority; }

        @Override
        public int compareTo(FrontierItem other) {
            return Integer.compare(this.priority, other.priority);
        }
    }

    private static class TokenBucket {
        private final int capacity;
        private final int refillRatePerSecond;
        private double tokens;
        private long lastRefillTimestamp;

        public TokenBucket(int capacity, int refillRatePerSecond) {
            this.capacity = capacity;
            this.refillRatePerSecond = refillRatePerSecond;
            this.tokens = capacity;
            this.lastRefillTimestamp = System.currentTimeMillis();
        }

        public synchronized boolean tryConsume() {
            refill();
            if (tokens >= 1.0) {
                tokens -= 1.0;
                return true;
            }
            return false;
        }

        private void refill() {
            long now = System.currentTimeMillis();
            double timePassedSeconds = (now - lastRefillTimestamp) / 1000.0;
            double tokensToAdd = timePassedSeconds * refillRatePerSecond;
            tokens = Math.min(capacity, tokens + tokensToAdd);
            lastRefillTimestamp = now;
        }
    }

    private final Map<String, CrawlJob> jobs = new ConcurrentHashMap<>();
    private final PriorityBlockingQueue<FrontierItem> frontier = new PriorityBlockingQueue<>();
    private final Set<String> seenUrls = ConcurrentHashMap.newKeySet();
    private final Set<String> seenContentHashes = ConcurrentHashMap.newKeySet();
    private final Map<String, TokenBucket> hostBuckets = new ConcurrentHashMap<>();

    private final int defaultBucketCapacity = 5;
    private final int defaultRefillRate = 1;

    public CrawlJob createJob(String id, List<String> seeds, String domainScope) {
        CrawlJob job = new CrawlJob(id, seeds, domainScope);
        jobs.put(id, job);
        for (String seed : seeds) {
            addUrlToFrontier(seed, 10, domainScope);
        }
        return job;
    }

    public void pauseJob(String id) {
        CrawlJob job = jobs.get(id);
        if (job != null) {
            job.setStatus(JobStatus.PAUSED);
        }
    }

    public void resumeJob(String id) {
        CrawlJob job = jobs.get(id);
        if (job != null) {
            job.setStatus(JobStatus.RUNNING);
        }
    }

    public JobStatus getJobStatus(String id) {
        CrawlJob job = jobs.get(id);
        return job != null ? job.getStatus() : null;
    }

    private boolean isWithinScope(String urlStr, String domainScope) {
        if (domainScope == null || domainScope.isEmpty()) return true;
        try {
            URI uri = new URI(urlStr);
            String host = uri.getHost();
            if (host == null) return false;
            return host.equals(domainScope) || host.endsWith("." + domainScope);
        } catch (URISyntaxException e) {
            return false;
        }
    }

    public boolean addUrlToFrontier(String url, int priority, String domainScope) {
        if (!isWithinScope(url, domainScope)) {
            return false;
        }
        if (seenUrls.add(url)) {
            frontier.add(new FrontierItem(url, priority));
            return true;
        }
        return false;
    }

    public String generateContentFingerprint(String content) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    public boolean isDuplicateContent(String content) {
        String hash = generateContentFingerprint(content);
        return !seenContentHashes.add(hash);
    }

    public String getHost(String urlStr) {
        try {
            URI uri = new URI(urlStr);
            return uri.getHost();
        } catch (URISyntaxException e) {
            return null;
        }
    }

    public boolean tryFetch(String urlStr) {
        String host = getHost(urlStr);
        if (host == null) return false;

        TokenBucket bucket = hostBuckets.computeIfAbsent(host, k -> new TokenBucket(defaultBucketCapacity, defaultRefillRate));
        return bucket.tryConsume();
    }

    public FrontierItem pollFrontier() {
        return frontier.poll();
    }

    public int getFrontierSize() {
        return frontier.size();
    }
}
