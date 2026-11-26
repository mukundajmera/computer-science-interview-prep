import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Simple DNS resolver simulation with cache and round-robin responses. */
public class DnsResolver {
    private final Map<String, List<String>> records;
    private final Map<String, CacheEntry> cache = new HashMap<>();
    private final Map<String, Integer> indices = new HashMap<>();

    public DnsResolver(Map<String, List<String>> records) {
        if (records == null || records.isEmpty()) {
            throw new IllegalArgumentException("records cannot be empty");
        }
        this.records = records;
    }

    public String resolve(String domain, long ttlMillis) {
        long now = System.currentTimeMillis();
        CacheEntry cached = cache.get(domain);
        if (cached != null && cached.expiresAt > now) {
            return cached.ip;
        }

        List<String> ips = records.get(domain);
        if (ips == null || ips.isEmpty()) {
            return null;
        }

        int idx = indices.getOrDefault(domain, 0);
        String ip = ips.get(idx % ips.size());
        indices.put(domain, idx + 1);
        cache.put(domain, new CacheEntry(ip, now + ttlMillis));
        return ip;
    }

    private static class CacheEntry {
        final String ip;
        final long expiresAt;

        CacheEntry(String ip, long expiresAt) {
            this.ip = ip;
            this.expiresAt = expiresAt;
        }
    }
}
