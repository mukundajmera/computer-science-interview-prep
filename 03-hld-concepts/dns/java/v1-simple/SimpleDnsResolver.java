import java.util.HashMap;
import java.util.Map;

/**
 * TTL-aware in-memory DNS resolver demo.
 */
public class SimpleDnsResolver {
    private static final class DnsRecord {
        private final String value;
        private final long expiresAtMillis;

        private DnsRecord(String value, long expiresAtMillis) {
            this.value = value;
            this.expiresAtMillis = expiresAtMillis;
        }
    }

    private final Map<String, DnsRecord> cache = new HashMap<>();
    private final Map<String, String> authoritative = new HashMap<>();

    public void upsertAuthoritativeRecord(String host, String address) {
        authoritative.put(host, address);
    }

    public String resolve(String host, long ttlMillis) {
        DnsRecord cached = cache.get(host);
        long now = System.currentTimeMillis();
        if (cached != null && now < cached.expiresAtMillis) {
            System.out.println("CACHE_HIT host=" + host + " value=" + cached.value);
            return cached.value;
        }

        if (cached != null) {
            System.out.println("CACHE_STALE host=" + host);
            cache.remove(host);
        } else {
            System.out.println("CACHE_MISS host=" + host);
        }

        String resolved = authoritative.get(host);
        if (resolved == null) {
            System.out.println("AUTHORITATIVE_MISS host=" + host);
            return null;
        }

        cache.put(host, new DnsRecord(resolved, now + ttlMillis));
        System.out.println("AUTHORITATIVE_HIT host=" + host + " value=" + resolved);
        return resolved;
    }

    public static void main(String[] args) throws InterruptedException {
        SimpleDnsResolver resolver = new SimpleDnsResolver();
        resolver.upsertAuthoritativeRecord("api.example.com", "10.0.1.12");

        long ttlMillis = 700;
        System.out.println("First resolve:  " + resolver.resolve("api.example.com", ttlMillis));
        System.out.println("Second resolve: " + resolver.resolve("api.example.com", ttlMillis));

        Thread.sleep(800);
        resolver.upsertAuthoritativeRecord("api.example.com", "10.0.2.44");
        System.out.println("After expiry:   " + resolver.resolve("api.example.com", ttlMillis));
    }
}
