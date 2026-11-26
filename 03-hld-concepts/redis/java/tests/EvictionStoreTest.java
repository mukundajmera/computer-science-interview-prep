import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v2.EvictionStore;

public class EvictionStoreTest {
    @Test
    public void testAllkeysLru() {
        EvictionStore store = new EvictionStore(2, "allkeys-lru");
        store.set("a", 1, null);
        store.set("b", 2, null);
        store.get("a"); // a is most recently used
        store.set("c", 3, null); // should evict b

        assertEquals(1, store.get("a"));
        assertNull(store.get("b"));
        assertEquals(3, store.get("c"));
    }

    @Test
    public void testVolatileLru() {
        EvictionStore store = new EvictionStore(2, "volatile-lru");
        store.set("a", 1, null); // no ttl
        store.set("b", 2, 10000L); // ttl
        store.set("c", 3, null); // should evict b

        assertEquals(1, store.get("a"));
        assertNull(store.get("b"));
        assertEquals(3, store.get("c"));
    }

    @Test
    public void testVolatileLruOom() {
        EvictionStore store = new EvictionStore(2, "volatile-lru");
        store.set("a", 1, null);
        store.set("b", 2, null);
        assertThrows(OutOfMemoryError.class, () -> {
            store.set("c", 3, null);
        });
    }

    @Test
    public void testTtlExpiration() throws InterruptedException {
        EvictionStore store = new EvictionStore(2, "allkeys-lru");
        store.set("a", 1, 100L);
        Thread.sleep(150);
        assertNull(store.get("a"));
    }
}
