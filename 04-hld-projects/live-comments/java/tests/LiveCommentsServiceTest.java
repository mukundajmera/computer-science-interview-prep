import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class LiveCommentsServiceTest {

    // v1-basic dummy implementation
    static class DummyLiveCommentsStreamService implements LiveCommentsStreamService {
        private final Map<String, String> comments = new HashMap<>();
        private int idCounter = 1;

        @Override
        public String create(String ownerId, String payload) {
            String id = String.valueOf(idCounter++);
            comments.put(id, payload);
            return id;
        }

        @Override
        public Optional<String> getById(String id) {
            return Optional.ofNullable(comments.get(id));
        }

        @Override
        public void mutate(String id, String mutationPayload, String idempotencyKey) {
            if (comments.containsKey(id)) {
                comments.put(id, comments.get(id) + mutationPayload);
            }
        }
    }

    // v2-scaled dummy implementation
    static class DummyLiveCommentsStreamServiceProjectionStore implements LiveCommentsStreamServiceProjectionStore {
        private final List<String> projections = new ArrayList<>();

        @Override
        public void upsertProjection(String id, String snapshot) {
            projections.add(snapshot);
        }

        @Override
        public List<String> recent(int limit) {
            return projections.subList(Math.max(0, projections.size() - limit), projections.size());
        }
    }

    static class DummyLiveCommentsStreamServiceV2 implements LiveCommentsStreamServiceV2 {
        private final Map<String, String> comments = new HashMap<>();
        private int idCounter = 1;
        private final LiveCommentsStreamServiceProjectionStore store = new DummyLiveCommentsStreamServiceProjectionStore();
        private final Set<String> processedKeys = new HashSet<>();

        private int createCalls = 0; // for rate limit simulation
        private long lastCreateTime = System.currentTimeMillis();

        @Override
        public String create(String ownerId, String payload) {
            // Simulate simple rate limiting
            long now = System.currentTimeMillis();
            if (now - lastCreateTime < 1000) {
                createCalls++;
                if (createCalls > 5) { // max 5 calls per second for testing
                    throw new RuntimeException("Rate limit exceeded");
                }
            } else {
                createCalls = 1;
                lastCreateTime = now;
            }

            String id = String.valueOf(idCounter++);
            comments.put(id, payload);
            store.upsertProjection(id, payload);
            return id;
        }

        @Override
        public void publishMutation(String id, String mutationPayload, String idempotencyKey) {
            if (processedKeys.contains(idempotencyKey)) return;
            processedKeys.add(idempotencyKey);

            if (comments.containsKey(id)) {
                String newValue = comments.get(id) + mutationPayload;
                comments.put(id, newValue);
                store.upsertProjection(id, newValue);
            }
        }

        @Override
        public List<String> readRecent(int limit) {
            return store.recent(limit);
        }
    }

    // v3-distributed dummy implementation
    static class DummyDistributedIdempotencyStore implements DistributedIdempotencyStore {
        private final Set<String> claimed = new HashSet<>();

        @Override
        public boolean claim(String key, long ttlMs) {
            return claimed.add(key);
        }
    }

    static class DummyDistributedLiveCommentsStreamService implements DistributedLiveCommentsStreamService {
        private final Map<String, String> comments = new HashMap<>();
        private final Map<String, List<String>> regionalViews = new HashMap<>();
        private int idCounter = 1;
        private final DistributedIdempotencyStore idempotencyStore = new DummyDistributedIdempotencyStore();
        private final List<String> pubsubTopics = new ArrayList<>(); // Simulate fanout topics

        @Override
        public String create(String ownerId, String payload, String region) {
            String id = String.valueOf(idCounter++);
            comments.put(id, payload);
            regionalViews.computeIfAbsent(region, k -> new ArrayList<>()).add(payload);
            return id;
        }

        @Override
        public void mutateWithReplayToken(String id, String mutationPayload, String idempotencyKey, String replayToken) {
            if (!idempotencyStore.claim(idempotencyKey, 1000)) return;

            if (comments.containsKey(id)) {
                String newValue = comments.get(id) + mutationPayload;
                comments.put(id, newValue);
                // Fanout logic simulation via pubsub topics to regions
                for (String region : regionalViews.keySet()) {
                     pubsubTopics.add("Fanout msg to " + region + ": " + newValue);
                     regionalViews.get(region).add(newValue);
                }
            }
        }

        @Override
        public List<String> readRegionView(String region, int limit) {
            List<String> views = regionalViews.getOrDefault(region, Collections.emptyList());
            return views.subList(Math.max(0, views.size() - limit), views.size());
        }

        public List<String> getPubsubMessages() {
            return pubsubTopics;
        }
    }

    @Test
    void testV1Basic() {
        LiveCommentsStreamService service = new DummyLiveCommentsStreamService();
        String id = service.create("user1", "Hello Live");
        assertTrue(service.getById(id).isPresent());
        assertEquals("Hello Live", service.getById(id).get());

        service.mutate(id, " - appended", "key1");
        assertEquals("Hello Live - appended", service.getById(id).get());
    }

    @Test
    void testV2ScaledWithRateLimit() {
        DummyLiveCommentsStreamServiceV2 service = new DummyLiveCommentsStreamServiceV2();
        String id = service.create("user1", "Hello V2");
        List<String> recent = service.readRecent(10);
        assertEquals(1, recent.size());
        assertEquals("Hello V2", recent.get(0));

        service.publishMutation(id, " (updated)", "idempotency-v2");
        recent = service.readRecent(10);
        assertEquals("Hello V2 (updated)", recent.get(recent.size() - 1));

        // Test idempotency
        service.publishMutation(id, " (updated)", "idempotency-v2");
        recent = service.readRecent(10);
        assertEquals("Hello V2 (updated)", recent.get(recent.size() - 1)); // no double update

        // Test rate limit
        boolean rateLimitExceptionThrown = false;
        try {
            for (int i = 0; i < 6; i++) {
                service.create("user1", "Spam");
            }
        } catch (RuntimeException e) {
            rateLimitExceptionThrown = true;
            assertEquals("Rate limit exceeded", e.getMessage());
        }
        assertTrue(rateLimitExceptionThrown, "Should have hit rate limit");
    }

    @Test
    void testV3DistributedPubSubFanout() {
        DummyDistributedLiveCommentsStreamService service = new DummyDistributedLiveCommentsStreamService();
        String id = service.create("user1", "Hello V3", "US-EAST");
        service.create("user2", "Hello EU", "EU-WEST"); // setup another region for fanout

        List<String> usEastView = service.readRegionView("US-EAST", 10);
        assertEquals(1, usEastView.size());
        assertEquals("Hello V3", usEastView.get(0));

        service.mutateWithReplayToken(id, " - dist update", "idempotency-v3", "token123");

        usEastView = service.readRegionView("US-EAST", 10);
        assertEquals("Hello V3 - dist update", usEastView.get(usEastView.size() - 1));

        // Verify fanout messages have been produced for both regions
        List<String> pubsubMessages = service.getPubsubMessages();
        assertEquals(2, pubsubMessages.size());
        assertTrue(pubsubMessages.stream().anyMatch(msg -> msg.contains("US-EAST")));
        assertTrue(pubsubMessages.stream().anyMatch(msg -> msg.contains("EU-WEST")));

        // Test idempotency claim fails on reuse
        service.mutateWithReplayToken(id, " - dist update", "idempotency-v3", "token456");
        usEastView = service.readRegionView("US-EAST", 10);
        assertEquals("Hello V3 - dist update", usEastView.get(usEastView.size() - 1));
    }
}
