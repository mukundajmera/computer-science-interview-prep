import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class DnsResolverTest {
    @Test
    void shouldUseCacheUntilTtlExpires() {
        DnsResolver resolver = new DnsResolver(Map.of("a.com", List.of("1.1.1.1", "1.1.1.2")));
        String first = resolver.resolve("a.com", 1000);
        String second = resolver.resolve("a.com", 1000);
        assertEquals(first, second);
    }

    @Test
    void shouldRotateAfterTtlExpiry() throws InterruptedException {
        DnsResolver resolver = new DnsResolver(Map.of("a.com", List.of("1.1.1.1", "1.1.1.2")));
        String first = resolver.resolve("a.com", 50);
        Thread.sleep(70);
        String second = resolver.resolve("a.com", 50);
        assertNotEquals(first, second);
    }

    @Test
    void shouldReturnNullForUnknownDomain() {
        DnsResolver resolver = new DnsResolver(Map.of("a.com", List.of("1.1.1.1")));
        assertNull(resolver.resolve("missing.com", 1000));
    }
}
