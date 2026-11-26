import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.*;
import java.lang.reflect.Field;

import static org.junit.jupiter.api.Assertions.*;

public class CachedAvailabilityServiceTest {

    static class InMemoryAvailabilityCache implements CachedAvailabilityService.AvailabilityCache {
        private final Map<String, List<String>> cache = new HashMap<>();

        @Override
        public Optional<List<String>> get(String key) {
            return Optional.ofNullable(cache.get(key));
        }

        @Override
        public void put(String key, List<String> itemIds, int ttlSeconds) {
            cache.put(key, itemIds);
        }

        @Override
        public void invalidateCenter(String centerId) {
            cache.entrySet().removeIf(entry -> entry.getKey().startsWith(centerId + ":"));
        }
    }

    static class InMemoryAvailabilitySource implements CachedAvailabilityService.AvailabilitySource {
        private final Map<String, List<String>> latLngToCenters = new HashMap<>();
        private final Map<String, List<String>> centerItems = new HashMap<>();

        public void addCenters(double lat, double lng, List<String> centers) {
            latLngToCenters.put(lat + "," + lng, centers);
        }

        public void addItems(String centerId, List<String> items) {
            centerItems.put(centerId, items);
        }

        @Override
        public List<String> queryCenter(String centerId, String keyword, int page, int pageSize) {
            List<String> items = centerItems.getOrDefault(centerId, Collections.emptyList());
            List<String> result = new ArrayList<>();
            for (String item : items) {
                if (item.contains(keyword)) {
                    result.add(item);
                }
            }
            return result;
        }

        @Override
        public List<String> resolveNearbyCenters(double lat, double lng, int limit) {
            return latLngToCenters.getOrDefault(lat + "," + lng, Collections.emptyList());
        }
    }

    private InMemoryAvailabilityCache cache;
    private InMemoryAvailabilitySource source;
    private CachedAvailabilityService service;

    @BeforeEach
    void setUp() throws Exception {
        cache = new InMemoryAvailabilityCache();
        source = new InMemoryAvailabilitySource();
        service = new CachedAvailabilityService();

        try {
            Field cacheField = CachedAvailabilityService.class.getDeclaredField("cache");
            cacheField.setAccessible(true);
            cacheField.set(service, cache);

            Field sourceField = CachedAvailabilityService.class.getDeclaredField("source");
            sourceField.setAccessible(true);
            sourceField.set(service, source);
        } catch (NoSuchFieldException e) {
            // See AvailabilityServiceTest note
        }
    }

    @Test
    void testSearchReturnsFromSourceAndCaches() {
        source.addCenters(10.0, 20.0, Arrays.asList("center1"));
        source.addItems("center1", Arrays.asList("item1", "item2"));

        try {
            List<String> results = service.search(10.0, 20.0, "item1", 1, 10);
            assertEquals(1, results.size());
            assertEquals("item1", results.get(0));
            assertTrue(cache.get("center1:item1:1").isPresent());
        } catch (UnsupportedOperationException e) {
            fail("Search is not implemented");
        }
    }

    @Test
    void testSearchReturnsFromCache() {
        source.addCenters(10.0, 20.0, Arrays.asList("center1"));
        cache.put("center1:item1:1", Arrays.asList("cached_item1"), 60);

        try {
            List<String> results = service.search(10.0, 20.0, "item1", 1, 10);
            assertEquals(1, results.size());
            assertEquals("cached_item1", results.get(0));
        } catch (UnsupportedOperationException e) {
            fail("Search is not implemented");
        }
    }

    @Test
    void testOnInventoryDeltaInvalidatesCacheOnZeroQty() {
        source.addCenters(10.0, 20.0, Arrays.asList("center1"));
        cache.put("center1:item1:1", Arrays.asList("cached_item1"), 60);

        try {
            service.onInventoryDelta("center1", "item1", 0, Instant.now());
            assertFalse(cache.get("center1:item1:1").isPresent());
        } catch (UnsupportedOperationException e) {
            fail("onInventoryDelta is not implemented");
        }
    }
    
    @Test
    void testOnInventoryDeltaDoesNotInvalidateCacheOnPositiveQty() {
        source.addCenters(10.0, 20.0, Arrays.asList("center1"));
        cache.put("center1:item1:1", Arrays.asList("cached_item1"), 60);

        try {
            service.onInventoryDelta("center1", "item1", 5, Instant.now());
            assertTrue(cache.get("center1:item1:1").isPresent());
        } catch (UnsupportedOperationException e) {
            fail("onInventoryDelta is not implemented");
        }
    }
}
