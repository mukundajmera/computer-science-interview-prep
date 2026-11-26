import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class SimpleRedisCacheTest {

    private SimpleRedisCache cache;

    @BeforeEach
    public void setUp() {
        cache = new SimpleRedisCache();
    }

    @Test
    public void testSetAndGet() {
        cache.set("key1", "value1", 1000);
        assertEquals("value1", cache.get("key1"));
        
        // Non-existent key
        assertNull(cache.get("missing"));
    }

    @Test
    public void testTtlExpiration() throws InterruptedException {
        cache.set("key2", "value2", 100); // 100ms TTL
        assertEquals("value2", cache.get("key2"));
        
        Thread.sleep(150); // Wait for expiration
        
        assertNull(cache.get("key2"));
    }

    @Test
    public void testSetIfAbsent() {
        assertTrue(cache.setIfAbsent("key3", "value3", 1000));
        assertEquals("value3", cache.get("key3"));
        
        assertFalse(cache.setIfAbsent("key3", "newValue", 1000));
        assertEquals("value3", cache.get("key3")); // Original value should remain
    }

    @Test
    public void testIncrement() {
        assertEquals(1, cache.increment("counter1", 1, 1000));
        assertEquals(5, cache.increment("counter1", 4, 1000));
        assertEquals("5", cache.get("counter1"));
        assertEquals(3, cache.increment("counter1", -2, 1000));
        assertEquals("3", cache.get("counter1"));
    }

    @Test
    public void testIncrementValue() {
        long result = cache.increment("counter", 1, 1000);
        assertEquals(1L, result);
        assertEquals("1", cache.get("counter"));
        
        long result2 = cache.increment("counter", 5, 1000);
        assertEquals(6L, result2);
        assertEquals("6", cache.get("counter"));
    }
    
    @Test
    public void testInvalidTtl() {
        assertThrows(IllegalArgumentException.class, () -> cache.set("key4", "value4", 0));
        assertThrows(IllegalArgumentException.class, () -> cache.set("key4", "value4", -10));
    }
}
