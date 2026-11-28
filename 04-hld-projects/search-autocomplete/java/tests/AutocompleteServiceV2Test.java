import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class AutocompleteServiceV2Test {

    // Fixed timestamps keep the sliding-window math deterministic.
    // bucketSeconds=60, windowBuckets=5 -> window covers buckets
    // (now/60 - 4) .. (now/60). 0 is bucket 0; 1000 is bucket 16;
    // 1301 is bucket 21, whose window starts at bucket 17.
    private static final long T_OLD = 0L;
    private static final long T_NOW = 1000L;
    private static final long T_EXPIRED = 1301L;

    private Set<String> profanityBlacklist;

    @BeforeEach
    public void setUp() {
        profanityBlacklist = new HashSet<>(Arrays.asList("badword", "profane"));
    }

    // ---------- v1 parity: every v1 behavior still holds on the v2 track ----------

    @Test
    public void testTop5SuggestionsRankedByFrequency() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        QueryAggregatorV2 aggregator = new QueryAggregatorV2(60L, 5);

        aggregator.addQuery("apple", T_NOW);
        aggregator.addQuery("apple", T_NOW);
        aggregator.addQuery("apple", T_NOW); // 3

        aggregator.addQuery("app", T_NOW);
        aggregator.addQuery("app", T_NOW);
        aggregator.addQuery("app", T_NOW);
        aggregator.addQuery("app", T_NOW); // 4

        aggregator.addQuery("application", T_NOW);
        aggregator.addQuery("application", T_NOW); // 2

        aggregator.addQuery("append", T_NOW); // 1
        aggregator.addQuery("appreciate", T_NOW); // 1
        aggregator.addQuery("apply", T_NOW); // 1
        aggregator.addQuery("apt", T_NOW); // 1 (different prefix)

        service.rebuildTrie(aggregator.getAggregatedFrequencies());

        List<String> suggestions = service.getSuggestions("app");
        assertEquals(5, suggestions.size());
        assertEquals("app", suggestions.get(0));
        assertEquals("apple", suggestions.get(1));
        assertEquals("application", suggestions.get(2));
    }

    @Test
    public void testPrefixLengthCapping() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        Map<String, Long> frequencies = new HashMap<>();

        String longPrefix = "a".repeat(50);
        String veryLongQuery = "a".repeat(60);
        frequencies.put(veryLongQuery, 10L);

        service.rebuildTrie(frequencies);

        List<String> suggestions = service.getSuggestions(longPrefix);
        assertEquals(1, suggestions.size());
        assertEquals(veryLongQuery, suggestions.get(0));

        List<String> suggestionsOverLimit = service.getSuggestions("a".repeat(70));
        assertEquals(1, suggestionsOverLimit.size());
        assertEquals(veryLongQuery, suggestionsOverLimit.get(0));
    }

    @Test
    public void testProfanityBlacklistFiltering() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        Map<String, Long> frequencies = new HashMap<>();

        frequencies.put("goodword", 10L);
        frequencies.put("badword", 20L);
        frequencies.put("profane language", 5L);
        frequencies.put("proper language", 15L);

        service.rebuildTrie(frequencies);

        List<String> suggestions = service.getSuggestions("pro");
        assertEquals(1, suggestions.size());
        assertEquals("proper language", suggestions.get(0));

        List<String> badSuggestions = service.getSuggestions("bad");
        assertEquals(0, badSuggestions.size());
    }

    @Test
    public void testBatchFrequencyAggregationSwap() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);

        Map<String, Long> freq1 = new HashMap<>();
        freq1.put("test", 10L);
        service.rebuildTrie(freq1);

        assertEquals(1, service.getSuggestions("te").size());
        assertEquals("test", service.getSuggestions("te").get(0));

        Map<String, Long> freq2 = new HashMap<>();
        freq2.put("tester", 20L);
        service.rebuildTrie(freq2); // Atomic swap

        List<String> suggestions = service.getSuggestions("te");
        assertEquals(1, suggestions.size());
        assertEquals("tester", suggestions.get(0));
    }

    @Test
    public void testEmptyAndUnknownPrefixHandling() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        Map<String, Long> frequencies = new HashMap<>();
        frequencies.put("hello", 10L);
        service.rebuildTrie(frequencies);

        assertTrue(service.getSuggestions("").isEmpty());
        assertTrue(service.getSuggestions(null).isEmpty());
        assertTrue(service.getSuggestions("unknown").isEmpty());
    }

    // ---------- v2 improvement 1: trending fast-path (FOLLOW-UPS.md #1) ----------

    @Test
    public void testTrendingQueryOvertakesBatchLeader() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        QueryAggregatorV2 aggregator = service.getAggregator();

        for (int i = 0; i < 20; i++) {
            aggregator.addQuery("apple", T_OLD);
        }
        for (int i = 0; i < 5; i++) {
            aggregator.addQuery("applestore", T_OLD);
        }
        for (int i = 0; i < 3; i++) {
            aggregator.addQuery("applestore", T_NOW);
        }

        service.rebuildTrie(aggregator.getAggregatedFrequencies());

        // Batch view: apple 20 beats applestore 8.
        List<String> plain = service.getSuggestions("app");
        assertEquals("apple", plain.get(0));

        // Blended at T_NOW: apple = 20 + 50*0 = 20;
        // applestore = 8 + 50*3 = 158 -> trending spike wins.
        List<String> blended = service.getBlendedSuggestions("app", T_NOW, null);
        assertEquals("applestore", blended.get(0));
        assertEquals("apple", blended.get(1));
    }

    @Test
    public void testTrendingWindowExpiresOldQueries() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        QueryAggregatorV2 aggregator = service.getAggregator();

        for (int i = 0; i < 10; i++) {
            aggregator.addQuery("zoo", T_OLD);
        }
        for (int i = 0; i < 3; i++) {
            aggregator.addQuery("zoom call", T_NOW);
        }

        service.rebuildTrie(aggregator.getAggregatedFrequencies());

        // Inside the window: zoom call = 3 + 50*3 = 153 beats zoo = 10.
        List<String> spiking = service.getBlendedSuggestions("zo", T_NOW, null);
        assertEquals("zoom call", spiking.get(0));

        // One bucket past the window: recent count is 0, batch order returns.
        List<String> settled = service.getBlendedSuggestions("zo", T_EXPIRED, null);
        assertEquals("zoo", settled.get(0));
    }

    @Test
    public void testBlendedMatchesPlainWhenNothingTrending() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        QueryAggregatorV2 aggregator = service.getAggregator();

        for (int i = 0; i < 3; i++) {
            aggregator.addQuery("apple", T_OLD);
        }
        for (int i = 0; i < 4; i++) {
            aggregator.addQuery("app", T_OLD);
        }
        for (int i = 0; i < 2; i++) {
            aggregator.addQuery("application", T_OLD);
        }

        service.rebuildTrie(aggregator.getAggregatedFrequencies());

        // All counts are far outside the window, so blending changes nothing.
        List<String> plain = service.getSuggestions("app");
        List<String> blended = service.getBlendedSuggestions("app", T_EXPIRED, null);
        assertEquals(plain.size(), blended.size());
        assertEquals(plain.get(0), blended.get(0));
        assertEquals(plain.get(1), blended.get(1));
        assertEquals(plain.get(2), blended.get(2));
    }

    @Test
    public void testTrendingCandidatesSkipProfanity() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        // Aggregator does not filter at write time (same as v1); the read
        // path must still keep profane trending queries out.
        service.getAggregator().addQuery("badword deals", T_NOW);

        service.rebuildTrie(service.getAggregator().getAggregatedFrequencies());

        assertTrue(service.getBlendedSuggestions("bad", T_NOW, null).isEmpty());
    }

    // ---------- v2 improvement 2: personalized autocomplete (FOLLOW-UPS variants) ----------

    @Test
    public void testPersonalHistoryBoostsOwnQueries() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        QueryAggregatorV2 aggregator = service.getAggregator();

        for (int i = 0; i < 20; i++) {
            aggregator.addQuery("apple", T_OLD);
        }
        for (int i = 0; i < 3; i++) {
            service.recordUserQuery("u1", "apple pie", T_OLD);
        }

        service.rebuildTrie(aggregator.getAggregatedFrequencies());

        // For u1: apple pie = 3 + 10*3 = 33 beats apple = 20.
        List<String> blended = service.getBlendedSuggestions("app", T_EXPIRED, "u1");
        assertEquals("apple pie", blended.get(0));
    }

    @Test
    public void testPersonalBoostNotSharedBetweenUsers() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(profanityBlacklist);
        QueryAggregatorV2 aggregator = service.getAggregator();

        for (int i = 0; i < 20; i++) {
            aggregator.addQuery("apple", T_OLD);
        }
        for (int i = 0; i < 3; i++) {
            service.recordUserQuery("u1", "apple pie", T_OLD);
        }

        service.rebuildTrie(aggregator.getAggregatedFrequencies());

        // u2 gets no personal boost: apple pie = 3 + 10*0 = 3 loses to apple = 20.
        List<String> blended = service.getBlendedSuggestions("app", T_EXPIRED, "u2");
        assertEquals("apple", blended.get(0));
    }

    @Test
    public void testUserHistoryEvictsOldestBeyondCap() {
        AutocompleteServiceV2 service = new AutocompleteServiceV2(
                profanityBlacklist, 50L, 10L, 3, 60L, 5);

        service.recordUserQuery("u1", "xa", T_OLD);
        service.recordUserQuery("u1", "xb", T_OLD);
        service.recordUserQuery("u1", "xc", T_OLD);
        service.recordUserQuery("u1", "xd", T_OLD);

        service.rebuildTrie(service.getAggregator().getAggregatedFrequencies());

        // "xa" was evicted, so it scores batch-only (1) while the capped
        // history still boosts xb/xc/xd to 1 + 10 = 11 each (lexicographic tie).
        List<String> blended = service.getBlendedSuggestions("x", T_EXPIRED, "u1");
        assertEquals(Arrays.asList("xb", "xc", "xd", "xa"), blended);
    }

    // ---------- v2 improvement 3: prefix-range sharding (FOLLOW-UPS.md #2) ----------

    @Test
    public void testShardRouterRoutesAndServes() {
        PrefixShardRouterV2 router = new PrefixShardRouterV2(profanityBlacklist);

        router.addQuery("apple", T_OLD);
        router.addQuery("mango", T_OLD);
        router.rebuildAll();

        // Boundaries a,d,g,j,m,p,s,v,y: 'a' -> shard 0 (a-c), 'm' -> shard 4 (m-o).
        assertEquals(0, router.shardIndex("apple"));
        assertEquals(4, router.shardIndex("mango"));

        assertEquals(Collections.singletonList("apple"), router.getSuggestions("app"));
        assertEquals(Collections.singletonList("mango"), router.getSuggestions("man"));
        // Each shard only holds its own range's queries.
        assertTrue(router.getShard(0).getSuggestions("man").isEmpty());
    }

    @Test
    public void testShardRouterCatchAllAndEmptyPrefix() {
        PrefixShardRouterV2 router = new PrefixShardRouterV2(profanityBlacklist);

        // Non-letter prefixes land on the catch-all (last) shard.
        assertEquals(router.shardCount() - 1, router.shardIndex("123abc"));
        router.addQuery("123abc", T_OLD);
        router.rebuildAll();
        assertEquals(Collections.singletonList("123abc"), router.getSuggestions("123"));

        // Empty prefix is a no-op everywhere.
        assertEquals(-1, router.shardIndex(""));
        router.addQuery("", T_OLD);
        assertTrue(router.getSuggestions("").isEmpty());
        assertTrue(router.getBlendedSuggestions("", T_NOW, null).isEmpty());
    }
}
