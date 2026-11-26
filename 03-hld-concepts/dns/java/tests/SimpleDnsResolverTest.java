import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

public class SimpleDnsResolverTest {

    private SimpleDnsResolver resolver;

    @BeforeEach
    public void setUp() {
        resolver = new SimpleDnsResolver();
    }

    @Test
    public void testAuthoritativeMissReturnsNull() {
        assertNull(resolver.resolve("unknown.com", 1000));
    }

    @Test
    public void testAuthoritativeHitAndCacheHit() {
        resolver.upsertAuthoritativeRecord("test.com", "1.2.3.4");

        // First resolve: AUTHORITATIVE_HIT
        String result1 = resolver.resolve("test.com", 10000);
        assertEquals("1.2.3.4", result1);

        // Update authoritative record to verify cache is being used
        resolver.upsertAuthoritativeRecord("test.com", "5.6.7.8");

        // Second resolve: CACHE_HIT
        String result2 = resolver.resolve("test.com", 10000);
        assertEquals("1.2.3.4", result2); // Should still return cached value
    }

    @Test
    public void testCacheExpiration() throws InterruptedException {
        resolver.upsertAuthoritativeRecord("expire.com", "9.9.9.9");

        // Resolve with small TTL
        assertEquals("9.9.9.9", resolver.resolve("expire.com", 100));

        // Wait for TTL to expire
        Thread.sleep(150);

        // Update authoritative to verify we get the new value after cache miss
        resolver.upsertAuthoritativeRecord("expire.com", "8.8.8.8");

        // Resolve again: CACHE_STALE -> AUTHORITATIVE_HIT
        assertEquals("8.8.8.8", resolver.resolve("expire.com", 10000));
    }
}
