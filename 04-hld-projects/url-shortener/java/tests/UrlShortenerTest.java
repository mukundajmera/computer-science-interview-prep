import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.time.Instant;
import java.util.Optional;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.ArrayList;

public class UrlShortenerTest {

    @Test
    public void testV1BasicShortening() throws Exception {
        UrlRepository repository = new InMemoryUrlRepository();
        ShortCodeGenerator codeGenerator = new CounterBasedGenerator();
        UrlShorteningService service = new BasicUrlShorteningService(repository, codeGenerator, "http://short.ly");

        CreateUrlRequest request = new CreateUrlRequest("https://www.example.com/very/long/url/path", "custom-alias", null, "user1");
        CreateUrlResponse response = service.createShortUrl(request);

        assertNotNull(response);
        assertEquals("custom-alias", response.getShortCode());
        assertEquals("http://short.ly/custom-alias", response.getShortUrl());

        Optional<String> originalUrl = service.getOriginalUrl("custom-alias");
        assertTrue(originalUrl.isPresent());
        assertEquals("https://www.example.com/very/long/url/path", originalUrl.get());

        assertThrows(AliasAlreadyExistsException.class, () -> {
            service.createShortUrl(request);
        });
    }

    @Test
    public void testV2ScaledCachingAndAnalytics() throws Exception {
        UrlRepository repository = new InMemoryUrlRepository();
        KeyRepository keyRepo = new InMemoryKeyRepository();
        ShortCodeGenerator codeGenerator = new KeyGenerationService(keyRepo);
        UrlCache cache = new InMemoryUrlCache();
        MessageQueue messageQueue = new InMemoryMessageQueue();

        CachedUrlShorteningService service = new CachedUrlShorteningService(
            repository, codeGenerator, cache, messageQueue, "http://short.ly"
        );

        CreateUrlRequest request = new CreateUrlRequest("https://www.google.com");
        CreateUrlResponse response = service.createShortUrl(request);

        String shortCode = response.getShortCode();
        assertNotNull(shortCode);

        assertTrue(cache.exists(shortCode));
        assertEquals("https://www.google.com", cache.get(shortCode).get());

        Optional<String> originalUrl = service.getOriginalUrl(shortCode);
        assertTrue(originalUrl.isPresent());

        if (messageQueue instanceof InMemoryMessageQueue) {
            InMemoryMessageQueue memQueue = (InMemoryMessageQueue) messageQueue;
            List<ClickEvent> events = memQueue.drain();
            assertEquals(1, events.size());
            assertEquals(shortCode, events.get(0).getShortCode());
        }
    }

    @Test
    public void testV3DistributedRoutingAndCache() throws Exception {
        ConsistentHashRouter router = new ConsistentHashRouter(Set.of("us-east", "us-west", "eu-central"));
        String region1 = router.getRegion("shortCode1");
        String region2 = router.getRegion("shortCode2");
        assertNotNull(region1);
        assertNotNull(region2);

        Map<String, RegionalService> regionalServices = new HashMap<>();
        regionalServices.put("us-east", new DummyRegionalService("us-east"));
        regionalServices.put("us-west", new DummyRegionalService("us-west"));

        DistributedCache cache = new DummyDistributedCache();

        DistributedUrlService service = new MultiRegionUrlService(
            "us-east", regionalServices, cache, "http://short.ly"
        );

        Optional<String> resolved = service.getOriginalUrl("someCode");
        assertFalse(resolved.isPresent());

        CreateUrlRequest request = new CreateUrlRequest("https://test.com");
        CreateUrlResponse response = service.createShortUrl(request);
        assertEquals("dummy-code", response.getShortCode());
    }

    static class InMemoryUrlRepository implements UrlRepository {
        private Map<String, UrlEntity> storage = new HashMap<>();
        @Override public void save(UrlEntity entity) {
            try {
                java.lang.reflect.Field field = UrlEntity.class.getDeclaredField("shortCode");
                field.setAccessible(true);
                String shortCode = (String) field.get(entity);
                storage.put(shortCode, entity);
            } catch (Exception e) { throw new RuntimeException(e); }
        }
        @Override public Optional<UrlEntity> findByShortCode(String shortCode) {
            return Optional.ofNullable(storage.get(shortCode));
        }
        @Override public Optional<UrlEntity> findByLongUrl(String longUrl) {
            return storage.values().stream()
                .filter(e -> {
                    try {
                        java.lang.reflect.Field field = UrlEntity.class.getDeclaredField("longUrl");
                        field.setAccessible(true);
                        return longUrl.equals(field.get(e));
                    } catch (Exception ex) { return false; }
                })
                .findFirst();
        }
        @Override public boolean existsByShortCode(String shortCode) {
            return storage.containsKey(shortCode);
        }
        @Override public boolean deleteByShortCode(String shortCode) {
            return storage.remove(shortCode) != null;
        }
        @Override public void incrementClickCount(String shortCode) {}
        @Override public List<UrlEntity> findByUserId(String userId) {
            return new ArrayList<>();
        }
    }

    static class InMemoryKeyRepository implements KeyRepository {
        private List<String> availableKeys = new ArrayList<>();
        private List<String> usedKeys = new ArrayList<>();
        public InMemoryKeyRepository() {
            availableKeys.add("key1");
            availableKeys.add("key2");
            availableKeys.add("key3");
        }
        @Override public List<String> getUnusedKeys(int limit) {
            List<String> res = new ArrayList<>();
            for(int i=0; i<Math.min(limit, availableKeys.size()); i++) {
                res.add(availableKeys.remove(0));
            }
            return res;
        }
        @Override public void markAsUsed(String key) { usedKeys.add(key); }
        @Override public void addKeys(List<String> keys) { availableKeys.addAll(keys); }
        @Override public int getUnusedKeyCount() { return availableKeys.size(); }
    }

    static class InMemoryUrlCache implements UrlCache {
        private Map<String, String> cache = new HashMap<>();
        @Override public Optional<String> get(String shortCode) { return Optional.ofNullable(cache.get(shortCode)); }
        @Override public void put(String shortCode, String longUrl, int ttlSeconds) { cache.put(shortCode, longUrl); }
        @Override public void evict(String shortCode) { cache.remove(shortCode); }
        @Override public boolean exists(String shortCode) { return cache.containsKey(shortCode); }
    }

    static class InMemoryMessageQueue implements MessageQueue {
        private List<ClickEvent> events = new ArrayList<>();
        @Override public void publishClickEvent(ClickEvent event) { events.add(event); }
        public List<ClickEvent> drain() {
            List<ClickEvent> copy = new ArrayList<>(events);
            events.clear();
            return copy;
        }
    }

    static class DummyRegionalService implements RegionalService {
        private final String region;
        public DummyRegionalService(String region) { this.region = region; }
        @Override public CreateUrlResponse createUrl(CreateUrlRequest request, String baseUrl) {
            return new CreateUrlResponse("dummy-code", baseUrl, request.getLongUrl(), Instant.now(), null);
        }
        @Override public Optional<String> getUrl(String shortCode) { return Optional.empty(); }
        @Override public Optional<UrlStats> getStats(String shortCode) { return Optional.empty(); }
        @Override public boolean deleteUrl(String shortCode) { return false; }
        @Override public void replicate(String shortCode, String longUrl) {}
        @Override public String getRegion() { return region; }
    }

    static class DummyDistributedCache implements DistributedCache {
        private Map<String, String> local = new HashMap<>();
        @Override public Optional<String> getLocal(String key) { return Optional.ofNullable(local.get(key)); }
        @Override public Optional<String> get(String key) { return Optional.empty(); }
        @Override public void put(String key, String value, int ttlSeconds) { local.put(key, value); }
        @Override public void evict(String key) { local.remove(key); }
        @Override public void invalidateGlobal(String key) { local.remove(key); }
        @Override public boolean exists(String key) { return local.containsKey(key); }
        @Override public CacheStats getStats() { return new CacheStats(0, 0, 0); }
    }
}
