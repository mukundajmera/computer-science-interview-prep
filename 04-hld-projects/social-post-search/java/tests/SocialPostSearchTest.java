import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.stream.Collectors;

public class SocialPostSearchTest {

    // v1-basic Dummy Implementation
    static class InMemorySocialPostSearchService implements SocialPostSearchService {
        private final Map<String, String> dataStore = new HashMap<>();
        private final Map<String, List<String>> invertedIndex = new HashMap<>();

        @Override
        public String create(String ownerId, String payload) {
            String id = UUID.randomUUID().toString();
            dataStore.put(id, payload);

            // Simple tokenization for search by keyword
            String[] tokens = payload.toLowerCase().split("\\W+");
            for (String token : tokens) {
                if (token.isEmpty()) continue;
                invertedIndex.computeIfAbsent(token, k -> new ArrayList<>()).add(id);
            }
            return id;
        }

        @Override
        public Optional<String> getById(String id) {
            return Optional.ofNullable(dataStore.get(id));
        }

        @Override
        public void mutate(String id, String mutationPayload, String idempotencyKey) {
            if (dataStore.containsKey(id)) {
                dataStore.put(id, dataStore.get(id) + " " + mutationPayload);
            }
        }

        // Exposing a simple search for the test
        public List<String> searchByKeyword(String keyword) {
            List<String> ids = invertedIndex.getOrDefault(keyword.toLowerCase(), Collections.emptyList());
            return ids.stream().map(dataStore::get).collect(Collectors.toList());
        }
    }

    // v2-scaled Dummy Implementation
    static class InMemorySocialPostSearchServiceV2 implements SocialPostSearchServiceV2 {
        private final Map<String, String> dataStore = new HashMap<>();
        private final Map<String, Integer> relevanceScores = new HashMap<>();
        private final Map<String, String> cache = new HashMap<>();

        @Override
        public String create(String ownerId, String payload) {
            String id = UUID.randomUUID().toString();
            dataStore.put(id, payload);
            relevanceScores.put(id, 0);
            cache.put(id, payload); // Cache the latest payload
            return id;
        }

        @Override
        public void publishMutation(String id, String mutationPayload, String idempotencyKey) {
            if (dataStore.containsKey(id)) {
                // E.g., mutation could be a like, which increases relevance
                if (mutationPayload.contains("like")) {
                    relevanceScores.put(id, relevanceScores.get(id) + 1);
                }
            }
        }

        @Override
        public List<String> readRecent(int limit) {
            return dataStore.entrySet().stream()
                .sorted((a, b) -> Integer.compare(relevanceScores.get(b.getKey()), relevanceScores.get(a.getKey())))
                .limit(limit)
                .map(Map.Entry::getValue)
                .collect(Collectors.toList());
        }
    }

    // v3-distributed Dummy Implementation
    static class InMemoryDistributedSocialPostSearchService implements DistributedSocialPostSearchService {
        private final Map<String, Map<String, String>> regionalStores = new HashMap<>();
        private final Map<String, Boolean> idempotencyKeys = new HashMap<>();

        @Override
        public String create(String ownerId, String payload, String region) {
            String id = UUID.randomUUID().toString();
            regionalStores.computeIfAbsent(region, k -> new HashMap<>()).put(id, payload);
            return id;
        }

        @Override
        public void mutateWithReplayToken(String id, String mutationPayload, String idempotencyKey, String replayToken) {
            if (idempotencyKeys.putIfAbsent(idempotencyKey, true) != null) {
                return; // Already processed
            }
            // Mutate logic...
        }

        @Override
        public List<String> readRegionView(String region, int limit) {
            Map<String, String> regionData = regionalStores.getOrDefault(region, Collections.emptyMap());
            return regionData.values().stream()
                .limit(limit)
                .collect(Collectors.toList());
        }

        // Expose a method to merge search results across shards for testing
        public List<String> distributedSearchAndMerge() {
            List<String> allResults = new ArrayList<>();
            for (Map<String, String> regionData : regionalStores.values()) {
                allResults.addAll(regionData.values());
            }
            return allResults;
        }
    }

    @Test
    public void testV1BasicSearchByKeyword() {
        InMemorySocialPostSearchService service = new InMemorySocialPostSearchService();
        String id1 = service.create("user1", "Hello world, this is a social post search test");
        String id2 = service.create("user2", "Another post with keyword hello");

        assertTrue(service.getById(id1).isPresent());

        List<String> searchResults = service.searchByKeyword("hello");
        assertEquals(2, searchResults.size());
        assertTrue(searchResults.contains("Hello world, this is a social post search test"));
        assertTrue(searchResults.contains("Another post with keyword hello"));

        List<String> specificSearch = service.searchByKeyword("search");
        assertEquals(1, specificSearch.size());
        assertEquals("Hello world, this is a social post search test", specificSearch.get(0));
    }

    @Test
    public void testV2ScaledCachingAndRelevance() {
        InMemorySocialPostSearchServiceV2 service = new InMemorySocialPostSearchServiceV2();
        String id1 = service.create("user1", "Post 1");
        String id2 = service.create("user2", "Post 2");
        String id3 = service.create("user3", "Post 3");

        // Add some 'likes'
        service.publishMutation(id2, "like", "key1");
        service.publishMutation(id2, "like", "key2");
        service.publishMutation(id1, "like", "key3");

        // Read recent should be ordered by relevance (likes) -> Post 2, Post 1, Post 3
        List<String> recentPosts = service.readRecent(3);
        assertEquals(3, recentPosts.size());
        assertEquals("Post 2", recentPosts.get(0));
        assertEquals("Post 1", recentPosts.get(1));
        assertEquals("Post 3", recentPosts.get(2));
    }

    @Test
    public void testV3DistributedShardSearchMerge() {
        InMemoryDistributedSocialPostSearchService service = new InMemoryDistributedSocialPostSearchService();

        service.create("user1", "Post in US-East", "US-EAST");
        service.create("user2", "Another Post in US-East", "US-EAST");
        service.create("user3", "Post in EU-West", "EU-WEST");

        List<String> usEastView = service.readRegionView("US-EAST", 10);
        assertEquals(2, usEastView.size());

        List<String> euWestView = service.readRegionView("EU-WEST", 10);
        assertEquals(1, euWestView.size());

        List<String> mergedResults = service.distributedSearchAndMerge();
        assertEquals(3, mergedResults.size());
        assertTrue(mergedResults.contains("Post in US-East"));
        assertTrue(mergedResults.contains("Another Post in US-East"));
        assertTrue(mergedResults.contains("Post in EU-West"));

        // Idempotency check
        service.mutateWithReplayToken("id", "mutation", "idem-key-1", "token1");
        service.mutateWithReplayToken("id", "mutation", "idem-key-1", "token2"); // Should be ignored
    }
}
